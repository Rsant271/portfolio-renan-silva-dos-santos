# 🚦 Sistema de Farol Inteligente — Cidade Inteligente

## 📝 Descrição do Projeto
Este projeto consiste no desenvolvimento manual (em caderno) de um **algoritmo de controle de semáforos para uma cidade inteligente**, capaz de ler o número de carros em quatro cruzamentos (sensores A, B, C e D) e decidir automaticamente qual modo de operação a rede deve assumir: **Livre**, **Ajuste**, **Crise** ou **Onda Verde**. O objetivo principal é reduzir congestionamento e priorizar emergências sem intervenção humana.

Desenvolvido como parte da disciplina de **Engenharia de Soluções Lógicas (2026.1)** — Exercício 02, o projeto aplica conceitos fundamentais de **lógica de programação estruturada**: declaração de variáveis tipadas, leitura de entradas, blocos condicionais em cascata, cálculo de totais e valores máximos, e teste de mesa para validar o comportamento do algoritmo em diferentes cenários.

A entrega é composta por **fluxograma desenhado à mão**, **pseudocódigo estruturado** em blocos (entrada, processo, decisões e saída) e **teste de mesa** em três cenários distintos para validar a lógica.

## 🚀 Tecnologias Utilizadas
* **Linguagem:** pseudocódigo (Português estruturado)
* **Ferramentas:** caderno, caneta (azul para estrutura, vermelha para destaques)
* **Conceitos aplicados:** declaração de variáveis, condicionais aninhadas, operadores lógicos, teste de mesa

## 📊 Resultados e Aprendizados
O algoritmo foi testado em três cenários distintos no teste de mesa, validando o comportamento esperado em situações normais, de fronteira e com falhas de sensor.
* **Decisões em cascata:** aprendi a estruturar três níveis de decisão (rede congestionada → emergência crítica → onda verde possível) usando `SE/SENÃO` aninhados, garantindo que apenas um modo seja ativado por ciclo.
* **Valores de fronteira:** ao testar o Cenário B (valor exato 50), percebi que a condição `crítico > 50` não ativa a emergência quando o valor é exatamente 50 — entendi a importância de definir com precisão se a comparação deve ser `>` ou `>=` antes de codificar.
* **Validação de entrada:** o Cenário C (sensor quebrado retornando valor negativo) mostrou que o algoritmo aceitava dados inválidos sem questionar — aprendi que toda leitura precisa de uma validação (`ENQUANTO sensor < 0 FAÇA ESCREVA "Valor inválido"`) para garantir robustez.

## 🔧 Como Executar
1. Abra as imagens da pasta na ordem `1.jpeg` a `6.jpeg` para visualizar o exercício completo.
2. As imagens `3.jpeg` mostram o **fluxograma**, e `4.jpeg`, `5.jpeg` e `6.jpeg` mostram o **pseudocódigo** estruturado em blocos.
3. As imagens `1.jpeg` e `2.jpeg` apresentam o **teste de mesa** com os três cenários e a análise crítica das falhas encontradas.

---
[Voltar ao início](https://github.com/Rsant271/portfolio-renan-silva-dos-santos)
