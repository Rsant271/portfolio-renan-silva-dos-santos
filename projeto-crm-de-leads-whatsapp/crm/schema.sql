-- CRM de disparos: schema do banco. Idempotente (pode rodar mais de uma vez sem quebrar nada).

CREATE TABLE IF NOT EXISTS leads (
  tel            TEXT PRIMARY KEY,
  nome           TEXT,
  nome_msg       TEXT,
  origem         TEXT,
  tipo           TEXT,
  primeira_data  DATE,
  fontes         TEXT[] NOT NULL DEFAULT '{}',
  aba_planilha   TEXT,
  linha_planilha INTEGER,
  cor_planilha   TEXT,
  etapa_crm      TEXT,
  id_crm         TEXT,
  segmento       TEXT,
  status_sistema TEXT,
  wa_existe      BOOLEAN,
  wa_checado_em  TIMESTAMPTZ,
  wa_jid         TEXT,
  wa_lid         TEXT,
  ultima_msg_em  TIMESTAMPTZ,
  ultima_msg_de  TEXT,
  bairro         TEXT,
  criado_em      TIMESTAMPTZ NOT NULL DEFAULT now(),
  atualizado_em  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS supressao (
  id         BIGSERIAL PRIMARY KEY,
  tel        TEXT NOT NULL REFERENCES leads(tel),
  motivo     TEXT NOT NULL,
  fonte      TEXT NOT NULL,
  evidencia  TEXT,
  desde      TIMESTAMPTZ NOT NULL DEFAULT now(),
  ate        TIMESTAMPTZ,
  UNIQUE (tel, motivo, desde)
);
CREATE INDEX IF NOT EXISTS supressao_ativa ON supressao (tel) WHERE ate IS NULL;

CREATE TABLE IF NOT EXISTS eventos (
  id           BIGSERIAL PRIMARY KEY,
  tel          TEXT NOT NULL REFERENCES leads(tel),
  tipo         TEXT NOT NULL,
  campanha     TEXT,
  toque        SMALLINT,
  variante     TEXT,
  quando       TIMESTAMPTZ NOT NULL,
  canal        TEXT NOT NULL DEFAULT 'whatsapp',
  instancia    TEXT,
  msg_id       TEXT,
  entrega      TEXT,
  midia        BOOLEAN,
  texto        TEXT,
  fonte        TEXT NOT NULL,
  fonte_ref    TEXT,
  UNIQUE NULLS NOT DISTINCT (tel, tipo, campanha, toque, quando)
);
CREATE INDEX IF NOT EXISTS eventos_tel ON eventos (tel, quando DESC);
CREATE INDEX IF NOT EXISTS eventos_campanha ON eventos (campanha, toque);

CREATE TABLE IF NOT EXISTS etiquetas (
  tel     TEXT NOT NULL REFERENCES leads(tel),
  tag     TEXT NOT NULL,
  origem  TEXT NOT NULL,
  desde   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (tel, tag)
);
CREATE INDEX IF NOT EXISTS etiquetas_tag ON etiquetas (tag);

CREATE TABLE IF NOT EXISTS campanhas (
  nome        TEXT PRIMARY KEY,
  descricao   TEXT,
  inicio      DATE,
  fim         DATE,
  fonte_hist  TEXT
);

-- Linhas da planilha de leads como vieram (auditoria + história entre abas). 1 linha por (aba, linha).
CREATE TABLE IF NOT EXISTS planilha_linhas (
  aba            TEXT NOT NULL,
  linha          INTEGER NOT NULL,
  tel            TEXT REFERENCES leads(tel),
  tel_original   TEXT,
  data           DATE,
  origem         TEXT,
  nome           TEXT,
  tipo           TEXT,
  data_contato   TEXT,
  agendado_por   TEXT,
  status         TEXT,
  data_agenda    TEXT,
  hora_agenda    TEXT,
  contato        TEXT,
  bairro         TEXT,
  compareceu     TEXT,
  proximo_contato TEXT,
  fechou         TEXT,
  cor            TEXT,
  cor_hex        TEXT,
  lida_em        TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (aba, linha)
);
CREATE INDEX IF NOT EXISTS planilha_linhas_tel ON planilha_linhas (tel);

-- Telefones que não viraram lead (inválidos), pra conferência.
CREATE TABLE IF NOT EXISTS rejeitados (
  id        BIGSERIAL PRIMARY KEY,
  fonte     TEXT NOT NULL,
  fonte_ref TEXT,
  valor     TEXT,
  motivo    TEXT,
  nome      TEXT,
  quando    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Ajustes manuais feitos pela tela (auditoria).
CREATE TABLE IF NOT EXISTS ajustes (
  id      BIGSERIAL PRIMARY KEY,
  tel     TEXT REFERENCES leads(tel),
  acao    TEXT NOT NULL,
  detalhe TEXT,
  quando  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Nível de consciência (escala de Schwartz, 1 a 5)
-- Calculado por evidência observável: o que a pessoa digitou na conversa (peso 3),
-- o botão do anúncio que ela clicou (peso 1) e sinais do CRM comercial.
-- Para quem nunca digitou nada, `nivel_confianca` fica 'baixa'.
ALTER TABLE leads ADD COLUMN IF NOT EXISTS nivel_consciencia SMALLINT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS nivel_confianca   TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS nivel_motivo      TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS objecao_dominante TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS msgs_digitadas    SMALLINT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS nivel_calculado_em TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS leads_nivel ON leads (nivel_consciencia, nivel_confianca);
CREATE INDEX IF NOT EXISTS leads_objecao ON leads (objecao_dominante);
