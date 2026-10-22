# Workflow Inbound — atendimento

Workflow do n8n que recebe mensagens do WhatsApp e responde com um agente de IA.

**Arquivo:** [`promptzeiros-inbound.json`](promptzeiros-inbound.json) (importar no n8n)

---

## O que ele faz

Quando alguém manda mensagem para o WhatsApp pareado com a Evolution API, o workflow:

1. Recebe o evento via Webhook.
2. Filtra para ignorar mensagens que não interessam (grupos, listas de transmissão, eco do próprio bot).
3. Verifica se a mensagem é um **opt-out** (palavras `SAIR`, `PARAR`, `CANCELAR`).
4. Se for opt-out, responde com mensagem padrão e sai.
5. Se não for, envia a mensagem para o **AI Agent** (GPT-4o-mini com o system prompt + memória da sessão).
6. Devolve a resposta da IA pelo WhatsApp.

11 nós no total.

---

## Fluxo

```
Webhook Evolution
   └── Filtra mensagem pessoal
          ├── (descarta) → Skip Bot Echo
          └── (válida)   → Extract Message Data
                             └── Detecta opt-out
                                    ├── (sim) → Resposta opt-out → Send Evolution
                                    └── (não) → AI Agent → Sanitize Output → Send Evolution
```

---

## O que precisa configurar ao importar

| Credencial / config | Onde |
|---|---|
| OpenAI API key | nó `Promptzeiros AI Agent` |
| Evolution API key | nós `Send via Evolution API` (HTTP Header Auth) |
| URL da sua instância Evolution | nós que fazem POST `/message/sendText/...` |
| Webhook da Evolution | apontar para a URL pública do n8n no caminho `/webhook/promptzeiros-inbound` |

---

## Memória

O nó `Simple Memory` guarda as últimas 20 mensagens da sessão (chave por número de telefone). Permite que o agente lembre das respostas anteriores dentro da mesma triagem.
