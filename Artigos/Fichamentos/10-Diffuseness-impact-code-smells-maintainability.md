# Fichamento: On the Diffuseness and the Impact on Maintainability of Code Smells – Large Scale Empirical Investigation

## Referência
Palomba, F., Bavota, G., Di Penta, M., Fasano, F., Oliveto, R., & De Lucia, A. (2018). On the diffuseness and the impact on maintainability of code smells: a large scale empirical investigation. *Empirical Software Engineering*, 23(3), 1188–1221.

## Objetivo
Investigar em larga escala a **difusão** de code smells e seu **impacto** em change-proneness e fault-proneness (manutenibilidade) em 395 releases de 30 projetos open source, com 17.350 instâncias validadas manualmente de 13 tipos de smells.

## Métricas e metodologia
- Change-proneness e fault-proneness como proxies de manutenibilidade.
- Comparação entre classes com e sem smells; análise da magnitude do efeito e within-artifact.
- Smells caracterizados por código longo/complexo (ex.: Complex Class) mais difusos; classes com smells mais change- e fault-prone.

## Relação com os enunciados do laboratório
- **Lab 01**: Não cobre diretamente as RQs do Lab 01; oferece **métricas de qualidade de código** (smells, change-/fault-proneness) que podem ser usadas em extensões (ex.: “repositórios mais populares têm menos smells?” ou “mais PRs correlacionam com mais mudanças em classes smelly?”).
- **Medição e experimentação**: Exemplo de **métricas validadas** para manutenibilidade; tamanho da amostra e validação manual como padrão de rigor; útil para definir métricas em estudos que combinem dados do GitHub com análise de código.
