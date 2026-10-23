# -*- coding: utf-8 -*-
# Trecho simplificado do robô: normalização de telefone (versão 4.1).
# Todos os telefones deste arquivo são fictícios.
# Rodar: python3 trechos/normaliza_telefone.py
import re

BR_CEL = re.compile(r'^[1-9][1-9]9\d{8}$')       # celular já normalizado: DDD + 9 + 8 dígitos
FIXO_BR = re.compile(r'^[1-9][1-9][2-5]\d{7}$')  # DDD + 8 dígitos começando em 2 a 5 = telefone fixo


def norm(t):
    """Devolve (telefone só com dígitos, últimos 8 dígitos para achar duplicado)."""
    d = re.sub(r'\D', '', str(t or ''))
    if d.startswith('55') and len(d) >= 12:
        d = d[2:]
    # Celular antigo, de antes de 2012, sem o 9: o número do assinante começa em 6 a 9.
    if len(d) == 10 and re.match(r'^[1-9][1-9][6-9]\d{7}$', d):
        d = d[:2] + '9' + d[2:]
    # 10 dígitos começando em 2 a 5 é FIXO e fica como veio.
    # Na versão 4, antes da revisão, o 9 entrava em qualquer número de 10 dígitos, e um fixo virava o celular de outra pessoa.
    return d, (d[-8:] if len(d) >= 8 else '')


def classifica_telefone(t):
    tel, _ = norm(t)
    if BR_CEL.match(tel):
        return 'celular'
    if FIXO_BR.match(tel):
        return 'dúvida: telefone fixo (revisar)'
    return 'dúvida: fora do padrão de celular BR (revisar)'


if __name__ == '__main__':
    casos = [
        ('(11) 90000-0001', '11900000001', 'celular'),
        ('+55 11 90000-0002', '11900000002', 'celular'),
        ('(11) 8000-0003', '11980000003', 'celular'),                          # antigo: ganha o 9
        ('(11) 3000-0004', '1130000004', 'dúvida: telefone fixo (revisar)'),   # fixo: NÃO ganha o 9
        ('123', '123', 'dúvida: fora do padrão de celular BR (revisar)'),
    ]
    for entrada, esperado, classe in casos:
        tel, _ = norm(entrada)
        assert tel == esperado, (entrada, tel)
        assert classifica_telefone(entrada) == classe, (entrada, classifica_telefone(entrada))
        print(f'{entrada:<20} -> {tel:<12} {classe}')
    print('ok: os', len(casos), 'casos passaram')
