"""Páginas principais contra o crm_demo. Só GET.

Nenhum telefone de lead em id ou mensagem: os asserts sobre o HTML usam booleano calculado antes,
para que uma falha não despeje a lista (nomes e telefones) na saída do pytest.
"""
import time

import pytest

from crm.app import fmt_tel

LIMITE_S = 2.0


def _get(client, url):
    t = time.time()
    r = client.get(url)
    return r, time.time() - t


def test_raiz_redireciona_para_leads(client):
    r = client.get('/')
    assert r.status_code == 307
    assert r.headers['location'] == '/leads'
    r2 = client.get(r.headers['location'])
    assert r2.status_code == 200


@pytest.mark.parametrize('url', ['/leads', '/leads?page=2', '/campanhas', '/leads?campanha=nenhuma&sup=nao',
                                 '/leads?q=maria'])
def test_pagina_200_e_rapida(client, url):
    r, _ = _get(client, url)
    assert r.status_code == 200
    r, dt = _get(client, url)                     # 2a chamada: pool e cache aquecidos
    assert r.status_code == 200
    assert dt < LIMITE_S, f'{dt:.2f}s'


def test_leads_tem_lista(client):
    r = client.get('/leads')
    ok = 'href="/leads/' in r.text and 'CRM de disparos' in r.text
    assert ok, 'lista de leads sem linhas'


@pytest.mark.parametrize('page', ['0', '-3', '999999999999'])
def test_page_fora_da_faixa_nao_da_500(client, page):
    r = client.get(f'/leads?page={page}')
    assert r.status_code == 200


def test_ficha_do_lead(client, tel_lead):
    client.get(f'/leads/{tel_lead}')
    r, dt = _get(client, f'/leads/{tel_lead}')
    assert r.status_code == 200
    ok = fmt_tel(tel_lead) in r.text
    assert ok, 'ficha sem o telefone formatado'
    assert dt < LIMITE_S, f'{dt:.2f}s'


def test_lead_inexistente_404(client):
    r = client.get('/leads/00000000000')
    assert r.status_code == 404


def test_busca_pelos_8_ultimos_digitos(client, tel_lead):
    r = client.get('/leads', params={'q': tel_lead[-8:]})
    assert r.status_code == 200
    ok = f'href="/leads/{tel_lead}"' in r.text
    assert ok, 'busca pelo final do telefone não achou o lead'


def test_busca_pelo_telefone_com_mascara(client, tel_lead):
    r = client.get('/leads', params={'q': '+55 ' + fmt_tel(tel_lead)})
    assert r.status_code == 200
    ok = f'href="/leads/{tel_lead}"' in r.text
    assert ok, 'busca pelo telefone com máscara não achou o lead'


def test_estrangeiro_tem_ficha_e_e_achado(client, tel_estrangeiro):
    r = client.get(f'/leads/{tel_estrangeiro}')
    assert r.status_code == 200
    r = client.get('/leads', params={'q': tel_estrangeiro})
    assert r.status_code == 200
    ok = f'href="/leads/{tel_estrangeiro}"' in r.text
    assert ok, 'busca pelo telefone estrangeiro não achou o lead'


@pytest.mark.parametrize('q', ['4321', "';--", '%', '_', '\\'])
def test_busca_curta_ou_maliciosa(client, q):
    r = client.get('/leads', params={'q': q})
    assert r.status_code == 200


def test_busca_curta_e_por_nome(client, monkeypatch):
    """q com menos de 8 dígitos continua virando busca por nome (ILIKE), não por telefone."""
    from crm import app as m
    vistos = []
    real = m.db.conectar

    class Espia:
        def __init__(self, cx):
            self.cx = cx

        def execute(self, sql, params=None):
            vistos.append((sql, params))
            return self.cx.execute(sql, params)

    from contextlib import contextmanager

    @contextmanager
    def conectar(*a, **k):
        with real(*a, **k) as cx:
            yield Espia(cx)

    monkeypatch.setattr(m.db, 'conectar', conectar)
    m.resumo()                                    # cache do cabeçalho fora da conta
    vistos.clear()
    r = client.get('/leads', params={'q': '4321'})
    assert r.status_code == 200
    sql, params = vistos[0]
    assert 'l.nome ILIKE' in sql and params['q'] == '%4321%'
    assert 'tel_like' not in params
