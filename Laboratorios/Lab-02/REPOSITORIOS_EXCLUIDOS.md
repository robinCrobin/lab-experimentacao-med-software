# Repositórios excluídos da análise

Dos 1.000 repositórios coletados em `data/top_java_repos.csv`, **30** foram
excluídos do `data/metrics_consolidated.csv` (e portanto de todas as RQs e
estatísticas derivadas). Restam **970** repositórios válidos.

A exclusão acontece em `analysis/build_metrics.py:93` (pula `class.csv`
vazio) e `:48-49` (pula `class.csv` sem nenhuma classe).

## Categoria 1 — CK falhou ao executar (22 repositórios)

`class.csv` foi criado vazio. São, em sua maioria, projetos gigantes ou que
usam sintaxe Java moderna que o parser JDT embutido no CK não suporta. Mesmo
com o fallback `use_jars=False` (`main.py:385-393`) o CK lança NPE.

| # | Repositório |
|---|---|
| 1 | elastic/elasticsearch |
| 2 | NationalSecurityAgency/ghidra |
| 3 | dbeaver/dbeaver |
| 4 | openjdk/jdk |
| 5 | oracle/graal |
| 6 | thingsboard/thingsboard |
| 7 | JetBrains/intellij-community |
| 8 | questdb/questdb |
| 9 | Grasscutters/Grasscutter |
| 10 | neo4j/neo4j |
| 11 | projectlombok/lombok |
| 12 | trinodb/trino |
| 13 | provectus/kafka-ui |
| 14 | aosp-mirror/platform_frameworks_base |
| 15 | checkstyle/checkstyle |
| 16 | facebook/buck |
| 17 | haifengl/smile |
| 18 | google/j2objc |
| 19 | apache/groovy |
| 20 | dragonwell-project/dragonwell8 |
| 21 | JabRef/jabref |
| 22 | eclipse-openj9/openj9 |

## Categoria 2 — CK rodou mas não encontrou classes Java (8 repositórios)

`class.csv` existe e tem cabeçalho, porém nenhuma linha de dados. São
repositórios que aparecem na busca como "Java" no GitHub mas não contêm
código Java compilável (geralmente são tutoriais, listas em Markdown,
APKs decompilados, ou bindings nativos).

| # | Repositório | Observação |
|---|---|---|
| 1 | hollischuang/toBeTopJavaer | Tutorial em Markdown |
| 2 | frank-lam/fullstack-tutorial | Tutorial em Markdown |
| 3 | react-native-camera/react-native-camera | Bindings RN; Java mínimo |
| 4 | CoderLeixiaoshuai/java-eight-part | Conteúdo de estudo |
| 5 | Archmage83/tvapk | Lista de APKs |
| 6 | RedSpider1/concurrent | Conteúdo de estudo |
| 7 | jlegewie/zotfile | Plugin Zotero (JS) |
| 8 | NotFound9/interviewGuide | Guia de entrevistas |

## Como reproduzir esta lista

```bash
cd Laboratorios/Lab-02
python3 - <<'PY'
import csv
from pathlib import Path
all_repos = [r['nameWithOwner'] for r in csv.DictReader(open('data/top_java_repos.csv'))]
included = {r['name_with_owner'] for r in csv.DictReader(open('data/metrics_consolidated.csv'))}
print(sorted(set(all_repos) - included))
PY
```
