"""canonico(), internacional() e telefones(). Telefones fictícios (98765-4321, 555-0100): nenhum é de lead."""
import re

import pytest

from crm.normaliza import canonico, internacional, telefones

CASOS = [
    # (entrada, esperado, tipo)
    ('11987654321', '11987654321', 'celular canonico'),
    (11987654321, '11987654321', 'int'),
    ('5511987654321', '11987654321', 'com 55'),
    ('+55 (11) 98765-4321', '11987654321', 'com +55 e mascara'),
    ('1187654321', '11987654321', 'sem 9o digito'),
    ('551187654321', '11987654321', 'com 55 sem 9o'),
    ('(11) 8765-4321', '11987654321', 'sem 9o com mascara'),
    ('1123456789', '1123456789', 'fixo'),
    ('55 11 2345-6789', '1123456789', 'fixo com 55'),
    ('011 98765-4321', '11987654321', '0 de tronco 12 digitos'),
    ('01187654321', '11987654321', '0 de tronco sem 9o'),
    ('01123456789', '1123456789', '0 de tronco fixo'),
    ('55991234567', '55991234567', 'DDD 55 sem prefixo'),
    ('5555991234567', '55991234567', 'DDD 55 com prefixo'),
    ('555591234567', '55991234567', 'DDD 55 com prefixo sem 9o'),
    ('11 98765-4321 ramal', '11987654321', 'texto em volta'),
    ('+5511987654321', '11987654321', '+55 E.164'),
    ('+55 11 98765-4321', '11987654321', '+55 com espacos'),
    ('+ 55 (11) 8765-4321', '11987654321', '+ espaco 55 sem 9o'),
    ('+1 718 555 0100', None, 'EUA'),
    ('+61 412 345 678', None, 'Australia'),
    ('+591 71234567', None, 'Bolivia'),
    ('+90 532 123 4567', None, 'Turquia'),
    ('+351 912 345 678', None, 'Portugal'),
    ('+51 912 345 678', None, 'Peru'),
    ('+47 912 34 567', None, 'Noruega'),
    ('+45 20 12 34 56', None, 'Dinamarca'),
    ('+53 5123 4567', None, 'Cuba'),
    ('+11 98765-4321', None, '+ com codigo 11'),
    ('0800 123 4567', None, '0800'),
    ('10987654321', None, 'DDD inexistente'),
    ('11387654321', None, '11 digitos sem 9'),
    ('1113456789', None, 'fixo com 3o digito 1'),
    ('119876543210', None, '12 digitos sem 55'),
    ('00000000000', None, 'zeros'),
    ('abc', None, 'lixo letras'),
    ('123', None, 'lixo curto'),
    ('-', None, 'lixo traco'),
    ('１１９８７６５４３２１', None, 'digitos largura total'),
    ('١١٩٨٧٦٥٤٣٢١', None, 'digitos arabicos'),
    ('1198765432１', None, 'ASCII com um digito largura total'),
    ('', None, 'vazio'),
    (None, None, 'None'),
    ('   ', None, 'espacos'),
]


@pytest.mark.parametrize('entrada,esperado', [(e, s) for e, s, _ in CASOS], ids=[t for _, _, t in CASOS])
def test_canonico(entrada, esperado):
    assert canonico(entrada) == esperado


@pytest.mark.parametrize('entrada', [e for e, _, _ in CASOS], ids=[t for _, _, t in CASOS])
def test_canonico_so_ascii_e_idempotente(entrada):
    r = canonico(entrada)
    assert r is None or (re.fullmatch(r'[0-9]{10,11}', r, re.ASCII) and canonico(r) == r)


@pytest.mark.parametrize('entrada,esperado', [
    ('+1 718 555 0100', '17185550100'),
    ('+61 412 345 678', '61412345678'),
    ('5511987654321', None),
    ('11987654321', None),
])
def test_internacional(entrada, esperado):
    assert internacional(entrada) == esperado


@pytest.mark.parametrize('entrada,esperado', [
    ('11 98765-4321 / 11 2345-6789', ['11987654321', '1123456789']),
    ('11987654321 ou 11987654321', ['11987654321']),
    ('11 98765-4321 / +1 718 555 0100', ['11987654321']),
    ('+47 912 34 567', []),
    ('', []),
])
def test_telefones(entrada, esperado):
    assert telefones(entrada) == esperado


def test_canonico_idempotente_no_banco(todos_tels):
    """Os telefones do crm_demo: quem continua canônico não muda; os rejeitados são poucos (os estrangeiros)."""
    rejeitados = sum(canonico(t) is None for t in todos_tels)
    alterados = sum(canonico(t) not in (None, t) for t in todos_tels)
    assert alterados == 0, f'{alterados} telefones mudariam com a regra nova'
    assert rejeitados < len(todos_tels) / 100, f'{rejeitados} rejeitados de {len(todos_tels)}'
