"""One-time setup: create database if missing, schema, RLS policy, restricted reader role, 4 users."""
import re
from config import (ROOT, connect, DBNAME, READER_ROLE, READER_PASSWORD, SIGNING_KEY, TENANT)

USER_GROUPS = {
    'priya': ('Priya', ['APP_ENG', 'ALL_EMPLOYEES']),
    'arjun': ('Arjun', ['PLATFORM_ENG', 'ALL_EMPLOYEES']),
    'meena': ('Meena', ['SECURITY_ENG', 'ALL_EMPLOYEES']),
    'divya': ('Divya', ['APP_ENG', 'SECURITY_ENG', 'ALL_EMPLOYEES']),
}


def ident(name):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name):
        raise ValueError(f'unsafe identifier: {name}')
    return name


def main():
    if not READER_PASSWORD or not SIGNING_KEY:
        raise RuntimeError('READER_PASSWORD and APP_SIGNING_KEY must be set in .env')
    server = connect('server')
    server.autocommit = True
    cur = server.cursor()
    cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (DBNAME,))
    if cur.fetchone():
        print(f'Using existing database {DBNAME}')
    else:
        cur.execute(f'CREATE DATABASE {ident(DBNAME)}')
        print(f'Created database {DBNAME}')
    server.close()

    db = connect('admin')
    cur = db.cursor()
    for stmt in (ROOT / 'sql/schema.sql').read_text().split('-- GO'):
        if stmt.strip():
            cur.execute(stmt)
    role = ident(READER_ROLE)
    cur.execute('SELECT 1 FROM pg_roles WHERE rolname = %s', (READER_ROLE,))
    pw = READER_PASSWORD.replace("'", "''")
    cur.execute(f"{'ALTER' if cur.fetchone() else 'CREATE'} ROLE {role} LOGIN PASSWORD '{pw}' "
                'NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS')
    for stmt in (
        f'GRANT CONNECT ON DATABASE {ident(DBNAME)} TO {role}',
        f'GRANT USAGE ON SCHEMA k8s_rag TO {role}',
        f'REVOKE ALL ON ALL TABLES IN SCHEMA k8s_rag FROM {role}',
        f'GRANT SELECT ON k8s_rag.chunks TO {role}',          # RLS-protected; the only table the reader sees
        f'GRANT EXECUTE ON FUNCTION k8s_rag.may_read(text, text) TO {role}',  # needed by the policy
    ):
        cur.execute(stmt)
    cur.execute('INSERT INTO k8s_rag.auth_secret(id, signing_key) VALUES (1, %s) '
                'ON CONFLICT (id) DO UPDATE SET signing_key = EXCLUDED.signing_key', (SIGNING_KEY,))
    for uid, (name, groups) in USER_GROUPS.items():
        cur.execute('INSERT INTO k8s_rag.users(user_id, display_name, tenant_id) VALUES (%s,%s,%s) '
                    'ON CONFLICT (user_id) DO UPDATE SET display_name = EXCLUDED.display_name, '
                    'tenant_id = EXCLUDED.tenant_id', (uid, name, TENANT))
        cur.execute('DELETE FROM k8s_rag.user_groups WHERE user_id = %s', (uid,))
        for g in groups:
            cur.execute('INSERT INTO k8s_rag.user_groups(user_id, group_name) VALUES (%s,%s)', (uid, g))
    db.commit()
    db.close()
    print('Bootstrap complete. Next: python ingest.py')


if __name__ == '__main__':
    main()
