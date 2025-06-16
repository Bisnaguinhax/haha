Pipeline de Dados Seguro: Da Ingestão à Visualização Analítica📋 ÍndiceI. Objetivo do CaseII. Arquitetura da Solução e Arquitetura TécnicaIII. Explicação sobre o Case DesenvolvidoIV. Melhorias e Considerações FinaisV. Reprodutibilidade da ArquiteturaVI. Resultados e EvidênciasI. 🎯 Objetivo do CaseDesafioO objetivo deste projeto é demonstrar a construção de um pipeline de dados ponta a ponta em uma arquitetura 100% local e open-source, garantindo total reprodutibilidade. A solução abrange desde a ingestão de múltiplas fontes até a criação de um dashboard analítico interativo, com um foco rigoroso em segurança, qualidade, governança e automação.Competências DemonstradasEste projeto é uma evidência prática de competências avançadas em Engenharia de Dados, abrangendo:🔧 Orquestração de fluxos complexos e resilientes com Apache Airflow, utilizando DAGs modularizadas.⚡ Processamento de dados em larga escala com Apache Spark, incluindo otimizações para ambiente distribuído.🏗️ Modelagem dimensional e arquitetura Star Schema para Data Warehouses.🔐 Desenvolvimento de um Framework de Segurança customizado (principal diferencial), com Vault de segredos criptografado e sistema de auditoria.📊 Implementação de Quality Gates com Great Expectations para garantir a qualidade dos dados em diferentes estágios.🏛️ Construção de uma arquitetura de Data Lake Medallion (Bronze, Silver, Gold) com MinIO.🤖 Automação de processos de setup e refatoração de código, demonstrando um olhar para a eficiência e manutenibilidade.📈 Visualização analítica e Business Intelligence com Streamlit e Grafana.🐳 Gestão de ambientes com Docker e Docker Compose, garantindo portabilidade e reprodutibilidade.Valor de NegócioA solução demonstra uma abordagem de engenharia completa, preparada para os desafios e requisitos de segurança de ambientes de produção. Ela possibilita o processamento seguro de dados heterogêneos, a geração de insights acionáveis para tomada de decisão empresarial, e serve como um template robusto para pipelines futuros, com foco em compliance e governança.II. 🏛️ Arquitetura da Solução e Arquitetura TécnicaVisão Geral da ArquiteturaA arquitetura foi desenhada para ser totalmente contida no ambiente local, utilizando ferramentas open-source que simulam um ecossistema de dados corporativo moderno e robusto.graph TD
    subgraph "🌐 Fontes de Dados"
        API1[API Banco Central<br/>IPCA]
        API2[API OpenWeather<br/>Dados Climáticos]
        DS1[Dataset Olist<br/>E-commerce]
    end
    
    subgraph "🎯 Orquestração"
        AF[Apache Airflow<br/>DAGs Modularizadas]
    end

    subgraph "🔐 Camada de Segurança"
        VAULT[Security Vault<br/>AES-128 Encryption]
        AUDIT[Audit Logger<br/>Rastreabilidade]
        CONN[Secure Connection Pool<br/>Runtime Credentials]
    end
    
    subgraph "🗄️ Data Lake (MinIO)"
        BRONZE[Bronze Layer<br/>Raw Data]
        SILVER[Silver Layer<br/>Cleansed + PII Masked]
        GOLD[Gold Layer<br/>Aggregated]
        COLD[Cold Storage Layer<br/>Archived Data]
    end
    
    subgraph "⚡ Processamento & Qualidade"
        SPARK[Apache Spark<br/>Distributed Processing]
        GE[Great Expectations<br/>Quality Gates]
    end
    
    subgraph "🏛️ Data Warehouse"
        PG[(PostgreSQL<br/>Star Schema)]
    end
    
    subgraph "📊 Visualização & Monitoramento"
        ST[Streamlit Dashboard<br/>Interactive Analytics]
        GF[Grafana<br/>Monitoring & Alerts]
    end
    
    API1 --> AF
    API2 --> AF
    DS1 --> AF

    AF --> VAULT
    AF --> AUDIT
    AF --> CONN

    AF --> BRONZE
    BRONZE --> SPARK
    SPARK --> SILVER
    SILVER --> SPARK
    SPARK --> GOLD
    GOLD --> GE
    GE --> PG
    PG --> ST
    PG --> GF
    
    VAULT --> CONN
    CONN --> SPARK
    CONN --> PG

    AUDIT -.->|Logs| AF
    AF -.->|Health Checks| PG
    AF -.->|Health Checks| MinIO_Container
    AF -.->|Health Checks| Redis_Container
    MinIO_Container[MinIO Service] --> BRONZE
    MinIO_Container --> SILVER
    MinIO_Container --> GOLD
    MinIO_Container --> COLD

    BRONZE --> COLD[Movimentação de Lifecycle]
Detalhamento dos ComponentesA solução é composta por um conjunto de serviços orquestrados via Docker Compose, cada um com uma responsabilidade bem definida:Apache Airflow: O coração da orquestração. Gerencia o agendamento e a execução de todas as DAGs, que representam os pipelines de dados.PostgreSQL: Atua como o banco de dados de metadados do Airflow e como o Data Warehouse/Data Mart principal, hospedando o modelo Star Schema.MinIO: Simula um Object Storage compatível com S3 (Data Lake), onde os dados são armazenados nas camadas Bronze, Silver e Gold, além de uma camada de Cold Storage.Redis: Utilizado como broker de mensagens para o Celery Executor do Airflow, permitindo a execução distribuída e escalável de tarefas.Apache Spark: Motor de processamento distribuído, ideal para transformações e agregações em larga escala, especialmente na transição entre as camadas do Data Lake.Streamlit: Uma interface simples e poderosa para construir dashboards interativos de Business Intelligence, conectando-se aos dados processados no PostgreSQL.Grafana: Ferramenta para monitoramento e visualização de métricas operacionais, podendo ser integrada para acompanhar a saúde dos serviços e do pipeline.🔐 Framework de Segurança (Customizado - plugins/security_system/)Este é o principal diferencial do projeto, demonstrando um profundo conhecimento em segurança de dados e engenharia de software. Ele garante a integridade, confidencialidade e rastreabilidade dos dados em todo o pipeline:Security Vault (VaultManager em plugins/security_system/vault_manager_helper.py): Um cofre digital baseado em arquivo JSON, criptografado com Fernet (AES-128 GCM). Armazena credenciais sensíveis (APIs externas, MinIO, PostgreSQL) de forma centralizada e segura, recuperando-as em tempo de execução.Diferencial: Separação clara de responsabilidades da AirflowSecurityManager (integração UI do Airflow) e VaultManager (gestão real de segredos).Audit Logger (AuditLogger em plugins/security_system/audit.py): Um sistema de auditoria abrangente que registra todas as operações críticas do pipeline (acessos a segredos, uploads, transformações, validações, incidentes de segurança) em um formato estruturado para conformidade (LGPD, SOX) e rastreabilidade.Secure Connection Pool (SecureConnectionPool em plugins/security_system/secure_connection_pool.py): Um gerenciador que facilita a obtenção segura de clientes para serviços externos (MinIO, PostgreSQL), buscando as credenciais do Vault e garantindo que nunca sejam hardcoded.Exceções Customizadas (plugins/security_system/exceptions.py): Uma hierarquia de exceções específicas para o sistema de segurança, permitindo tratamento de erros granular e informativo.Rotação de Chaves (plugins/security_system/key_rotation.py): Módulo que simula a rotação segura de chaves criptográficas, armazenando versões antigas para descriptografia de dados legados.🗄️ Data Lake com Arquitetura Medallion (MinIO)Implementação de um Data Lake multicamadas para governança e qualidade de dados:CamadaDescriçãoCaracterísticasBronzeDados Brutos e Imutáveis: Ingestão direta de fontes.Raw data, schema-on-read, auditável, imutável.SilverDados Limpos e Padronizados: PII mascarado, validado.LGPD compliant, deduplicado, pronto para análise exploratória.GoldDados Agregados e Otimizados: Para consumo de BI.Regras de negócio aplicadas, sumarizado, alta performance.Cold StorageDados Arquivados/Inativos: Para retenção de longo prazo.Otimização de custos, acesso menos frequente.⚡ Processamento Distribuído (Apache Spark)Utilizado para transformações complexas e em larga escala:Processamento na Transição Bronze -> Silver -> Gold: Executa operações de limpeza, normalização, enriquecimento e agregação.Injeção Segura de Credenciais: Credenciais para MinIO/S3 são passadas de forma segura ao Spark em tempo de execução via variáveis de ambiente, prevenindo o hardcoding.Persistência em Parquet: Formato colunar otimizado para Big Data, ideal para eficiência de leitura e escrita.📊 Qualidade de Dados (Great Expectations)Implementação de Quality Gates para garantir a confiança nos dados:Validação em Etapas Críticas: Aplicação de suítes de expectativas em datasets (ex: após consolidação ou antes da carga no Data Warehouse).Fail-Fast Strategy: Pipelines são interrompidos automaticamente se as expectativas críticas de qualidade não forem atendidas, prevenindo a propagação de dados ruins.Rastreabilidade: Os resultados das validações são logados e auditados.III. ⚙️ Explicação sobre o Case DesenvolvidoO projeto demonstra um pipeline de dados completo e seguro, orquestrado por uma série de DAGs no Apache Airflow. Cada DAG possui uma responsabilidade clara e se integra nativamente com o framework de segurança customizado desenvolvido.Fluxo de Trabalho do Pipelineflowchart TD
    subgraph "Orquestração Airflow"
        A[1. Coleta Segura<br/>(IPCA, Clima, Olist)] --> B[2. Consolidação e Mascaramento PII<br/>(Olist)]
        B --> C[3. Processamento Spark<br/>(Silver -> Gold)]
        C --> D[4. Validação Qualidade<br/>(Great Expectations)]
        D --> E[5. Carga no Data Mart<br/>(Star Schema - PostgreSQL)]
        E --> F[6. Gerenciamento de Lifecycle<br/>(MinIO Cold Storage)]
    end

    F --> G[7. Dashboard de BI<br/>(Streamlit)]
    E --> H[8. Monitoramento Operacional<br/>(Grafana)]

    subgraph "Camada de Segurança Integrada"
        Vault_Core[Security Vault<br/>(VaultManager)]
        Audit_Core[Audit Logger]
    end

    A -- Credenciais de API --> Vault_Core
    Vault_Core --> B
    B -- Dados Mascarados --> C
    C -- Dados Processados --> D
    D -- Dados Validados --> E
    E -- Dados Carregados --> F
    
    A, B, C, D, E, F -.-> Audit_Core[Logs de Auditoria]
    A, B, C, D, E, F -.-> Airflow_UI[Monitoramento Airflow UI]
🔄 Etapas Detalhadas do PipelineColeta Segura (dag_01_coleta_segura_v1, dag_coleta_dados_externos_enterprise_v1)Objetivo: Ingestão inicial de dados brutos de fontes externas.Fontes: APIs externas (Banco Central para IPCA, OpenWeatherMap para clima) e datasets locais (Olist).Segurança: Credenciais (ex: API Key do OpenWeatherMap) são obtidas do Security Vault em tempo de execução.Destino: Dados brutos persistidos na camada Bronze do MinIO.Diferencial: Demonstra o uso de PythonOperator para ingestão, Requests para APIs, e integração com o framework de segurança.Exemplo de Log de Sucesso (Coleta e Validação):Consolidação e Mascaramento PII (dag_03_consolidacao_e_mascaramento_v1)Objetivo: Limpar, unificar e proteger dados sensíveis.Processo: Dados lidos da camada Bronze e unificados via pandas.merge.Segurança PII: Aplica mascaramento de informações pessoalmente identificáveis (PII) como customer_city (estático) e customer_state (hash), garantindo LGPD/GDPR compliance.Destino: Dados limpos e mascarados persistidos na camada Silver do MinIO.Diferencial: Implementação prática de técnicas de Data Privacy (DataProtection module) e auditoria detalhada das transformações.Exemplo de Gráfico de Duração (Consolidação e Mascaramento):Processamento em Larga Escala (dag_04_processamento_spark_seguro_v1)Objetivo: Transformar dados da camada Silver em dados agregados e otimizados para BI.Processo: Um job Spark é submetido pelo Airflow, processando dados do MinIO/S3.Segurança: Credenciais para acesso ao MinIO/S3 (camadas Silver/Gold) são injetadas de forma segura no ambiente do Spark em tempo de execução, diretamente do Security Vault.Destino: Geração da camada Gold no MinIO, com dados sumarizados e prontos para consumo analítico (ex: vendas por categoria).Diferencial: Demonstra o uso de BashOperator para spark-submit, passando credenciais de forma segura via ambiente, e configurações robustas de conectividade S3A.Exemplo de Gráfico de Duração (Processamento Spark):Validação de Qualidade (dag_05_validacao_segura_v1, scripts/examples/19-validacao_great_expectations_avancada.py)Objetivo: Assegurar a integridade e consistência dos dados antes de seu consumo final.Processo: Aplicação de uma suíte de expectativas de qualidade (Great Expectations) nos dados da camada Gold.Qualidade: Atua como um "Quality Gate", falhando a DAG se os dados não atenderem aos critérios mínimos.Auditoria: Os resultados das validações são registrados detalhadamente no Audit Logger.Diferencial: Uso de uma ferramenta de ponta para qualidade de dados, integrada ao fluxo de orquestração e auditoria.Carga no Data Mart (dag_06_carrega_star_schema_segura_enterprise_v1, dag_minio_para_postgresql_enterprise_v1)Objetivo: Carregar dados da camada Gold do Data Lake para o Data Mart relacional.Modelo: População de um modelo dimensional Star Schema (dimensões de cliente e produto, e tabela de fato de vendas) no PostgreSQL.Transacional: As cargas são realizadas dentro de transações ACID (Atomicity, Consistency, Isolation, Durability) para garantir a integridade dos dados.Segurança: Conexão segura ao PostgreSQL utilizando credenciais obtidas do Security Vault.Diferencial: Demonstra ETL de Data Lake para Data Mart, transações ACID, e uso de SecureConnectionPool para gerenciar conexões com credenciais seguras.Exemplo de Grafo da DAG (MinIO para PostgreSQL):Exemplo de Duracao de Task (Carga Star Schema):Gerenciamento de Lifecycle (dag_gerenciamento_lifecycle_enterprise_v1)Objetivo: Otimizar custos de armazenamento e gerenciar a retenção de dados.Processo: Move automaticamente arquivos antigos da camada Bronze para uma camada de Cold Storage (simulada no MinIO).Segurança: Operações de movimentação de dados são autenticadas via Security Vault e auditadas.Diferencial: Abordagem prática para governança de dados e otimização de infraestrutura.Exemplo de Logs (Gerenciamento de Lifecycle):Visualização de InsightsDashboard Streamlit: Conecta-se ao PostgreSQL para exibir KPIs e análises de vendas, permitindo a exploração de dados por stakeholders.Grafana: Pode ser integrado para monitoramento de métricas operacionais e alertas.Fontes de Dados IntegradasFonteTipoDescriçãoSimulação de VolumeBanco CentralAPI RESTIndicadores econômicos (IPCA)Pequeno VolumeOpenWeatherAPI RESTDados meteorológicos por região (temperatura, etc.)Pequeno VolumeOlistDataset CSVDados reais de e-commerce brasileiro (público)Grande VolumeIV. 🧠 Melhorias e Considerações FinaisDecisões de Projeto e Práticas de ProduçãoÉ fundamental que as decisões de projeto reflitam a consciência sobre as diferenças entre um ambiente de demonstração/desenvolvimento e um sistema produtivo em larga escala.Modularidade e Reuso de Componentes de Segurança: O framework de segurança (security_system nos plugins) foi projetado para ser um conjunto de módulos reutilizáveis.VaultManager vs. AirflowSecurityManager: Mantivemos a AirflowSecurityManager (plugins/security_system/vault.py) focada em estender a segurança da UI do Airflow. A lógica de gestão real de segredos (criptografia, leitura/escrita no vault.json) foi delegada ao VaultManager (plugins/security_system/vault_manager_helper.py). Essa separação é crucial para clareza e manutenção em um ambiente enterprise.Reuso: Em vez de replicar a lógica de os.getenv('SECRET_KEY') e instanciação do Vault em cada DAG/script, o VaultManager encapsula isso, e as DAGs/scripts apenas o instanciam e o utilizam.Configuração de Credenciais:No Case (Demo): Para fins de reprodutibilidade e simplicidade da demonstração, as credenciais para serviços como MinIO e PostgreSQL são lidas de variáveis de ambiente do .env (populadas via docker-compose.yml) e então inseridas no Security Vault via scripts/setup_vault_secrets.py.Em Produção: Em um ambiente real, a SECURITY_VAULT_SECRET_KEY viria de um serviço de gerenciamento de segredos da nuvem (ex: AWS Secrets Manager, HashiCorp Vault Server) ou de um sistema de orquestração de segredos, nunca de um arquivo .env versionado ou acessível diretamente. O setup_vault_secrets.py seria parte de um processo de deploy seguro.Automação da Refatoração (refinar_projeto.py):No Case: Um script Python foi desenvolvido para automatizar a adaptação de caminhos hardcoded e a inserção de blocos de validação de segurança em outros arquivos Python.Valor Demonstrado: Isso mostra uma mentalidade de engenharia que busca resolver problemas de forma programática, aumenta a produtividade e reduz erros, uma prática essencial em equipes de alta performance.🚀 Melhorias Propostas para Próximas IteraçõesPara evoluir este projeto para um nível de produção ainda mais avançado e escalável, as seguintes melhorias são propostas:Infraestrutura como Código (IaC)Terraform: Para automatização completa da provisão de recursos em nuvem (ex: EC2, RDS, S3, EMR, MWAA).Ansible: Para configuração e automação de deploy de aplicações nos servidores.CI/CD para PipelinesGitHub Actions / GitLab CI: Para automação de testes unitários, de integração e end-to-end.Deploy Automatizado: Novas versões de DAGs e códigos seriam implantadas automaticamente em ambientes de teste e produção.Testes de Integração Automatizados: Cenários de teste que validam o fluxo de dados entre múltiplos componentes.Catálogo de DadosIntegração com Apache Atlas ou Amundsen: Para documentação automática de metadados, linhagem de dados (data lineage) e descoberta de dados.Observabilidade AvançadaMétricas Customizadas com Prometheus / Grafana: Para monitoramento granular de performance do pipeline e recursos da infraestrutura.Alertas Proativos: Configuração de alertas em caso de anomalias ou falhas críticas.Distributed Tracing com Jaeger / OpenTelemetry: Para depuração de pipelines complexos em ambientes distribuídos.📈 Escalabilidade e Performance (Projeções)AspectoImplementação Atual (Local Docker)Melhoria Proposta (Cloud / Otimizações)Volume~100k registros OlistPetabytes (particionamento horizontal, sharding)Latência< 30 segundos (pipeline end-to-end)< 10 segundos (para ingestão, com Kafka/Redis)Concorrência3 DAGs paralelas (com CeleryExecutor)10+ DAGs e tasks simultâneas (Kubernetes, Fargate)MonitoramentoLogs básicos, Airflow UIAPM completo, dashboards Grafana, alertas SMS/emailPersistênciaVolumes Docker, MinIO localS3/GCS/Azure Blob Storage, Databases gerenciados🏆 Considerações FinaisEste case entrega uma solução de dados enterprise-grade, segura, confiável, escalável e totalmente reprodutível. As decisões de projeto, como a criação de um framework de segurança customizado e a automação de tarefas de desenvolvimento/deploy, demonstram um domínio de conceitos que vão muito além do básico, focando nos desafios reais de um ambiente corporativo moderno.A arquitetura implementada é production-ready em seus princípios e pode ser facilmente adaptada e estendida para ambientes de nuvem em grande escala, mantendo os mesmos pilares de segurança, qualidade e governança.V. 🛠️ Reprodutibilidade da ArquiteturaEste projeto foi construído com foco na reprodutibilidade e portabilidade, utilizando Docker para isolar o ambiente. As instruções a seguir detalham como configurar e executar o projeto em qualquer máquina (macOS, Linux, Windows) com Docker instalado.Pré-requisitos do SistemaSoftwares NecessáriosPython 3.8+ (com pip)Git (versão 2.25+)Docker Desktop (para Windows/macOS) ou Docker Engine (para Linux)Docker Compose (geralmente incluído com o Docker Desktop/Engine)Apache Spark 3.5+: Embora as DAGs rodem o Spark via spark-submit dentro do contêiner Airflow, ter o Spark instalado localmente pode ser útil para depuração ou execução de scripts Spark standalone.macOS: brew install apache-sparkLinux/Windows: Download oficialRecursos de Hardware MínimosRAM: 8GB (recomendado 16GB para performance ideal com Spark e Airflow)Armazenamento: 10GB livresCPU: 4 cores (recomendado 8 cores)🚀 Instalação e ExecuçãoSiga os passos rigorosamente para garantir a correta inicialização do ambiente.Passo 1: Clonagem do RepositórioAbra seu terminal e execute:# Clone o repositório
git clone https://github.com/felipesbonatti/case-data-master-engenharia-de-dados.git
cd case-data-master-engenharia-de-dados

# Verifique a estrutura do projeto
# (O comando 'tree' pode não estar disponível no Windows por padrão, use 'dir /s /b' ou explore manualmente)
tree -L 2
Passo 2: Configuração do AmbienteEste passo é CRÍTICO para a segurança do Vault e o funcionamento do pipeline.# Crie o arquivo de ambiente (.env) a partir do template
cp .env.example .env

# Gere uma chave de criptografia segura para o Vault e adicione ao .env
# Esta chave é fundamental para criptografar/decriptar seus segredos no Vault.
python -c "from cryptography.fernet import Fernet; print('SECURITY_VAULT_SECRET_KEY=' + Fernet.generate_key().decode())" >> .env

# Abra o arquivo .env e configure suas API keys reais e senhas fortes.
# EXEMPLO DE .env (SUBSTITUA OS VALORES PADRÃO POR SEUS VALORES REAIS E SEGUROS):
# SECURITY_VAULT_SECRET_KEY=SUA_CHAVE_FERNET_GERADA_AQUI
# OPENWEATHER_API_KEY=SUA_CHAVE_DA_OPENWEATHERMAP_AQUI
# POSTGRES_USER=airflow_user_real
# POSTGRES_PASSWORD=sua_senha_segura_postgres
# MINIO_ROOT_USER=minio_admin_real
# MINIO_ROOT_PASSWORD=sua_senha_segura_minio
# ... (demais variaveis)
Atenção: Mantenha o arquivo .env seguro e não o adicione ao controle de versão público. Ele já está incluído no .gitignore para sua segurança.Passo 3: Adaptação do Projeto (Portabilidade)Este script ajusta caminhos de arquivo internos para garantir que o projeto funcione em qualquer sistema operacional (Linux, macOS, Windows).# Execute o script de configuração (CRUCIAL para portabilidade)
python configure.py

# Este script automatiza a adaptação de caminhos para seu ambiente local,
# garantindo que o projeto funcione corretamente independentemente do seu sistema operacional.
# Ele também cria um backup automático antes de fazer as modificações e pode realizar rollback em caso de falha.
Passo 4: Instalação de Dependências# Crie um ambiente virtual (recomendado para isolar as dependências do projeto)
python -m venv venv

# Ative o ambiente virtual
# Para Linux/macOS:
source venv/bin/activate
# Para Windows PowerShell:
# venv\Scripts\activate

# Instale todas as dependências Python listadas no requirements.txt
pip install -r requirements.txt

# Verifique se as principais bibliotecas foram instaladas
pip list | grep -E "(airflow|pyspark|pandas|great-expectations|streamlit|minio|psycopg2|sqlalchemy|cryptography)"
Passo 5: Inicialização da Infraestrutura DockerEste passo levanta todos os serviços essenciais (PostgreSQL, MinIO, Redis, Airflow Webserver, Airflow Scheduler).# O comando a seguir faz uma limpeza profunda e reconstrói as imagens para garantir um ambiente limpo.
# Isso é crucial para que todas as configurações e dependências (JARs do Spark) sejam aplicadas.
docker-compose down -v --rmi all
docker system prune -a --volumes -f
docker-compose up -d --build

# Verifique se os serviços Docker estão rodando e saudáveis
docker-compose ps

# Esperado (Status 'healthy' ou 'running'):
# - minio_object_storage (porta 9000/9001)
# - postgres_data_warehouse (porta 5432)
# - redis_cache_layer (porta 6379)
# - airflow_webserver (porta 8080)
# - airflow_scheduler
Passo 6: Configuração do Security VaultEste passo popula o Vault de Segurança com as credenciais para MinIO, PostgreSQL e APIs externas, utilizando a SECURITY_VAULT_SECRET_KEY do seu .env.# Acesse o shell do contêiner do scheduler (onde o Python e os plugins estão disponíveis)
docker-compose exec airflow-scheduler bash

# Dentro do contêiner, exporte a SECURITY_VAULT_SECRET_KEY do seu .env
# Isso é necessário para que o script setup_vault_secrets.py possa usá-la.
export SECURITY_VAULT_SECRET_KEY=$(grep 'SECURITY_VAULT_SECRET_KEY=' /opt/airflow/.env | cut -d '=' -f2)

# Popule o vault com as credenciais (MinIO, PostgreSQL, OpenWeatherMap, Masking Key)
# Este script lê as variáveis de ambiente e as armazena criptografadas no vault.json.
python /opt/airflow/scripts/setup_vault_secrets.py

# Saia do shell do contêiner
exit

# Opcional: Teste a conectividade dos serviços (requer que o Vault tenha sido populado)
python scripts/health_check.py

# Saída esperada:
# ✅ PostgreSQL: Connected
# ✅ MinIO: Connected  
# ✅ Redis: Connected
# ✅ Security Vault: Initialized (se o test_connections.py verificar isso)
Passo 7: Inicialização do AirflowEste passo inicia os componentes internos do Airflow (banco de dados de metadados, usuário admin).# Configure as variáveis de ambiente (se não estiver usando um entrypoint que já faz isso)
export AIRFLOW_HOME=$(pwd)
export AIRFLOW__CORE__DAGS_FOLDER=${AIRFLOW_HOME}/dags
export AIRFLOW__CORE__PLUGINS_FOLDER=${AIRFLOW_HOME}/plugins
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Inicialize/atualize o banco de dados de metadados do Airflow
airflow db upgrade

# Crie o usuário administrador padrão para a UI do Airflow (admin/admin)
# O `|| true` evita que o comando falhe se o usuário já existir.
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com || true

# Os serviços `airflow-webserver` e `airflow-scheduler` já estão rodando
# (iniciados no Passo 5 via docker-compose up -d)
# Não é necessário rodar `airflow scheduler` ou `airflow webserver` aqui novamente.
Passo 8: Execução do Dashboard# Abra um NOVO terminal ou aba de terminal e ative o ambiente virtual (se nao ativado)
# source venv/bin/activate # Linux/macOS
# venv\Scripts\activate     # Windows

# Execute o dashboard Streamlit
streamlit run dashboard/app.py --server.port 8501

# Acesse o dashboard no seu navegador: http://localhost:8501

# Opcional: Execute o Grafana (se configurado no docker-compose.yml e descomentado)
# Acesse Grafana no seu navegador: http://localhost:3000 (admin/admin)
🔍 Verificação da InstalaçãoApós seguir os passos, verifique a saúde do ambiente:URLs de AcessoAirflow UI: http://localhost:8080 (Usuário: admin, Senha: admin)Streamlit Dashboard: http://localhost:8501MinIO Console: http://localhost:9001 (Usuário: minioadmin, Senha: minio_secure_2024 - ou a senha que você configurou no .env)Grafana: http://localhost:3000 (Usuário: admin, Senha: admin - se configurado)Testes de ConectividadeExecute no terminal na raiz do projeto (com o ambiente virtual ativado):# Teste todas as conexões
python scripts/health_check.py

# Saída esperada:
# ✅ PostgreSQL: Connected
# ✅ MinIO: Connected  
# ✅ Redis: Connected
# ✅ Security Vault: Initialized (se o test_connections.py verificar isso)
Execução do PipelineApós verificar as URLs e conectividade, você pode ativar e monitorar suas DAGs na interface do Airflow.Acesse a Airflow UI (http://localhost:8080).Ative as DAGs clicando no botão "toggle" (interruptor) ao lado do nome de cada DAG.Dispare as DAGs clicando no ícone de "Play" ao lado do nome da DAG para iniciar uma execução manual.Sugestão de Ordem de Execução (para gerar dados para as próximas etapas):dag_coleta_segura_v1dag_03_consolidacao_e_mascaramento_v1dag_04_processamento_spark_seguro_v1dag_05_validacao_segura_v1dag_06_carrega_star_schema_segura_enterprise_v1dag_upload_bronze_minio_enterprise_v1 (se os dados locais de Olist não estiverem no MinIO ainda)dag_upload_silver_minio_enterprise_v1dag_gerenciamento_lifecycle_enterprise_v1Monitore a execução pela interface do Airflow (visualizações Graph, Gantt, Logs). Você também pode usar a CLI (no terminal com ambiente virtual ativado):# Monitore o status de uma DAG (exemplo)
airflow dags state dag_04_processamento_spark_seguro_v1
🐛 Solução de ProblemasProblemas ComunsProblemaSoluçãoPorta já em usoIdentifique o processo usando a porta (netstat -tlnp | grep :<PORTA>) e finalize-o, ou altere a porta no docker-compose.yml e airflow.cfg.Erro de permissão DockerAdicione seu usuário ao grupo docker (sudo usermod -aG docker $USER) e reinicie o terminal ou a sessão (logout/login). No Windows/macOS, verifique se o Docker Desktop está rodando.spark-submit: command not foundVerifique o Dockerfile e airflow.cfg para a configuração correta do PATH. A solução final implementada no projeto usa export PATH="/home/airflow/.local/bin:${PATH}" no bash_command da DAG para garantir a detecção do spark-submit dentro do contêiner Airflow.Airflow não inicia / DAGs 'Broken'Verifique os logs do contêiner airflow-webserver ou airflow-scheduler (docker-compose logs airflow-webserver). As mensagens de erro indicarão o problema (ex: SyntaxError em DAGs, problemas de conexão com DB/Redis, variáveis de ambiente ausentes).Credenciais não encontradas no VaultCertifique-se de que o Passo 6: Configuração do Security Vault foi executado corretamente, e que a SECURITY_VAULT_SECRET_KEY no seu .env é a mesma usada para criptografar o vault.json.Logs e Debugging# Logs de um serviço Docker Compose (exemplo para o scheduler)
docker-compose logs -f airflow-scheduler

# Logs do Docker Compose de todos os serviços
docker-compose logs -f

# Logs de tarefas do Airflow (acessíveis via UI do Airflow ou diretamente no host)
tail -f logs/dag_id=<NOME_DA_DAG>/<run_id>/<task_id>/*.log

# Teste individual de componentes (no terminal com ambiente virtual ativado)
python scripts/health_check.py
# Para verificar acesso ao Vault:
# python -c "from plugins.security_system.vault_manager_helper import VaultManager; import os; vm = VaultManager(vault_path=os.getenv('AIRFLOW_HOME','/opt/airflow')+'/plugins/security_system/vault.json', secret_key=os.getenv('SECURITY_VAULT_SECRET_KEY')); print(vm.get_secret('minio_local_credentials'))"
📦 Estrutura do Projetopipeline-dados-seguro/
├── 📁 dags/                  # DAGs do Apache Airflow (.py)
│   ├── dag_01_coleta_segura_v1.py
│   ├── dag_03_consolidacao_e_mascaramento_v1.py
│   ├── dag_04_processamento_spark_seguro_v1.py
│   ├── dag_05_validacao_segura_v1.py
│   ├── dag_06_carrega_star_schema_segura_enterprise_v1.py
│   ├── dag_coleta_dados_externos_enterprise_v1.py
│   ├── dag_consolida_olist_enterprise_v1.py
│   ├── dag_gerenciamento_lifecycle_enterprise_v1.py
│   ├── dag_minio_para_postgresql_enterprise_v1.py
│   ├── dag_upload_bronze_minio_enterprise_v1.py
│   └── dag_upload_silver_minio_enterprise_v1.py
├── 📁 plugins/               # Plugins customizados do Airflow
│   └── security_system/     # Framework de segurança customizado
│       ├── audit.py         # Audit Logger
│       ├── connections.py   # Secure Connection Pool
│       ├── data_protection.py # Mascaramento de Dados
│       ├── exceptions.py    # Exceções customizadas
│       ├── key_rotation.py  # Rotação de Chaves
│       ├── monitoring.py    # Monitoramento de Segurança
│       ├── vault.py         # Airflow Security Manager (FAB override)
│       ├── vault_manager_helper.py # Vault Manager (lógica de segredos)
│       └── verify_minio_upload.py # Utilitário de Verificação MinIO
├── 📁 scripts/               # Scripts utilitários e de configuração
│   ├── configure.py         # Script de configuração automática de paths
│   ├── setup_vault_secrets.py # Script de setup de segredos no Vault
│   ├── health_check.py      # Script de teste de conectividade
│   └── examples/            # Scripts Spark/Pandas/GE de exemplo
│       ├── 01-coleta_ipca.py
│       ├── 02-coleta_clima.py
│       ├── 07-validacao_olist.py
│       ├── 09-escrever_avro.py
│       ├── 10-ler_avro.py
│       ├── 12-processa_vendas.py # Job PySpark
│       ├── 15-processador_stream_vendas.py # Processador de Stream
│       ├── 18-popular_star_schema.py # População Star Schema
│       ├── 19-validacao_great_expectations_avancada.py
│       ├── 21-valida_vendas.py # Validação no Data Lake
│       └── 23-upload_criptografado_sse.py # Upload SSE
├── 📁 dashboard/             # Dashboard Streamlit
│   └── app.py
├── 📁 data/                  # Dados de entrada e saída (mapeado como volume)
│   ├── olist/               # Datasets Olist e dados consolidados
│   └── security_vault.db    # Banco de dados SQLite do Vault (criptografado)
├── 📁 logs/                  # Logs do Airflow e de Auditoria (mapeado como volume)
├── 📁 docs/                  # Documentação adicional e imagens
│   └── images/              # Imagens para o README e apresentacao
├── 📁 init-scripts/          # Scripts de inicializacao de containers
│   └── entrypoint.sh        # Script de entrada customizado para Docker
├── 🐳 docker-compose.yml     # Infraestrutura
├── 📋 requirements.txt      # Dependencias Python do projeto
├── ⚙️ .env.example          # Template de variaveis de ambiente
└── 📜 LICENSE               # Licenca do projeto (ex: MIT)
✅ Checklist de Validação para a BancaEste checklist pode ser usado pela banca para validar a solução:[ ] O repositório Git é público e acessível.[ ] O arquivo README.md está presente e bem formatado.[ ] Todos os pré-requisitos de software e hardware estão claros.[ ] O script configure.py foi executado para adaptar os caminhos.[ ] Os serviços Docker (minio, postgres, redis, airflow-webserver, airflow-scheduler) estão rodando e saudáveis (docker-compose ps).[ ] O Security Vault foi populado com sucesso (python scripts/setup_vault_secrets.py executado).[ ] A Airflow UI está acessível em http://localhost:8080.[ ] As DAGs aparecem na interface do Airflow (não como 'Broken DAG').[ ] Pelo menos uma DAG (ex: dag_04_processamento_spark_seguro_v1) foi executada com sucesso.[ ] Os dados processados aparecem no MinIO (verificar em http://localhost:9001).[ ] O Dashboard Streamlit está funcionando (http://localhost:8501).[ ] Os logs de auditoria (logs/security_audit/) estão sendo gerados.VI. 📊 Resultados e EvidênciasEste projeto não é apenas um conjunto de scripts; é um ecossistema de dados funcional e seguro, validado por evidências concretas.🗄️ Arquitetura de Data Lake em Ação (MinIO)Nossa implementação do Data Lake em MinIO segue a arquitetura Medallion, garantindo organização, qualidade e governança dos dados em diferentes estágios de processamento.Visão Geral dos Buckets: Os buckets b-prd.sand-ux-indc-brasil (Bronze), s-prd.sand-ux-indc-brasil (Silver), g-prd.sand-ux-indcs (Gold) e glacier-mock (Cold Storage) demonstram a separação de camadas.Conteúdo da Camada Bronze: A camada Bronze armazena os dados brutos e imutáveis, como os datasets da Olist.Conteúdo da Camada Silver: A camada Silver contém os dados já limpos, consolidados e com PII mascarado, prontos para análises ou promoção.📊 Qualidade de Dados Garantida (Great Expectations)A implementação de Quality Gates com Great Expectations assegura que apenas dados de alta qualidade progridam no pipeline, prevenindo problemas a jusante.Log de Sucesso da Validação: A DAG de validação com Great Expectations (dag_05_validacao_segura_v1) mostra o sucesso na aplicação das expectativas de qualidade.⚡ Pipeline em Execução e Métricas de Performance (Airflow UI)As DAGs no Airflow demonstram a orquestração robusta, o paralelismo e a eficiência do pipeline.Grafo da DAG de MinIO para PostgreSQL: Demonstra a orquestração do processo de ETL, com todas as tarefas concluídas com sucesso.Duração da Tarefa de Processamento Spark: Evidência da execução do job Spark, fundamental para as transformações em larga escala.Duração da Tarefa de Consolidação e Mascaramento: Mostra a eficiência da etapa de processamento e proteção de dados.Duração da Tarefa de Carga Star Schema: Ilustra o tempo necessário para popular o Data Mart.Duração das Tarefas de Coleta e Validação (IPCA/Clima): Demonstra a execução de múltiplos pipelines de ingestão e qualidade.Logs do Gerenciamento de Lifecycle: Confirma que a lógica de movimentação de dados (Hot para Cold Storage) está operando.🔐 Segurança Implementada (Framework Customizado)O framework de segurança é um dos maiores destaques, garantindo que o pipeline é robusto e está em conformidade.Credenciais Criptografadas: As credenciais para todos os serviços (MinIO, PostgreSQL, APIs externas) são armazenadas criptografadas no Security Vault (vault.json) e recuperadas em tempo de execução, garantindo que nunca estejam expostas no código ou em logs.Auditoria Completa: Cada operação de segurança e acesso a dados é registrada detalhadamente pelo Audit Logger, fornecendo um rastro para conformidade (LGPD, SOX) e investigação de incidentes.Mascaramento de PII: Demonstra o uso de técnicas como hash e mascaramento estático para proteger informações pessoalmente identificáveis.Criptografia Server-Side (SSE): Capacidade de fazer upload de arquivos para o MinIO com criptografia SSE-S3, protegendo os dados em repouso.IV. 🧠 Melhorias e Considerações FinaisDecisões de Projeto e Práticas de ProduçãoÉ fundamental que as decisões de projeto reflitam a consciência sobre as diferenças entre um ambiente de demonstração/desenvolvimento e um sistema produtivo em larga escala.Modularidade e Reuso de Componentes de Segurança: O framework de segurança (security_system nos plugins) foi projetado para ser um conjunto de módulos reutilizáveis.VaultManager vs. AirflowSecurityManager: Mantivemos a AirflowSecurityManager (plugins/security_system/vault.py) focada em estender a segurança da UI do Airflow. A lógica de gestão real de segredos (criptografia, leitura/escrita no vault.json) foi delegada ao VaultManager (plugins/security_system/vault_manager_helper.py). Essa separação é crucial para clareza e manutenção em um ambiente enterprise.Reuso: Em vez de replicar a lógica de os.getenv('SECRET_KEY') e instanciação do Vault em cada DAG/script, o VaultManager encapsula isso, e as DAGs/scripts apenas o instanciam e o utilizam.Configuração de Credenciais:No Case (Demo): Para fins de reprodutibilidade e simplicidade da demonstração, as credenciais para serviços como MinIO e PostgreSQL são lidas de variáveis de ambiente do .env (populadas via docker-compose.yml) e então inseridas no Security Vault via scripts/setup_vault_secrets.py.Em Produção: Em um ambiente real, a SECURITY_VAULT_SECRET_KEY viria de um serviço de gerenciamento de segredos da nuvem (ex: AWS Secrets Manager, HashiCorp Vault Server) ou de um sistema de orquestração de segredos, nunca de um arquivo .env versionado ou acessível diretamente. O setup_vault_secrets.py seria parte de um processo de deploy seguro.Automação da Refatoração (refinar_projeto.py):No Case: Um script Python foi desenvolvido para automatizar a adaptação de caminhos hardcoded e a inserção de blocos de validação de segurança em outros arquivos Python.Valor Demonstrado: Isso mostra uma mentalidade de engenharia que busca resolver problemas de forma programática, aumenta a produtividade e reduz erros, uma prática essencial em equipes de alta performance.🚀 Melhorias Propostas para Próximas IteraçõesPara evoluir este projeto para um nível de produção ainda mais avançado e escalável, as seguintes melhorias são propostas:Infraestrutura como Código (IaC)Terraform: Para automatização completa da provisão de recursos em nuvem (ex: EC2, RDS, S3, EMR, MWAA).Ansible: Para configuração e automação de deploy de aplicações nos servidores.CI/CD para PipelinesGitHub Actions / GitLab CI: Para automação de testes unitários, de integração e end-to-end.Deploy Automatizado: Novas versões de DAGs e códigos seriam implantadas automaticamente em ambientes de teste e produção.Testes de Integração Automatizados: Cenários de teste que validam o fluxo de dados entre múltiplos componentes.Catálogo de DadosIntegração com Apache Atlas ou Amundsen: Para documentação automática de metadados, linhagem de dados (data lineage) e descoberta de dados.Observabilidade AvançadaMétricas Customizadas com Prometheus / Grafana: Para monitoramento granular de performance do pipeline e recursos da infraestrutura.Alertas Proativos: Configuração de alertas em caso de anomalias ou falhas críticas.Distributed Tracing com Jaeger / OpenTelemetry: Para depuração de pipelines complexos em ambientes distribuídos.📈 Escalabilidade e Performance (Projeções)AspectoImplementação Atual (Local Docker)Melhoria Proposta (Cloud / Otimizações)Volume~100k registros OlistPetabytes (particionamento horizontal, sharding)Latência< 30 segundos (pipeline end-to-end)< 10 segundos (para ingestão, com Kafka/Redis)Concorrência3 DAGs paralelas (com CeleryExecutor)10+ DAGs e tasks simultâneas (Kubernetes, Fargate)MonitoramentoLogs básicos, Airflow UIAPM completo, dashboards Grafana, alertas SMS/emailPersistênciaVolumes Docker, MinIO localS3/GCS/Azure Blob Storage, Databases gerenciados🏆 Considerações FinaisEste case entrega uma solução de dados enterprise-grade, segura, confiável, escalável e totalmente reprodutível. As decisões de projeto, como a criação de um framework de segurança customizado e a automação de tarefas de desenvolvimento/deploy, demonstram um domínio de conceitos que vão muito além do básico, focando nos desafios reais de um ambiente corporativo moderno.A arquitetura implementada é production-ready em seus princípios e pode ser facilmente adaptada e estendida para ambientes de nuvem em grande escala, mantendo os mesmos pilares de segurança, qualidade e governança.V. 🛠️ Reprodutibilidade da ArquiteturaEste projeto foi construído com foco na reprodutibilidade e portabilidade, utilizando Docker para isolar o ambiente. As instruções a seguir detalham como configurar e executar o projeto em qualquer máquina (macOS, Linux, Windows) com Docker instalado.Pré-requisitos do SistemaSoftwares NecessáriosPython 3.8+ (com pip)Git (versão 2.25+)Docker Desktop (para Windows/macOS) ou Docker Engine (para Linux)Docker Compose (geralmente incluído com o Docker Desktop/Engine)Apache Spark 3.5+: Embora as DAGs rodem o Spark via spark-submit dentro do contêiner Airflow, ter o Spark instalado localmente pode ser útil para depuração ou execução de scripts Spark standalone.macOS: brew install apache-sparkLinux/Windows: Download oficialRecursos de Hardware MínimosRAM: 8GB (recomendado 16GB para performance ideal com Spark e Airflow)Armazenamento: 10GB livresCPU: 4 cores (recomendado 8 cores)🚀 Instalação e ExecuçãoSiga os passos rigorosamente para garantir a correta inicialização do ambiente.Passo 1: Clonagem do RepositórioAbra seu terminal e execute:# Clone o repositório
git clone https://github.com/felipesbonatti/case-data-master-engenharia-de-dados.git
cd case-data-master-engenharia-de-dados

# Verifique a estrutura do projeto
# (O comando 'tree' pode não estar disponível no Windows por padrão, use 'dir /s /b' ou explore manualmente)
tree -L 2
Passo 2: Configuração do AmbienteEste passo é CRÍTICO para a segurança do Vault e o funcionamento do pipeline.# Crie o arquivo de ambiente (.env) a partir do template
cp .env.example .env

# Gere uma chave de criptografia segura para o Vault e adicione ao .env
# Esta chave é fundamental para criptografar/decriptar seus segredos no Vault.
python -c "from cryptography.fernet import Fernet; print('SECURITY_VAULT_SECRET_KEY=' + Fernet.generate_key().decode())" >> .env

# Abra o arquivo .env e configure suas API keys reais e senhas fortes.
# EXEMPLO DE .env (SUBSTITUA OS VALORES PADRÃO POR SEUS VALORES REAIS E SEGUROS):
# SECURITY_VAULT_SECRET_KEY=SUA_CHAVE_FERNET_GERADA_AQUI
# OPENWEATHER_API_KEY=SUA_CHAVE_DA_OPENWEATHERMAP_AQUI
# POSTGRES_USER=airflow_user_real
# POSTGRES_PASSWORD=sua_senha_segura_postgres
# MINIO_ROOT_USER=minio_admin_real
# MINIO_ROOT_PASSWORD=sua_senha_segura_minio
# ... (demais variaveis)
Atenção: Mantenha o arquivo .env seguro e não o adicione ao controle de versão público. Ele já está incluído no .gitignore para sua segurança.Passo 3: Adaptação do Projeto (Portabilidade)Este script ajusta caminhos de arquivo internos para garantir que o projeto funcione em qualquer sistema operacional (Linux, macOS, Windows).# Execute o script de configuração (CRUCIAL para portabilidade)
python configure.py

# Este script automatiza a adaptação de caminhos para seu ambiente local,
# garantindo que o projeto funcione corretamente independentemente do seu sistema operacional.
# Ele também cria um backup automático antes de fazer as modificações e pode realizar rollback em caso de falha.
Passo 4: Instalação de Dependências# Crie um ambiente virtual (recomendado para isolar as dependências do projeto)
python -m venv venv

# Ative o ambiente virtual
# Para Linux/macOS:
source venv/bin/activate
# Para Windows PowerShell:
# venv\Scripts\activate

# Instale todas as dependências Python listadas no requirements.txt
pip install -r requirements.txt

# Verifique se as principais bibliotecas foram instaladas
pip list | grep -E "(airflow|pyspark|pandas|great-expectations|streamlit|minio|psycopg2|sqlalchemy|cryptography)"
Passo 5: Inicialização da Infraestrutura DockerEste passo levanta todos os serviços essenciais (PostgreSQL, MinIO, Redis, Airflow Webserver, Airflow Scheduler).# O comando a seguir faz uma limpeza profunda e reconstrói as imagens para garantir um ambiente limpo.
# Isso é crucial para que todas as configurações e dependências (JARs do Spark) sejam aplicadas.
docker-compose down -v --rmi all
docker system prune -a --volumes -f
docker-compose up -d --build

# Verifique se os serviços Docker estão rodando e saudáveis
docker-compose ps

# Esperado (Status 'healthy' ou 'running'):
# - minio_object_storage (porta 9000/9001)
# - postgres_data_warehouse (porta 5432)
# - redis_cache_layer (porta 6379)
# - airflow_webserver (porta 8080)
# - airflow_scheduler
Passo 6: Configuração do Security VaultEste passo popula o Vault de Segurança com as credenciais para MinIO, PostgreSQL e APIs externas, utilizando a SECURITY_VAULT_SECRET_KEY do seu .env.# Acesse o shell do contêiner do scheduler (onde o Python e os plugins estão disponíveis)
docker-compose exec airflow-scheduler bash

# Dentro do contêiner, exporte a SECURITY_VAULT_SECRET_KEY do seu .env
# Isso é necessário para que o script setup_vault_secrets.py possa usá-la.
export SECURITY_VAULT_SECRET_KEY=$(grep 'SECURITY_VAULT_SECRET_KEY=' /opt/airflow/.env | cut -d '=' -f2)

# Popule o vault com as credenciais (MinIO, PostgreSQL, OpenWeatherMap, Masking Key)
# Este script lê as variáveis de ambiente e as armazena criptografadas no vault.json.
python /opt/airflow/scripts/setup_vault_secrets.py

# Saia do shell do contêiner
exit

# Opcional: Teste a conectividade dos serviços (requer que o Vault tenha sido populado)
python scripts/health_check.py

# Saída esperada:
# ✅ PostgreSQL: Connected
# ✅ MinIO: Connected  
# ✅ Redis: Connected
# ✅ Security Vault: Initialized (se o test_connections.py verificar isso)
Passo 7: Inicialização do AirflowEste passo inicia os componentes internos do Airflow (banco de dados de metadados, usuário admin).# Configure as variáveis de ambiente (se não estiver usando um entrypoint que já faz isso)
export AIRFLOW_HOME=$(pwd)
export AIRFLOW__CORE__DAGS_FOLDER=${AIRFLOW_HOME}/dags
export AIRFLOW__CORE__PLUGINS_FOLDER=${AIRFLOW_HOME}/plugins
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Inicialize/atualize o banco de dados de metadados do Airflow
airflow db upgrade

# Crie o usuário administrador padrão para a UI do Airflow (admin/admin)
# O `|| true` evita que o comando falhe se o usuário já existir.
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com || true

# Os serviços `airflow-webserver` e `airflow-scheduler` já estão rodando
# (iniciados no Passo 5 via docker-compose up -d)
# Não é necessário rodar `airflow scheduler` ou `airflow webserver` aqui novamente.
Passo 8: Execução do Dashboard# Abra um NOVO terminal ou aba de terminal e ative o ambiente virtual (se nao ativado)
# source venv/bin/activate # Linux/macOS
# venv\Scripts\activate     # Windows

# Execute o dashboard Streamlit
streamlit run dashboard/app.py --server.port 8501

# Acesse o dashboard no seu navegador: http://localhost:8501

# Opcional: Execute o Grafana (se configurado no docker-compose.yml e descomentado)
# Acesse Grafana no seu navegador: http://localhost:3000 (admin/admin)
🔍 Verificação da InstalaçãoApós seguir os passos, verifique a saúde do ambiente:URLs de AcessoAirflow UI: http://localhost:8080 (Usuário: admin, Senha: admin)Streamlit Dashboard: http://localhost:8501MinIO Console: http://localhost:9001 (Usuário: minioadmin, Senha: minio_secure_2024 - ou a senha que você configurou no .env)Grafana: http://localhost:3000 (Usuário: admin, Senha: admin - se configurado)Testes de ConectividadeExecute no terminal na raiz do projeto (com o ambiente virtual ativado):# Teste todas as conexões
python scripts/health_check.py

# Saída esperada:
# ✅ PostgreSQL: Connected
# ✅ MinIO: Connected  
# ✅ Redis: Connected
# ✅ Security Vault: Initialized (se o test_connections.py verificar isso)
Execução do PipelineApós verificar as URLs e conectividade, você pode ativar e monitorar suas DAGs na interface do Airflow.Acesse a Airflow UI (http://localhost:8080).Ative as DAGs clicando no botão "toggle" (interruptor) ao lado do nome de cada DAG.Dispare as DAGs clicando no ícone de "Play" ao lado do nome da DAG para iniciar uma execução manual.Sugestão de Ordem de Execução (para gerar dados para as próximas etapas):dag_coleta_segura_v1dag_03_consolidacao_e_mascaramento_v1dag_04_processamento_spark_seguro_v1dag_05_validacao_segura_v1dag_06_carrega_star_schema_segura_enterprise_v1dag_upload_bronze_minio_enterprise_v1 (se os dados locais de Olist não estiverem no MinIO ainda)dag_upload_silver_minio_enterprise_v1dag_gerenciamento_lifecycle_enterprise_v1Monitore a execução pela interface do Airflow (visualizações Graph, Gantt, Logs). Você também pode usar a CLI (no terminal com ambiente virtual ativado):# Monitore o status de uma DAG (exemplo)
airflow dags state dag_04_processamento_spark_seguro_v1
🐛 Solução de ProblemasProblemas ComunsProblemaSoluçãoPorta já em usoIdentifique o processo usando a porta (netstat -tlnp | grep :<PORTA>) e finalize-o, ou altere a porta no docker-compose.yml e airflow.cfg.Erro de permissão DockerAdicione seu usuário ao grupo docker (sudo usermod -aG docker $USER) e reinicie o terminal ou a sessão (logout/login). No Windows/macOS, verifique se o Docker Desktop está rodando.spark-submit: command not foundVerifique o Dockerfile e airflow.cfg para a configuração correta do PATH. A solução final implementada no projeto usa export PATH="/home/airflow/.local/bin:${PATH}" no bash_command da DAG para garantir a detecção do spark-submit dentro do contêiner Airflow.Airflow não inicia / DAGs 'Broken'Verifique os logs do contêiner airflow-webserver ou airflow-scheduler (docker-compose logs airflow-webserver). As mensagens de erro indicarão o problema (ex: SyntaxError em DAGs, problemas de conexão com DB/Redis, variáveis de ambiente ausentes).Credenciais não encontradas no VaultCertifique-se de que o Passo 6: Configuração do Security Vault foi executado corretamente, e que a SECURITY_VAULT_SECRET_KEY no seu .env é a mesma usada para criptografar o vault.json.Logs e Debugging# Logs de um serviço Docker Compose (exemplo para o scheduler)
docker-compose logs -f airflow-scheduler

# Logs do Docker Compose de todos os serviços
docker-compose logs -f

# Logs de tarefas do Airflow (acessíveis via UI do Airflow ou diretamente no host)
tail -f logs/dag_id=<NOME_DA_DAG>/<run_id>/<task_id>/*.log

# Teste individual de componentes (no terminal com ambiente virtual ativado)
python scripts/health_check.py
# Para verificar acesso ao Vault:
# python -c "from plugins.security_system.vault_manager_helper import VaultManager; import os; vm = VaultManager(vault_path=os.getenv('AIRFLOW_HOME','/opt/airflow')+'/plugins/security_system/vault.json', secret_key=os.getenv('SECURITY_VAULT_SECRET_KEY')); print(vm.get_secret('minio_local_credentials'))"
