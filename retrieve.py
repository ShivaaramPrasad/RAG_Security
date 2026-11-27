"""Secure retrieval. The 'trusted backend' (this process) signs the identity; PostgreSQL RLS then
filters chunks BEFORE ranking results reach the caller (and therefore before any LLM)."""
import argparse
from config import TENANT, connect, embed, vec, sign_identity

QUERY_PREFIX = 'Represent this sentence for searching relevant passages: '  # BGE query instruction

SQL = """SELECT document_id, chunk_no, heading_path, doc_title, source_url, source_path, access_group,
                round((embedding <=> %s::vector)::numeric, 4) AS distance, chunk_text
         FROM k8s_rag.chunks
         ORDER BY embedding <=> %s::vector
         LIMIT %s"""


def query_vector(question):
    return embed([QUERY_PREFIX + question])[0]


def set_identity(cur, user_id, sig=None):
    """Session identity for this transaction only (set_config is_local = true)."""
    cur.execute('SELECT set_config(%s, %s, true)', ('app.user_id', user_id))
    cur.execute('SELECT set_config(%s, %s, true)', ('app.tenant_id', TENANT))
    cur.execute('SELECT set_config(%s, %s, true)', ('app.identity_sig', sig if sig is not None else sign_identity(user_id)))


def run_search(user_id, question, k=5, show=True, qvec=None):
    qv = vec(qvec or query_vector(question))
    db = connect('reader')
    try:
        cur = db.cursor()
        set_identity(cur, user_id)
        cur.execute(SQL, (qv, qv, k))
        keys = ['document_id', 'chunk_no', 'heading_path', 'doc_title', 'source_url', 'source_path',
                'access_group', 'distance', 'chunk_text']
        results = [dict(zip(keys, r)) for r in cur.fetchall()]
        db.rollback()
    finally:
        db.close()
    if show:
        print(f'IDENTITY={user_id} | QUESTION={question!r} | authorized results={len(results)}')
        for r in results:
            print(f"  {r['document_id']:10} chunk {r['chunk_no']:<3} dist {float(r['distance']):.4f}  "
                  f"[{r['access_group']}] {r['heading_path']}\n             {r['source_url']}")
        if not results:
            print('  No authorized matching chunks.')
    return results


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--user', required=True, help='simulated identity (priya, arjun, meena, divya, ...)')
    p.add_argument('--question', required=True)
    p.add_argument('--k', type=int, default=5)
    a = p.parse_args()
    run_search(a.user.lower(), a.question, a.k)
