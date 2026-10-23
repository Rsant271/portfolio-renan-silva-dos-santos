"""Carga da planilha de leads (uma aba por mês) no CRM. Idempotente: rodar de novo só atualiza.

No uso real a carga lia o Google Sheets pela API. Nesta versão de portfólio cada aba é um CSV
(`Set-26.csv`, `Out-26.csv`...) na pasta CRM_PLANILHA_DIR (padrão: demo/planilha), com as colunas
A..Q da planilha e mais uma coluna `cor_fundo` com a cor da linha em hexadecimal.

Uso:  python -m crm.carga_planilha            (todas as abas *-26)
      python -m crm.carga_planilha Set-26     (só uma aba)
      python -m crm.carga_planilha --dry-run  (lê e conta, não grava)

Regras:
- chave = telefone canônico; linha sem telefone válido vai pra `rejeitados`
- cor da linha: verde/vermelho/amarelo/branco; laranja = duplicado (etiqueta), não é cor
- entre abas: aba_planilha = mais recente; primeira_data = mais antiga; cor = mais recente não-laranja
- coluna M (Observação) e Q (Valor) NÃO entram no CRM.
"""
import os
import re
import csv
import sys
import pathlib
import datetime as dt

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from crm import db
from crm.normaliza import telefones, internacional, nome_limpo, nome_msg, cor_nome, origem_norm

PASTA = pathlib.Path(os.environ.get('CRM_PLANILHA_DIR') or pathlib.Path(__file__).resolve().parent.parent / 'demo' / 'planilha')
MESES = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}


def abas_2026():
    """(título, arquivo) de cada CSV no formato Mmm-26, em ordem de mês."""
    out = []
    for f in PASTA.glob('*.csv'):
        m = re.fullmatch(r'([A-Za-z]{3})-(\d{2})', f.stem.strip())
        if m and m.group(1).lower() in MESES and m.group(2) == '26':
            out.append((f.stem, f))
    return sorted(out, key=lambda x: MESES[x[0][:3].lower()])


def ler_aba(titulo, arquivo):
    """Linhas da aba como (nº da linha na planilha, 17 células A..Q, cor hex). Linha 1 é o cabeçalho."""
    linhas = []
    with open(arquivo, encoding='utf-8', newline='') as fh:
        for i, row in enumerate(list(csv.reader(fh))[1:]):
            cells = [(v or '').strip() for v in row[:17]] + [''] * (17 - len(row[:17]))
            if not any(cells[:4]):
                continue
            cor = (row[17].strip() or None) if len(row) > 17 else None
            linhas.append((i + 2, cells, cor))
    return linhas


def data_br(s, ano=2026):
    """'18/ago.' | '18/08' | '18/08/2026' -> date."""
    s = (s or '').strip().lower().rstrip('.')
    m = re.match(r'(\d{1,2})/([a-z]{3})\.?(?:/(\d{2,4}))?$', s)
    if m and m.group(2) in MESES:
        y = int(m.group(3)) if m.group(3) else ano
        y = y + 2000 if y < 100 else y
        try:
            return dt.date(y, MESES[m.group(2)], int(m.group(1)))
        except ValueError:
            return None
    m = re.match(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?$', s)
    if m:
        y = int(m.group(3)) if m.group(3) else ano
        y = y + 2000 if y < 100 else y
        try:
            return dt.date(y, int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def aba_ord(t):
    return MESES[t[:3].lower()]


def main(argv):
    dry = '--dry-run' in argv
    so = [a for a in argv if not a.startswith('--')]
    abas = abas_2026()
    if so:
        abas = [a for a in abas if a[0] in so]
    print('abas:', [a[0] for a in abas])
    tot = dict(linhas=0, validas=0, rejeitadas=0, dup_na_aba=0)
    leads = {}      # tel -> dict agregado
    linhas_db = []  # planilha_linhas
    rejeitados = []
    for titulo, arquivo in abas:
        ls = ler_aba(titulo, arquivo)
        vistos_aba = {}
        print(f'  {titulo}: {len(ls)} linhas')
        for n, c, corhex in ls:
            tot['linhas'] += 1
            tels = telefones(c[3])
            cor = cor_nome(corhex)
            nome = nome_limpo(c[2])
            data = data_br(c[0])
            if not tels:
                tot['rejeitadas'] += 1
                motivo = 'sem telefone' if not c[3] else ('internacional' if internacional(c[3]) else 'telefone invalido')
                rejeitados.append(('planilha', f'{titulo}!{n}', c[3], motivo, nome))
                linhas_db.append(dict(aba=titulo, linha=n, tel=None, c=c, cor=cor, corhex=corhex, data=data))
                continue
            tel = tels[0]
            tot['validas'] += 1
            if tel in vistos_aba:
                tot['dup_na_aba'] += 1
            vistos_aba[tel] = n
            linhas_db.append(dict(aba=titulo, linha=n, tel=tel, c=c, cor=cor, corhex=corhex, data=data))
            L = leads.setdefault(tel, dict(tel=tel, nome=None, origem=None, tipo=None, primeira_data=None,
                                           aba=None, linha=None, cor=None, bairro=None, abas=set(), cores=[],
                                           status=None, compareceu=None, fechou=None, extra_tels=set()))
            L['abas'].add(titulo)
            for t2 in tels[1:]:
                L['extra_tels'].add(t2)
            if data and (L['primeira_data'] is None or data < L['primeira_data']):
                L['primeira_data'] = data
            # mais recente manda (aba maior, linha maior)
            if L['aba'] is None or (aba_ord(titulo), n) >= (aba_ord(L['aba']), L['linha'] or 0):
                L['aba'], L['linha'] = titulo, n
                if nome:
                    L['nome'] = nome
                if c[1]:
                    L['origem'] = origem_norm(c[1])
                if c[4]:
                    L['tipo'] = c[4]
                if c[11] and c[11] != '*':
                    L['bairro'] = c[11]
                L['status'] = c[7] or L['status']
                L['compareceu'] = c[13] or L['compareceu']
                L['fechou'] = c[15] or L['fechou']
            if cor != 'laranja':
                L['cores'].append((aba_ord(titulo), n, cor))
            else:
                L['dup_planilha'] = True
            if not L['nome'] and nome:
                L['nome'] = nome
    for L in leads.values():
        L['cor'] = sorted(L['cores'])[-1][2] if L['cores'] else 'branco'
    print('totais:', tot, '| leads distintos:', len(leads), '| rejeitados:', len(rejeitados))
    cores = {}
    for L in leads.values():
        cores[L['cor']] = cores.get(L['cor'], 0) + 1
    print('por cor:', cores)
    if dry:
        return
    with db.conectar() as cx:
      antes = cx.execute("SELECT count(*) n FROM leads").fetchone()['n']
      with cx.pipeline():
        for L in leads.values():
            cx.execute("""
                INSERT INTO leads (tel, nome, nome_msg, origem, tipo, primeira_data, fontes, aba_planilha, linha_planilha,
                                   cor_planilha, bairro)
                VALUES (%(tel)s, %(nome)s, %(nome_msg)s, %(origem)s, %(tipo)s, %(primeira_data)s, '{planilha}',
                        %(aba)s, %(linha)s, %(cor)s, %(bairro)s)
                ON CONFLICT (tel) DO UPDATE SET
                  nome = COALESCE(EXCLUDED.nome, leads.nome),
                  nome_msg = COALESCE(EXCLUDED.nome_msg, leads.nome_msg),
                  origem = COALESCE(EXCLUDED.origem, leads.origem),
                  tipo = COALESCE(EXCLUDED.tipo, leads.tipo),
                  primeira_data = LEAST(EXCLUDED.primeira_data, leads.primeira_data),
                  fontes = (SELECT ARRAY(SELECT DISTINCT unnest(leads.fontes || '{planilha}'))),
                  aba_planilha = EXCLUDED.aba_planilha, linha_planilha = EXCLUDED.linha_planilha,
                  cor_planilha = EXCLUDED.cor_planilha,
                  bairro = COALESCE(EXCLUDED.bairro, leads.bairro),
                  atualizado_em = now()""",
                dict(tel=L['tel'], nome=L['nome'], nome_msg=nome_msg(L['nome']), origem=L['origem'], tipo=L['tipo'],
                     primeira_data=L['primeira_data'], aba=L['aba'], linha=L['linha'], cor=L['cor'], bairro=L['bairro']))
            tags = []
            if L.get('dup_planilha') or len(L['abas']) > 1:
                tags.append('duplicado-planilha')
            if nome_msg(L['nome']) is None:
                tags.append('nome-generico')
            st = (L['status'] or '').lower()
            if L['cor'] == 'verde' or st.startswith('agend'):
                tags.append('agendado')
            if L['cor'] == 'vermelho':
                tags.append('descartado')
            if L['cor'] == 'amarelo':
                tags.append('em-negociacao')
            cp = (L['compareceu'] or '').lower()
            if cp.startswith('compar'):
                tags.append('compareceu')
            if (L['fechou'] or '').strip():
                tags.append('fechou')
            for t in tags:
                cx.execute("INSERT INTO etiquetas (tel, tag, origem) VALUES (%s, %s, 'carga_inicial') ON CONFLICT DO NOTHING", (L['tel'], t))
            if L['cor'] == 'vermelho':
                cx.execute("""INSERT INTO supressao (tel, motivo, fonte, evidencia)
                              SELECT %s, 'descartado', 'planilha', %s
                              WHERE NOT EXISTS (SELECT 1 FROM supressao WHERE tel=%s AND motivo='descartado' AND ate IS NULL)""",
                           (L['tel'], f"linha vermelha {L['aba']}!{L['linha']}", L['tel']))
            for t2 in L['extra_tels']:
                cx.execute("INSERT INTO eventos (tel, tipo, quando, texto, fonte, fonte_ref) VALUES (%s,'nota',now(),%s,'planilha',%s) ON CONFLICT DO NOTHING",
                           (L['tel'], f'segundo telefone na mesma celula: {t2}', f"{L['aba']}!{L['linha']}"))
        for ln in linhas_db:
            c = ln['c']
            cx.execute("""
                INSERT INTO planilha_linhas (aba, linha, tel, tel_original, data, origem, nome, tipo, data_contato, agendado_por,
                    status, data_agenda, hora_agenda, contato, bairro, compareceu, proximo_contato, fechou, cor, cor_hex, lida_em)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())
                ON CONFLICT (aba, linha) DO UPDATE SET tel=EXCLUDED.tel, tel_original=EXCLUDED.tel_original, data=EXCLUDED.data,
                    origem=EXCLUDED.origem, nome=EXCLUDED.nome, tipo=EXCLUDED.tipo, data_contato=EXCLUDED.data_contato,
                    agendado_por=EXCLUDED.agendado_por, status=EXCLUDED.status, data_agenda=EXCLUDED.data_agenda,
                    hora_agenda=EXCLUDED.hora_agenda, contato=EXCLUDED.contato, bairro=EXCLUDED.bairro, compareceu=EXCLUDED.compareceu,
                    proximo_contato=EXCLUDED.proximo_contato, fechou=EXCLUDED.fechou, cor=EXCLUDED.cor, cor_hex=EXCLUDED.cor_hex, lida_em=now()""",
                (ln['aba'], ln['linha'], ln['tel'], c[3], ln['data'], c[1], nome_limpo(c[2]), c[4], c[5], c[6], c[7], c[8], c[9], c[10],
                 c[11], c[13], c[14], c[15], ln['cor'], ln['corhex']))
        cx.execute("DELETE FROM rejeitados WHERE fonte='planilha'")
        for r in rejeitados:
            cx.execute("INSERT INTO rejeitados (fonte, fonte_ref, valor, motivo, nome) VALUES (%s,%s,%s,%s,%s)", r)
      cx.commit()
      depois = cx.execute("SELECT count(*) n FROM leads").fetchone()['n']
    print(f'gravado: leads novos {depois - antes} · atualizados {len(leads) - (depois - antes)} · linhas {len(linhas_db)} · rejeitados {len(rejeitados)}')


if __name__ == '__main__':
    main(sys.argv[1:])
