from __future__ import annotations

import os
from pathlib import Path

import pendulum
import boto3
from botocore.exceptions import ClientError

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
# ===================================================================================
# DAG DE UPLOAD PARA DATA LAKE (CAMADA SILVER) - DEMONSTRAÇÃO TÉCNICA
# ===================================================================================
# Esta DAG orquestra o upload dos arquivos processados e consolidados
# para a camada Silver do Data Lake, hospedada no MinIO.
#
# 🔐 SEGURANÇA:
# - As credenciais do MinIO são recuperadas de forma segura do Vault,
#   evitando exposição no código fonte.
#
# 📌 INSTRUÇÕES:
# 1. Execute a DAG `dag_consolida_dados_olist_v1` antes para gerar o arquivo consolidado.
# 2. Em seguida, execute esta DAG para promover os dados para a camada Silver.
# ===================================================================================

def _upload_para_silver_seguro():
    """Executa o upload do arquivo consolidado para a camada Silver no MinIO, de forma segura."""
    # Importação movida para dentro da função para ser carregada pelo executor do Airflow
    from plugins.security_system.vault import AirflowSecurityManager
    
    print("🔐 Acessando o Vault para recuperar as credenciais do MinIO...")
    SECRET_KEY = os.getenv('SECURITY_VAULT_SECRET_KEY')

    if not SECRET_KEY:
        raise ValueError("ERRO CRÍTICO: A variável de ambiente 'SECURITY_VAULT_SECRET_KEY' não está definida.")

    # Caminho do Vault dentro do contêiner Docker
    VAULT_DB_PATH = '/opt/airflow/data/security_vault.db'
    
    # Logger simplificado para o security manager
    class SimpleLogger:
        def log(self, *args, **kwargs): pass

    sec_manager = AirflowSecurityManager(VAULT_DB_PATH, SECRET_KEY, SimpleLogger())
    minio_creds = sec_manager.get_secret("minio_local_credentials")

    if not minio_creds: 
        raise ValueError("Credenciais do MinIO não encontradas no Vault.")

    bucket_name = "silver-layer"
    s3 = boto3.client(
        "s3",
        endpoint_url=minio_creds['endpoint_url'],
        aws_access_key_id=minio_creds['access_key'],
        aws_secret_access_key=minio_creds['secret_key'],
    )

    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"✔️ Bucket '{bucket_name}' já existe.")
    except ClientError:
        s3.create_bucket(Bucket=bucket_name)
        print(f"🪣 Bucket '{bucket_name}' criado.")

    # Caminho do arquivo de dados dentro do contêiner Docker
    caminho_local = "/opt/airflow/data/olist/dados_consolidados.csv"
    caminho_minio = "vendas/consolidado_vendas.csv"
    
    print(f"\n🚀 Iniciando upload para a camada Silver do Data Lake...")
    caminho = Path(caminho_local)
    if caminho.exists():
        print(f"   -> Enviando arquivo: {caminho.name} para s3://{bucket_name}/{caminho_minio}")
        s3.upload_file(str(caminho), bucket_name, caminho_minio)
    else:
        print(f"   -> ⚠️ AVISO: Arquivo não encontrado, pulando upload: {caminho_local}")

    print("\n✅ Upload para a camada Silver finalizado com sucesso.")


with DAG(
    dag_id="dag_upload_silver_minio_v1",
    start_date=pendulum.datetime(2025, 6, 10, tz="UTC"),
    schedule=None,
    catchup=False,
    doc_md="""
### Upload para Camada Silver
Promove os dados consolidados da Olist para a camada Silver do Data Lake.
""",
    tags=['silver', 'minio', 'upload', 'datamart'],
) as dag:
    
    tarefa_upload_silver = PythonOperator(
        task_id="upload_consolidado_para_silver",
        python_callable=_upload_para_silver_seguro
    )