# Fichamento: When Code Smells Meet ML – ML-specific Code Smells in ML-enabled Systems

## Referência
Recupito, G., Giordano, G., Ferrucci, F., Di Nucci, D., & Palomba, F. (2023/2024). When Code Smells Meet ML: On the Lifecycle of ML-specific Code Smells in ML-enabled Systems. *MSR’24*.

## Objetivo
Investigar surgimento e evolução de **ML-specific code smells** em sistemas habilitados por ML: prevalência, como são introduzidos e removidos, sobrevivência; plano de estudo com mineração de 400k+ commits em 337 projetos e detector CodeSmile.

## Conceitos
- ML-specific code smells: soluções subótimas em pipelines ML que reduzem qualidade e manutenibilidade.
- Dívida técnica em sistemas ML-enabled; necessidade de abordagens de garantia de qualidade específicas para ML.

## Relação com os enunciados do laboratório
- **Lab 01**: Conexão indireta: repositórios populares incluem projetos ML; métricas de **atividade** (commits, PRs, releases) podem ser usadas em estudos que relacionem atividade a introdução/remoção de smells (incl. ML).
- **Medição e experimentação**: Modelo de **mineração em larga escala** (muitos repositórios e commits); definição de smells específicos de domínio; pipeline de detecção + análise de histórico – padrão MSR aplicável a outros tipos de smells ou métricas.
