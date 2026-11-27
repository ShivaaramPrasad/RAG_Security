# Enterprise RAG: Chunking & Role-Based Security (Kubernetes docs)

Week 7 homework - TestLeaf FDE program. Ingests 30 official Kubernetes docs, compares four chunking
strategies, stores BGE-small embeddings in PostgreSQL/pgvector, and enforces document access with
PostgreSQL Row-Level Security so unauthorized chunks never reach retrieval results.

## 1. Installation and execution

Requirements: Python 3.12+ (tested on 3.14), Docker Desktop, internet (GitHub + first model download).
The DB driver is pure-Python `pg8000`, so no compiled DB binaries are needed.

```powershell
copy .env.example .env            # then edit the passwords / signing key
docker compose up -d              # PostgreSQL 16 + pgvector on port 5434
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # if blocked: Set-ExecutionPolicy -Scope Process Bypass
python -m pip install -r requirements.txt

python fetch_docs.py              # download the 30 Markdown files + data/manifest.json
python compare_chunking.py        # Exercise A  -> reports/chunking_comparison.md
python bootstrap.py               # DB, schema, RLS, reader role, 4 users
python ingest.py                  # Exercise B  -> 736 chunks with embeddings
python retrieve.py --user priya --question "How does a Kubernetes Deployment manage application replicas?"
python exercise_d.py              # Exercise D  -> reports/retrieval_results.md
python test_security.py           # Exercise E  -> reports/security_tests.txt
```

## 2. Dataset, license and selected files

Source: <https://github.com/kubernetes/website> (`content/en/docs/concepts/...`), (c) The Kubernetes
Authors, licensed **CC BY 4.0**. Files are unmodified copies in `data/docs/`; original filename, title,
source path and kubernetes.io URL are in `data/manifest.json`. The department restrictions are
**fictional** policies for this exercise only.

| Access group | Source area | Files (document id) |
|---|---|---|
| APP_ENG | concepts/workloads | APP-001..010: deployment, replicaset, statefulset, daemonset, job, cron-jobs, pods/_index, pod-lifecycle, init-containers, autoscaling |
| PLATFORM_ENG | concepts/storage | PLAT-001..010: volumes, persistent-volumes, storage-classes, dynamic-provisioning, volume-snapshots, ephemeral-volumes, projected-volumes, storage-capacity, volume-snapshot-classes, volume-pvc-datasource |
| SECURITY_ENG | concepts/security | SEC-001..005: rbac-good-practices, service-accounts, pod-security-standards, secrets-good-practices, multi-tenancy |
| ALL_EMPLOYEES (shared) | concepts/overview | SHARED-001..005: overview/_index, components, kubectl, kubernetes-api, working-with-objects/_index |

Pre-processing (`chunking.clean_markdown`): strip Hugo front matter, shortcodes (`glossary_tooltip` ->
its text, `note/warning/caution` -> bold label) and HTML comments; the same cleaned text feeds every
strategy.

## 3. Chunking comparison (Exercise A)

Run on all 30 documents (563 KB of cleaned Markdown). Full output and examples:
[reports/chunking_comparison.md](reports/chunking_comparison.md).

| Metric | Fixed | Recursive | **Markdown (structure-aware)** | Semantic |
|---|---|---|---|---|
| Config | 1000 chars | 1000 chars, `##`/`###`/blank line/line/sentence separators | max 1200, heading-path prefix, code fences kept whole | block embeddings, split above 85th-pct distance |
| Overlap | 150 | 150 | none | none |
| Total chunks | 672 | 732 | 736 | 530 |
| Avg / min / max chars | 980 / 154 / 1000 | 800 / 114 / 1000 | 819 / 85 / 2040 | 1059 / 30 / 11882 |
| Chunks carrying heading context | 65.0% | 60.0% | **100%** | 64.5% |
| Start on a clean block boundary | 6.0% | 82.9% | 90.6% | 96.0% |
| End on a clean block boundary | 5.2% | 87.8% | 94.0% | 100% |
| Chunks with a broken code fence | 82 | 12 | 8 | 0 |
| Chunks > 1500 chars | 0 | 0 | 1 | 14 |

Heading context for fixed/recursive/semantic means the chunk happens to contain a heading line; only
the markdown strategy guarantees the section path (`Deployments > Writing a Deployment Spec > Replicas`).

Boundary examples:
- *Poor (fixed)*: windows cut through sentences and code blocks (82 chunks contain half a fenced block).
- *Poor (markdown)*: an indented `**Note:**` continuation inside a list item is split from its list item
  because it sits behind a blank line.
- *Good (markdown)*: `Deployments > Writing a Deployment Spec > Replicas` is one self-contained section chunk, so
  the query "How does a Deployment manage replicas" ranks it #3 with its heading in the embedded text.
- *Good (semantic)*: `## Use Case` + its bullet list stays together; *poor (semantic)*: it never splits a
  code fence but produced 14 oversize chunks (largest 11,882 chars - one giant YAML/code block).

**Recommendation: Markdown structure-aware chunking** for technical documentation. It is the only one that
attaches the heading path to every chunk (traceable citations, better embeddings), keeps code and tables
intact, needs no extra model calls, and yields consistent sizes. Semantic chunking had the cleanest cut
points but costs an embedding pass, is non-deterministic across model changes, and let code blocks grow to
~12 KB. Ingestion (`ingest.py`) therefore uses the markdown chunker (736 chunks).

## 4. Database schema, groups and RLS (Exercises B and C)

Tables in schema `k8s_rag` ([sql/schema.sql](sql/schema.sql)):

| Table | Purpose |
|---|---|
| `documents` | document_id, title, filename, source_path, github_url, source_url, access_group, license |
| `document_acl` | document_id -> group_name (the group permission) |
| `users`, `user_groups` | the four identities and their group memberships |
| `chunks` | document_id, chunk_no, heading_path, chunk_text, embedding `vector(384)`, plus denormalised doc_title / source_url / source_path / access_group so every hit is attributable |
| `auth_secret` | HMAC key shared by the trusted backend and the DB owner only |

Group memberships (every user also belongs to `ALL_EMPLOYEES`):

| User | Groups | May retrieve |
|---|---|---|
| Priya | APP_ENG | Application + shared |
| Arjun | PLATFORM_ENG | Platform + shared |
| Meena | SECURITY_ENG | Security + shared |
| Divya | APP_ENG, SECURITY_ENG | Application + Security + shared |

Retrieval query (cosine distance, ranked, attributable):

```sql
SELECT document_id, chunk_no, heading_path, doc_title, source_url,
       round((embedding <=> :q::vector)::numeric, 4) AS distance
FROM k8s_rag.chunks ORDER BY embedding <=> :q::vector LIMIT 5;
```

There is **no WHERE clause for permissions** in that query - the database applies this policy:

```sql
CREATE POLICY authorized_chunks ON k8s_rag.chunks FOR SELECT
USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')
       AND k8s_rag.may_read(document_id, tenant_id));
```

`may_read()` (SECURITY DEFINER) joins `documents -> document_acl -> user_groups` for
`k8s_rag.verified_user()`. The filter runs inside the scan, before `ORDER BY ... LIMIT`, so ranking only
ever sees authorized rows and a restricted chunk can never push out or appear among the top-k.

### Trust boundary and database roles

| Role | Rights |
|---|---|
| `fde` (admin, owner) | bootstrap, ingestion and audit scripts only. Never used by retrieval. Superuser/owner bypasses RLS. |
| `k8s_rag_reader` | `NOSUPERUSER NOBYPASSRLS`; `SELECT` on `chunks` only (RLS applies) and `EXECUTE` on `may_read`. No access to documents, ACLs, memberships or the signing key. |

The retrieval backend (`retrieve.py`) is the trust boundary: it authenticates the user (simulated by
`--user` here), then sets `app.user_id`, `app.tenant_id` and `app.identity_sig` = HMAC-SHA256(user|tenant,
`APP_SIGNING_KEY`) with `set_config(..., is_local = true)`. `verified_user()` recomputes the HMAC inside the
database and returns NULL on mismatch, so someone holding only the reader credentials who sets
`app.user_id = 'meena'` still sees **zero** rows (tested). Production: replace `--user` with a verified
token (OIDC/JWT) checked by the backend, keep the reader password and signing key in a secret manager.

## 5. Role-by-role retrieval results (Exercise D)

Full tables (top-5 per user, distances, source links, admin audit of withheld hits):
[reports/retrieval_results.md](reports/retrieval_results.md). Top-1 hit per question and identity:

| Question | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|
| How does a Deployment manage application replicas? | **APP-001 Deployments 0.1577** | SHARED-005 Objects 0.2128 | SHARED-005 Objects 0.2128 | **APP-001 Deployments 0.1577** |
| What are PersistentVolumes and PVCs? | APP-003 StatefulSets > Stable Storage 0.2278 | **PLAT-002 Persistent Volumes 0.1820** | SEC-001 RBAC > PV creation 0.2983 | APP-003 StatefulSets 0.2278 |
| Recommended Kubernetes RBAC practices? | SHARED-001 Overview 0.2534 | SHARED-001 Overview 0.2534 | **SEC-001 RBAC Good Practices 0.1553** | **SEC-001 0.1553** |
| Main Kubernetes components? | SHARED-002 0.1199 | SHARED-002 0.1199 | SHARED-002 0.1199 | SHARED-002 0.1199 |

Every returned row is authorized (`yes`). The admin audit shows what was withheld, e.g. for the
Deployment question Arjun and Meena had 4 of the unfiltered top-5 hits withheld (all APP_ENG); for the RBAC
question Priya and Arjun had all 5 withheld (all SEC-001/005/004 chunks). `exercise_d.py` also asserts that
the RLS output equals "the admin's unfiltered ranking filtered by ACL" for all 16 runs.

## 6. Negative-access and revocation evidence (Exercise E)

Output of `python test_security.py` is saved in [reports/security_tests.txt](reports/security_tests.txt):

- Authorized: Meena and Divya read SEC-001 (RBAC good practices) - PASS.
- Unauthorized: Priya and Arjun see 0 chunks of SEC-001; Priya's top-10 for the RBAC question contains no
  SECURITY_ENG chunk; Arjun cannot see APP-001, Meena cannot see PLAT-002 - PASS.
- Shared document SHARED-002 is visible to all four - PASS.
- Unknown identity: no identity set -> 0 rows; validly signed but unknown user -> 0 rows; forged
  `user_id=meena` with no / wrong / replayed (Priya's) signature -> 0 rows - PASS.
- Least privilege: reader gets `permission denied` on documents, document_acl, user_groups, auth_secret and
  cannot DELETE chunks - PASS.
- Revocation: `DELETE FROM user_groups ... meena/SECURITY_ENG` -> Meena immediately loses SEC-001 but keeps
  shared docs; the chunk table is not touched (row count and max chunk_id identical: no re-embedding or
  re-ingest). Restoring the membership restores access - PASS.

## 7. Known limitations and improvements

- Denied queries return only the nearest *authorized* material (e.g. Priya's PersistentVolume question
  returns StatefulSet storage text). There is no "you lack access" hint by design (see reflection 2).
- Exact vector scan, no HNSW/IVFFlat. With ANN indexes + RLS, filtered recall drops; use partitioning by
  group or iterative scans at scale.
- Identity is simulated; the signing key lives in `.env`. Use real authentication and a secret manager.
- The admin role owns the tables and bypasses RLS; separate the migration owner from the ingest role.
- One group per document (the ACL table supports many). Indented list continuations are split by the
  markdown chunker; oversized code blocks are kept whole (max 2040 chars) rather than split.
- Chunking metrics are structural (boundary/heading/fence), not retrieval-quality (no labelled relevance set).
- Tested only on Windows 11 / Docker Desktop with a pure-Python driver (a compiled psycopg binary was blocked
  by an application-control policy on the dev machine).

## 8. Final reflection

1. **Is semantic chunking always better?** No. In this run semantic chunking had the cleanest cut points
   (96% / 100% clean start/end, 0 broken fences) but the worst size control (14 chunks > 1500 chars, one of
   11,882), only 64.5% of chunks carried any heading context, it needs an embedding pass over every block,
   and its boundaries shift with the model/threshold. Markdown structure-aware chunking gave 100% heading
   path coverage, 94% clean ends and deterministic output with no model cost, which matters more for
   citations in technical docs. Semantic helps on unstructured prose without headings.
2. **If the most relevant document is restricted?** Return only the best *authorized* chunks (possibly
   none), never the restricted one, its title, its distance or even a count of withheld hits to the model or
   user. Optionally show a generic "no accessible answer - request access" message through a separate
   audited channel. Example: Priya's RBAC question returns shared overview text; the SEC-001 chunks at
   distance ~0.155 are not returned.
3. **Why enforce permissions in retrieval rather than ask the LLM?** An LLM that has seen the restricted text
   can leak it through paraphrase, prompt injection or jailbreak, and its compliance cannot be audited or
   guaranteed. Enforcing access in the database retrieval path means unauthorized text is never placed in
   the prompt, so it cannot be disclosed regardless of model behaviour; it also stays correct instantly on
   revocation because the check runs per query.
