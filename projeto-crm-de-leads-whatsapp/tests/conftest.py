"""Fixtures comuns. Os testes só LEEM o crm_demo (nenhum POST, nenhuma escrita).

Regras: no máximo 2 conexões do pytest (CRM_POOL_MAX=2); nenhum telefone de lead em id de teste ou em mensagem.
"""
import os

os.environ['CRM_POOL_MAX'] = '2'          # antes de importar crm.db (a raiz entra no path pelo pytest.ini)

import psycopg  # noqa: E402
import pytest  # noqa: E402

from crm import db  # noqa: E402
from crm.normaliza import canonico  # noqa: E402

BANCO = 'crm_demo'


@pytest.fixture(scope='session', autouse=True)
def confere_crm_demo():
    """Antes de qualquer teste: o banco é o crm_demo e responde. Senão, para a suíte inteira na hora."""
    try:
        with psycopg.connect(db.DATABASE_URL or '', connect_timeout=15,
                             application_name='crm-disparos-pytest') as cx:
            banco = cx.execute('SELECT current_database()').fetchone()[0]
    except Exception as e:
        motivo = (str(e).strip().splitlines() or [''])[0][:200]
        pytest.exit(f'Banco não responde ({type(e).__name__}: {motivo}). A suíte precisa do {BANCO}.', returncode=3)
    if banco != BANCO:
        pytest.exit(f'Banco errado: {banco}. A suíte só roda contra o {BANCO}.', returncode=3)
    yield


@pytest.fixture(scope='session')
def todos_tels(confere_crm_demo):
    """Todos os telefones de leads, numa consulta só."""
    return [r['tel'] for r in db.q('SELECT tel FROM leads')]


@pytest.fixture(scope='session')
def tel_lead(confere_crm_demo):
    """Um celular canônico de lead que tem evento, lido do banco na hora."""
    r = db.q("""SELECT l.tel FROM leads l
                WHERE length(l.tel)=11 AND substr(l.tel,3,1)='9'
                  AND EXISTS (SELECT 1 FROM eventos e WHERE e.tel=l.tel)
                ORDER BY l.tel LIMIT 1""", one=True)
    assert r is not None, 'crm_demo sem lead com evento'
    assert canonico(r['tel']) == r['tel'], 'tel_lead não é canônico'
    return r['tel']


@pytest.fixture(scope='session')
def tel_estrangeiro(todos_tels):
    """Um lead cujo telefone não é canônico (os estrangeiros do crm_demo)."""
    fora = sorted(t for t in todos_tels if canonico(t) is None)
    assert fora, 'crm_demo sem telefone estrangeiro'
    return fora[0]


@pytest.fixture(scope='session')
def client(confere_crm_demo):
    from fastapi.testclient import TestClient
    from crm.app import app
    with TestClient(app, follow_redirects=False) as c:
        yield c
