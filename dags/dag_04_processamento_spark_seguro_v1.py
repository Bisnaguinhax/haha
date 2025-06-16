# A importação __future__ DEVE ser a primeira linha de código
from __future__ import annotations

# Adiciona o diretório raiz do Airflow ao path do Python para garantir as importações
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

# ===============================================================================
# DAG DE PROCESSAMENTO SPARK COM INJEÇÃO SEGURA DE CREDENCIAIS
# ===============================================================================
# Esta DAG demonstra um padrão de segurança avançado: recuperar credenciais
# do Vault e injetá-las como variáveis de ambiente para um processo externo
# (neste caso, um job Spark).
# ===============================================================================

def _get_minio_env_vars():
    """
    Obtém credenciais do MinIO diretamente das variáveis de ambiente.
    Isso é feito para evitar erros de parse da DAG, assumindo que
    as variáveis já foram populadas pelo script setup_vault_secrets.py.
    """
    print("🔐 Buscando credenciais do MinIO de variáveis de ambiente para o PARSE da DAG...")
    
    minio_endpoint = os.getenv("MINIO_ENDPOINT_URL")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")

    if not all([minio_endpoint, minio_access_key, minio_secret_key]):
        print("⚠️ Aviso: Credenciais do MinIO (ENDPOINT, ACCESS_KEY, SECRET_KEY) NÃO ENCONTRADAS como variáveis de ambiente durante o PARSE DA DAG.")
        print("         Se o script Spark as busca do Vault em tempo de execução, isso é esperado no PARSE.")
        return {} 

    print("✅ Credenciais do Minio recuperadas das variáveis de ambiente para o parse da DAG.")
    return {
        "MINIO_ENDPOINT_URL": minio_endpoint,
        "MINIO_ACCESS_KEY": minio_access_key,
        "MINIO_SECRET_KEY": minio_secret_key,
    }

with DAG(
    dag_id='dag_04_processamento_spark_seguro_v1',
    start_date=pendulum.datetime(2025, 6, 10, tz="UTC"),
    schedule=None,
    catchup=False,
    doc_md="### Processamento Spark com Injeção Segura de Credenciais\\nObtém segredos do Vault e os passa como variáveis de ambiente para o job Spark.",
    tags=['spark', 'batch', 'security', 'vault'],
) as dag:
    
    minio_env_vars = _get_minio_env_vars()
    
    # O comando bash_command agora define o PATH explicitamente antes de chamar spark-submit
    tarefa_spark_segura = BashOperator(
        task_id='submeter_job_spark_seguro',
        bash_command='export PATH="/home/airflow/.local/bin:${PATH}" && spark-submit --jars /opt/airflow/jars/hadoop-aws-3.3.1.jar,/opt/airflow/jars/aws-java-sdk-bundle-1.11.901.jar /opt/airflow/scripts/examples/12-processa_vendas.py',
        env=minio_env_vars, # Injeta as credenciais no ambiente da task
    )