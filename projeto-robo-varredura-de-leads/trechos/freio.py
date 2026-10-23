# -*- coding: utf-8 -*-
# Trecho simplificado do robô: o freio.
# Antes de cada varredura o robô olha a variável SWEEP_STOP. Se ela vale 1, ele pula a rodada
# sem precisar mexer no código nem derrubar o servidor. As outras rotinas do mesmo servidor
# seguem a mesma ideia, cada uma com o seu *_STOP.
# Rodar: python3 trechos/freio.py   ou   SWEEP_STOP=1 python3 trechos/freio.py
import os


def freio():
    return (os.environ.get('SWEEP_STOP') or '0').strip().lower() in ('1', 'true', 'sim')


def uma_rodada():
    if freio():
        return 'freio puxado (SWEEP_STOP): pulando esta varredura'
    return 'varredura executada'


if __name__ == '__main__':
    print(uma_rodada())
