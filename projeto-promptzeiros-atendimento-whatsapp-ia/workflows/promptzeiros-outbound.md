# Workflow Outbound — disparo

Workflow do n8n que faz disparo controlado de mensagens a partir de uma planilha.

**Arquivo:** [`promptzeiros-outbound.json`](promptzeiros-outbound.json) (importar no n8n)

**Trigger:** manual (clique em "Execute workflow" no editor — não tem webhook).

---

## O que ele faz

1. Lê os leads da planilha do Google Sheets (filtros: `status=pending`, `consentimento=TRUE`, `opt_out=FALSE`).
2. Processa um lead por vez (loop com `batchSize=1`).
3. Valida horário comercial, escolhe um dos 3 templates, preenche `{{nome}}` e checa palavras proibidas.
4. Confirma se o número tem WhatsApp ativo (Evolution API).
5. Espera um tempo aleatório (15–90 s).
6. Mostra "digitando..." no WhatsApp do destinatário (parecer humano).
7. Envia a mensagem.
8. Atualiza o status do lead na planilha (`sent`, `failed` ou `skipped`).

15 nós no total.

---

## Fluxo

```
Manual Trigger
  └── Read Leads from Sheets
        └── Loop por Lead [1 por vez]
              └── Validações + Template + Delay
                    ├── (inválido) → Marcar Skipped
                    └── (válido)   → Checar WhatsApp
                                       ├── (sem WA) → Marcar Falhou
                                       └── (com WA) → Wait (delay aleatório)
                                                       └── Mostrar Digitando
                                                             └── Wait (typing 3-7s)
                                                                   └── Enviar Mensagem
                                                                         ├── (ok)  → Marcar Enviado
                                                                         └── (erro) → Marcar Falhou
```

---

## Schema da planilha

| Coluna | Descrição |
|---|---|
| `id` | identificador único do lead |
| `nome` | usado em `{{nome}}` do template |
| `telefone` | telefone com DDI e DDD (ex: `5511XXXXXXXXX`) |
| `consentimento` | `TRUE` / `FALSE` — LGPD: lead consentiu o contato? |
| `opt_out` | `TRUE` / `FALSE` — lead pediu para sair? |
| `status` | `pending`, `sent`, `failed`, `skipped` |
| `template_alvo` | `A`, `B`, `C` ou vazio (sorteia) |
| `tentativas` | quantas vezes tentamos disparar |
| `erro` | última mensagem de erro |

---

## 3 templates (rotação anti-bloqueio)

O nó `Validações + Template + Delay` sorteia entre A, B e C — variar a redação reduz o risco do WhatsApp detectar repetição.

### Template A — formal (220 chars)
```
Oi {{nome}}, aqui é o Marcos da SP Imoveis. Vi que voce demonstrou interesse em imoveis na zona norte. Posso te ajudar com avaliacao gratuita ou busca direcionada. Qual seu objetivo agora?

Pra parar de receber, responda SAIR.
```

### Template B — médio (320 chars)
```
{{nome}}, tudo bem? Aqui é a SP Imoveis. A gente trabalha na zona norte de SP ha 6 anos com compra, venda e locacao. Avaliacao de imovel é por nossa conta. Se tiver pensando em vender ou comprar nos proximos meses, me conta sua situacao que te ajudo a entender as opcoes.

Nao quer mais? Manda SAIR.
```

### Template C — conversacional (240 chars)
```
Olá {{nome}}! A gente da SP Imoveis ta fazendo uma rodada de avaliacoes gratuitas de imoveis na zona norte essa semana. Se voce tiver interesse (comprar, vender ou alugar), me responde aqui que te explico em 1 minuto. Tudo bem?

SAIR pra cancelar.
```

---

## O que precisa configurar ao importar

| Credencial / config | Onde |
|---|---|
| Google Sheets OAuth2 | nós `Read Leads from Sheets`, `Marcar Enviado`, `Marcar Falhou`, `Marcar Skipped` |
| ID da planilha | mesmos nós |
| Evolution API key | nós HTTP que fazem POST para a Evolution |
| URL da sua instância Evolution | mesmos nós |
