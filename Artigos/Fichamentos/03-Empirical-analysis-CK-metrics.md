# Fichamento: Empirical Analysis of CK Metrics for Object-Oriented Design Complexity

## Referência
Subramanyam, R., & Krishnan, M. S. (2003). Empirical Analysis of CK Metrics for Object-Oriented Design Complexity: Implications for Software Defects. *IEEE Transactions on Software Engineering*, 29(4), 297–310.

## Objetivo
Fornecer evidência empírica de que métricas de complexidade de design OO (subconjunto da suíte Chidamber & Kemerer – CK) estão associadas a defeitos em software, controlando para tamanho e comparando amostras em C++ e Java.

## Métricas e metodologia
- **Métricas CK** utilizadas: acoplamento, coesão, herança e outras da suíte CK.
- Regressão linear ponderada; controle para tamanho do software; comparação entre linguagens (C++ e Java).
- Dados industriais; defeitos definidos como reportados por clientes ou identificados em testes de aceitação.

## Resultados principais
- Mesmo controlando para tamanho, as métricas CK estão significativamente associadas a defeitos.
- O efeito das métricas sobre defeitos varia entre C++ e Java.
- Implicações para desenho de software OO de alta qualidade.

## Relação com os enunciados do laboratório
- **Lab 01**: Não trata diretamente de repositórios GitHub; oferece **fundamento para métricas de qualidade** que podem ser usadas em laboratórios futuros (análise de código, qualidade de projetos populares).
- **Medição e experimentação**: Exemplo de **validação empírica de métricas** (CK), controle de variáveis (tamanho), comparação entre contextos (linguagens) e uso de análise estatística – modelo para formular hipóteses e interpretar métricas em experimentos.
