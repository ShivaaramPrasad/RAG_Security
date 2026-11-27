"""Exercise A: run fixed / recursive / markdown / semantic chunking on the same 30 docs and
write reports/chunking_comparison.md (+ .json)."""
import json, statistics as st
from config import ROOT, embed
from chunking import clean_markdown, fixed_chunks, recursive_chunks, markdown_chunks, semantic_chunks

CFG = {
    'fixed':     'size=1000, overlap=150',
    'recursive': 'size=1000, overlap=150, seps: ## / ### / #### / blank line / line / sentence / space',
    'markdown':  'max=1200, min section=250, heading path prefix, code fences never split',
    'semantic':  'block embeddings, split above 85th-percentile cosine distance, min=300, max=1500',
}


def boundary_clean(body, c):
    """Clean = chunk begins at the start of a block (after a blank line) and ends where a block ends,
    ignoring surrounding whitespace."""
    s, e = c['start'], c['end']
    raw = body[s:e]
    s2 = s + len(raw) - len(raw.lstrip())
    e2 = s2 + len(raw.strip())
    start_ok = s2 == 0 or body[max(0, s2 - 2):s2] == '\n\n'
    end_ok = e2 >= len(body.rstrip()) or body[e2:e2 + 2] == '\n\n'
    return start_ok, end_ok


def broken_fence(c):
    raw = c['text']
    return raw.count('```') % 2 == 1


def has_heading(c):
    t = c['text']
    first = t.split('\n', 1)[0]
    return first.startswith('#') or '\n#' in t or (c['heading_path'] and t.startswith(c['heading_path']))


def preview(c, n=260):
    t = c['text'].replace('\n', '\\n')
    return t[:n] + ('...' if len(t) > n else '')


def main():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    docs = []
    for m in manifest:
        title, body = clean_markdown((ROOT / m['local_file']).read_text(encoding='utf-8'))
        docs.append((m['document_id'], title or m['title'], body))
    print(f'{len(docs)} documents, {sum(len(b) for _, _, b in docs):,} characters of cleaned Markdown')

    results, examples = {}, {}
    for name in ('fixed', 'recursive', 'markdown', 'semantic'):
        allc = []
        for doc_id, title, body in docs:
            if name == 'semantic':
                cs = semantic_chunks(body, title, embed)
            else:
                cs = {'fixed': fixed_chunks, 'recursive': recursive_chunks, 'markdown': markdown_chunks}[name](body, title)
            for c in cs:
                c['doc'], c['body'] = doc_id, body
            allc.extend(cs)
            print(f'  {name:9} {doc_id:11} {len(cs):4} chunks')
        sizes = [len(c['text']) for c in allc]
        starts = [boundary_clean(c['body'], c) for c in allc]
        n = len(allc)
        results[name] = {
            'config': CFG[name], 'chunks': n, 'avg': round(st.mean(sizes)), 'min': min(sizes), 'max': max(sizes),
            'median': round(st.median(sizes)),
            'heading_pct': round(100 * sum(map(has_heading, allc)) / n, 1),
            'clean_start_pct': round(100 * sum(s for s, _ in starts) / n, 1),
            'clean_end_pct': round(100 * sum(e for _, e in starts) / n, 1),
            'broken_code_fences': sum(map(broken_fence, allc)),
            'tiny_lt150': sum(1 for x in sizes if x < 150),
            'oversize_gt1500': sum(1 for x in sizes if x > 1500),
        }
        poor = next((c for c in allc if len(c['text']) > 200 and (broken_fence(c) or not all(boundary_clean(c['body'], c)))), None)
        good = next((c for c in allc if len(c['text']) > 300 and all(boundary_clean(c['body'], c)) and has_heading(c)), None)
        examples[name] = {'poor': poor and (poor['doc'], preview(poor)), 'good': good and (good['doc'], preview(good))}

    (ROOT / 'reports').mkdir(exist_ok=True)
    (ROOT / 'reports/chunking_comparison.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    rows = [
        ('Total chunks', 'chunks'), ('Average size (chars)', 'avg'), ('Median size', 'median'),
        ('Minimum size', 'min'), ('Maximum size', 'max'),
        ('Chunks carrying heading context (%)', 'heading_pct'),
        ('Chunks starting on a clean boundary (%)', 'clean_start_pct'),
        ('Chunks ending on a clean boundary (%)', 'clean_end_pct'),
        ('Chunks with a broken code fence', 'broken_code_fences'),
        ('Tiny chunks (<150 chars)', 'tiny_lt150'), ('Oversize chunks (>1500 chars)', 'oversize_gt1500'),
    ]
    names = list(results)
    md = ['# Chunking comparison (30 Kubernetes docs, identical cleaned input)\n',
          '| Metric | ' + ' | '.join(names) + ' |', '|---|' + '---|' * len(names)]
    for label, key in rows:
        md.append(f'| {label} | ' + ' | '.join(str(results[n][key]) for n in names) + ' |')
    md.append('| Overlap | ' + ' | '.join('150 chars' if n in ('fixed', 'recursive') else 'none' for n in names) + ' |')
    md.append('\n## Configuration\n')
    md += [f'- **{n}**: {CFG[n]}' for n in names]
    md.append('\n## Boundary examples\n')
    for n in names:
        md.append(f'### {n}')
        for kind in ('good', 'poor'):
            ex = examples[n][kind]
            md.append(f'- **{kind.title()} boundary** ' + (f'({ex[0]}): `{ex[1]}`' if ex else '(none found)'))
        md.append('')
    (ROOT / 'reports/chunking_comparison.md').write_text('\n'.join(md), encoding='utf-8')
    print('\n'.join(md[:20]))


if __name__ == '__main__':
    main()
