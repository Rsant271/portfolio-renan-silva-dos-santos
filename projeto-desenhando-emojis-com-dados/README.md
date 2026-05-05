# 🎨 Desenhando Emojis com Dados

## 📝 Descrição do Projeto
Este projeto reúne três desafios em Python que treinam manipulação de **listas, tuplas e dicionários** com **três níveis de loops aninhados**. O Desafio 1 monta um emoji do Claude Code em pixel art 5×5 (dicionário com lista de listas de tuplas RGB) e aplica um filtro de sombra reduzindo o brilho dos pixels laranja em 50%, gerando uma nova tupla pra cada pixel alterado. O Desafio 2 transpõe matrizes 2×2 dos tons das notificações sonoras (Start, Success, Error) usando `dict.update()` para trocar o valor da chave. O Desafio 3 é o integrador: monta uma "Galeria do Claude" com Opus 4.7, Sonnet 4.6 e Haiku 4.5, e gera um relatório de performance usando `.keys()`, `.count()`, `.pop()`, `.insert()` e `.update()`.

Desenvolvido como parte da disciplina de **Programação de Computadores (2026.1)** — atividade **EX6 — Desenhando Emojis com Dados**, o trabalho aplica imutabilidade de tuplas, métodos nativos de cada estrutura de dados e visualização gráfica do resultado com `matplotlib`.

## 🚀 Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Bibliotecas:** `matplotlib.pyplot` (visualização do emoji em pixel art)
* **Ferramentas:** Google Colab, Jupyter Notebook

## 📊 Resultados e Aprendizados
Os três desafios rodaram conforme o esperado: o emoji do Claude Code é renderizado primeiro com o laranja vibrante e depois com o filtro de sombra (50% do brilho), as três matrizes de tons são transpostas corretamente e o relatório integrador imprime os scores de código de cada modelo com a contagem da tag mais frequente.
* **Tuplas são imutáveis — sempre crie uma nova:** entendi na prática por que não dá pra mudar `pixel[0]` direto. Pra aplicar o filtro de sombra, foi preciso montar `(r//2, g//2, b//2)` como tupla nova e fazer `append()` na lista.
* **`dict.update()` para trocar o valor de uma chave:** usei o `.update()` no Desafio 2 pra substituir a matriz original pela transposta dentro do mesmo dicionário, em vez de criar um novo dicionário do zero.
* **3 níveis de `for` exigem planejamento de variáveis intermediárias:** percebi que com loops aninhados profundos é fácil perder o controle do escopo, então criei listas intermediárias (`nova_linha`, `nova_linha_0`, `nova_linha_1`) pra montar o resultado antes de devolver pra estrutura final.

## 🔧 Como Executar
1. Abra o arquivo `projeto-desenhando-emojis-com-dados.ipynb` no Google Colab ou Jupyter Notebook (ou acesse direto pelo [link do Colab](https://colab.research.google.com/drive/1Bt7McLcgHERkHAXovlQXP5yUijlJ8SSq?usp=sharing)).
2. Execute as células em ordem — o Desafio 1 mostra o emoji original e depois com o filtro de sombra, o Desafio 2 imprime as matrizes transpostas e o Desafio 3 monta o relatório da galeria.
3. Para rodar localmente, garanta que o `matplotlib` está instalado (`pip install matplotlib`).

---
[Voltar ao início](https://github.com/Rsant271/portfolio-renan-silva-dos-santos)
