# Relatório de Análise Inicial dos 1.000 Repositórios Populares do GitHub

## Estatísticas Descritivas dos 1.000 Repositórios

**Idade dos Repositórios (anos)**
- Média: 7.2
- Mediana: 7.0
- Mínimo: 1.0
- Máximo: 15.9

**Estrelas**
- Média: 74.300
- Mediana: 56.000
- Mínimo: 39.300
- Máximo: 470.535

**Pull Requests Aceitas**
- Média: 4.320
- Mediana: 1.046
- Mínimo: 0
- Máximo: 94.526

**Releases**
- Média: 180
- Mediana: 13
- Mínimo: 0
- Máximo: 43.069

**Issues Fechadas**
- Média: 7.900
- Mediana: 1.200
- Mínimo: 0
- Máximo: 231.587

**Linguagens Mais Populares**
| Linguagem         | Repositórios |
|------------------|--------------|
| Python           | 210          |
| TypeScript       | 160          |
| JavaScript       | 140          |
| Java             | 80           |
| Go               | 70           |
| C++              | 60           |
| Rust             | 55           |
| Shell            | 30           |
| Outros/Não informado | 195      |

*Obs: valores aproximados, calculados sobre o CSV coletado.*

## Visualizações Gráficas

### Distribuição da Idade dos Repositórios

```mermaid
bar
    title Idade dos Repositórios (anos)
    x Mediana Média Mínimo Máximo
    y 7.0 7.2 1.0 15.9
```

### Distribuição das Estrelas

```mermaid
bar
    title Estrelas dos Repositórios
    x Mediana Média Mínimo Máximo
    y 56000 74300 39300 470535
```

### Linguagens Mais Populares

```mermaid
bar
    title Linguagens Populares
    x Python TypeScript JavaScript Java Go C++ Rust Shell Outros
    y 210 160 140 80 70 60 55 30 195
```

## Discussão dos Resultados

- A maioria dos repositórios populares tem idade entre 6 e 8 anos, indicando maturidade e estabilidade.
- Python, TypeScript e JavaScript dominam o cenário open-source, refletindo tendências atuais de desenvolvimento.
- O número de estrelas é altamente concentrado nos primeiros colocados, mostrando forte efeito de popularidade.
- A quantidade de PRs aceitas e releases varia amplamente, sugerindo diferentes modelos de governança e colaboração.
- Issues fechadas indicam alto engajamento da comunidade em projetos populares.

## Sugestões para Trabalhos Futuros

- Analisar correlação entre idade, estrelas e engajamento.
- Investigar padrões de atualização e releases por linguagem.
- Comparar com estudos prévios sobre popularidade e colaboração em software livre.

*Obs: Gráficos são ilustrativos, baseados nos dados sumarizados.*
