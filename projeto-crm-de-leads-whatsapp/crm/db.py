"""Conexão com o Postgres do CRM. Lê DATABASE_URL do arquivo .env da pasta do projeto ou do ambiente.

No uso real o banco ficava num servidor fora do Brasil e a tela rodava aqui: cada ida e volta custava
~180 ms e abrir conexão nova custava ~1,5 s. Por isso as conexões ficam num POOL reaproveitado entre requisições.
"""
import os
import pathlib
import atexit
import psycopg
from psycopg.rows import dict_row

_ENV = pathlib.Path(__file__).resolve().parent.parent / '.env'


def _load_env():
    if _ENV.exists():
        for line in _ENV.read_text(encoding='utf-8').splitlines():
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_env()
DATABASE_URL = os.environ.get('CRM_DATABASE_URL') or os.environ.get('DATABASE_URL')
_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        from psycopg_pool import ConnectionPool
        if not DATABASE_URL:
            raise SystemExit('DATABASE_URL ausente (veja o README, passo 3)')
        _pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=int(os.environ.get('CRM_POOL_MAX', '4')), timeout=30,
                               max_idle=300, kwargs=dict(row_factory=dict_row,
                                                         application_name='crm-disparos'),
                               open=True)
        _pool.wait(timeout=30)
        atexit.register(_fechar)
    return _pool


def _fechar():
    global _pool
    if _pool is not None:
        try:
            _pool.close()
        except Exception:
            pass
        _pool = None


def conectar(autocommit=False):
    """Context manager que entrega uma conexão do pool (commit no fim, devolve ao pool)."""
    if autocommit:
        if not DATABASE_URL:
            raise SystemExit('DATABASE_URL ausente (veja o README, passo 3)')
        return psycopg.connect(DATABASE_URL, row_factory=dict_row, autocommit=True,
                               connect_timeout=20, application_name='crm-disparos-ddl')
    return _get_pool().connection()


def aplicar_schema():
    sql = (pathlib.Path(__file__).parent / 'schema.sql').read_text(encoding='utf-8')
    with conectar(autocommit=True) as cx:
        cx.execute(sql)


def q(sql, params=None, one=False):
    with conectar() as cx:
        cur = cx.execute(sql, params)
        if cur.description is None:
            return None
        rows = cur.fetchall()
        return (rows[0] if rows else None) if one else rows


if __name__ == '__main__':
    import time
    aplicar_schema()
    t0 = time.time()
    with conectar() as cx:
        r = cx.execute("SELECT current_database() db, version() v").fetchone()
        t = cx.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY 1").fetchall()
    t1 = time.time()
    with conectar() as cx:
        cx.execute("SELECT 1").fetchone()
    print('db:', r['db'], '|', r['v'].split(',')[0])
    print('tabelas:', [x['table_name'] for x in t])
    print(f'1a conexao+2 queries: {t1 - t0:.2f}s | query no pool quente: {time.time() - t1:.2f}s')
