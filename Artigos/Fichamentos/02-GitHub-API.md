# Fichamento: GitHub API (Material de Apoio)

## Referência
Aramuni, J. P. *GitHub API*. Material de apoio – PUC Minas. Roteiro de aula prática sobre coleta e análise de características de repositórios populares no GitHub (incl. microsserviços).

## Objetivo
Fornecer roteiro de aula prática para elaboração de experimento que coleta e analisa características dos repositórios mais populares do GitHub, com demonstração de uso da API.

## Conteúdo relevante
- Apresentação do professor e contexto da disciplina.
- Uso da API do GitHub (REST/GraphQL) para obter dados de repositórios.
- Relação direta com laboratórios que exigem consulta GraphQL própria (sem bibliotecas de terceiros para consumo da API).

## Relação com os enunciados do laboratório
- **Lab 01**: Suporte direto à **Lab01S01** (consulta GraphQL para repositórios e métricas necessárias às RQs) e **Lab01S02** (paginação para 1000 repositórios, exportação CSV). O enunciado proíbe bibliotecas de terceiros que realizem consultas à API; o material apoia a escrita da query GraphQL e do script de consumo.
- **Medição**: Fonte de dados para métricas como estrelas, PRs, releases, issues, linguagem, datas de criação e última atualização.
