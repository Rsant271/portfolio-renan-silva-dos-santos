# 💰 Sistema de Caixa e Troco

## 📝 Descrição do Projeto
Este projeto resolve o desafio "Dividir para Conquistar — A Arte da Modularização": escrever um algoritmo que lê um valor de compra e o valor pago pelo cliente, calcula o troco total e determina o **menor número possível de notas** (R$ 100, R$ 50, R$ 10, R$ 5 e R$ 1) para devolver. Em vez de escrever um único bloco gigante de código ("código espaguete"), o problema foi dividido em três funções independentes, cada uma com uma única responsabilidade — `validar_pagamento(compra, pago)`, `calcular_troco(compra, pago)` e `decompor_notas(troco)` — e um programa principal que orquestra o fluxo.

Desenvolvido como parte da disciplina de **Programação de Computadores (2026.1)** — atividade **Desafio Unplugged: Papel, Caneta e Lógica**, o trabalho aplica os quatro critérios da matriz de avaliação (DRY, coesão funcional, isolamento de escopo e clareza top-down) e é entregue em três camadas: fluxograma em Mermaid, pseudocódigo estruturado e implementação em Python como bônus de validação.

## 🚀 Tecnologias Utilizadas
* **Linguagem:** Python 3 (e pseudocódigo em Português estruturado)
* **Bibliotecas:** funções nativas do Python (sem dependências externas)
* **Ferramentas:** Google Colab, Jupyter Notebook, Mermaid (fluxograma)

## 📊 Resultados e Aprendizados
O algoritmo rodou conforme esperado e devolveu corretamente a decomposição mínima de notas em todos os cenários testados (incluindo o exemplo do enunciado: compra R$ 57, pago R$ 100, troco R$ 43 → 4×R$ 10 + 3×R$ 1).
* **Modularização (alta coesão, baixo acoplamento):** entendi na prática a diferença entre "código espaguete" e código modular. Cada função faz uma única coisa e devolve o resultado por `return`, sem variáveis globais poluindo o sistema.
* **Algoritmo guloso com divisão inteira e resto:** apliquei `quantidade = int(valor_restante // d)` percorrendo a lista `[100, 50, 10, 5, 1]` em ordem decrescente, sempre tentando a maior nota primeiro, e atualizando `valor_restante = valor_restante - (quantidade * d)` para a próxima iteração.
* **Top-Down e clareza do fluxo principal:** o programa principal conta a história do fluxo (ler → validar → calcular → decompor → mostrar) sem se perder em detalhes matemáticos, porque cada etapa foi delegada para a função especialista correspondente.

## 🔧 Como Executar
1. Abra o arquivo `projeto-sistema-caixa-e-troco.ipynb` no Google Colab ou Jupyter Notebook.
2. Execute as células em ordem e digite o valor da compra e o valor pago quando solicitado.
3. Confira o relatório final com o total, o valor pago, o troco e a quantidade de cada nota a ser devolvida.

---
[Voltar ao início](https://github.com/Rsant271/portfolio-renan-silva-dos-santos)
