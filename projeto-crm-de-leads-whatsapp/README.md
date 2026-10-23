# 📇 CRM de Leads para Disparos no WhatsApp

## 📝 Descrição do Projeto
Este é um projeto pessoal, fora das disciplinas, feito para a equipe comercial de uma clínica odontológica em São Paulo onde eu trabalho com marketing. Os contatos que chegam pelos anúncios ficam numa planilha com uma aba por mês. Com o tempo apareceram três problemas: o mesmo lead aparecia em várias abas, o telefone era escrito de jeitos diferentes e não havia um lugar que mostrasse quem já recebeu cada campanha e quem pediu para não receber mais mensagens.

O CRM resolve isso em três partes:
* **Banco de dados:** PostgreSQL com 8 tabelas (leads, eventos, etiquetas, supressão, campanhas, linhas da planilha, rejeitados e ajustes). A chave de cada lead é o telefone já normalizado.
* **Carga da planilha:** lê as abas mensais, junta o mesmo lead de abas diferentes, guarda cada linha original para conferência e separa os telefones inválidos numa tabela de rejeitados. Pode rodar de novo sem duplicar nada.
* **Tela local:** lista com filtros, ficha do lead com linha do tempo, etiquetas, notas e o bloqueio "não receber mais". A tela não envia mensagem, ela só consulta e organiza.

Esta versão do portfólio roda com **dados fictícios**: nomes sorteados, telefones em sequência (11 90000-0001, 11 90000-0002...) e campanhas inventadas. Nenhum dado de paciente ou de lead real está neste repositório.

![Lista de leads](img/lista-de-leads.png)

![Ficha do lead](img/ficha-do-lead.png)

![Campanhas](img/campanhas.png)

## 🚀 Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Banco de dados:** PostgreSQL 17, com psycopg 3 e pool de conexões
* **Tela:** FastAPI, Jinja2 e Tailwind CSS
* **Testes:** pytest, com 133 testes
* **Apoio de IA:** o código foi escrito com o Claude Code, assistente de programação da Anthropic. Eu levantei as regras de negócio com a equipe, tomei as decisões do projeto (banco na nuvem ligado 24 horas, eventos que só acumulam, tela que não envia mensagem), conferi os resultados e uso o sistema no dia a dia.

```mermaid
flowchart LR
    PL[Planilha de leads<br/>uma aba por mês] --> CG[Carga<br/>carga_planilha.py]
    CG --> DB[(PostgreSQL)]
    EV[Envios, respostas<br/>e pedidos de saída] --> DB
    DB <--> TL[Tela local<br/>FastAPI]
```

## 📊 Resultados e Aprendizados
* **Uma regra só para telefone:** a mesma função é usada na carga, na busca da tela e nos testes. Os testes cobrem 44 formatos: com máscara, com +55, com 0 de tronco, celular antigo sem o 9, fixo, números estrangeiros e até dígitos de outro alfabeto, que parecem números mas não são.
* **Eventos só acumulam:** envio, resposta e pedido de saída entram como linhas novas e não são apagados. Assim dá para montar a linha do tempo de cada lead e calcular a taxa de resposta de cada campanha direto do banco.
* **"Não receber mais" tem tabela própria:** cada bloqueio guarda motivo, data e o que a pessoa disse. Revogar não apaga o registro, só fecha a data final.
* **Desempenho:** no uso real o banco fica num servidor fora do Brasil. Cada ida e volta custa cerca de 180 ms e abrir uma conexão nova custa cerca de 1,5 s. Com pool de conexões, uma consulta por página e cache de 90 segundos nos números do topo, a primeira página abre em cerca de 3 s e as seguintes em cerca de 0,6 s.
* **Testes que nasceram de erro:** a página `?page=0` dava erro 500 (o OFFSET ficava negativo) e a busca só achava o telefone digitado exatamente igual. Hoje os dois casos têm teste, e a busca usa os 8 últimos dígitos.
* **Limitações:** a tela foi feita para rodar só no computador de quem usa (127.0.0.1). Ela não tem login nem proteção contra CSRF nos formulários, então não pode ir para a internet do jeito que está. A parte de montar a lista de disparo ainda não foi feita.

## 🔧 Como Executar
1. Suba um PostgreSQL 15 ou mais novo. Com Docker: `docker compose up -d` (usa o `docker-compose.yml` desta pasta).
2. Crie o ambiente e instale as dependências:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Aponte o endereço do banco:
   ```bash
   export DATABASE_URL=postgresql://crm:crm@127.0.0.1:5432/crm_demo
   ```
4. Monte a demonstração (cria as tabelas, gera as planilhas fictícias em CSV, faz a carga e cria as campanhas):
   ```bash
   python demo/gera_dados_ficticios.py
   ```
5. Rode os testes com `pytest` e abra a tela com `python -m crm.app` (endereço http://127.0.0.1:8765).

---
[Voltar ao início](https://github.com/Rsant271/portfolio-renan-silva-dos-santos)
