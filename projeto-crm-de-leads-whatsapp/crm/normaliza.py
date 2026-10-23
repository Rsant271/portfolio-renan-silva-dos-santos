"""Normalização de telefone e nome: a MESMA regra em todo lugar (carga, tela e testes)."""
import re
import unicodedata

_CMD = re.compile(r'(ignore|envie|send|http|www\.|@|\.com)', re.I)
_NAO_DIGITO = re.compile(r'[^0-9]')                # só dígito ASCII: o \D do Python aceita '１' e '١'

# Os 67 DDDs da Anatel.
DDDS = frozenset(
    list(range(11, 20)) + [21, 22, 24, 27, 28] + list(range(31, 36)) + [37, 38] + list(range(41, 50))
    + [51, 53, 54, 55] + list(range(61, 70)) + [71, 73, 74, 75, 77, 79] + list(range(81, 90)) + list(range(91, 100)))


def canonico(s):
    """Telefone canônico BR: 10 (fixo) ou 11 dígitos (celular com 9), sem 55. None = inválido.

    '+' antes do primeiro dígito = código de país: só vale '+55'. Tira o 0 de tronco ('011 9...').
    O DDD tem que existir; celular (11 dígitos) começa com 9 depois do DDD; fixo (10) com 2 a 5.
    """
    txt = str(s or '')
    if any(c.isdigit() and c not in '0123456789' for c in txt):
        return None                              # dígito de outro alfabeto: não adivinha
    d = _NAO_DIGITO.sub('', txt)
    if not d:
        return None
    antes = txt[:txt.index(d[0])]
    if '+' in antes or '＋' in antes:             # E.164: '+<país>...'
        if not d.startswith('55'):
            return None
        d = d[2:]
    else:
        if d.startswith('55') and len(d) in (12, 13):
            d = d[2:]
        if d.startswith('0') and len(d) in (11, 12):
            d = d[1:]
    if len(d) not in (10, 11) or int(d[:2]) not in DDDS:
        return None
    if len(d) == 10 and d[2] in '6789':          # celular antigo sem o 9
        d = d[:2] + '9' + d[2:]
    if len(d) == 11:
        return d if d[2] == '9' else None
    return d if d[2] in '2345' else None


def internacional(s):
    """Dígitos completos se parecer número fora do Brasil (não começa com 55, 11–15 dígitos)."""
    d = _NAO_DIGITO.sub('', str(s or ''))
    if d.startswith('55') or d.startswith('0'):
        return None
    return d if 11 <= len(d) <= 15 and canonico(d) is None else None


def telefones(celula):
    """Uma célula pode ter 2 telefones ('11 9... / 11 9...'). Devolve lista de canônicos válidos, sem repetição."""
    partes = re.split(r'[/;,]|\s{2,}|\be\b|\bou\b', str(celula or ''))
    vistos, out = set(), []
    for p in partes:
        c = canonico(p)
        if c and c not in vistos:
            vistos.add(c); out.append(c)
    if not out:                                   # tenta a célula inteira (ex.: '11 99999-9999')
        c = canonico(celula)
        if c:
            out.append(c)
    return out


def para_evolution(tel):
    return '55' + tel


_ACENTOS = {'jose': 'José', 'tercio': 'Tércio', 'antonio': 'Antônio', 'joao': 'João', 'ines': 'Inês',
            'fabio': 'Fábio', 'cesar': 'César', 'andrea': 'Andréa', 'debora': 'Débora', 'monica': 'Mônica',
            'veronica': 'Verônica', 'lucia': 'Lúcia', 'julia': 'Júlia', 'tania': 'Tânia', 'sonia': 'Sônia',
            'angela': 'Ângela', 'helio': 'Hélio', 'flavio': 'Flávio', 'mario': 'Mário', 'sergio': 'Sérgio',
            'claudia': 'Cláudia', 'patricia': 'Patrícia', 'marcio': 'Márcio', 'otavio': 'Otávio'}


def _sem_acento(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def nome_limpo(s):
    s = re.sub(r'\s+', ' ', str(s or '')).strip()
    return s


def nome_msg(nome):
    """Primeiro nome pra {nome} na mensagem. None = a mensagem usa o texto genérico, sem nome."""
    n = nome_limpo(nome)
    if not n or _CMD.search(n):
        return None
    primeiro = n.split(' ')[0].strip('.,;:-')
    if len(primeiro) <= 2 or not primeiro.isalpha():
        return None
    if primeiro.isupper() and len(primeiro) <= 4:      # siglas
        return None
    low = _sem_acento(primeiro).lower()
    if low in ('sr', 'sra', 'dr', 'dra', 'dona', 'seu', 'deus', 'cliente', 'lead', 'teste', 'whatsapp'):
        return None
    if low in _ACENTOS:
        return _ACENTOS[low]
    return primeiro[0].upper() + primeiro[1:].lower() if primeiro.islower() or primeiro.isupper() else primeiro


COR = {'#A9D08E': 'verde', '#E06666': 'vermelho', '#FFD966': 'amarelo', '#FFE599': 'amarelo', '#FF6D01': 'laranja',
       '#FFFFFF': 'branco', None: 'branco'}


def cor_nome(hexa):
    """Hex '#RRGGBB' → verde|vermelho|amarelo|laranja|branco|outro."""
    if not hexa:
        return 'branco'
    h = hexa.upper()
    if h in COR:
        return COR[h]
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    if r > 235 and g > 235 and b > 235:
        return 'branco'
    if g > r and g > b:
        return 'verde'
    if r > 200 and g < 130 and b < 130:
        return 'vermelho'
    if r > 200 and 80 < g < 140 and b < 60:
        return 'laranja'
    if r > 200 and g > 180 and b < 140:
        return 'amarelo'
    return 'outro'


def origem_norm(s):
    o = _sem_acento(nome_limpo(s)).lower()
    if not o:
        return None
    if 'google' in o:
        return 'Google'
    if 'meta' in o or 'face' in o or 'insta' in o or 'whats' in o:
        return 'Meta'
    if 'indic' in o:
        return 'Indicacao'
    if 'intern' in o or 'organ' in o:
        return 'Interno'
    return nome_limpo(s)
