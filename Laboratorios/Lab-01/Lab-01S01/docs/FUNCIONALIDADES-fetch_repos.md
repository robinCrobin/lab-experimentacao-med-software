# Documentação das Funcionalidades do fetch_repos.py

Este documento descreve as principais funcionalidades implementadas no script `fetch_repos.py` localizado em `Laboratórios/Lab-01`.

## Funcionalidades

### 1. Coleta de Repositórios Populares
- Utiliza a API GraphQL do GitHub para buscar repositórios com mais de 10.000 estrelas.
- Realiza paginação automática até atingir o número desejado de repositórios (100).
- Exibe progresso da coleta a cada página processada.

### 2. Persistência dos Dados
- Os dados coletados são armazenados em uma lista Python (`all_repos`).
- Ao final da coleta, os dados são salvos em um arquivo JSON formatado (`data/repositorios.json`).
- O arquivo é salvo com encoding UTF-8 e indentação para facilitar leitura.

### 3. Organização dos Dados
- Cria automaticamente a pasta `data/` para armazenar o arquivo de dados, separando persistência do restante do código.

### 4. Garantia de 100 Repositórios
- O script limita o número de repositórios salvos no arquivo JSON para exatamente 100, mesmo que mais sejam coletados.

### 5. Mensagens Amigáveis ao Usuário
- Exibe mensagens claras ao final da execução, informando sucesso e o local onde os dados foram salvos.
- Informa que o arquivo pode ser utilizado para análises futuras ou integração com outros experimentos.

### 6. Validação Simples de Integridade
- Após salvar o arquivo, realiza uma verificação simples:
    - Confirma se o arquivo contém 100 repositórios.
    - Verifica se cada repositório possui os campos essenciais (`name` e `url`).
- Exibe mensagem indicando se o arquivo está íntegro ou se há problemas na coleta.

### 7. Autenticação via Token
- Exige que o usuário defina a variável de ambiente `GITHUB_TOKEN` para autenticação na API do GitHub.
- Exibe mensagem de erro e encerra o script caso o token não esteja definido.

### 8. Tratamento de Erros
- Exibe mensagens de erro amigáveis em caso de problemas de autenticação ou falhas na requisição à API.

---

Este script está pronto para ser utilizado em experimentos, análises e integrações com outros projetos, garantindo robustez, organização e facilidade de uso.
