# Fichamento: When and Why Your Code Starts to Smell Bad

## Referência
Tufano, M., Palomba, F., Bavota, G., Oliveto, R., Di Penta, M., De Lucia, A., & Poshyvanyk, D. (2015). When and Why Your Code Starts to Smell Bad. *Proceedings of ICSE’15*.

## Objetivo
Investigar **quando** e **por que** code smells são introduzidos em projetos, por meio de estudo empírico em larga escala no histórico de mudanças de 200 projetos open source (Android, Apache, Eclipse).

## Metodologia e métricas
- Estratégia para identificar commits que introduzem smells; mineração de mais de 0,5M de commits; análise manual de 9.164 commits smell-introducing.
- Métricas/indicadores: momento da introdução (evolutivo vs. repentino), circunstâncias, responsáveis.

## Resultados principais
- Resultados em grande parte **contradizem** o senso comum de que smells são introduzidos principalmente em tarefas evolutivas sob pressão.
- Evidência quantitativa e qualitativa sobre quando e por que smells aparecem; implicações para sistemas de recomendação e planejamento de refatoração.

## Relação com os enunciados do laboratório
- **Lab 01**: Conexão indireta: repositórios populares (como os 1000 do Lab 01) são candidatos a estudos similares (histórico de commits, PRs, issues). Métricas de **atividade** (RQ02–RQ04) podem ser relacionadas a qualidade/evolução em trabalhos futuros.
- **Medição e experimentação**: Modelo de **estudo em larga escala** (muitos repositórios), mineração de histórico, definição operacional de “smell-introducing commit” e combinação de análise quantitativa e qualitativa.
