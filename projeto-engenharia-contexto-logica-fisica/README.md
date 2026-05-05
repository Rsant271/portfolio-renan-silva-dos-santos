# 🌆 Engenharia de Contexto e Lógica Física

## 📝 Descrição do Projeto
Este projeto reúne dois algoritmos em Python que partem de coleta manual de dados no mundo real e traduzem essa observação em estruturas lógicas executáveis. A primeira parte processa dados de microclima (temperatura, umidade e IQA) coletados em três pontos do trajeto Pq. Novo Mundo → Sé → Tatuapé (UNICID) em dois horários do dia, classifica a qualidade do ar pelas faixas oficiais da CETESB / CONAMA 491/2018 e calcula uma "Nota de Conforto Urbano" com fórmula própria. A segunda parte é um simulador de evacuação de emergência que mapeia o trajeto real entre o quarto e o portão da minha casa, com obstáculos como porta trancada e chave a ser coletada.

Desenvolvido como parte da disciplina de **Programação de Computadores (2026.1)** — atividade **EX5 — Engenharia de Contexto e Lógica Física**, o trabalho aplica Listas de Listas, `for` aninhado, `match-case`, `while`, `if` aninhado, inventário do agente e fórmulas com operadores lógicos (`and`, `>=`).

## 🚀 Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Bibliotecas:** funções nativas do Python (sem dependências externas)
* **Ferramentas:** Google Colab, Jupyter Notebook
* **Fontes de dados externas:** CETESB QUALAR (IQA), CGE-SP / Climatempo (temperatura e umidade)

## 📊 Resultados e Aprendizados
Os dois programas rodaram conforme o esperado: a análise de microclima imprimiu o relatório dos seis registros (3 locais × 2 horários) com a classificação correta da qualidade do ar e a Nota de Conforto Urbano de cada ponto, e o simulador de evacuação encontrou a saída em todos os cenários testados, retrocedendo corretamente quando o agente chegava à porta trancada sem a chave no inventário.
* **Lista de listas + `for` aninhado:** aprendi a percorrer uma matriz onde o laço externo passa pelos locais e o interno percorre as métricas numéricas, mantendo o índice alinhado com os rótulos.
* **`match-case` em vez de `if/elif` longo:** apliquei o `match-case` (Python 3.10+) com o operador `|` (ou) e o caso `_` (default) para classificar as faixas de IQA de forma mais limpa que uma cadeia de `if/elif`.
* **`while` + inventário do agente:** programei um agente "cego" que decide avançar ou retroceder na lista com base em `if` aninhado que checa o inventário, simulando uma navegação real com gasto de energia a cada movimento.

## 🔧 Como Executar
1. Abra o arquivo `projeto-engenharia-de-contexto-e-logica-fisica.ipynb` no Google Colab ou Jupyter Notebook (ou acesse direto pelo [link do Colab](https://colab.research.google.com/drive/1rRJU_vJbD0hJuaxN1UwEwzB6PWYNnddQ?usp=sharing)).
2. Execute as células em ordem — a Parte 1 imprime o relatório de microclima dos seis registros e a Parte 2 simula a evacuação do quarto até o portão.
3. Compare a saída do simulador com o mapa físico real e confira se a classificação de IQA bate com as faixas oficiais da CETESB.

---
[Voltar ao início](https://github.com/Rsant271/portfolio-renan-silva-dos-santos)
