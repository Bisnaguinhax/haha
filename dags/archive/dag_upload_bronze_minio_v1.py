# ===================================================================================
# DAG DE UPLOAD PARA DATA LAKE (CAMADA BRONZE) - DEMONSTRAÇÃO TÉCNICA
# ===================================================================================
# Esta DAG orquestra o envio de arquivos locais para o MinIO (Data Lake),
# utilizando um sistema seguro baseado em Vault e logging de auditoria.
#
# 🔐 SEGURANÇA:
# - As credenciais do MinIO são extraídas do Vault via objeto seguro.
# - Caminhos de arquivos são relativos ao ambiente do contêiner.
# - Os uploads são rastreados por sistema de auditoria customizado.
#
# ✅ OBJETIVO:
# Popular a camada Bronze com dados brutos prontos para ingestão futura.
#
# 📌 INSTRUÇÕES:
# 1. Execute `setup_vault_secrets.py` para registrar as credenciais no Vault.
# 2. Depois, rode esta DAG manualmente para validar os uploads.
# ===================================================================================

from __future__ import annotations
import os
import pendulum
from pathlib import Path

# Importações podem falhar se os pacotes não estiverem instalados,
# o ideal é tratar isso no Dockerfile com um requirements.txt
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    ClientError = None

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

# Caminhos relativos ao ambiente do contêiner Airflow
# Estes caminhos correspondem aos volumes montados no docker-compose.yml
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME', '/opt/airflow')
AUDIT_LOG_PATH = f'{AIRFLOW_HOME}/logs/security_audit/audit.csv'
SYSTEM_LOG_PATH = f'{AIRFLOW_HOME}/logs/security_audit/system.log'
VAULT_DB_PATH = f'{AIRFLOW_HOME}/data/security_vault.db'


# === 🚀 Função principal de upload ===
def _upload_para_minio_seguro():
    """
    Recupera credenciais do MinIO via Vault e realiza o upload
    de arquivos locais para a camada Bronze do Data Lake.
    """
    if boto3 is None:
        raise RuntimeError("A biblioteca 'boto3' não está instalada. Adicione 'boto3' ao requirements.txt.")

    # Importação local (isolada) do sistema de segurança
    from plugins.security_system.audit import AuditLogger
    from plugins.security_system.vault import AirflowSecurityManager

    SECRET_KEY = os.getenv('SECURITY_VAULT_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("ERRO CRÍTICO: A variável de ambiente 'SECURITY_VAULT_SECRET_KEY' não está definida.")

    print("🔐 Obtendo credenciais seguras do Vault...")
    
    # Inicializa os componentes de segurança
    audit = AuditLogger(AUDIT_LOG_PATH, SYSTEM_LOG_PATH)
    sec_manager = AirflowSecurityManager(VAULT_DB_PATH, SECRET_KEY, audit)

    minio_creds = sec_manager.get_secret("minio_local_credentials")
    if not minio_creds:
        raise ValueError("❌ ERRO: Credenciais 'minio_local_credentials' não encontradas no Vault.")

    bucket_name = "bronze" # Camada bronze geralmente tem nome simples
    print(f"🌐 Conectando ao MinIO em: {minio_creds['endpoint_url']}")

    # Cliente MinIO
    s3_client = boto3.client(
        "s3",
        endpoint_url=minio_creds['endpoint_url'],
        aws_access_key_id=minio_creds['access_key'],
        aws_secret_access_key=minio_creds['secret_key'],
    )

    # Verifica ou cria o bucket
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✔️ Bucket '{bucket_name}' já existe.")
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"🪣 Bucket '{bucket_name}' criado com sucesso.")

    # Mapeia arquivos locais (dentro do contêiner) -> objetos no MinIO
    # O caminho base agora é o do contêiner
    base_path_container = f'{AIRFLOW_HOME}/data'
    arquivos_para_upload = {
        f"{base_path_container}/clima/clima_coletado.csv": "clima/clima_coletado.csv",
        f"{base_path_container}/indicadores/ipca_coletado.csv": "indicadores/ipca_coletado.csv",
        f"{base_path_container}/olist/dados_consolidados.csv": "olist/dados_consolidados.csv"
    }

    print("\n📤 Iniciando upload dos arquivos...")

    for caminho_local, caminho_minio in arquivos_para_upload.items():
        caminho = Path(caminho_local)
        if caminho.exists():
            print(f"   ⬆️ {caminho.name} → s3://{bucket_name}/{caminho_minio}")
            s3_client.upload_file(str(caminho), bucket_name, caminho_minio)
            # Log de auditoria
            audit.log('MINIO_UPLOAD_SUCCESS', f'Arquivo {caminho.name} enviado para o bucket {bucket_name}.', user='airflow_dag')
        else:
            print(f"   ⚠️ Arquivo não encontrado, pulando: {caminho_local}")
            audit.log('FILE_NOT_FOUND', f'Arquivo de origem não encontrado em {caminho_local}.', user='airflow_dag')

    print("\n✅ Upload concluído com sucesso para o MinIO Bronze.")


# === 📅 Definição da DAG ===
with DAG(
    dag_id="dag_upload_bronze_minio_v1",
    start_date=pendulum.datetime(2025, 6, 10, tz="UTC"),
    schedule=None,
    catchup=False,
    doc_md="""
### DAG de Upload para a Camada Bronze
Esta DAG realiza o envio de arquivos brutos para o MinIO com segurança.
As credenciais são recuperadas de um Vault local e todo o processo é auditado.
""",
    tags=['bronze', 'minio', 'upload', 'vault']
) as dag:

    tarefa_upload_minio = PythonOperator(
        task_id="upload_ficheiros_para_camada_bronze",
        python_callable=_upload_para_minio_seguro
    )