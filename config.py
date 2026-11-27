"""Shared configuration, DB connections (pure-Python pg8000) and embeddings."""
import hashlib, hmac, os
from functools import lru_cache
from pathlib import Path
import pg8000.dbapi
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')

TENANT = 'KUBERNETES_DEMO'
HOST = os.getenv('DB_HOST', '127.0.0.1')
PORT = int(os.getenv('DB_PORT', '5434'))
DBNAME = os.getenv('DB_NAME', 'k8s_rag')
ADMIN_USER = os.getenv('ADMIN_USER', 'fde')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')
READER_ROLE = os.getenv('READER_ROLE', 'k8s_rag_reader')
READER_PASSWORD = os.getenv('READER_PASSWORD', '')
SIGNING_KEY = os.getenv('APP_SIGNING_KEY', '')
MODEL = os.getenv('EMBED_MODEL', 'BAAI/bge-small-en-v1.5')
USERS = ('priya', 'arjun', 'meena', 'divya')


def connect(role='reader'):
    """role: 'reader' (restricted, RLS applies), 'admin' (owner of k8s_rag),
    'server' (admin on the postgres maintenance db, used only to CREATE DATABASE)."""
    if role == 'reader':
        user, pw, db = READER_ROLE, READER_PASSWORD, DBNAME
    else:
        user, pw, db = ADMIN_USER, ADMIN_PASSWORD, ('postgres' if role == 'server' else DBNAME)
    if not pw:
        raise RuntimeError('Missing password: copy .env.example to .env and fill it in')
    return pg8000.dbapi.connect(user=user, password=pw, host=HOST, port=PORT, database=db)


def vec(v):
    """pgvector text literal; use as  %s::vector"""
    return '[' + ','.join(f'{x:.7f}' for x in v) + ']'


def sign_identity(user_id, tenant=TENANT):
    """Trusted-backend step: HMAC that the database verifies. The signing key is never
    readable by the reader role, so a reader-role holder cannot forge another identity."""
    return hmac.new(SIGNING_KEY.encode(), f'{user_id}|{tenant}'.encode(), hashlib.sha256).hexdigest()


@lru_cache(maxsize=1)
def get_model():
    from fastembed import TextEmbedding
    print(f'Loading embedding model {MODEL} ...')
    return TextEmbedding(model_name=MODEL)


def embed(texts, batch_size=32):
    out = [v.tolist() for v in get_model().embed(list(texts), batch_size=batch_size)]
    if any(len(v) != 384 for v in out):
        raise RuntimeError('Expected 384-dimensional embeddings')
    return out
