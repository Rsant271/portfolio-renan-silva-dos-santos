"""CRM de disparos: tela local (FastAPI + Jinja) sobre um banco Postgres.

Uso:  python -m crm.app     → abre http://127.0.0.1:8765
      CRM_PORT=8766 CRM_NO_BROWSER=1 python -m crm.app   → outra porta, sem abrir navegador
A tela NUNCA envia mensagem; só lê o banco e registra etiquetas/supressão/notas.
"""
import os
import re
import sys
import pathlib
import threading
import webbrowser
import datetime as dt
from urllib.parse import urlencode

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from crm import db
from crm.normaliza import canonico

APP_DIR = pathlib.Path(__file__).parent
app = FastAPI(title='CRM de disparos (demo)')
tpl = Jinja2Templates(directory=str(APP_DIR / 'templates'))
PAGE = 50

CORES = ['verde', 'amarelo', 'branco', 'vermelho']
TAGS_MANUAIS = ['perdido', 'em-negociacao', 'mudo', 'prioridade', 'revisar', 'nao-perturbe']
MOTIVOS_SUPRESSAO = ['opt_out', 'em_tratamento', 'fechou', 'blacklist', 'sem_whatsapp']


def fmt_tel(t):
    if not t:
        return ''
    if len(t) == 11:
        return f'({t[:2]}) {t[2:7]}-{t[7:]}'
    if len(t) == 10:
        return f'({t[:2]}) {t[2:6]}-{t[6:]}'
    return t


def _local(d):
    """timestamptz vem em UTC; mostrar na hora de São Paulo."""
    if d.tzinfo is None:
        return d
    try:
        return d.astimezone(dt.timezone(dt.timedelta(hours=-3)))
    except Exception:
        return d


def fmt_data(v):
    if isinstance(v, dt.datetime):
        return _local(v).strftime('%d/%m/%Y %H:%M')
    if isinstance(v, dt.date):
        return v.strftime('%d/%m/%Y')
    if isinstance(v, str) and len(v) >= 10 and v[4] == '-' and v[7] == '-':
        try:                                    # veio de jsonb: '2026-09-09' ou '2026-09-09T14:00:00+00:00'
            if len(v) > 10:
                return _local(dt.datetime.fromisoformat(v)).strftime('%d/%m/%Y %H:%M')
            return dt.date.fromisoformat(v[:10]).strftime('%d/%m/%Y')
        except ValueError:
            return v
    return v or ''


tpl.env.filters['tel'] = fmt_tel
tpl.env.filters['dt'] = fmt_data


_CACHE = {'em': 0.0, 'dados': None}
CACHE_SEG = 90


def invalida_cache():
    _CACHE['em'] = 0.0


def resumo():
    """Números do cabeçalho e das listas de filtro. Uma ida ao banco, cacheada (cada ida ao banco remoto custa caro)."""
    import time
    if _CACHE['dados'] is not None and time.time() - _CACHE['em'] < CACHE_SEG:
        return _CACHE['dados']
    with db.conectar() as cx:
        r = {}
        g = cx.execute("""
            WITH t AS (SELECT count(*) n FROM leads),
                 co AS (SELECT cor_planilha cor, count(*) n FROM leads GROUP BY 1),
                 og AS (SELECT origem, count(*) n FROM leads GROUP BY 1),
                 ab AS (SELECT DISTINCT aba_planilha a FROM leads WHERE aba_planilha IS NOT NULL),
                 tg AS (SELECT tag, count(*) n FROM etiquetas GROUP BY 1),
                 tp AS (SELECT tipo, count(*) n FROM leads WHERE tipo IS NOT NULL GROUP BY 1),
                 cp AS (SELECT count(DISTINCT tel) n FROM eventos WHERE tipo='envio'),
                 sp AS (SELECT count(DISTINCT tel) n FROM supressao WHERE ate IS NULL),
                 ca AS (SELECT c.nome, c.inicio, c.fim,
                          count(e.id) FILTER (WHERE e.tipo='envio') envios,
                          count(DISTINCT e.tel) FILTER (WHERE e.tipo='envio') leads,
                          count(DISTINCT e.tel) FILTER (WHERE e.tipo='resposta') respostas,
                          count(DISTINCT e.tel) FILTER (WHERE e.tipo='opt_out') optouts
                        FROM campanhas c LEFT JOIN eventos e ON e.campanha=c.nome GROUP BY 1,2,3)
            SELECT (SELECT n FROM t) total,
                   (SELECT n FROM cp) com_campanha,
                   (SELECT n FROM sp) suprimidos,
                   (SELECT jsonb_object_agg(COALESCE(cor,'branco'), n) FROM co) cores,
                   (SELECT jsonb_agg(jsonb_build_object('origem', origem, 'n', n) ORDER BY n DESC) FROM og) origens,
                   (SELECT jsonb_agg(a) FROM ab) abas,
                   (SELECT jsonb_agg(jsonb_build_object('tag', tag, 'n', n) ORDER BY n DESC) FROM tg) tags,
                   (SELECT jsonb_agg(tipo ORDER BY n DESC) FROM tp) tipos,
                   (SELECT jsonb_agg(to_jsonb(ca) ORDER BY inicio) FROM ca) campanhas
        """).fetchone()
    r['total'] = g['total']
    r['com_campanha'] = g['com_campanha']
    r['suprimidos'] = g['suprimidos']
    r['cores'] = g['cores'] or {}
    r['origens'] = g['origens'] or []
    r['abas'] = g['abas'] or []
    r['tags'] = g['tags'] or []
    r['tipos'] = (g['tipos'] or [])[:12]
    r['campanhas'] = g['campanhas'] or []
    _CACHE['dados'] = r
    _CACHE['em'] = time.time()
    return r


MESES = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}


@app.get('/', response_class=HTMLResponse)
def home():
    return RedirectResponse('/leads')


@app.get('/leads', response_class=HTMLResponse)
def leads(request: Request, q: str = '', cor: str = '', origem: str = '', tag: str = '', aba: str = '',
          tipo: str = '', campanha: str = '', sup: str = '', page: int = 1):
    page = min(max(1, page), 100000)             # page=0 ou negativo dava OFFSET negativo (erro 500)
    where, params = [], {}
    if q:
        d = canonico(q)
        so_digitos = re.sub(r'[^0-9]', '', q)
        if d:
            where.append("(l.tel = %(tel)s OR l.tel LIKE %(tel_like)s)"); params['tel'] = d; params['tel_like'] = f'%{d[-8:]}'
        elif len(so_digitos) >= 8:                  # número que não é canônico (estrangeiro) ou só o final dele
            where.append("l.tel LIKE %(tel_like)s"); params['tel_like'] = f'%{so_digitos[-8:]}'
        else:
            where.append("l.nome ILIKE %(q)s"); params['q'] = f'%{q}%'
    if cor:
        where.append("COALESCE(l.cor_planilha,'branco') = %(cor)s"); params['cor'] = cor
    if origem:
        where.append("l.origem = %(origem)s"); params['origem'] = origem
    if aba:
        where.append("l.aba_planilha = %(aba)s"); params['aba'] = aba
    if tipo:
        where.append("l.tipo = %(tipo)s"); params['tipo'] = tipo
    if tag:
        where.append("EXISTS (SELECT 1 FROM etiquetas t WHERE t.tel=l.tel AND t.tag=%(tag)s)"); params['tag'] = tag
    if campanha == 'nenhuma':
        where.append("NOT EXISTS (SELECT 1 FROM eventos e WHERE e.tel=l.tel AND e.tipo='envio')")
    elif campanha:
        where.append("EXISTS (SELECT 1 FROM eventos e WHERE e.tel=l.tel AND e.tipo='envio' AND e.campanha=%(camp)s)"); params['camp'] = campanha
    if sup == 'sim':
        where.append("EXISTS (SELECT 1 FROM supressao s WHERE s.tel=l.tel AND s.ate IS NULL)")
    elif sup == 'nao':
        where.append("NOT EXISTS (SELECT 1 FROM supressao s WHERE s.tel=l.tel AND s.ate IS NULL)")
    sql_where = (' WHERE ' + ' AND '.join(where)) if where else ''
    params['lim'] = PAGE; params['off'] = (page - 1) * PAGE
    with db.conectar() as cx:
        rows = cx.execute(f"""
            SELECT count(*) OVER () total_rows,
                   l.tel, l.nome, l.nome_msg, l.origem, l.tipo, l.primeira_data, l.aba_planilha, l.linha_planilha,
                   COALESCE(l.cor_planilha,'branco') cor, l.bairro, l.etapa_crm, l.status_sistema,
                   (SELECT string_agg(tag, ' ' ORDER BY tag) FROM etiquetas t WHERE t.tel=l.tel) tags,
                   (SELECT max(quando) FROM eventos e WHERE e.tel=l.tel AND e.tipo='envio') ultimo_envio,
                   (SELECT count(*) FROM eventos e WHERE e.tel=l.tel AND e.tipo='envio') envios,
                   EXISTS (SELECT 1 FROM eventos e WHERE e.tel=l.tel AND e.tipo='resposta') respondeu,
                   (SELECT string_agg(motivo, ',') FROM supressao s WHERE s.tel=l.tel AND s.ate IS NULL) supressao
            FROM leads l{sql_where}
            ORDER BY l.primeira_data DESC NULLS LAST, l.linha_planilha DESC
            LIMIT %(lim)s OFFSET %(off)s""", params).fetchall()
    total = rows[0]['total_rows'] if rows else 0
    r = resumo()
    r['abas'] = sorted(r['abas'], key=lambda a: MESES.get(a[:3].lower(), 0))
    f = dict(q=q, cor=cor, origem=origem, tag=tag, aba=aba, tipo=tipo, campanha=campanha, sup=sup)
    qs = urlencode({k: v for k, v in f.items() if v})
    return tpl.TemplateResponse(request, 'leads.html', dict(rows=rows, total=total, page=page,
                                pages=max(1, -(-total // PAGE)), f=f, qs=qs, r=r, cores=CORES))


@app.get('/leads/{tel}', response_class=HTMLResponse)
def lead(request: Request, tel: str, msg: str = ''):
    with db.conectar() as cx:   # uma ida só ao banco: o lead e todas as listas da ficha
        g = cx.execute("""
            SELECT to_jsonb(l) lead,
              (SELECT jsonb_agg(to_jsonb(t) ORDER BY t.desde) FROM etiquetas t WHERE t.tel=l.tel) tags,
              (SELECT jsonb_agg(to_jsonb(s) ORDER BY s.desde DESC) FROM supressao s WHERE s.tel=l.tel) sup,
              (SELECT jsonb_agg(to_jsonb(e) ORDER BY e.quando DESC) FROM eventos e WHERE e.tel=l.tel) ev,
              (SELECT jsonb_agg(to_jsonb(p) ORDER BY p.data DESC NULLS LAST, p.aba, p.linha) FROM planilha_linhas p WHERE p.tel=l.tel) linhas,
              (SELECT jsonb_agg(to_jsonb(a) ORDER BY a.quando DESC) FROM ajustes a WHERE a.tel=l.tel) ajustes
            FROM leads l WHERE l.tel=%s""", (tel,)).fetchone()
    if not g:
        return HTMLResponse('<p>lead não encontrado</p>', status_code=404)
    L = g['lead']
    L['fontes'] = L.get('fontes') or []
    return tpl.TemplateResponse(request, 'lead.html', dict(L=L, tags=g['tags'] or [], sup=g['sup'] or [],
                                ev=g['ev'] or [], linhas=g['linhas'] or [], ajustes=g['ajustes'] or [],
                                msg=msg, tags_manuais=TAGS_MANUAIS, motivos=MOTIVOS_SUPRESSAO))


@app.post('/leads/{tel}/tag')
def add_tag(tel: str, tag: str = Form(...)):
    tag = tag.strip().lower().replace(' ', '-')[:40]
    if tag:
        with db.conectar() as cx:
            cx.execute("INSERT INTO etiquetas (tel, tag, origem) VALUES (%s,%s,'manual') ON CONFLICT DO NOTHING", (tel, tag))
            cx.execute("INSERT INTO ajustes (tel, acao, detalhe) VALUES (%s,'tag+',%s)", (tel, tag))
            cx.commit()
        invalida_cache()
    return RedirectResponse(f'/leads/{tel}?msg=etiqueta+adicionada', status_code=303)


@app.post('/leads/{tel}/tag/remover')
def del_tag(tel: str, tag: str = Form(...)):
    with db.conectar() as cx:
        cx.execute("DELETE FROM etiquetas WHERE tel=%s AND tag=%s", (tel, tag))
        cx.execute("INSERT INTO ajustes (tel, acao, detalhe) VALUES (%s,'tag-',%s)", (tel, tag))
        cx.commit()
    invalida_cache()
    return RedirectResponse(f'/leads/{tel}?msg=etiqueta+removida', status_code=303)


@app.post('/leads/{tel}/supressao')
def add_sup(tel: str, motivo: str = Form(...), evidencia: str = Form('')):
    if motivo not in MOTIVOS_SUPRESSAO:
        return RedirectResponse(f'/leads/{tel}?msg=motivo+invalido', status_code=303)
    with db.conectar() as cx:
        cx.execute("""INSERT INTO supressao (tel, motivo, fonte, evidencia) SELECT %s,%s,'manual',%s
                      WHERE NOT EXISTS (SELECT 1 FROM supressao WHERE tel=%s AND motivo=%s AND ate IS NULL)""",
                   (tel, motivo, evidencia.strip() or None, tel, motivo))
        cx.execute("INSERT INTO etiquetas (tel, tag, origem) VALUES (%s,%s,'manual') ON CONFLICT DO NOTHING", (tel, motivo.replace('_', '-')))
        cx.execute("INSERT INTO ajustes (tel, acao, detalhe) VALUES (%s,'supressao+',%s)", (tel, f'{motivo}: {evidencia.strip()}'))
        cx.commit()
    invalida_cache()
    return RedirectResponse(f'/leads/{tel}?msg=nao+recebe+mais+({motivo})', status_code=303)


@app.post('/leads/{tel}/supressao/{sid}/revogar')
def revoga_sup(tel: str, sid: int):
    with db.conectar() as cx:
        s = cx.execute("UPDATE supressao SET ate=now() WHERE id=%s AND tel=%s AND ate IS NULL RETURNING motivo", (sid, tel)).fetchone()
        if s:
            cx.execute("DELETE FROM etiquetas WHERE tel=%s AND tag=%s", (tel, s['motivo'].replace('_', '-')))
            cx.execute("INSERT INTO ajustes (tel, acao, detalhe) VALUES (%s,'supressao-',%s)", (tel, s['motivo']))
        cx.commit()
    invalida_cache()
    return RedirectResponse(f'/leads/{tel}?msg=supressao+revogada', status_code=303)


@app.post('/leads/{tel}/nota')
def add_nota(tel: str, texto: str = Form(...)):
    texto = texto.strip()[:2000]
    if texto:
        with db.conectar() as cx:
            cx.execute("INSERT INTO eventos (tel, tipo, quando, texto, fonte) VALUES (%s,'nota',now(),%s,'manual')", (tel, texto))
            cx.commit()
    return RedirectResponse(f'/leads/{tel}?msg=nota+gravada', status_code=303)


@app.post('/leads/{tel}/nome_msg')
def set_nome_msg(tel: str, nome_msg: str = Form('')):
    n = nome_msg.strip()[:40] or None
    with db.conectar() as cx:
        cx.execute("UPDATE leads SET nome_msg=%s, atualizado_em=now() WHERE tel=%s", (n, tel))
        if n:
            cx.execute("DELETE FROM etiquetas WHERE tel=%s AND tag='nome-generico'", (tel,))
        else:
            cx.execute("INSERT INTO etiquetas (tel, tag, origem) VALUES (%s,'nome-generico','manual') ON CONFLICT DO NOTHING", (tel,))
        cx.execute("INSERT INTO ajustes (tel, acao, detalhe) VALUES (%s,'nome_msg',%s)", (tel, n or '(generico)'))
        cx.commit()
    invalida_cache()
    return RedirectResponse(f'/leads/{tel}?msg=nome+da+mensagem+atualizado', status_code=303)


@app.get('/campanhas', response_class=HTMLResponse)
def campanhas(request: Request):
    return tpl.TemplateResponse(request, 'campanhas.html', dict(r=resumo()))


def _porta_ocupada(port, espera=1.5):
    import socket
    with socket.socket() as s:
        s.settimeout(espera)
        return s.connect_ex(('127.0.0.1', port)) == 0


def _confere_banco():
    """(nome do banco, nº de leads). Uma ida ao banco."""
    with db.conectar() as cx:
        g = cx.execute('SELECT current_database() banco, (SELECT count(*) FROM leads) n').fetchone()
    return g['banco'], g['n']


def _config():
    """Porta e navegador pelo ambiente. Sem variáveis: 8765 com navegador (uso normal).

    CRM_PORT: 1..65535 (vazia = 8765). CRM_NO_BROWSER: vazia ou '0' = abre o navegador; outro valor = não abre.
    """
    bruto = os.environ.get('CRM_PORT', '').strip()
    port = 8765
    if bruto:
        if not bruto.isascii() or not bruto.isdigit() or not 1 <= int(bruto) <= 65535:
            raise SystemExit(f'CRM_PORT inválida: {bruto}')
        port = int(bruto)
    navegador = os.environ.get('CRM_NO_BROWSER', '').strip() in ('', '0')
    return port, navegador


def main():
    import uvicorn
    port, navegador = _config()
    alvo = f'http://127.0.0.1:{port}/leads'
    # porta ocupada = provavelmente o CRM ja esta aberto: so abre o navegador
    if _porta_ocupada(port):
        print(f'CRM ja esta rodando. Abrindo {alvo}' if navegador else f'CRM ja esta rodando em {alvo}')
        if navegador:
            webbrowser.open(alvo)
        return
    try:
        banco, n = _confere_banco()
    except Exception as e:
        print()
        print('NAO consegui falar com o banco.')
        print('Motivo:', type(e).__name__, (str(e).strip().splitlines() or [''])[0])
        print('Confira se o Postgres esta rodando e o DATABASE_URL do arquivo .env.')
        print()
        raise SystemExit(1)
    exige = os.environ.get('CRM_EXIGE_BANCO', '').strip()
    if exige and banco != exige:
        print(f'Banco errado: {banco} (esperado {exige}). Nao subi a tela.')
        raise SystemExit(1)
    print(f'Banco ok: {banco}, {n} leads.')

    def abrir_quando_subir():
        """Só abre o navegador depois que a porta aceita conexão — evita 'nao foi possivel acessar'."""
        import time
        for _ in range(120):
            if _porta_ocupada(port, espera=1):
                webbrowser.open(alvo)
                return
            time.sleep(0.5)
        print('O servidor demorou pra subir. Abra manualmente:', alvo)

    if navegador:
        threading.Thread(target=abrir_quando_subir, daemon=True).start()
    print(f'Servindo em http://127.0.0.1:{port}  (Ctrl+C para encerrar)', flush=True)
    uvicorn.run(app, host='127.0.0.1', port=port, log_level='warning')


if __name__ == '__main__':
    main()
