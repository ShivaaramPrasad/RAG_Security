"""Ingest the 30 Kubernetes docs with markdown structure-aware chunking, embed with BGE-small,
store chunks + source metadata + ACLs in PostgreSQL/pgvector. Safe to re-run (replaces by document)."""
import json, time
from config import ROOT, TENANT, connect, embed, vec
from chunking import clean_markdown, markdown_chunks


def main():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    rows = []
    for m in manifest:
        title, body = clean_markdown((ROOT / m['local_file']).read_text(encoding='utf-8'))
        for i, c in enumerate(markdown_chunks(body, title or m['title'])):
            rows.append((m, i, c))
    print(f'{len(manifest)} documents -> {len(rows)} chunks')
    t0, vectors = time.monotonic(), []
    for i in range(0, len(rows), 32):
        vectors.extend(embed([c['text'] for _, _, c in rows[i:i + 32]]))
        print(f'  embedded {len(vectors)}/{len(rows)}')

    db = connect('admin')
    cur = db.cursor()
    for m in manifest:
        cur.execute("""INSERT INTO k8s_rag.documents(document_id, tenant_id, title, filename, source_path,
                       github_url, source_url, access_group, license) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                       ON CONFLICT (document_id) DO UPDATE SET title=EXCLUDED.title, filename=EXCLUDED.filename,
                       source_path=EXCLUDED.source_path, github_url=EXCLUDED.github_url,
                       source_url=EXCLUDED.source_url, access_group=EXCLUDED.access_group,
                       license=EXCLUDED.license""",
                    (m['document_id'], TENANT, m['title'], m['filename'], m['source_path'], m['github_url'],
                     m['source_url'], m['access_group'], m['license']))
        cur.execute('DELETE FROM k8s_rag.document_acl WHERE document_id = %s', (m['document_id'],))
        cur.execute('INSERT INTO k8s_rag.document_acl(document_id, group_name) VALUES (%s,%s)',
                    (m['document_id'], m['access_group']))
        cur.execute('DELETE FROM k8s_rag.chunks WHERE document_id = %s', (m['document_id'],))
    for (m, i, c), v in zip(rows, vectors):
        cur.execute("""INSERT INTO k8s_rag.chunks(document_id, tenant_id, chunk_no, heading_path, chunk_text,
                       doc_title, source_url, source_path, access_group, embedding)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)""",
                    (m['document_id'], TENANT, i, c['heading_path'], c['text'], m['title'],
                     m['source_url'], m['source_path'], m['access_group'], vec(v)))
    db.commit()
    cur.execute('SELECT access_group, count(DISTINCT document_id), count(*) FROM k8s_rag.chunks GROUP BY 1 ORDER BY 1')
    for g, d, c in cur.fetchall():
        print(f'  {g:14} {d:3} docs {c:4} chunks')
    db.close()
    print(f'Done in {time.monotonic() - t0:.1f}s. Next: python retrieve.py --user priya --question "..."')


if __name__ == '__main__':
    main()
