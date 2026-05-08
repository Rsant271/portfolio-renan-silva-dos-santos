# 🏢 Auditoria de Orçamentos Corporativos (Python)

[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-concluído-brightgreen.svg)]()

## 📖 Sobre o Projeto
Este projeto foi desenvolvido como parte da disciplina de **Programação de Computadores** do curso de **Análise e Desenvolvimento de Sistemas** (UNICID 2026.1). O objetivo do script é processar e calcular o orçamento de uma estrutura organizacional complexa (dicionários aninhados) de uma multinacional, aplicando regras de negócio dinâmicas e auditoria de execução.

A solução foi arquitetada utilizando conceitos avançados de Python para garantir flexibilidade, performance e rastreabilidade.

## 🚀 Funcionalidades
- **Cálculo Hierárquico:** Varredura completa da estrutura corporativa, independentemente do nível de profundidade.
- **Filtros Dinâmicos:** Capacidade de ignorar setores específicos e todos os seus subsetores na hora do cálculo financeiro.
- **Conversão de Câmbio:** Suporte a parâmetros opcionais para conversão de moedas em tempo de execução.
- **Sistema de Auditoria:** Monitoramento automatizado de tempo de execução e registro (logging) dos parâmetros utilizados na transação financeira.

## 🛠️ Tecnologias e Conceitos Aplicados
Este projeto foi construído utilizando Python puro (Standard Library), com foco nos seguintes paradigmas e recursos:
* **Funções Recursivas (Recursion):** Utilizadas para a navegação na árvore de dados (dicionários aninhados).
* **Decorators:** Implementação do `@auditor` para injetar comportamentos de log e cronometragem sem modificar a lógica de negócios.
* **Empacotamento de Argumentos (`*args` e `**kwargs`):** Utilizados tanto no decorator quanto na função principal para permitir a passagem dinâmica de departamentos a serem ignorados e taxas de câmbio.

## ⚙️ Como Executar

### Pré-requisitos
* Python 3.8 ou superior instalado.

### Passo a Passo
1. Clone este repositório:
   ```bash
   git clone https://github.com/Rsant271/portfolio-renan-silva-dos-santos.git
   ```
2. Acesse a pasta do projeto:
   ```bash
   cd portfolio-renan-silva-dos-santos/projeto-sistema-de-auditoria-de-recursos-corporativos
   ```
3. Abra o arquivo `projeto-sistema-de-auditoria-de-recursos-corporativos.ipynb` no Google Colab ou Jupyter Notebook e execute as células em ordem.

## 🧠 Lógica e Estrutura do Código
Breve explicação de como o código foi organizado:
* A recursão foi construída em uma função auxiliar (`calcular_orcamento_recursivo`) que percorre cada chave do dicionário, verifica se o valor é outro dicionário (caso recursivo, chama a si mesma descendo um nível) ou um número (caso base, soma na variável local). A função principal `calcular_orcamento` chama esse helper, recebe a soma total e aplica a conversão de moeda apenas no final, garantindo que a multiplicação pela taxa aconteça uma única vez. O decorator `@auditor` foi acoplado somente à função principal e não ao helper recursivo, para que o cabeçalho de auditoria e a medição de tempo apareçam apenas uma vez por execução, e não em cada chamada recursiva.
* **Dados:** Os dados simulados da empresa foram estruturados em um dicionário aninhado raiz chamado `empresa_data`, contendo o nó "Matriz" e três departamentos principais (TI, RH e Financeiro), com sub-departamentos em diferentes profundidades — alguns chegando a três níveis abaixo da raiz. As folhas da árvore são valores numéricos inteiros que representam o orçamento de cada item em USD.

## 👤 Autor

* **Renan Silva dos Santos**
* LinkedIn: https://www.linkedin.com/in/renan-santos-7584901a1
* E-mail: comprasrsant@gmail.com

---
*Projeto acadêmico com foco na aplicação prática de conceitos avançados da linguagem Python.*
