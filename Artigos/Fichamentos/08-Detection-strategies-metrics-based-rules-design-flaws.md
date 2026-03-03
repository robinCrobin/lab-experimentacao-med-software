# Fichamento: Detection Strategies – Metrics-Based Rules for Detecting Design Flaws

## Referência
Marinescu, R. (2004). Detection Strategies: Metrics-Based Rules for Detecting Design Flaws. *Proceedings of ICSM’04*. IEEE.

## Objetivo
Propor o mecanismo **detection strategy**: regras baseadas em métricas que capturam desvios de princípios e heurísticas de bom design, permitindo localizar classes/métodos com falhas de design (ex.: God Class) em vez de inferir o problema a partir de valores métricos isolados.

## Conceitos principais
- **Problema**: Métricas usadas isoladamente são muito finas e não indicam a “doença” (causa) por trás dos sintomas (valores anormais).
- **Solução**: Abordagem top-down – estratégias de detecção que combinam métricas em regras que mapeiam para falhas de design conhecidas.
- Validação em estudos de caso em larga escala; definição de estratégias para cerca de dez falhas de design OO da literatura.

## Relação com os enunciados do laboratório
- **Lab 01**: Não aplicável diretamente às RQs de repositórios; útil em **laboratórios futuros** que analisem qualidade de código ou design (ex.: correlação entre popularidade e presença de design flaws).
- **Medição e experimentação**: Exemplo de **derivação de métricas a partir de objetivos** (GQM em ação); ligação entre métricas brutas e interpretação (design flaws); modelo para pipelines de análise estática em estudos em escala.
