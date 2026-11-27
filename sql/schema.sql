-- Run as the database owner/admin (never as the reader role).
-- Statements are separated by marker lines because pg8000 sends one statement per call.
CREATE EXTENSION IF NOT EXISTS vector;
-- GO
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- GO
CREATE SCHEMA IF NOT EXISTS k8s_rag;
-- GO
REVOKE ALL ON SCHEMA k8s_rag FROM PUBLIC;
-- GO
CREATE TABLE IF NOT EXISTS k8s_rag.users (
    user_id      text PRIMARY KEY,
    display_name text NOT NULL,
    tenant_id    text NOT NULL
);
-- GO
CREATE TABLE IF NOT EXISTS k8s_rag.user_groups (
    user_id    text NOT NULL REFERENCES k8s_rag.users(user_id) ON DELETE CASCADE,
    group_name text NOT NULL,
    PRIMARY KEY (user_id, group_name)
);
-- GO
CREATE TABLE IF NOT EXISTS k8s_rag.documents (
    document_id  text PRIMARY KEY,
    tenant_id    text NOT NULL,
    title        text NOT NULL,
    filename     text NOT NULL,
    source_path  text NOT NULL,
    github_url   text NOT NULL,
    source_url   text NOT NULL,
    access_group text NOT NULL,          -- classification: APP_ENG / PLATFORM_ENG / SECURITY_ENG / ALL_EMPLOYEES
    license      text NOT NULL
);
-- GO
CREATE TABLE IF NOT EXISTS k8s_rag.document_acl (
    document_id text NOT NULL REFERENCES k8s_rag.documents(document_id) ON DELETE CASCADE,
    group_name  text NOT NULL,
    PRIMARY KEY (document_id, group_name)
);
-- GO
-- Chunks carry denormalised source metadata so retrieval results are attributable while the
-- reader role needs SELECT on this one RLS-protected table only.
CREATE TABLE IF NOT EXISTS k8s_rag.chunks (
    chunk_id     bigserial PRIMARY KEY,
    document_id  text NOT NULL REFERENCES k8s_rag.documents(document_id) ON DELETE CASCADE,
    tenant_id    text NOT NULL,
    chunk_no     integer NOT NULL,
    heading_path text NOT NULL,
    chunk_text   text NOT NULL,
    doc_title    text NOT NULL,
    source_url   text NOT NULL,
    source_path  text NOT NULL,
    access_group text NOT NULL,
    embedding    vector(384) NOT NULL,
    UNIQUE (document_id, chunk_no)
);
-- GO
CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON k8s_rag.chunks(document_id);
-- GO
-- Secret shared only between the trusted backend and the database owner.
CREATE TABLE IF NOT EXISTS k8s_rag.auth_secret (
    id          integer PRIMARY KEY CHECK (id = 1),
    signing_key text NOT NULL
);
-- GO
-- Verified identity: app.user_id is honoured only if app.identity_sig is the HMAC the trusted
-- backend computed with the signing key. A reader-role holder who sets app.user_id to someone
-- else cannot produce the signature, so impersonation through the database fails closed.
CREATE OR REPLACE FUNCTION k8s_rag.verified_user() RETURNS text
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, public, k8s_rag
AS $$
  SELECT u.user_id
  FROM k8s_rag.users u
  WHERE u.user_id   = nullif(current_setting('app.user_id', true), '')
    AND u.tenant_id = nullif(current_setting('app.tenant_id', true), '')
    AND encode(hmac(u.user_id || '|' || u.tenant_id,
                    (SELECT signing_key FROM k8s_rag.auth_secret WHERE id = 1), 'sha256'), 'hex')
        = nullif(current_setting('app.identity_sig', true), '')
$$;
-- GO
CREATE OR REPLACE FUNCTION k8s_rag.may_read(p_document_id text, p_tenant text) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, public, k8s_rag
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM k8s_rag.documents d
    JOIN k8s_rag.document_acl a ON a.document_id = d.document_id
    JOIN k8s_rag.user_groups ug ON ug.group_name = a.group_name
    WHERE d.document_id = p_document_id
      AND d.tenant_id   = p_tenant
      AND ug.user_id    = k8s_rag.verified_user()
  )
$$;
-- GO
REVOKE ALL ON FUNCTION k8s_rag.verified_user() FROM PUBLIC;
-- GO
REVOKE ALL ON FUNCTION k8s_rag.may_read(text, text) FROM PUBLIC;
-- GO
ALTER TABLE k8s_rag.chunks ENABLE ROW LEVEL SECURITY;
-- GO
DROP POLICY IF EXISTS authorized_chunks ON k8s_rag.chunks;
-- GO
-- Applies to every non-owner role (the reader). The admin/owner account is used only by
-- bootstrap, ingestion and audit scripts and is never given to the retrieval path.
CREATE POLICY authorized_chunks ON k8s_rag.chunks FOR SELECT
USING (
  tenant_id = nullif(current_setting('app.tenant_id', true), '')
  AND k8s_rag.may_read(document_id, tenant_id)
);
