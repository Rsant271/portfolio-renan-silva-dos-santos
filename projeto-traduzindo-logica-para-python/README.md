# 🐍 Traduzindo Lógica para Python

## 📝 Descrição do Projeto
Este projeto pega quatro pseudocódigos escritos em sala de aula (em português estruturado) e traduz cada um para Python funcional. A ideia foi sair da lógica desenhada no papel e transformar em código que roda de verdade no notebook, exercitando entrada de dados, decisões em cascata, repetição com `for`, acumuladores e cálculo de juros compostos.

Desenvolvido como parte da disciplina de **Programação de Computadores (2026.1)** — atividade **EX4 — Traduzindo Lógica para Python**, o trabalho reúne quatro funções independentes (`processar_vendas`, `analisar_clima`, `sistema_notas_turma` e `simulador_poupanca`) e duas perguntas de reflexão sobre tipagem dinâmica e o comportamento do `range()`.

## 🚀 Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Bibliotecas:** funções nativas do Python (sem dependências externas)
* **Ferramentas:** Google Colab, Jupyter Notebook

## 📊 Resultados e Aprendizados
As quatro funções rodaram conforme o esperado e cada cenário de teste retornou a saída prevista no pseudocódigo. As reflexões finais ajudaram a consolidar dois pontos que costumam derrubar quem está começando.
* **Tipagem dinâmica e conversão de tipos:** entendi na prática por que `input()` sempre devolve texto e que sem `float()` ou `int()` o Python não consegue fazer cálculo, dando `TypeError`.
* **`range()` é exclusivo no limite superior:** descobri que `range(1, 5)` para no 4 e por isso o padrão correto pra repetir N vezes é `range(1, quantidade + 1)`.
* **Decisão em cascata com `if/elif/else`:** apliquei faixas de valor (clima, notas, vendas) usando `elif` em vez de vários `if` soltos, deixando o fluxo mais limpo e mais rápido.

## 🔧 Como Executar
1. Abra o arquivo `projeto-traduzindo-logica-para-python.ipynb` no Google Colab ou Jupyter Notebook.
2. Execute as células em ordem e digite os valores pedidos (quantidade de vendas, temperatura, notas dos alunos, valor inicial da poupança).
3. Confira a saída de cada função e compare com o pseudocódigo original entregue em sala.

---
[Voltar ao início](https://github.com/Rsant271/portfolio-renan-silva-dos-santos)
