# Índice dos Fichamentos – Material de Apoio (LabMedExp)

Fichamentos em português dos artigos da pasta `Artigos`, com foco na **relação com os enunciados** dos problemas a serem medidos e experimentados (Laboratório 01 e práticas de medição/experimentação em engenharia de software empírica).

---

## Mapeamento rápido: artigo → enunciados / RQs

| Fichamento | Relação direta com Lab 01 | Uso em medição/experimentação |
|------------|---------------------------|------------------------------|
| **01-GQM** | Estrutura Goal → Questions → Metrics (RQs 01–07 e métricas) | Base para definir o que medir e como interpretar |
| **02-GitHub-API** | Consulta GraphQL, paginação, CSV (Lab01S01, S02) | Fonte de dados para métricas de repositórios |
| **03-CK-metrics** | Suporte a métricas de qualidade em extensões | Validação empírica de métricas; controle de variáveis |
| **04-Evidence-based-SE** | Hipóteses, metodologia, discussão do relatório | EBSE; evidência vs. demonstração |
| **05-Guidelines-case-study** | Metodologia e discussão do relatório (estudo observacional) | Diretrizes para relatar estudos empíricos |
| **06-Experimental-models** | Métricas explícitas por RQ; interpretação dos dados | Validação de técnicas; experimento vs. exemplo |
| **07-Should-CS-experiment** | Hipóteses informais; análise crítica dos resultados | Fundamentação da experimentação em SE |
| **08-Detection-strategies** | Laboratórios futuros (qualidade/design) | GQM aplicado; métricas → interpretação |
| **09-When-why-code-smells** | Atividade (commits/PRs) em estudos de histórico | Estudo em larga escala; mineração de repos |
| **10-Diffuseness-code-smells** | Métricas de manutenibilidade em extensões | Métricas validadas; change-/fault-proneness |
| **11-DPy** | RQ05 (linguagem); análise de código Python | Ferramenta para pipelines de métricas/smells |
| **12-Software-metrics-agile** | RQ05/RQ07 (análise por linguagem); comparação de grupos | Métricas CK; sumarização por categoria |
| **13-Test-smells-JNose** | Laboratórios de qualidade de testes | Medição de qualidade de ferramentas (precision/recall) |
| **14-Abstract-factory-decorator** | Laboratórios com métricas CK em código | GQM; métricas OO; antes/depois |
| **15-Agile-systematic-review** | Discussão: padrões ágeis vs. resultados (releases, PRs) | Revisão sistemática; síntese de evidência |
| **16-Code-smells-ML** | Atividade em repos; estudos de histórico | Mineração em larga escala; pipeline MSR |
| **17-SmellyCode++** | Análise de qualidade em repos (extensões) | Pipeline: repo → análise estática → métricas |
| **18-Information-needs** | Interpretação de PRs, issues, colaboração | Contexto para discutir métricas de equipe |
| **19-SWEBOK** | Vocabulário e justificativa das métricas | Objetos de medição; atributos de qualidade |

---

## RQs do Lab 01 (referência)

- **RQ01**: Sistemas populares são maduros/antigos? → idade do repositório  
- **RQ02**: Muita contribuição externa? → total de PRs aceitas  
- **RQ03**: Lançam releases com frequência? → total de releases  
- **RQ04**: Atualizados com frequência? → tempo até última atualização  
- **RQ05**: Escritos nas linguagens mais populares? → linguagem primária  
- **RQ06**: Alto percentual de issues fechadas? → razão issues fechadas / total  
- **RQ07 (bônus)**: Por linguagem – mais contribuição, releases e atualizações?

---

## Lista de arquivos

1. `01-GQM-Goal-Question-Metric-approach.md`
2. `02-GitHub-API.md`
3. `03-Empirical-analysis-CK-metrics.md`
4. `04-Evidence-based-software-engineering.md`
5. `05-Guidelines-case-study-research-SE.md`
6. `06-Experimental-models-validating-technology.md`
7. `07-Should-computer-scientists-experiment-more.md`
8. `08-Detection-strategies-metrics-based-rules-design-flaws.md`
9. `09-When-and-why-your-code-starts-to-smell-bad.md`
10. `10-Diffuseness-impact-code-smells-maintainability.md`
11. `11-DPy-code-smells-detection-python.md`
12. `12-Software-metrics-in-agile-software.md`
13. `13-On-the-test-smells-detection-JNose.md`
14. `14-Impact-abstract-factory-decorator-maintainability.md`
15. `15-Empirical-studies-agile-systematic-review.md`
16. `16-When-code-smells-meet-ML.md`
17. `17-SmellyCode-plus-plus.md`
18. `18-Information-needs-collocated-teams.md`
19. `19-SWEBOK-v4.md`
