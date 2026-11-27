"""Exercise E: negative tests, identity forgery, and live revocation. Output saved to
reports/security_tests.txt. Restores any revoked membership in `finally`."""
import sys
from config import ROOT, TENANT, connect, sign_identity
from retrieve import run_search, set_identity

LOG = []


def say(msg):
    print(msg)
    LOG.append(msg)


def check(label, actual, expected):
    ok = actual == expected
    say(f"{'PASS' if ok else 'FAIL'}  {label} => {actual}")
    if not ok:
        raise AssertionError(label)


def rows_visible(doc_id=None, user=None, sig='auto'):
    """Number of chunks the reader role can see; user=None sets no identity at all."""
    db = connect('reader')
    try:
        cur = db.cursor()
        if user is not None:
            set_identity(cur, user, sign_identity(user) if sig == 'auto' else sig)
        if doc_id:
            cur.execute('SELECT count(*) FROM k8s_rag.chunks WHERE document_id = %s', (doc_id,))
        else:
            cur.execute('SELECT count(*) FROM k8s_rag.chunks')
        n = cur.fetchone()[0]
        db.rollback()
        return n
    finally:
        db.close()


def admin_exec(sql, args=()):
    db = connect('admin')
    cur = db.cursor()
    cur.execute(sql, args)
    db.commit()
    db.close()


def chunk_total():
    db = connect('admin')
    cur = db.cursor()
    cur.execute('SELECT count(*), max(chunk_id) FROM k8s_rag.chunks')
    r = cur.fetchone()
    db.close()
    return r


def denied(sql):
    db = connect('reader')
    try:
        db.cursor().execute(sql)
        return False
    except Exception as e:
        return 'permission denied' in str(e)
    finally:
        db.close()


def main():
    say('== 1. Authorized user retrieves restricted document (SEC-001: RBAC good practices) ==')
    check('Meena (Security) sees SEC-001 chunks > 0', rows_visible('SEC-001', 'meena') > 0, True)
    check('Divya (App+Security) sees SEC-001 chunks > 0', rows_visible('SEC-001', 'divya') > 0, True)

    say('\n== 2. Unauthorized users cannot retrieve the same document ==')
    check('Priya (Application) sees SEC-001 chunks', rows_visible('SEC-001', 'priya'), 0)
    check('Arjun (Platform) sees SEC-001 chunks', rows_visible('SEC-001', 'arjun'), 0)
    res = run_search('priya', 'What are recommended Kubernetes RBAC practices?', 10, show=False)
    check('Priya top-10 RBAC question contains no SECURITY_ENG chunk',
          any(r['access_group'] == 'SECURITY_ENG' for r in res), False)
    check('Arjun cannot see APP-001', rows_visible('APP-001', 'arjun'), 0)
    check('Meena cannot see PLAT-002', rows_visible('PLAT-002', 'meena'), 0)

    say('\n== 3. Shared knowledge is readable by everyone ==')
    for u in ('priya', 'arjun', 'meena', 'divya'):
        check(f'{u} sees SHARED-002 (components)', rows_visible('SHARED-002', u) > 0, True)

    say('\n== 4. Unknown / forged identities cannot read protected chunks ==')
    check('No identity set at all', rows_visible(user=None), 0)
    check('Unknown user, validly signed by backend', rows_visible(user='unknown-person'), 0)
    check('Forged: user_id=meena without a signature', rows_visible('SEC-001', 'meena', sig=''), 0)
    check('Forged: user_id=meena with wrong signature', rows_visible('SEC-001', 'meena', sig='00' * 32), 0)
    check("Forged: Priya's signature replayed for meena", rows_visible('SEC-001', 'meena', sig=sign_identity('priya')), 0)

    say('\n== 5. Reader role is least-privilege ==')
    check('Reader cannot read documents', denied('SELECT * FROM k8s_rag.documents LIMIT 1'), True)
    check('Reader cannot read document_acl', denied('SELECT * FROM k8s_rag.document_acl LIMIT 1'), True)
    check('Reader cannot read user_groups', denied('SELECT * FROM k8s_rag.user_groups LIMIT 1'), True)
    check('Reader cannot read the signing key', denied('SELECT signing_key FROM k8s_rag.auth_secret'), True)
    check('Reader cannot modify chunks', denied("DELETE FROM k8s_rag.chunks WHERE document_id = 'SEC-001'"), True)

    say('\n== 6. Revocation takes effect immediately, without re-embedding ==')
    before = chunk_total()
    check('Meena sees SEC-001 before revocation', rows_visible('SEC-001', 'meena') > 0, True)
    try:
        admin_exec("DELETE FROM k8s_rag.user_groups WHERE user_id = 'meena' AND group_name = 'SECURITY_ENG'")
        check('Meena denied SEC-001 right after revocation', rows_visible('SEC-001', 'meena'), 0)
        check('Meena still sees shared SHARED-002', rows_visible('SHARED-002', 'meena') > 0, True)
        check('Chunk table untouched (count, max chunk_id) - no re-ingest', chunk_total(), before)
    finally:
        admin_exec("INSERT INTO k8s_rag.user_groups(user_id, group_name) VALUES ('meena', 'SECURITY_ENG') "
                   'ON CONFLICT DO NOTHING')
    say('\n== 7. Restoring membership restores access ==')
    check('Meena regains SEC-001 after restore', rows_visible('SEC-001', 'meena') > 0, True)
    check('Chunk table still untouched', chunk_total(), before)

    say('\nALL CHECKS PASSED. --user only simulates identities; production identities must come from '
        'a trusted backend that signs them (see README trust boundary).')
    (ROOT / 'reports/security_tests.txt').write_text('\n'.join(LOG) + '\n', encoding='utf-8')


if __name__ == '__main__':
    try:
        main()
    except AssertionError as e:
        say(f'FAILED: {e}')
        (ROOT / 'reports/security_tests.txt').write_text('\n'.join(LOG) + '\n', encoding='utf-8')
        sys.exit(1)
