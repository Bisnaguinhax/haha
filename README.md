# 🚀 Pipeline de Dados Seguro: Da Ingestão à Visualização Analítica

<p align="center">
  <img src="docs/images/pipeline_cover.png" alt="Capa do Projeto" width="700"/>
</p>

<p align="center">
  <em>Uma arquitetura de engenharia de dados robusta, segura e 100% reprodutível para ambientes empresariais.</em>
</p>

---

## 📋 Índice

* [I. 🎯 Objetivo do Case](#i--objetivo-do-case)
* [II. 🏛️ Arquitetura da Solução](#ii--arquitetura-da-solução)
* [III. ⚙️ O Case em Ação](#iii--o-case-em-ação)
* [IV. 🧠 Melhorias e Próximos Passos](#iv--melhorias-e-próximos-passos)
* [V. 🛠️ Reprodutibilidade da Arquitetura](#v--reprodutibilidade-da-arquitetura)
* [VI. 📊 Resultados e Evidências](#vi--resultados-e-evidências)

---

## I. 🎯 Objetivo do Case

### Desafio
Construir um **pipeline de dados ponta a ponta** em uma arquitetura **100% local e open-source**, garantindo total reprodutibilidade. A solução abrange desde a ingestão de múltiplas fontes até a criação de um dashboard analítico interativo, com um foco rigoroso em **segurança, qualidade, governança e automação**.

### Competências Demonstradas
Este projeto é uma evidência prática de **competências avançadas em Engenharia de Dados**, abrangendo:

- **🔧 Orquestração de fluxos complexos e resilientes** com Apache Airflow.
- **⚡ Processamento de dados em larga escala** com Apache Spark.
- **🏗️ Modelagem dimensional e arquitetura Star Schema** para Data Warehouses.
- **🔐 Desenvolvimento de um Framework de Segurança customizado**, com Vault de segredos e auditoria.
- **📊 Implementação de Quality Gates** com Great Expectations.
- **🏛️ Construção de uma arquitetura de Data Lake Medallion** (Bronze, Silver, Gold) com MinIO.
- **🤖 Automação de processos** de setup e refatoração de código.
- **📈 Visualização analítica e Business Intelligence** com Streamlit e Grafana.
- **🐳 Gestão de ambientes com Docker e Docker Compose** para portabilidade total.

### Valor de Negócio
A solução demonstra uma abordagem de engenharia completa, preparada para os desafios de ambientes de produção. Ela possibilita o processamento seguro de dados heterogêneos, a geração de insights acionáveis e serve como um **template robusto para pipelines futuros com foco em compliance e governança**.

---

## II. 🏛️ Arquitetura da Solução

### Visão Geral da Arquitetura

> **Nota Importante:** O GitHub não renderiza diagramas Mermaid diretamente. A melhor prática é gerar uma imagem (PNG/SVG) a partir do código Mermaid e inseri-la aqui. Você pode usar o [Editor Online do Mermaid](https://mermaid.live) para gerar a imagem.

<p align="center">
  <img src="docs/images/architecture_diagram.png" alt="Visão Geral da Arquitetura" width="800"/>
  <br>
  <em><strong>Ação Necessária:</strong> Gere a imagem do seu diagrama Mermaid e salve em <code>docs/images/architecture_diagram.png</code> (ou atualize o caminho).</em>
</p>


### Detalhamento dos Componentes

- **Apache Airflow:** O cérebro da orquestração, gerenciando o agendamento e a execução de todos os pipelines (DAGs).
- **PostgreSQL:** Atua como o banco de metadados do Airflow e como o Data Warehouse final, hospedando o modelo Star Schema.
- **MinIO:** Simula um Object Storage (compatível com S3) para nosso Data Lake, com as camadas Bronze, Silver, Gold e Cold.
- **Redis:** Broker de mensagens para o Celery Executor do Airflow, permitindo a execução distribuída de tarefas.
- **Apache Spark:** Motor de processamento distribuído para transformações e agregações em larga escala.
- **Streamlit:** Interface para construir dashboards interativos de Business Intelligence.
- **Grafana:** Ferramenta para monitoramento e visualização de métricas operacionais.

### 🔐 Framework de Segurança Customizado (`plugins/security_system/`)

> **Diferencial do Projeto:** Este framework garante a integridade, confidencialidade e rastreabilidade dos dados em todo o pipeline, demonstrando conhecimento avançado em segurança e engenharia de software.

- **Security Vault:** Um cofre digital criptografado (AES-128) que armazena credenciais sensíveis e as fornece em tempo de execução, eliminando o *hardcoding*.
- **Audit Logger:** Um sistema de auditoria que registra todas as operações críticas (acessos a segredos, transformações, validações), essencial para conformidade (LGPD, SOX).
- **Secure Connection Pool:** Um gerenciador que facilita a obtenção segura de conexões a serviços externos (MinIO, PostgreSQL), abstraindo o uso do Vault.

### 🗄️ Data Lake com Arquitetura Medallion (MinIO)

| Camada         | Descrição                    | Características                                              |
| :------------- | :--------------------------- | :----------------------------------------------------------- |
| 🥉 **Bronze** | Dados Brutos e Imutáveis     | Raw data, schema-on-read, auditável.                         |
| 🥈 **Silver** | Dados Limpos e Padronizados  | LGPD compliant (PII mascarado), validado, pronto para análise. |
| 🥇 **Gold** | Dados Agregados e Otimizados | Regras de negócio aplicadas, sumarizado, alta performance para BI. |
| 🧊 **Cold Storage** | Dados Arquivados/Inativos    | Otimização de custos, retenção de longo prazo.               |

### ⚡ Processamento Distribuído (Apache Spark)
Utilizado para transformações complexas, executando limpeza, normalização, enriquecimento e agregação, com credenciais injetadas de forma segura em tempo de execução e persistindo os dados no formato colunar otimizado Parquet.

### 📊 Qualidade de Dados (Great Expectations)
Implementamos **Quality Gates** em etapas críticas. Os pipelines são interrompidos automaticamente se as expectativas de qualidade não forem atendidas, prevenindo a propagação de dados ruins e garantindo a confiança nos resultados.

---

## III. ⚙️ O Case em Ação

### Fluxo de Trabalho do Pipeline

<p align="center">
  <img src="docs/images/pipeline_flow.png" alt="Fluxo de Trabalho do Pipeline" width="800"/>
  <br>
  <em><strong>Ação Necessária:</strong> Gere a imagem do seu segundo diagrama e salve em <code>docs/images/pipeline_flow.png</code> (ou atualize o caminho).</em>
</p>

### 🔄 Etapas Detalhadas do Pipeline

1.  **Coleta Segura:**
    - **Objetivo:** Ingestão de dados brutos de APIs e datasets.
    - **Segurança:** Credenciais são obtidas do Security Vault.
    - **Destino:** Camada **Bronze** do MinIO.

2.  **Consolidação e Mascaramento PII:**
    - **Objetivo:** Limpar, unificar e proteger dados sensíveis (LGPD).
    - **Destino:** Camada **Silver** do MinIO.

3.  **Processamento em Larga Escala com Spark:**
    - **Objetivo:** Transformar dados da camada Silver em agregados para BI.
    - **Segurança:** Credenciais para o MinIO são injetadas de forma segura no Spark.
    - **Destino:** Camada **Gold** do MinIO.

4.  **Validação de Qualidade:**
    - **Objetivo:** Assegurar a integridade dos dados com Great Expectations, atuando como um "Quality Gate".
    - **Auditoria:** Resultados das validações são registrados no Audit Logger.

5.  **Carga no Data Mart (Star Schema):**
    - **Objetivo:** Carregar dados da camada Gold para o PostgreSQL de forma transacional (ACID).
    - **Segurança:** Conexão segura ao PostgreSQL utilizando credenciais do Vault.

6.  **Gerenciamento de Lifecycle:**
    - **Objetivo:** Otimizar custos movendo dados antigos da camada Bronze para o Cold Storage.

### Fontes de Dados Integradas

| Fonte           | Tipo       | Descrição                        | Volume Simulado |
| :-------------- | :--------- | :------------------------------- | :-------------- |
| **Banco Central** | API REST   | Indicadores econômicos (IPCA)    | Pequeno         |
| **OpenWeather** | API REST   | Dados meteorológicos por região  | Pequeno         |
| **Olist** | Dataset CSV | Dados reais de e-commerce brasileiro | Grande          |

---

## IV. 🧠 Melhorias e Próximos Passos

### 🚀 Melhorias Propostas
- **🏗️ Infraestrutura como Código (IaC):** Utilizar **Terraform** e **Ansible**.
- **🔄 CI/CD para Pipelines:** Implementar **GitHub Actions / GitLab CI**.
- **📚 Catálogo de Dados:** Integrar com **Apache Atlas** ou **Amundsen**.
- **🔭 Observabilidade Avançada:** Usar **Prometheus / Grafana** e **Jaeger / OpenTelemetry**.

### 📈 Projeções de Escalabilidade

| Aspecto       | Implementação Atual (Local) | Proposta de Melhoria (Cloud)             |
| :------------ | :-------------------------- | :--------------------------------------- |
| **Volume** | ~100k registros             | **Petabytes** (particionamento, sharding) |
| **Latência** | < 30s (end-to-end)          | **< 10s** (ingestão com Kafka/Redis)      |
| **Concorrência**| 3 DAGs paralelas            | **10+ DAGs e tasks simultâneas** (K8s)    |
| **Monitoramento** | Logs básicos, Airflow UI    | **APM completo**, dashboards, alertas    |

### 🏆 Considerações Finais

> Este case entrega uma solução de dados **enterprise-grade, segura, confiável e totalmente reprodutível**. As decisões de projeto demonstram um domínio de conceitos que vão muito além do básico, focando nos desafios reais de um ambiente corporativo. A arquitetura está pronta para ser adaptada e estendida para ambientes de nuvem em grande escala.

---

## V. 🛠️ Reprodutibilidade da Arquitetura

### Pré-requisitos e Instalação

1.  **Pré-requisitos:**
    - Python 3.8+, Git, Docker e Docker Compose.
    - **Hardware Mínimo:** 8GB RAM (16GB recomendado), 4 CPU cores, 10GB de armazenamento.

2.  **Clonagem do Repositório:**
    ```bash
    git clone [https://github.com/felipesbonatti/case-data-master-engenharia-de-dados.git](https://github.com/felipesbonatti/case-data-master-engenharia-de-dados.git)
    cd case-data-master-engenharia-de-dados
    ```

3.  **Configuração do Ambiente:**
    > **Atenção:** Este passo é CRÍTICO para a segurança e funcionamento do pipeline.

    ```bash
    # Crie o arquivo de ambiente a partir do template
    cp .env.example .env

    # Gere uma chave de criptografia segura e adicione-a ao .env
    python -c "from cryptography.fernet import Fernet; print('SECURITY_VAULT_SECRET_KEY=' + Fernet.generate_key().decode())" >> .env

    # ABRA O ARQUIVO .env E CONFIGURE SUAS API KEYS E SENHAS REAIS!
    ```

4.  **Inicialização da Infraestrutura:**
    ```bash
    # Garante um ambiente limpo, reconstruindo as imagens e dependências
    docker-compose down -v --rmi all && docker system prune -a --volumes -f

    # Inicia todos os serviços em background
    docker-compose up -d --build
    ```

5.  **Configuração do Security Vault e Airflow:**
    ```bash
    # Acesse o contêiner do Airflow scheduler
    docker-compose exec airflow-scheduler bash

    # Dentro do contêiner, popule o Vault com as credenciais do seu .env
    python /opt/airflow/scripts/setup_vault_secrets.py
    
    # Saia do contêiner
    exit

    # Inicialize o banco de dados e crie o usuário admin
    docker-compose exec airflow-webserver airflow db upgrade
    docker-compose exec airflow-webserver airflow users create \
        --username admin --password admin \
        --firstname Admin --lastname User \
        --role Admin --email admin@example.com || true
    ```

### Verificação e Execução
- **Airflow UI:** `http://localhost:8080` (admin/admin)
- **MinIO Console:** `http://localhost:9001` (usuário/senha do seu `.env`)
- **Streamlit Dashboard:** Execute com `streamlit run dashboard/app.py` e acesse `http://localhost:8501`.

---

## VI. 📊 Resultados e Evidências

### 🗄️ Data Lake em Ação (MinIO)
A implementação no MinIO segue a arquitetura Medallion, com buckets separados para as camadas **Bronze**, **Silver** e **Gold**, demonstrando organização e governança.

### 📊 Qualidade de Dados Garantida (Great Expectations)
A DAG `dag_05_validacao_segura_v1` demonstra o sucesso na aplicação dos Quality Gates, assegurando que apenas dados de alta qualidade progridam no pipeline.

### ⚡ Pipeline em Execução e Métricas de Performance (Airflow UI)
As DAGs no Airflow demonstram orquestração robusta e eficiência, com métricas de performance visíveis na UI para tarefas de **processamento Spark**, **consolidação/mascaramento** e **carga no Data Mart**.

### 🔐 Segurança Implementada
O framework de segurança é validado por:
- **Credenciais Criptografadas:** O arquivo `vault.json` armazena segredos de forma segura.
- **Auditoria Completa:** Os logs em `logs/security_audit/` registram cada operação crítica.
- **Mascaramento de PII:** A camada Silver contém dados sensíveis protegidos, em conformidade com a LGPD.
