"""main() do crm/app.py: porta e navegador pelo ambiente, sem abrir porta nem navegador de verdade."""
import threading

import pytest
import uvicorn

from crm import app as m


@pytest.fixture
def dubles(monkeypatch):
    """uvicorn.run, webbrowser.open, a checagem de porta e o banco trocados por dublês.

    A porta passa a "aceitar conexão" quando o uvicorn.run falso é chamado, como na vida real;
    o run falso espera até 3 s o navegador abrir (ou não) e volta.
    """
    estado = {'run': None, 'abertos': [], 'subiu': False, 'ocupada_antes': False}
    aberto = threading.Event()

    def run(app, **kw):
        estado['run'] = kw
        estado['subiu'] = True
        aberto.wait(3 if estado['esperar_navegador'] else 1)

    def abrir(url, *a, **k):
        estado['abertos'].append(url)
        aberto.set()
        return True

    def ocupada(port, espera=1.5):
        return estado['ocupada_antes'] or estado['subiu']

    monkeypatch.setattr(uvicorn, 'run', run)
    monkeypatch.setattr(m.webbrowser, 'open', abrir)
    monkeypatch.setattr(m, '_porta_ocupada', ocupada)
    monkeypatch.setattr(m, '_confere_banco', lambda: ('crm_demo', 1))
    for v in ('CRM_PORT', 'CRM_NO_BROWSER', 'CRM_EXIGE_BANCO'):
        monkeypatch.delenv(v, raising=False)
    estado['esperar_navegador'] = True
    return estado


@pytest.mark.parametrize('porta_env', [None, ''], ids=['sem_variavel', 'vazia'])
def test_main_padrao_8765_com_navegador(dubles, monkeypatch, porta_env):
    if porta_env is not None:
        monkeypatch.setenv('CRM_PORT', porta_env)
    m.main()
    assert dubles['run']['port'] == 8765
    assert dubles['run']['host'] == '127.0.0.1'
    assert dubles['abertos'] == ['http://127.0.0.1:8765/leads']


def test_main_sem_navegador(dubles, monkeypatch):
    monkeypatch.setenv('CRM_PORT', '8766')
    monkeypatch.setenv('CRM_NO_BROWSER', '1')
    dubles['esperar_navegador'] = False
    m.main()
    assert dubles['run']['port'] == 8766
    assert dubles['run']['host'] == '127.0.0.1'
    assert dubles['abertos'] == []


@pytest.mark.parametrize('valor', ['true', 'sim'])
def test_main_no_browser_outros_valores(dubles, monkeypatch, valor):
    monkeypatch.setenv('CRM_NO_BROWSER', valor)
    dubles['esperar_navegador'] = False
    m.main()
    assert dubles['abertos'] == []


def test_main_no_browser_zero_abre(dubles, monkeypatch):
    monkeypatch.setenv('CRM_NO_BROWSER', '0')
    m.main()
    assert dubles['abertos'] == ['http://127.0.0.1:8765/leads']


@pytest.mark.parametrize('valor', ['abc', '0', '70000', '-1', '８７６６'])
def test_main_porta_invalida(dubles, monkeypatch, valor):
    monkeypatch.setenv('CRM_PORT', valor)
    with pytest.raises(SystemExit) as e:
        m.main()
    assert 'CRM_PORT inválida' in str(e.value)
    assert dubles['run'] is None
    assert dubles['abertos'] == []


def test_main_ja_rodando_sem_navegador(dubles, monkeypatch):
    monkeypatch.setenv('CRM_NO_BROWSER', '1')
    dubles['ocupada_antes'] = True
    m.main()
    assert dubles['run'] is None
    assert dubles['abertos'] == []


def test_main_ja_rodando_com_navegador(dubles):
    dubles['ocupada_antes'] = True
    m.main()
    assert dubles['run'] is None
    assert dubles['abertos'] == ['http://127.0.0.1:8765/leads']


def test_main_banco_errado_nao_sobe(dubles, monkeypatch):
    monkeypatch.setenv('CRM_EXIGE_BANCO', 'crm_demo')
    monkeypatch.setattr(m, '_confere_banco', lambda: ('outro', 1))
    with pytest.raises(SystemExit):
        m.main()
    assert dubles['run'] is None
