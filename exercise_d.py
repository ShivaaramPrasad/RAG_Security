"""Exercise D: same question, different identities. Writes reports/retrieval_results.md.

For every (question, user) we record the RLS-filtered top-5 (what the application may see) and an
ADMIN AUDIT of the unfiltered top-5 showing which hits the database withheld. The audit uses the
admin account purely as evidence; it is never part of the retrieval path."""
from config import USERS, connect, vec, ROOT
from retrieve import run_search, query_vector, SQL

QUESTIONS = [
    ('How does a Kubernetes Deployment manage application replicas?', 'Application Engineering'),
    ('What are PersistentVolumes and PersistentVolumeClaims?', 'Platform Engineering'),
    ('What are recommended Kubernetes RBAC practices?', 'Security Engineering'),
    ('What are the main Kubernetes components?', 'Shared knowledge'),
]
K = 5


def main():
    admin = connect('admin')
    cur = admin.cursor()
    cur.execute('SELECT ug.user_id, ug.group_name FROM k8s_rag.user_groups ug')
    groups = {}
    for u, g in cur.fetchall():
        groups.setdefault(u, set()).add(g)

    md = ['# Exercise D - same question, different identities\n',
          'Distances are cosine distances (lower = closer). "Authorized" = the row survived database RLS. '
          '"Withheld" rows come from an admin audit of the unfiltered ranking and were **never returned** '
          'to the user.\n']
    for q, area in QUESTIONS:
        qv = query_vector(q)
        cur.execute(SQL, (vec(qv), vec(qv), 1000))
        unfiltered = cur.fetchall()
        md.append(f'## {q}\n*Primary knowledge area: {area}*\n')
        for user in USERS:
            res = run_search(user, q, K, show=False, qvec=qv)
            print(f'{user:6} {q[:55]:55} -> {[r["document_id"] for r in res]}')
            md.append(f'### {user.title()} ({", ".join(sorted(groups[user] - {"ALL_EMPLOYEES"}))} + shared)\n')
            md.append('| Rank | Document | Heading | Cosine dist. | Source link | Authorized |')
            md.append('|---|---|---|---|---|---|')
            for i, r in enumerate(res, 1):
                md.append(f"| {i} | {r['document_id']} | {r['heading_path']} | {float(r['distance']):.4f} | "
                          f"{r['source_url']} | yes |")
            # evidence: unfiltered top-K and the check that RLS == admin ranking filtered by ACL
            top = unfiltered[:K]
            withheld = [r for r in top if r[6] not in groups[user]]
            expected = [(r[0], r[1]) for r in unfiltered if r[6] in groups[user]][:K]
            got = [(r['document_id'], r['chunk_no']) for r in res]
            assert got == expected, f'RLS result differs from ACL-filtered ranking for {user}'
            md.append(f'\nAdmin audit of the unfiltered top-{K}: {len(withheld)} withheld from {user.title()}'
                      + (': ' + ', '.join(f'{r[0]} [{r[6]}] dist {float(r[7]):.4f}' for r in withheld) if withheld else '')
                      + '\n')
    admin.close()
    (ROOT / 'reports/retrieval_results.md').write_text('\n'.join(md), encoding='utf-8')
    print('Wrote reports/retrieval_results.md (RLS output verified equal to ACL-filtered ranking)')


if __name__ == '__main__':
    main()
