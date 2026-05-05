# 📊 Algoritmo de Auditoria de Dados

## 📝 Descrição do Projeto
Este projeto consiste em um algoritmo simples de auditoria de vendas que recebe três valores digitados pelo usuário, calcula a média do dia e dispara alertas automáticos quando algum valor está fora do padrão esperado. O objetivo principal é simular como um sistema real de uma loja poderia identificar **vendas suspeitas** (possíveis erros de digitação ou fraude) e **dias de faturamento atípico**.

Desenvolvido como parte da disciplina de **Programação de Computadores (2026.1)**, o algoritmo aplica conceitos básicos como variáveis globais, funções, conversão de tipos, estruturas condicionais e formatação de saída com f-strings, tudo em um único programa funcional.

## 🚀 Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Bibliotecas:** funções nativas do Python (sem dependências externas)
* **Ferramentas:** Google Colab, Jupyter Notebook

## 📊 Resultados e Aprendizados
O projeto rodou conforme esperado, gerando o relatório de vendas e disparando os alertas corretos em todos os cenários de teste.
* **Variáveis globais e funções:** aprendi a usar `global` dentro de uma função para acessar uma variável declarada fora dela (`LIMITE_SEGURANCA`).
* **Conversão de tipos:** apliquei `float()` para transformar a entrada de texto do usuário em número e a função `type()` para confirmar o tipo de cada variável.
* **Estruturas condicionais:** implementei dois alertas distintos com `if`, um comparando a média ao limite de segurança e outro comparando cada venda individual a 5x a média do dia.

## 🔧 Como Executar
1. Abra o arquivo `projeto-algoritmo-de-auditoria-de-dados.ipynb` no Google Colab ou Jupyter Notebook.
2. Execute as células em ordem e digite os 3 valores de venda quando solicitado.
3. Confira o relatório gerado e os alertas que forem disparados.

---
[Voltar ao início](https://github.com/Rsant271/portfolio-renan-silva-dos-santos)
