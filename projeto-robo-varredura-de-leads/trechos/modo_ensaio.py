# -*- coding: utf-8 -*-
# Trecho simplificado do robô: modo ensaio x modo escrever.
# O robô só grava na planilha quando a variável SWEEP_MODO vale "escrever".
# Sem a variável, ele roda em ensaio: faz a mesma análise e só manda o relatório.
# Rodar: python3 trechos/modo_ensaio.py   ou   SWEEP_MODO=escrever python3 trechos/modo_ensaio.py
import os

MODO = (os.environ.get('SWEEP_MODO') or 'ensaio').strip().lower()


def varredura(candidatos, escrever=None):
    escrever = (MODO == 'escrever') if escrever is None else escrever
    novos = [c for c in candidatos if c['classe'] == 'NOVO']
    duvidas = [c for c in candidatos if c['classe'] == 'DUVIDA']
    if escrever and novos:
        grava_na_planilha(novos)
    # Dúvida nunca é gravada, em nenhum modo: vai no relatório para uma pessoa decidir.
    cab = 'Leads novos' + ('' if escrever else ' (ensaio, nada escrito)')
    linhas = [cab, f'{"Gravei" if escrever else "Gravaria"}: {len(novos)}', f'Para revisar: {len(duvidas)}']
    linhas += [f'  {d["nome"]}: {d["motivo"]}' for d in duvidas]
    return '\n'.join(linhas)


def grava_na_planilha(novos):
    print(f'(aqui o robô real grava {len(novos)} linha(s) na aba do mês)')


if __name__ == '__main__':
    exemplo = [
        {'nome': 'Lead A', 'classe': 'NOVO', 'motivo': 'anúncio'},
        {'nome': 'Lead B', 'classe': 'NOVO', 'motivo': 'keyword do Google'},
        {'nome': 'Lead C', 'classe': 'DUVIDA', 'motivo': 'telefone fixo (revisar)'},
    ]
    print(varredura(exemplo))
