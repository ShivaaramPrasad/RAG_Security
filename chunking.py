"""Four chunking strategies over the same cleaned Markdown body.

Every chunker returns a list of dicts:
  text          text that is embedded / stored (markdown strategy prefixes the heading path)
  start, end    character span of the raw content inside the cleaned body (for boundary metrics)
  heading_path  'Doc title > H2 > H3' that the chunk belongs to
"""
import re
import numpy as np

# ----------------------------------------------------------------------------- cleaning
FRONT = re.compile(r'\A---\n(.*?)\n---\n', re.S)
SHORTCODE = re.compile(r'\{\{[<%]\s*(/?)\s*([\w-]+)([^>%]*?)\s*[>%]\}\}')
ADMON = {'note': '**Note:**', 'warning': '**Warning:**', 'caution': '**Caution:**'}


def _shortcode(m):
    closing, name, args = m.group(1), m.group(2), m.group(3)
    if name in ADMON and not closing:
        return ADMON[name]
    if name == 'glossary_tooltip':
        t = re.search(r'text="([^"]+)"', args)
        return t.group(1) if t else ''
    if name in ('code_sample', 'codenew'):
        f = re.search(r'file="([^"]+)"', args)
        return f'(example manifest: {f.group(1)})' if f else ''
    return ''


def clean_markdown(raw):
    """Strip Hugo front matter + shortcodes. Returns (title, body)."""
    title = ''
    m = FRONT.match(raw)
    if m:
        t = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', m.group(1), re.M)
        title = t.group(1) if t else ''
        raw = raw[m.end():]
    body = SHORTCODE.sub(_shortcode, raw)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)  # Hugo section markers such as <!-- overview -->
    body = re.sub(r'[ \t]+\n', '\n', body)
    body = re.sub(r'\n{3,}', '\n\n', body).strip() + '\n'
    return title, body


# ----------------------------------------------------------------------------- block parser
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')


def parse_blocks(body, title):
    """Split into blocks (heading line / paragraph / list / fenced code intact / table).
    Returns list of dict(start,end,text,kind,path,level)."""
    blocks, stack, cur = [], [], None
    in_fence, pos = False, 0

    def flush(end):
        nonlocal cur
        if cur:
            cur['end'] = end
            cur['text'] = body[cur['start']:end].rstrip('\n')
            cur['end'] = cur['start'] + len(cur['text'])
            blocks.append(cur)
            cur = None

    def path():
        return ' > '.join(x for x in [title] + [t for _, t in stack] if x)

    for line in body.splitlines(keepends=True):
        s, e = pos, pos + len(line)
        pos = e
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            if cur is None:
                cur = dict(start=s, kind='code', path=path(), level=0)
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        h = HEADING.match(line)
        if h:
            flush(s)
            level, text = len(h.group(1)), re.sub(r'\s*\{#[^}]*\}', '', h.group(2))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, text))
            blocks.append(dict(start=s, end=e - (1 if line.endswith('\n') else 0), text=line.strip(),
                               kind='heading', path=path(), level=level))
            continue
        if not stripped:
            flush(s)
            continue
        if cur is None:
            cur = dict(start=s, kind='text', path=path(), level=0)
    flush(len(body))
    return blocks


# ----------------------------------------------------------------------------- 1. fixed
def fixed_chunks(body, title, size=1000, overlap=150):
    out, i = [], 0
    while i < len(body):
        j = min(i + size, len(body))
        out.append(dict(text=body[i:j], start=i, end=j, heading_path=title))
        if j == len(body):
            break
        i = j - overlap
    return _label(out, body, title)


# ----------------------------------------------------------------------------- 2. recursive
SEPS = ['\n## ', '\n### ', '\n#### ', '\n\n', '\n', '. ', ' ']


def _split_span(body, s, e, seps, size):
    if e - s <= size:
        return [(s, e)]
    if not seps:
        return [(i, min(i + size, e)) for i in range(s, e, size)]
    sep, rest = seps[0], seps[1:]
    cuts, i = [s], s
    while True:
        k = body.find(sep, i, e)
        if k == -1:
            break
        cut = k + 1 if sep.startswith('\n#') else k + len(sep)
        if s < cut < e:
            cuts.append(cut)
        i = k + len(sep)
    cuts.append(e)
    if len(cuts) == 2:
        return _split_span(body, s, e, rest, size)
    out = []
    for a, b in zip(cuts, cuts[1:]):
        out.extend(_split_span(body, a, b, rest, size) if b - a > size else [(a, b)])
    return out


def recursive_chunks(body, title, size=1000, overlap=150):
    spans = _split_span(body, 0, len(body), SEPS, size)
    chunks, cur = [], []
    for sp in spans:
        if cur and sp[1] - cur[0][0] > size:
            chunks.append((cur[0][0], cur[-1][1]))
            keep, total = [], 0
            for piece in reversed(cur):
                if total + (piece[1] - piece[0]) > overlap:
                    break
                keep.insert(0, piece)
                total += piece[1] - piece[0]
            cur = keep
            if cur and sp[1] - cur[0][0] > size:
                cur = []
        cur.append(sp)
    if cur:
        chunks.append((cur[0][0], cur[-1][1]))
    out = [dict(text=body[a:b], start=a, end=b, heading_path=title) for a, b in chunks if body[a:b].strip()]
    return _label(out, body, title)


# ----------------------------------------------------------------------------- 3. markdown structure-aware
def markdown_chunks(body, title, max_chars=1200, min_chars=250):
    """Section = heading + following blocks. A section that fits is one chunk; a larger one is
    packed block by block (code fences/tables never split). Every chunk is prefixed with its
    heading path. Tiny sections are merged forward instead of becoming stray fragments."""
    blocks = _split_oversized(parse_blocks(body, title), max_chars)
    out, group = [], []  # group: blocks being packed

    def emit():
        nonlocal group
        if not group:
            return
        raw = '\n\n'.join(b['text'] for b in group)
        # heading path of the first content block (falls back to the heading itself)
        path = next((b['path'] for b in group if b['kind'] != 'heading'), group[0]['path'])
        out.append(dict(text=f'{path}\n\n{raw}', start=group[0]['start'], end=group[-1]['end'],
                        heading_path=path, raw_len=len(raw)))
        group = []

    for b in blocks:
        size = sum(len(x['text']) + 2 for x in group)
        if b['kind'] == 'heading':
            # new section: flush unless what we have is still tiny
            if group and size >= min_chars:
                emit()
            group.append(b)
            continue
        if group and size + len(b['text']) > max_chars and any(x['kind'] != 'heading' for x in group):
            emit()
            # keep the nearest heading as context only through the path prefix
        group.append(b)
    emit()
    return out


# ----------------------------------------------------------------------------- 4. semantic
def semantic_chunks(body, title, embed_fn, percentile=85, max_chars=1500, min_chars=300):
    """Split where cosine distance between adjacent blocks jumps (above the doc's Nth percentile)."""
    blocks = [b for b in parse_blocks(body, title)]
    if not blocks:
        return []
    vecs = np.array(embed_fn([b['text'][:600] for b in blocks]))
    dist = 1 - np.sum(vecs[:-1] * vecs[1:], axis=1) / (
        np.linalg.norm(vecs[:-1], axis=1) * np.linalg.norm(vecs[1:], axis=1))
    thr = np.percentile(dist, percentile) if len(dist) else 1
    out, group = [], [blocks[0]]

    def emit():
        raw = '\n\n'.join(b['text'] for b in group)
        out.append(dict(text=raw, start=group[0]['start'], end=group[-1]['end'],
                        heading_path=group[0]['path']))

    for i, b in enumerate(blocks[1:]):
        size = sum(len(x['text']) + 2 for x in group)
        if (dist[i] > thr and size >= min_chars) or size + len(b['text']) > max_chars:
            emit()
            group = []
        group.append(b)
    emit()
    return out


# ----------------------------------------------------------------------------- helpers
def _split_oversized(blocks, max_chars):
    """Break a huge non-code block (long list/table) on line boundaries. Code fences stay whole."""
    out = []
    for b in blocks:
        if b['kind'] != 'text' or len(b['text']) <= max_chars:
            out.append(b)
            continue
        buf, start = '', b['start']
        for line in b['text'].split('\n'):
            if buf and len(buf) + len(line) + 1 > max_chars:
                out.append({**b, 'start': start, 'end': start + len(buf), 'text': buf})
                start += len(buf) + 1
                buf = ''
            buf = buf + '\n' + line if buf else line
        if buf:
            out.append({**b, 'start': start, 'end': start + len(buf), 'text': buf})
    return out


def _label(chunks, body, title):
    """Attach heading_path to offset-only chunkers (fixed / recursive) from the block map."""
    blocks = parse_blocks(body, title)
    for c in chunks:
        p = title
        for b in blocks:
            if b['start'] > c['start']:
                break
            p = b['path']
        c['heading_path'] = p
    return chunks


STRATEGIES = {'fixed': fixed_chunks, 'recursive': recursive_chunks, 'markdown': markdown_chunks}
