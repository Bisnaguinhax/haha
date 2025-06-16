# PASSO 1: A importação __future__ movida para ser a primeira linha do arquivo.
from __future__ import annotations

import os
import io
import pendulum
import pandas as pd

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

def _carregar_star_schema(**kwargs):
    """
    Popula as tabelas do Star Schema lendo os dados processados do Data Lake (MinIO)
    e carregando-os de forma segura e transacional no Data Mart (PostgreSQL).
    """
    from plugins.security_system.audit import AuditLogger
    from plugins.security_system.connections import SecureConnectionPool
    from plugins.security_system.vault import AirflowSecurityManager
    from sqlalchemy import text

    # PASSO 2: Caminhos de arquivo corrigidos para o ambiente do contêiner.
    SECRET_KEY = os.getenv('SECURITY_VAULT_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("ERRO CRÍTICO: A variável de ambiente 'SECURITY_VAULT_SECRET_KEY' não está definida.")
    
    # Usando caminhos relativos ao AIRFLOW_HOME dentro do contêiner
    VAULT_PATH = '/opt/airflow/plugins/security_system/vault.json'
    AUDIT_LOG_PATH = '/opt/airflow/logs/security_audit/audit.csv'
    
    # Instanciando os componentes de segurança
    audit = AuditLogger(AUDIT_LOG_PATH)
    sec_manager = AirflowSecurityManager(VAULT_PATH, SECRET_KEY, audit)
    pool = SecureConnectionPool(security_manager=sec_manager, audit_logger=audit)
    
    dag_id = kwargs.get('dag_run').dag_id
    audit.log("Iniciando task de carregamento do Star Schema.", action="STAR_SCHEMA_LOAD_START", dag_id=dag_id)

    try:
        # PASSO 3: Lógica aprimorada para ler os dados do MinIO (Data Lake).
        # Assume-se que uma DAG anterior salvou os arquivos processados no bucket 'gold'.
        minio_client = pool.get_minio_client()
        bucket_name = 'gold' 

        print(f"✅ Conectado ao MinIO. Lendo dados do bucket '{bucket_name}'.")

        # Função auxiliar para ler um arquivo Parquet do MinIO para um DataFrame
        def read_parquet_from_minio(object_name):
            try:
                response = minio_client.get_object(bucket_name, object_name)
                buffer = io.BytesIO(response.read())
                return pd.read_parquet(buffer)
            finally:
                response.close()
                response.release_conn()

        # Leitura dos dados processados
        print("   -> Lendo datasets processados do MinIO...")
        df_cliente_final = read_parquet_from_minio('dim_cliente.parquet')
        df_produto_final = read_parquet_from_minio('dim_produto.parquet')
        df_fato_final = read_parquet_from_minio('fato_vendas.parquet')
        print("✅ Datasets lidos com sucesso.")
        
        # Obtém a conexão segura com o banco de dados
        db_engine = pool.get_engine("postgres_datamart")
        print("✅ Conexão segura com o Data Mart estabelecida.")
        
        with db_engine.connect() as conn:
            with conn.begin() as transaction:  # Inicia uma transação
                try:
                    # Limpeza e carga das tabelas
                    print("⚙️ Limpando e carregando tabelas de destino (dimensões e fato)...")
                    conn.execute(text("TRUNCATE TABLE fato_vendas, dim_produto, dim_cliente RESTART IDENTITY;"))
                    audit.log("Tabelas de destino limpas.", action="DB_TABLES_TRUNCATED", dag_id=dag_id)
                    
                    print("   -> Carregando dim_cliente...")
                    df_cliente_final.to_sql('dim_cliente', conn, if_exists='append', index=False)
                    
                    print("   -> Carregando dim_produto...")
                    df_produto_final.to_sql('dim_produto', conn, if_exists='append', index=False)
                    
                    print("   -> Carregando fato_vendas...")
                    df_fato_final.to_sql('fato_vendas', conn, if_exists='append', index=False)
                    
                    # O bloco 'with' com 'begin()' faz o commit automático se não houver erro.
                    print("✅ Carga transacional bem-sucedida.")

                except Exception:
                    # O bloco 'with' com 'begin()' faz o rollback automático em caso de erro.
                    print("❌ ERRO: Realizando rollback da transação.")
                    raise

        print("✅ Carga do Star Schema concluída com sucesso!")
        audit.log("Carga do Star Schema concluída.", action="STAR_SCHEMA_LOAD_SUCCESS", dag_id=dag_id)
        
    except Exception as e:
        error_msg = f"Erro ao carregar Star Schema: {e}"
        audit.log(error_msg, level="CRITICAL", action="STAR_SCHEMA_LOAD_FAIL", dag_id=dag_id)
        raise

with DAG(
    dag_id='dag_06_carrega_star_schema_segura_v1',
    start_date=pendulum.datetime(2025, 6, 10, tz="UTC"),
    schedule=None,
    catchup=False,
    doc_md="### Carga do Data Mart\nCarrega os dados processados do MinIO no modelo Star Schema do PostgreSQL de forma segura.",
    tags=['datamart', 'starschema', 'seguranca'],
) as dag:

    tarefa_carregar_schema = PythonOperator(
        task_id='carregar_star_schema_task',
        python_callable=_carregar_star_schema,
    )