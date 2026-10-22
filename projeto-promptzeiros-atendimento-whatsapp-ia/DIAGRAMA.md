# Diagrama do Ecossistema Promptzeiros

> Renderiza no GitHub, GitLab, VSCode, Notion ou qualquer viewer com suporte a Mermaid

---

## Visão geral — 4 Camadas do Agente (Murta 2023)

```mermaid
flowchart LR
    subgraph PERCEPTIVA["Camada Perceptiva"]
        WA[Cliente no WhatsApp]
        EVO_IN[Evolution API<br/>Webhook]
    end

    subgraph COGNITIVA["Camada Cognitiva"]
        AI[GPT-4o-mini<br/>+ Memory<br/>+ System Prompt v5]
        SP[(System Prompt<br/>BANT triagem)]
    end

    subgraph DECISORIA["Camada Decisória"]
        FILTER[Filtrar Mensagem<br/>Pessoal IF]
        OPTOUT[Detectar Opt-Out<br/>IF SAIR/PARAR/CANCELAR]
        SANIT[Sanitize Output<br/>Code]
        VALID[Validações + Templates<br/>+ Anti-ban Code]
        TEM_WA{Tem WhatsApp?}
    end

    subgraph EXECUTIVA["Camada Executiva"]
        SEND[Send via Evolution API]
        SHEETS[(Google Sheets<br/>Leads & Triagens)]
        OPTOUT_RESP[Resposta Opt-Out<br/>Determinística]
    end

    WA --> EVO_IN
    EVO_IN --> FILTER
    FILTER -- mensagem pessoal --> OPTOUT
    OPTOUT -- normal --> AI
    AI -.- SP
    AI --> SANIT
    SANIT --> SEND
    OPTOUT -- SAIR --> OPTOUT_RESP --> SEND
    SEND --> WA

    SHEETS -.lê leads pending.-> VALID
    VALID --> TEM_WA
    TEM_WA -- sim --> SEND
    SEND -.atualiza status.-> SHEETS

    style PERCEPTIVA fill:#e1f5ff,stroke:#0288d1
    style COGNITIVA fill:#f3e5f5,stroke:#7b1fa2
    style DECISORIA fill:#fff9c4,stroke:#f9a825
    style EXECUTIVA fill:#c8e6c9,stroke:#388e3c
```

---

## Workflow 1 — Inbound (Promptzeiros AI Agent)

```mermaid
flowchart TB
    A[Webhook<br/>POST /webhook/promptzeiros-inbound] --> B{Filtrar Mensagem<br/>Pessoal}
    B -- false: bot/grupo/broadcast --> C[Skip Bot Echo]
    B -- true: mensagem real --> D[Extract Message Data<br/>user_message, session_id,<br/>system_prompt]
    D --> E{Detectar Opt-Out<br/>SAIR/PARAR/CANCELAR}
    E -- sim --> F[Resposta Opt-Out<br/>'Ok, removemos seu numero...']
    E -- não --> G[AI Agent<br/>GPT-4o-mini + Memoria]
    G --> H[Sanitize Output<br/>limpa formato da resposta]
    F --> I[Send via Evolution API<br/>POST /message/sendText]
    H --> I

    style A fill:#e3f2fd
    style B fill:#fff3e0
    style E fill:#fff3e0
    style F fill:#fce4ec
    style G fill:#f3e5f5
    style H fill:#fce4ec
    style I fill:#c8e6c9
```

**11 nós** · webhook path: `/webhook/promptzeiros-inbound`

---

## Workflow 2 — Outbound (Promptzeiros Outbound Disparo)

```mermaid
flowchart TB
    T[Manual Trigger] --> R[Read Leads from Sheets<br/>filters: status=pending<br/>consentimento=TRUE<br/>opt_out=FALSE]
    R --> L[Loop por Lead<br/>splitInBatches batchSize=1]
    L --> V[Validações + Template + Delay<br/>Code: 14 vetores anti-ban]
    V --> VAL{Válido?}
    VAL -- não --> SK[Marcar Skipped<br/>+ erro na planilha]
    VAL -- sim --> CW[Checar WhatsApp<br/>Evolution /chat/whatsappNumbers]
    CW --> TWA{Tem WhatsApp?}
    TWA -- não --> FAIL[Marcar Falhou]
    TWA -- sim --> W1[Wait delay aleatório<br/>15-90s não-redondo]
    W1 --> P[Mostrar Digitando<br/>Evolution presence composing]
    P --> W2[Wait typing 3-7s]
    W2 --> S[Enviar Mensagem<br/>Evolution /message/sendText]
    S --> EN{Enviado?}
    EN -- sim --> ME[Marcar Enviado<br/>status=sent + msg_id]
    EN -- não --> FAIL
    ME --> L
    FAIL --> L
    SK --> L

    style T fill:#e1bee7
    style R fill:#bbdefb
    style L fill:#fff9c4
    style V fill:#ffe0b2
    style VAL fill:#ffe0b2
    style CW fill:#bbdefb
    style TWA fill:#ffe0b2
    style W1 fill:#f8bbd0
    style W2 fill:#f8bbd0
    style P fill:#d1c4e9
    style S fill:#c8e6c9
    style EN fill:#ffe0b2
    style ME fill:#a5d6a7
    style FAIL fill:#ef9a9a
    style SK fill:#ffcc80
```

**15 nós** · dispara manualmente pelo botão "Execute Workflow" do n8n

---

## Diagrama de dados (LGPD)

```mermaid
flowchart LR
    subgraph CONSENT["Consentimento"]
        FORM[Form/LP/SDR]
        CONS[consentimento=TRUE]
    end

    subgraph DISP["Disparo Outbound"]
        OUT[Workflow Outbound]
    end

    subgraph Client["Cliente"]
        WA[WhatsApp]
    end

    subgraph LIM["Limpeza LGPD"]
        OPTOUT[opt_out=TRUE<br/>Branch determinístico inbound]
    end

    FORM --> CONS
    CONS --> OUT
    OUT --> WA
    WA -- responde SAIR --> OPTOUT
    OPTOUT --> OUT

    style CONS fill:#c8e6c9
    style OPTOUT fill:#ffcdd2
```

---

## Stack técnica

```mermaid
flowchart LR
    subgraph Cliente["Cliente"]
        APP[WhatsApp App<br/>iOS/Android]
    end

    subgraph Mensageria["Mensageria"]
        EVO[Evolution API<br/>hospedada em Railway]
    end

    subgraph Orq["Orquestração"]
        N8N[n8n Cloud<br/>workflows visuais]
    end

    subgraph IA["Inteligência"]
        GPT[OpenAI GPT-4o-mini<br/>via API]
        MEM[Simple Memory<br/>histórico da sessão]
    end

    subgraph Persist["Persistência"]
        GS[Google Sheets<br/>Leads + Triagens]
    end

    APP <--> EVO
    EVO <--> N8N
    N8N <--> GPT
    N8N <--> MEM
    N8N <--> GS

    style APP fill:#dcf8c6
    style EVO fill:#bbdefb
    style N8N fill:#ffe082
    style GPT fill:#e1bee7
    style MEM fill:#ffccbc
    style GS fill:#c5e1a5
```

