from __future__ import annotations

import os
import io
import pendulum
import pandas as pd
from sqlalchemy import create_engine, text
from minio import Minio

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

# ===================================================================================
# DOCUMENTAÇÃO DA DAG
# ===================================================================================
# Esta DAG orquestra um processo ETL que extrai dados da camada Bronze (MinIO),
# aplica transformações básicas e carrega os resultados no Data Mart (PostgreSQL).
#
# 🔐 SEGURANÇA:
# - As credenciais são recuperadas dinamicamente via Vault seguro.
# - Nenhum segredo é exposto em logs ou código-fonte.
#
# 📌 INSTRUÇÕES PARA AVALIADORES:
# 1. Confirme que o Vault já contém as chaves de acesso ao MinIO e PostgreSQL.
# 2. Execute a DAG `dag_upload_bronze_minio_v1` antes desta.
# 3. Execute esta DAG manualmente para validar a carga no Data Mart.
# ===================================================================================

def _minio_para_postgresql_seguro():
    """
    Realiza extração do MinIO, transforma os dados (se necessário)
    e carrega no PostgreSQL, com uso de Vault para autenticação.
    """
    # Importações locais para execução segura no contexto do Airflow
    from plugins.security_system.vault import AirflowSecurityManager

    print("🔐 Recuperando credenciais de serviço via Vault...")

    # 1. Recuperar a chave secreta do ambiente
    SECRET_KEY = os.getenv('SECURITY_VAULT_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("ERRO CRÍTICO: A variável de ambiente 'SECURITY_VAULT_SECRET_KEY' não está definida.")

    # 2. Apontar para o caminho do Vault DENTRO do contêiner
    # O caminho do seu PC é mapeado para /opt/airflow/plugins dentro do Docker
    vault_path = '/opt/airflow/plugins/security_system/vault.json'
    sec_manager = AirflowSecurityManager(vault_path=vault_path, secret_key=SECRET_KEY)

    # 3. Carregar credenciais de serviços
    minio_creds = sec_manager.get_secret("minio_local_credentials")
    pg_creds = sec_manager.get_secret("postgres_indicativos_credentials")

    if not minio_creds or not pg_creds:
        raise ValueError("❌ Credenciais para MinIO ou PostgreSQL não encontradas no Vault.")

    # --- ETAPA DE EXTRAÇÃO (MinIO) ---
    try:
        print("📥 Conectando ao MinIO para leitura do arquivo...")
        client = Minio(
            minio_creds['endpoint_url'].replace('http://', '').replace('https://', ''),
            access_key=minio_creds['access_key'],
            secret_key=minio_creds['secret_key'],
            secure=False
        )

        bucket_name = "bronze-layer"
        file_path = "olist/dados_consolidados.csv"
        
        print(f"   → Lendo o objeto: s3://{bucket_name}/{file_path}")
        data_object = client.get_object(bucket_name, file_path)
        data_bytes = data_object.read()
        
        df = pd.read_csv(io.BytesIO(data_bytes))
        print(f"✅ Dados extraídos com sucesso de '{file_path}' ({len(df)} linhas).")

    except Exception as e:
        print(f"❌ Falha na extração do MinIO: {e}")
        raise

    # --- ETAPA DE CARGA (PostgreSQL) ---
    try:
        print("\n📤 Conectando ao PostgreSQL para inserir dados...")
        db_url = (f"postgresql+psycopg2://{pg_creds['user']}:{pg_creds['password']}"
                  f"@{pg_creds['host']}:{pg_creds['port']}/{pg_creds['dbname']}")
        engine = create_engine(db_url)

        with engine.connect() as conn:
            print("   → Limpando tabela 'dados_olist'...")
            conn.execute(text("TRUNCATE TABLE dados_olist RESTART IDENTITY;"))
            conn.commit()  # Garante que o TRUNCATE seja efetivado

            print(f"   → Inserindo {len(df)} registros...")
            df.to_sql("dados_olist", conn, if_exists="append", index=False)
            conn.commit()

        print("✅ Carga finalizada com sucesso no Data Mart!")

    except Exception as e:
        print(f"❌ Erro ao carregar dados no PostgreSQL: {e}")
        raise

# === 📅 Definição da DAG ===
with DAG(
    dag_id="dag_minio_para_postgresql_v1",
    start_date=pendulum.datetime(2025, 6, 10, tz="UTC"),
    schedule=None,
    catchup=False,
    doc_md="""
### Carga do Data Lake para o Data Mart
Esta DAG executa uma pipeline ETL completa: extrai arquivos do MinIO (camada Bronze),
e insere no PostgreSQL (Data Mart).
""",
    tags=['datamart', 'etl', 'postgres', 'vault']
) as dag:

    tarefa_transferir_dados = PythonOperator(
        task_id='transferir_minio_para_postgres',
        python_callable=_minio_para_postgresql_seguro,
    )