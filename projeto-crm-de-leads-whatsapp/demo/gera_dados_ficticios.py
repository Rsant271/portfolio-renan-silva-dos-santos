"""Monta o banco de demonstração com dados 100% fictícios.

Passos: aplica o schema → gera as abas da planilha em CSV (demo/planilha) → roda a carga do CRM
→ cria campanhas, envios, respostas e pedidos de saída.

Uso:  python demo/gera_dados_ficticios.py

Nenhum dado vem de pessoa real. Os telefones são sequenciais (11 90000-0001, 11 90000-0002...),
os nomes são combinações sorteadas de nomes comuns e os textos das respostas foram inventados.
A planilha de propósito tem os problemas que a de verdade tinha: lead repetido entre abas, linha
laranja de duplicado, telefone inválido, número estrangeiro, dois telefones na mesma célula,
celular antigo sem o 9 e nome genérico ("WhatsApp", "Cliente").
"""
import csv
import sys
import random
import pathlib
import datetime as dt

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from crm import db  # noqa: E402
from crm import carga_planilha  # noqa: E402
from crm.normaliza import canonico  # noqa: E402

random.seed(2026)
PASTA = carga_planilha.PASTA
TZ = dt.timezone(dt.timedelta(hours=-3))

CABECALHO = ['Data', 'Origem', 'Nome', 'Telefone', 'Contato', 'Data contato', 'Agendado por', 'Status',
             'Data agenda', 'Hora agenda', 'Retorno', 'Bairro', 'Observação', 'Compareceu', 'Próximo contato',
             'Fechou', 'Valor', 'cor_fundo']

NOMES = ['Maria', 'Ana', 'Juliana', 'Patrícia', 'Fernanda', 'Camila', 'Aline', 'Beatriz', 'Larissa', 'Vanessa',
         'Adriana', 'Simone', 'Sandra', 'Luciana', 'Renata', 'Carla', 'Débora', 'Tatiane', 'José', 'João',
         'Antonio', 'Carlos', 'Paulo', 'Pedro', 'Lucas', 'Marcos', 'Rafael', 'Bruno', 'Thiago', 'Rodrigo',
         'Eduardo', 'Felipe', 'Gustavo', 'Daniel', 'Márcio', 'Sérgio', 'Roberto', 'André']
SOBRENOMES = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira', 'Lima',
              'Gomes', 'Costa', 'Ribeiro', 'Martins', 'Carvalho', 'Almeida', 'Lopes', 'Soares', 'Fernandes',
              'Vieira', 'Barbosa', 'Rocha', 'Dias', 'Nascimento', 'Andrade', 'Moreira', 'Nunes', 'Mendes']
BAIRROS = ['Santana', 'Tatuapé', 'Moema', 'Pinheiros', 'Butantã', 'Penha', 'Lapa', 'Ipiranga', 'Saúde',
           'Mooca', 'Vila Mariana', 'Tucuruvi', 'Casa Verde', 'Vila Prudente', 'Perdizes', '*', '']
ORIGENS = ['Google', 'Google', 'Meta ADS', 'Meta ADS', 'Meta ADS', 'Instagram', 'Indicação', 'Interno']
CANAIS = ['WhatsApp', 'WhatsApp', 'WhatsApp', 'Ligação', 'Formulário', 'Direct', 'Presencial']
ATENDENTES = ['Ana', 'Bruno', 'Carla']
RESPOSTAS = ['Quero saber o valor', 'Pode ser no sábado?', 'Tenho interesse sim', 'Qual o endereço?',
             'Agora não, obrigado', 'Vocês parcelam?', 'Me liga depois das 18h', 'Ok']
COR_HEX = {'verde': '#A9D08E', 'vermelho': '#E06666', 'amarelo': '#FFD966', 'laranja': '#FF6D01', 'branco': ''}
ABAS = [('Ago-26', 8, 100), ('Set-26', 9, 110), ('Out-26', 10, 120)]
CAMPANHAS = [
    ('reativacao-set', 'Reativação de quem pediu orçamento e não agendou', dt.date(2026, 9, 8), dt.date(2026, 9, 19)),
    ('lembrete-avaliacao', 'Lembrete para quem não compareceu na avaliação', dt.date(2026, 10, 1), dt.date(2026, 10, 10)),
    ('convite-retorno', 'Convite de retorno para limpeza', dt.date(2026, 10, 14), None),
]
ESTRANGEIROS = [('447700900123', 'Lead estrangeiro (Reino Unido)'), ('12025550123', 'Lead estrangeiro (EUA)')]

_seq = 0
_seq_antigo = 0


def novo_celular():
    """Próximo celular da série fictícia, já canônico: 11900000001, 11900000002..."""
    global _seq
    _seq += 1
    return f'1190000{_seq:04d}'


def novo_celular_antigo():
    """Celular escrito do jeito antigo, sem o 9: (11) 8000-0001. A carga tem de completar para 11980000001."""
    global _seq_antigo
    _seq_antigo += 1
    return f'(11) 8000-{_seq_antigo:04d}'


def mascara(tel):
    """Escreve o mesmo número de jeitos diferentes, como na planilha real."""
    jeito = random.random()
    if jeito < 0.45:
        return f'({tel[:2]}) {tel[2:7]}-{tel[7:]}'
    if jeito < 0.7:
        return tel
    if jeito < 0.85:
        return f'+55 {tel[:2]} {tel[2:7]}-{tel[7:]}'
    return '55' + tel


def data_txt(d):
    return f'{d.day:02d}/{d.month:02d}' if random.random() < 0.6 else f"{d.day}/{['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'][d.month - 1]}."


def linha(d, nome, tel_txt, cor=None):
    status = random.choices(['Agendado', 'Retornar', 'Sem interesse', 'Não atende', ''], [30, 20, 12, 18, 20])[0]
    if cor is None:
        cor = {'Agendado': 'verde', 'Retornar': 'amarelo', 'Sem interesse': 'vermelho'}.get(status, 'branco')
    agendado = status == 'Agendado'
    dia_ag = d + dt.timedelta(days=random.randint(1, 10))
    compareceu = random.choices(['Compareceu', 'Faltou'], [70, 30])[0] if agendado and dia_ag < dt.date(2026, 10, 20) else ''
    fechou = 'Sim' if compareceu == 'Compareceu' and random.random() < 0.35 else ''
    return [data_txt(d), random.choice(ORIGENS), nome, tel_txt, random.choice(CANAIS),
            data_txt(d + dt.timedelta(days=random.randint(0, 1))), random.choice(ATENDENTES) if agendado else '',
            status, f'{dia_ag.day:02d}/{dia_ag.month:02d}' if agendado else '',
            random.choice(['09:00', '10:30', '14:00', '15:30', '17:00']) if agendado else '',
            '', random.choice(BAIRROS),
            '', compareceu, '', fechou, '', COR_HEX[cor]]


def nome_sorteado():
    return f'{random.choice(NOMES)} {random.choice(SOBRENOMES)}'


def gera_planilha():
    PASTA.mkdir(parents=True, exist_ok=True)
    ja_vistos = []                                   # (nome, tel) das abas anteriores, para repetir lead entre abas
    for titulo, mes, n in ABAS:
        rows = []
        for i in range(n):
            d = dt.date(2026, mes, random.randint(1, 20 if mes == 10 else 28))
            r = random.random()
            if ja_vistos and r < 0.08:               # lead que volta em outra aba
                nome, tel = random.choice(ja_vistos)
                rows.append(linha(d, nome, mascara(tel)))
                continue
            if ja_vistos and r < 0.11:               # duplicado marcado de laranja
                nome, tel = random.choice(ja_vistos)
                rows.append(linha(d, nome, mascara(tel), cor='laranja'))
                continue
            nome = nome_sorteado()
            tel = novo_celular()
            rows.append(linha(d, nome, mascara(tel)))
            ja_vistos.append((nome, tel))
        # casos de borda, um pouco em cada aba
        d = dt.date(2026, mes, 15)
        rows.append(linha(d, nome_sorteado(), '123'))                           # telefone inválido
        rows.append(linha(d, nome_sorteado(), ''))                              # sem telefone
        rows.append(linha(d, 'WhatsApp', mascara(novo_celular())))               # nome genérico
        rows.append(linha(d, 'Cliente', mascara(novo_celular())))
        rows.append(linha(d, nome_sorteado(), novo_celular_antigo()))           # celular antigo, sem o 9
        if mes == 9:
            rows.append(linha(d, nome_sorteado(), '+351 910 000 001'))           # estrangeiro na planilha
            dois = novo_celular()
            rows.append(linha(d, 'Maria Aparecida Souza', f'({dois[:2]}) {dois[2:7]}-{dois[7:]} / (11) 3000-0001'))
        with open(PASTA / f'{titulo}.csv', 'w', encoding='utf-8', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(CABECALHO)
            w.writerows(rows)
        print(f'{titulo}.csv: {len(rows)} linhas')


def quando(dia, i):
    """Horário comercial determinístico dentro do dia."""
    h = 9 + (i * 7) % 9
    return dt.datetime(dia.year, dia.month, dia.day, h, (i * 13) % 60, tzinfo=TZ)


def gera_eventos():
    with db.conectar() as cx:
        for t, nome in ESTRANGEIROS:
            assert canonico(t) is None, t
            cx.execute("""INSERT INTO leads (tel, nome, origem, primeira_data, fontes)
                          VALUES (%s, %s, 'Meta', '2026-10-05', '{whatsapp}') ON CONFLICT (tel) DO NOTHING""", (t, nome))
        for nome, desc, ini, fim in CAMPANHAS:
            cx.execute("""INSERT INTO campanhas (nome, descricao, inicio, fim, fonte_hist)
                          VALUES (%s, %s, %s, %s, 'demo') ON CONFLICT (nome) DO NOTHING""", (nome, desc, ini, fim))
        aptos = [r['tel'] for r in cx.execute("""
            SELECT l.tel FROM leads l
            WHERE NOT EXISTS (SELECT 1 FROM supressao s WHERE s.tel=l.tel AND s.ate IS NULL)
            ORDER BY l.tel""").fetchall()]
        aptos += [t for t, _ in ESTRANGEIROS if t not in aptos]
        n = dict(envio=0, resposta=0, opt_out=0)
        saiu = set()
        for nome, _, ini, fim in CAMPANHAS:
            dias = ((fim or dt.date(2026, 10, 21)) - ini).days + 1
            alvo = random.sample([t for t in aptos if t not in saiu], k=min(90, len(aptos)))
            for i, tel in enumerate(alvo):
                dia = ini + dt.timedelta(days=i % dias)
                toques = 2 if random.random() < 0.3 else 1
                for toque in range(1, toques + 1):
                    q = quando(dia + dt.timedelta(days=3 * (toque - 1)), i)
                    cx.execute("""INSERT INTO eventos (tel, tipo, campanha, toque, variante, quando, instancia, entrega, fonte)
                                  VALUES (%s, 'envio', %s, %s, %s, %s, 'demo', 'entregue', 'demo') ON CONFLICT DO NOTHING""",
                               (tel, nome, toque, random.choice('AB'), q))
                    n['envio'] += 1
                sorte = random.random()
                if sorte < 0.03:
                    q = quando(dia, i) + dt.timedelta(hours=1)
                    cx.execute("""INSERT INTO eventos (tel, tipo, campanha, quando, texto, fonte)
                                  VALUES (%s, 'opt_out', %s, %s, 'SAIR', 'demo') ON CONFLICT DO NOTHING""", (tel, nome, q))
                    cx.execute("""INSERT INTO supressao (tel, motivo, fonte, evidencia, desde)
                                  SELECT %s, 'opt_out', 'campanha', %s, %s
                                  WHERE NOT EXISTS (SELECT 1 FROM supressao WHERE tel=%s AND motivo='opt_out' AND ate IS NULL)""",
                               (tel, f'respondeu SAIR na campanha {nome}', q, tel))
                    cx.execute("INSERT INTO etiquetas (tel, tag, origem) VALUES (%s, 'opt-out', 'demo') ON CONFLICT DO NOTHING", (tel,))
                    saiu.add(tel)
                    n['opt_out'] += 1
                elif sorte < 0.25:
                    q = quando(dia, i) + dt.timedelta(minutes=40)
                    cx.execute("""INSERT INTO eventos (tel, tipo, campanha, quando, texto, fonte)
                                  VALUES (%s, 'resposta', %s, %s, %s, 'demo') ON CONFLICT DO NOTHING""",
                               (tel, nome, q, random.choice(RESPOSTAS)))
                    cx.execute("INSERT INTO etiquetas (tel, tag, origem) VALUES (%s, 'respondeu', 'demo') ON CONFLICT DO NOTHING", (tel,))
                    n['resposta'] += 1
        cx.commit()
    print('eventos:', n)


def main():
    db.aplicar_schema()
    gera_planilha()
    carga_planilha.main([])
    gera_eventos()
    g = db.q("""SELECT (SELECT count(*) FROM leads) leads, (SELECT count(*) FROM rejeitados) rejeitados,
                       (SELECT count(*) FROM supressao WHERE ate IS NULL) suprimidos""", one=True)
    print(f"pronto: {g['leads']} leads, {g['rejeitados']} rejeitados, {g['suprimidos']} suprimidos")


if __name__ == '__main__':
    main()
