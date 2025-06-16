```markdown
# 🚀 Pipeline de Dados Seguro: Da Ingestão à Visualização Analítica

![Capa do Projeto](docs/images/pipeline_cover.png)

*Uma arquitetura de engenharia de dados robusta, segura e 100% reprodutível para ambientes empresariais.*

---

## 📋 Índice

* [I. 🎯 Objetivo do Case](#i--objetivo-do-case)
    * [Desafio](#desafio)
    * [Competências Demonstradas](#competências-demonstradas)
    * [Valor de Negócio](#valor-de-negócio)
* [II. 🏛️ Arquitetura da Solução e Arquitetura Técnica](#ii--arquitetura-da-solução-e-arquitetura-técnica)
    * [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
    * [Detalhamento dos Componentes](#detalhamento-dos-componentes)
    * [🔐 Framework de Segurança (Customizado - `plugins/security_system/`)](#-framework-de-segurança-customizado---pluginssecurity_system)
    * [🗄️ Data Lake com Arquitetura Medallion (MinIO)](#-data-lake-com-arquitetura-medallion-minio)
    * [⚡ Processamento Distribuído (Apache Spark)](#-processamento-distribuído-apache-spark)
    * [📊 Qualidade de Dados (Great Expectations)](#-qualidade-de-dados-great-expectations)
* [III. ⚙️ Explicação sobre o Case Desenvolvido](#iii--explicação-sobre-o-case-desenvolvido)
    * [Fluxo de Trabalho do Pipeline](#fluxo-de-trabalho-do-pipeline)
    * [🔄 Etapas Detalhadas do Pipeline](#-etapas-detalhadas-do-pipeline)
    * [Fontes de Dados Integradas](#fontes-de-dados-integradas)
* [IV. 🧠 Melhorias e Considerações Finais](#iv--melhorias-e-considerações-finais)
    * [Decisões de Projeto e Práticas de Produção](#decisões-de-projeto-e-práticas-de-produção)
    * [🚀 Melhorias Propostas para Próximas Iterações](#-melhorias-propostas-para-próximas-iterações)
    * [📈 Escalabilidade e Performance (Projeções)](#-escalabilidade-e-performance-projeções)
    * [🏆 Considerações Finais](#-considerações-finais)
* [V. 🛠️ Reprodutibilidade da Arquitetura](#v--reprodutibilidade-da-arquitetura)
    * [Pré-requisitos do Sistema](#pré-requisitos-do-sistema)
    * [🚀 Instalação e Execução](#-instalação-e-execução)
    * [🔍 Verificação da Instalação](#-verificação-da-instalação)
    * [Execução do Pipeline](#execução-do-pipeline)
    * [🐛 Solução de Problemas](#-solução-de-problemas)
    * [📦 Estrutura do Projeto](#-estrutura-do-projeto)
    * [✅ Checklist de Validação para a Banca](#-checklist-de-validação-para-a-banca)
* [VI. 📊 Resultados e Evidências](#vi--resultados-e-evidências)
    * [🗄️ Arquitetura de Data Lake em Ação (MinIO)](#-arquitetura-de-data-lake-em-ação-minio)
    * [📊 Qualidade de Dados Garantida (Great Expectations)](#-qualidade-de-dados-garantida-great-expectations)
    * [⚡ Pipeline em Execução e Métricas de Performance (Airflow UI)](#-pipeline-em-execução-e-métricas-de-performance-airflow-ui)
    * [🔐 Segurança Implementada (Framework Customizado)](#-segurança-implementada-framework-customizado)

---

## I. 🎯 Objetivo do Case

### Desafio

O objetivo deste projeto é demonstrar a construção de um **pipeline de dados ponta a ponta** em uma arquitetura **100% local e open-source**, garantindo total reprodutibilidade. A solução abrange desde a ingestão de múltiplas fontes até a criação de um dashboard analítico interativo, com um foco rigoroso em **segurança, qualidade, governança e automação**.

### Competências Demonstradas

Este projeto é uma evidência prática de **competências avançadas em Engenharia de Dados**, abrangendo:

* **🔧 Orquestração de fluxos complexos e resilientes** com Apache Airflow, utilizando DAGs modularizadas.
* **⚡ Processamento de dados em larga escala** com Apache Spark, incluindo otimizações para ambiente distribuído.
* **🏗️ Modelagem dimensional e arquitetura Star Schema** para Data Warehouses.
* **🔐 Desenvolvimento de um Framework de Segurança customizado** (principal diferencial), com Vault de segredos criptografado e sistema de auditoria.
* **📊 Implementação de Quality Gates** com Great Expectations para garantir a qualidade dos dados em diferentes estágios.
* **🏛️ Construção de uma arquitetura de Data Lake Medallion** (Bronze, Silver, Gold) com MinIO.
* **🤖 Automação de processos** de setup e refatoração de código, demonstrando um olhar para a eficiência e manutenibilidade.
* **📈 Visualização analítica e Business Intelligence** com Streamlit e Grafana.
* **🐳 Gestão de ambientes com Docker e Docker Compose**, garantindo portabilidade e reprodutibilidade.

### Valor de Negócio

A solução demonstra uma abordagem de engenharia completa, preparada para os desafios e requisitos de segurança de ambientes de produção. Ela possibilita o processamento seguro de dados heterogêneos, a geração de insights acionáveis para tomada de decisão empresarial, e serve como um template robusto para pipelines futuros, com foco em compliance e governança.

---

## II. 🏛️ Arquitetura da Solução e Arquitetura Técnica

### Visão Geral da Arquitetura

A arquitetura foi desenhada para ser totalmente contida no ambiente local, utilizando ferramentas open-source que simulam um ecossistema de dados corporativo moderno e robusto.

![Visão Geral da Arquitetura](docs/images/architecture_diagram.png)

> **Nota:** Para o diagrama acima ser exibido, gere uma imagem (PNG/SVG) a partir do código Mermaid correspondente e salve-a no caminho `docs/images/architecture_diagram.png`.

### Detalhamento dos Componentes

A solução é composta por um conjunto de serviços orquestrados via Docker Compose, cada um com uma responsabilidade bem definida:

* **Apache Airflow:** O coração da orquestração. Gerencia o agendamento e a execução de todas as DAGs, que representam os pipelines de dados.
* **PostgreSQL:** Atua como o banco de dados de metadados do Airflow e como o Data Warehouse/Data Mart principal, hospedando o modelo Star Schema.
* **MinIO:** Simula um Object Storage compatível com S3 (Data Lake), onde os dados são armazenados nas camadas Bronze, Silver e Gold, além de uma camada de Cold Storage.
* **Redis:** Utilizado como broker de mensagens para o Celery Executor do Airflow, permitindo a execução distribuída e escalável de tarefas.
* **Apache Spark:** Motor de processamento distribuído, ideal para transformações e agregações em larga escala, especialmente na transição entre as camadas do Data Lake.
* **Streamlit:** Uma interface simples e poderosa para construir dashboards interativos de Business Intelligence, conectando-se aos dados processados no PostgreSQL.
* **Grafana:** Ferramenta para monitoramento e visualização de métricas operacionais, podendo ser integrada para acompanhar a saúde dos serviços e do pipeline.

### 🔐 Framework de Segurança (Customizado - `plugins/security_system/`)

Este é o principal diferencial do projeto, demonstrando um profundo conhecimento em segurança de dados e engenharia de software. Ele garante a integridade, confidencialidade e rastreabilidade dos dados em todo o pipeline:

* **Security Vault** (`VaultManager` em `plugins/security_system/vault_manager_helper.py`): Um cofre digital baseado em arquivo JSON, criptografado com Fernet (AES-128 GCM). Armazena credenciais sensíveis de forma centralizada e segura, recuperando-as em tempo de execução.
* **Audit Logger** (`AuditLogger` em `plugins/security_system/audit.py`): Um sistema de auditoria abrangente que registra todas as operações críticas do pipeline em um formato estruturado para conformidade (LGPD, SOX) e rastreabilidade.
* **Secure Connection Pool** (`SecureConnectionPool` em `plugins/security_system/secure_connection_pool.py`): Um gerenciador que facilita a obtenção segura de clientes para serviços externos (MinIO, PostgreSQL), buscando as credenciais do Vault.
* **Exceções Customizadas** (`plugins/security_system/exceptions.py`): Uma hierarquia de exceções específicas para o sistema de segurança, permitindo tratamento de erros granular e informativo.
* **Rotação de Chaves** (`plugins/security_system/key_rotation.py`): Módulo que simula a rotação segura de chaves criptográficas, armazenando versões antigas para descriptografia de dados legados.

### 🗄️ Data Lake com Arquitetura Medallion (MinIO)

Implementação de um Data Lake multicamadas para governança e qualidade de dados:

| Camada          | Descrição                     | Características                                              |
| :-------------- | :---------------------------- | :----------------------------------------------------------- |
| 🥉 **Bronze** | Dados Brutos e Imutáveis      | Raw data, schema-on-read, auditável, imutável.               |
| 🥈 **Silver** | Dados Limpos e Padronizados   | LGPD compliant, PII mascarado, deduplicado, pronto para análise. |
| 🥇 **Gold** | Dados Agregados e Otimizados  | Regras de negócio aplicadas, sumarizado, alta performance para BI. |
| 🧊 **Cold Storage** | Dados Arquivados/Inativos     | Otimização de custos, acesso menos frequente.                |

### ⚡ Processamento Distribuído (Apache Spark)

Utilizado para transformações complexas e em larga escala, executando operações de limpeza, normalização, enriquecimento e agregação. As credenciais para MinIO/S3 são passadas de forma segura ao Spark em tempo de execução via variáveis de ambiente, prevenindo o hardcoding. A persistência em Parquet, formato colunar otimizado para Big Data, é ideal para eficiência de leitura e escrita.

### 📊 Qualidade de Dados (Great Expectations)

Implementação de Quality Gates para garantir a confiança nos dados. São aplicadas suítes de expectativas em datasets em etapas críticas. Com uma estratégia "Fail-Fast", os pipelines são interrompidos automaticamente se as expectativas críticas de qualidade não forem atendidas, prevenindo a propagação de dados ruins. Os resultados das validações são logados e auditados.

---

## III. ⚙️ Explicação sobre o Case Desenvolvido

O projeto demonstra um pipeline de dados completo e seguro, orquestrado por uma série de DAGs no Apache Airflow. Cada DAG possui uma responsabilidade clara e se integra nativamente com o framework de segurança customizado desenvolvido.

### Fluxo de Trabalho do Pipeline

![Fluxo de Trabalho do Pipeline](docs/images/pipeline_flow.png)

> **Nota:** Para o diagrama acima ser exibido, gere uma imagem (PNG/SVG) a partir do código Mermaid correspondente e salve-a no caminho `docs/images/pipeline_flow.png`.

### 🔄 Etapas Detalhadas do Pipeline

#### Coleta Segura (`dag_01_coleta_segura_v1`, `dag_coleta_dados_externos_enterprise_v1`)

* **Objetivo:** Ingestão inicial de dados brutos de fontes externas.
* **Fontes:** APIs externas (Banco Central para IPCA, OpenWeatherMap para clima) e datasets locais (Olist).
* **Segurança:** Credenciais (ex: API Key do OpenWeatherMap) são obtidas do Security Vault em tempo de execução.
* **Destino:** Dados brutos persistidos na camada **Bronze** do MinIO.
* **Diferencial:** Demonstra o uso de `PythonOperator` para ingestão, `Requests` para APIs, e integração com o framework de segurança.

#### Consolidação e Mascaramento PII (`dag_03_consolidacao_e_mascaramento_v1`)

* **Objetivo:** Limpar, unificar e proteger dados sensíveis.
* **Processo:** Dados lidos da camada Bronze e unificados via `pandas.merge`.
* **Segurança PII:** Aplica mascaramento de informações pessoalmente identificáveis (PII), garantindo LGPD/GDPR compliance.
* **Destino:** Dados limpos e mascarados persistidos na camada **Silver** do MinIO.
* **Diferencial:** Implementação prática de técnicas de Data Privacy (`DataProtection` module) e auditoria detalhada das transformações.

#### Processamento em Larga Escala (`dag_04_processamento_spark_seguro_v1`)

* **Objetivo:** Transformar dados da camada Silver em dados agregados e otimizados para BI.
* **Processo:** Um job Spark é submetido pelo Airflow, processando dados do MinIO/S3.
* **Segurança:** Credenciais para acesso ao MinIO/S3 são injetadas de forma segura no ambiente do Spark em tempo de execução, diretamente do Security Vault.
* **Destino:** Geração da camada **Gold** no MinIO, com dados sumarizados e prontos para consumo analítico.
* **Diferencial:** Demonstra o uso de `BashOperator` para `spark-submit`, passando credenciais de forma segura via ambiente.

#### Validação de Qualidade (`dag_05_validacao_segura_v1`, `scripts/examples/19-validacao_great_expectations_avancada.py`)

* **Objetivo:** Assegurar a integridade e consistência dos dados antes de seu consumo final.
* **Processo:** Aplicação de uma suíte de expectativas de qualidade (Great Expectations) nos dados da camada Gold.
* **Qualidade:** Atua como um "Quality Gate", falhando a DAG se os dados não atenderem aos critérios mínimos.
* **Auditoria:** Os resultados das validações são registrados detalhadamente no Audit Logger.

#### Carga no Data Mart (`dag_06_carrega_star_schema_segura_enterprise_v1`, `dag_minio_para_postgresql_enterprise_v1`)

* **Objetivo:** Carregar dados da camada Gold do Data Lake para o Data Mart relacional.
* **Modelo:** População de um modelo dimensional Star Schema no PostgreSQL, dentro de transações ACID.
* **Segurança:** Conexão segura ao PostgreSQL utilizando credenciais obtidas do Security Vault.
* **Diferencial:** Demonstra ETL de Data Lake para Data Mart, transações ACID, e uso de `SecureConnectionPool`.

#### Gerenciamento de Lifecycle (`dag_gerenciamento_lifecycle_enterprise_v1`)

* **Objetivo:** Otimizar custos de armazenamento e gerenciar a retenção de dados.
* **Processo:** Move automaticamente arquivos antigos da camada Bronze para uma camada de Cold Storage (simulada no MinIO).
* **Segurança:** Operações de movimentação de dados são autenticadas via Security Vault e auditadas.

### Fontes de Dados Integradas

| Fonte          | Tipo        | Descrição                                         | Volume Simulado |
| :------------- | :---------- | :------------------------------------------------ | :-------------- |
| **Banco Central** | API REST    | Indicadores econômicos (IPCA)                     | Pequeno         |
| **OpenWeather** | API REST    | Dados meteorológicos por região (temperatura, etc.) | Pequeno         |
| **Olist** | Dataset CSV | Dados reais de e-commerce brasileiro (público)    | Grande          |

---

## IV. 🧠 Melhorias e Considerações Finais

### Decisões de Projeto e Práticas de Produção

* **Modularidade e Reuso de Componentes de Segurança:** O framework de segurança (`security_system`) foi projetado como um conjunto de módulos reutilizáveis. A separação entre `VaultManager` (lógica de segredos) e `AirflowSecurityManager` (integração UI) é crucial para clareza e manutenção em um ambiente enterprise.
* **Configuração de Credenciais:** No Case, para fins de reprodutibilidade, as credenciais são lidas de variáveis de ambiente do `.env`. Em Produção, a `SECURITY_VAULT_SECRET_KEY` viria de um serviço como AWS Secrets Manager ou HashiCorp Vault, nunca de um arquivo `.env` versionado.
* **Automação da Refatoração (`refinar_projeto.py`):** Foi desenvolvido um script para automatizar a adaptação de caminhos e a inserção de validações. Isso mostra uma mentalidade de engenharia que busca resolver problemas de forma programática, uma prática essencial em equipes de alta performance.

### 🚀 Melhorias Propostas para Próximas Iterações

Para evoluir este projeto para um nível de produção ainda mais avançado, as seguintes melhorias são propostas:

* **Infraestrutura como Código (IaC):**
    * **Terraform:** Para automação da provisão de recursos em nuvem (ex: EC2, RDS, S3, EMR).
    * **Ansible:** Para configuração e deploy de aplicações nos servidores.
* **CI/CD para Pipelines:**
    * **GitHub Actions / GitLab CI:** Para automação de testes unitários, de integração e end-to-end.
    * **Deploy Automatizado:** Novas versões de DAGs seriam implantadas automaticamente.
* **Catálogo de Dados:**
    * Integração com **Apache Atlas** ou **Amundsen** para documentação automática de metadados e linhagem de dados.
* **Observabilidade Avançada:**
    * Métricas Customizadas com **Prometheus / Grafana** para monitoramento granular.
    * Distributed Tracing com **Jaeger / OpenTelemetry** para depuração de pipelines complexos.

### 📈 Escalabilidade e Performance (Projeções)

| Aspecto         | Implementação Atual (Local Docker)  | Melhoria Proposta (Cloud / Otimizações)               |
| :-------------- | :---------------------------------- | :---------------------------------------------------- |
| **Volume** | ~100k registros Olist               | **Petabytes** (particionamento horizontal, sharding)  |
| **Latência** | < 30 segundos (pipeline end-to-end) | **< 10 segundos** (para ingestão, com Kafka/Redis)    |
| **Concorrência**| 3 DAGs paralelas (com CeleryExecutor) | **10+ DAGs e tasks simultâneas** (Kubernetes, Fargate) |
| **Monitoramento**| Logs básicos, Airflow UI            | **APM completo**, dashboards Grafana, alertas SMS/email |
| **Persistência**| Volumes Docker, MinIO local         | **S3/GCS/Azure Blob Storage**, Databases gerenciados  |

### 🏆 Considerações Finais

Este case entrega uma solução de dados enterprise-grade, segura, confiável, escalável e totalmente reprodutível. As decisões de projeto, como a criação de um framework de segurança customizado e a automação de tarefas de desenvolvimento/deploy, demonstram um domínio de conceitos que vão muito além do básico, focando nos desafios reais de um ambiente corporativo moderno.

A arquitetura implementada é *production-ready* em seus princípios e pode ser facilmente adaptada e estendida para ambientes de nuvem em grande escala, mantendo os mesmos pilares de segurança, qualidade e governança.

---

## V. 🛠️ Reprodutibilidade da Arquitetura

Este projeto foi construído com foco na reprodutibilidade e portabilidade, utilizando Docker para isolar o ambiente. As instruções a seguir detalham como configurar e executar o projeto.

### Pré-requisitos do Sistema

* **Softwares Necessários**
    * Python 3.8+ (com pip)
    * Git (versão 2.25+)
    * Docker e Docker Compose
* **Recursos de Hardware Mínimos**
    * RAM: 8GB (recomendado 16GB)
    * Armazenamento: 10GB livres
    * CPU: 4 cores (recomendado 8 cores)

### 🚀 Instalação e Execução

Siga os passos rigorosamente para garantir a correta inicialização do ambiente.

**Passo 1: Clonagem do Repositório**
```bash
git clone [https://github.com/felipesbonatti/case-data-master-engenharia-de-dados.git](https://github.com/felipesbonatti/case-data-master-engenharia-de-dados.git)
cd case-data-master-engenharia-de-dados
```

**Passo 2: Configuração do Ambiente**
> **Atenção:** Este passo é CRÍTICO para a segurança do Vault e o funcionamento do pipeline.

```bash
# Crie o arquivo de ambiente (.env) a partir do template
cp .env.example .env

# Gere uma chave de criptografia segura para o Vault e adicione ao .env
python -c "from cryptography.fernet import Fernet; print('SECURITY_VAULT_SECRET_KEY=' + Fernet.generate_key().decode())" >> .env
```
Abra o arquivo `.env` e configure suas API keys e senhas fortes.

**Passo 3: Adaptação do Projeto (Portabilidade)**
Este script ajusta caminhos de arquivo internos para garantir que o projeto funcione em qualquer sistema operacional.
```bash
# Execute o script de configuração (CRUCIAL para portabilidade)
python configure.py
```

**Passo 4: Instalação de Dependências**
```bash
# Crie um ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# Para Linux/macOS:
source venv/bin/activate
# Para Windows PowerShell:
# venv\Scripts\activate

# Instale todas as dependências Python
pip install -r requirements.txt
```

**Passo 5: Inicialização da Infraestrutura Docker**
Este passo levanta todos os serviços essenciais (PostgreSQL, MinIO, Redis, Airflow).
```bash
# O comando a seguir faz uma limpeza profunda e reconstrói as imagens
docker-compose down -v --rmi all
docker system prune -a --volumes -f
docker-compose up -d --build
```

**Passo 6: Configuração do Security Vault**
Este passo popula o Vault com as credenciais para MinIO, PostgreSQL e APIs externas.
```bash
# Acesse o shell do contêiner do scheduler
docker-compose exec airflow-scheduler bash

# Dentro do contêiner, exporte a chave e popule o vault
export SECURITY_VAULT_SECRET_KEY=$(grep 'SECURITY_VAULT_SECRET_KEY=' /opt/airflow/.env | cut -d '=' -f2)
python /opt/airflow/scripts/setup_vault_secrets.py

# Saia do shell do contêiner
exit
```

**Passo 7: Inicialização do Airflow**
Este passo inicia os componentes internos do Airflow (banco de dados, usuário admin).
```bash
# Inicialize/atualize o banco de dados de metadados do Airflow
docker-compose exec airflow-webserver airflow db upgrade

# Crie o usuário administrador padrão (admin/admin)
docker-compose exec airflow-webserver airflow users create \
    --username admin --password admin \
    --firstname Admin --lastname User \
    --role Admin --email admin@example.com || true
```

### 🔍 Verificação da Instalação

Após seguir os passos, verifique a saúde do ambiente:

* **URLs de Acesso**
    * **Airflow UI:** `http://localhost:8080` (Usuário: admin, Senha: admin)
    * **Streamlit Dashboard:** `http://localhost:8501`
    * **MinIO Console:** `http://localhost:9001` (Credenciais do seu `.env`)
* **Testes de Conectividade**
    Execute no terminal na raiz do projeto (com o ambiente virtual ativado):
    ```bash
    # Teste todas as conexões
    python scripts/health_check.py
    ```

### Execução do Pipeline

1.  Acesse a Airflow UI (`http://localhost:8080`).
2.  Ative as DAGs clicando no botão "toggle" (interruptor).
3.  Dispare as DAGs clicando no ícone de "Play" para uma execução manual.
4.  Monitore a execução pela interface do Airflow (visualizações Graph, Gantt, Logs).

### 🐛 Solução de Problemas

| Problema                      | Solução                                                                                                         |
| :---------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| **Porta já em uso** | Identifique o processo usando a porta (`netstat -tlnp | grep <porta>`) e pare-o.                               |
| **Erro de permissão Docker** | Adicione seu usuário ao grupo `docker` (`sudo usermod -aG docker $USER`) e reinicie a sessão.                 |
| **`spark-submit` not found** | O `PATH` é ajustado dinamicamente na DAG para garantir a detecção do `spark-submit` no contêiner.                 |
| **DAGs 'Broken'** | Verifique os logs do `airflow-scheduler` (`docker-compose logs airflow-scheduler`) para erros de sintaxe ou import. |
| **Credenciais não encontradas** | Certifique-se de que o **Passo 6** foi executado corretamente e que a `SECURITY_VAULT_SECRET_KEY` está correta. |

### 📦 Estrutura do Projeto

```plaintext
pipeline-dados-seguro/
├── 📁 dags/               # DAGs do Apache Airflow (.py)
├── 📁 plugins/            # Plugins customizados do Airflow
│   └── security_system/  # Framework de segurança customizado
├── 📁 scripts/            # Scripts utilitários e de configuração
├── 📁 dashboard/          # Dashboard Streamlit
├── 📁 data/               # Dados de entrada e saída (mapeado como volume)
├── 📁 logs/               # Logs do Airflow e de Auditoria (mapeado como volume)
├── 📁 docs/               # Documentação adicional e imagens
├── 📁 init-scripts/       # Scripts de inicializacao de containers
├── 🐳 docker-compose.yml   # Infraestrutura
├── 📋 requirements.txt    # Dependencias Python
└── ⚙️ .env.example        # Template de variaveis de ambiente
```

### ✅ Checklist de Validação para a Banca

Este checklist pode ser usado pela banca para validar a solução:

-   [ ] O repositório Git é público e acessível.
-   [ ] O arquivo README.md está presente e bem formatado.
-   [ ] Todos os pré-requisitos de software e hardware estão claros.
-   [ ] O script `configure.py` foi executado para adaptar os caminhos.
-   [ ] Os serviços Docker (`minio`, `postgres`, `redis`, `airflow-webserver`, `airflow-scheduler`) estão rodando e saudáveis (`docker-compose ps`).
-   [ ] O Security Vault foi populado com sucesso (`python scripts/setup_vault_secrets.py` executado).
-   [ ] A Airflow UI está acessível em `http://localhost:8080`.
-   [ ] As DAGs aparecem na interface do Airflow (não como 'Broken DAG').
-   [ ] Pelo menos uma DAG (ex: `dag_04_processamento_spark_seguro_v1`) foi executada com sucesso.
-   [ ] Os dados processados aparecem no MinIO (verificar em `http://localhost:9001`).
-   [ ] O Dashboard Streamlit está funcionando (`http://localhost:8501`).
-   [ ] Os logs de auditoria (`logs/security_audit/`) estão sendo gerados.

---

## VI. 📊 Resultados e Evidências

Este projeto não é apenas um conjunto de scripts; é um ecossistema de dados funcional e seguro, validado por evidências concretas.

### 🗄️ Arquitetura de Data Lake em Ação (MinIO)

Nossa implementação do Data Lake em MinIO segue a arquitetura Medallion, garantindo organização, qualidade e governança dos dados em diferentes estágios de processamento. Os buckets `b-prd.sand-ux-indc-brasil` (Bronze), `s-prd.sand-ux-indc-brasil` (Silver), `g-prd.sand-ux-indcs` (Gold) e `glacier-mock` (Cold Storage) demonstram a separação de camadas.

### 📊 Qualidade de Dados Garantida (Great Expectations)

A implementação de Quality Gates com Great Expectations assegura que apenas dados de alta qualidade progridam no pipeline, prevenindo problemas a jusante. O log de sucesso da validação na DAG `dag_05_validacao_segura_v1` mostra a aplicação bem-sucedida das expectativas de qualidade.

### ⚡ Pipeline em Execução e Métricas de Performance (Airflow UI)

As DAGs no Airflow demonstram a orquestração robusta, o paralelismo e a eficiência do pipeline. O grafo da DAG de MinIO para PostgreSQL, a duração da tarefa de processamento Spark, e os logs do gerenciamento de lifecycle confirmam que a lógica de movimentação de dados está operando.

### 🔐 Segurança Implementada (Framework Customizado)

O framework de segurança é um dos maiores destaques, garantindo que o pipeline é robusto e está em conformidade.

* **Credenciais Criptografadas:** As credenciais para todos os serviços são armazenadas criptografadas no Security Vault (`vault.json`) e recuperadas em tempo de execução, garantindo que nunca estejam expostas no código ou em logs.
* **Auditoria Completa:** Cada operação de segurança e acesso a dados é registrada detalhadamente pelo Audit Logger, fornecendo um rastro para conformidade (LGPD, SOX) e investigação de incidentes.
* **Mascaramento de PII:** Demonstra o uso de técnicas como hash e mascaramento estático para proteger informações pessoalmente identificáveis.
* **Criptografia Server-Side (SSE):** Capacidade de fazer upload de arquivos para o MinIO com criptografia SSE-S3, protegendo os dados em repouso.

```
