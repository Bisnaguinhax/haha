# -*- coding: utf-8 -*-
"""
DAG de Gerenciamento de Lifecycle (HOT -> COLD STORAGE) - DEMONSTRAÇÃO
"""
# ===================================================================================
# 1. CORREÇÃO: A importação __future__ deve ser a primeira linha de código.
# ===================================================================================
from __future__ import annotations

import os
from datetime import datetime, timedelta

import pendulum
from botocore.exceptions import ClientError

from airflow.models.dag import DAG
from airflow.decorators import task

# ===================================================================================
# 2. CORREÇÃO: A lógica para criar o cliente MinIO foi reestruturada para
# funcionar corretamente e ser reutilizável pelas tarefas.
# ===================================================================================
def _get_minio_client():
    """
    Cria e retorna um cliente boto3 para interagir com o MinIO.

    As credenciais são obtidas de forma segura através do AirflowSecurityManager,
    que lê os segredos do Vault. A função garante que as variáveis de ambiente
    necessárias estejam presentes antes de tentar a conexão.
    """
    # Importa o SecurityManager de dentro do diretório de plugins
    from plugins.security_system.vault import AirflowSecurityManager
    
    # Obtém a chave secreta para decriptar o Vault
    secret_key = os.getenv('SECURITY_VAULT_SECRET_KEY')
    if not secret_key:
        raise ValueError("ERRO CRÍTICO: A variável de ambiente 'SECURITY_VAULT_SECRET_KEY' não está definida no ambiente Airflow.")

    # 3. CORREÇÃO: O caminho do Vault foi corrigido para o ambiente Docker.
    # O ideal é que o próprio SecurityManager saiba seu caminho, mas para este
    # exemplo, usamos o caminho correto dentro do contêiner.
    vault_path = '/opt/airflow/plugins/security_system/vault.json'
    
    # O logger aqui é simplificado pois este helper é chamado por tasks,
    # que já têm seu próprio contexto de log.
    class SimpleLogger:
        def log(self, *args, **kwargs): pass
        
    sec_manager = AirflowSecurityManager(vault_path=vault_path, secret_key=secret_key, logger=SimpleLogger())
    minio_creds = sec_manager.get_secret("minio_local_credentials")
    
    if not minio_creds:
        raise ValueError("Credenciais do MinIO 'minio_local_credentials' não encontradas no Vault.")
    
    # Retorna o cliente S3 (boto3) configurado
    return boto3.client(
        "s3",
        endpoint_url=minio_creds['endpoint_url'],
        aws_access_key_id=minio_creds['access_key'],
        aws_secret_access_key=minio_creds['secret_key'],
    )


@task
def criar_bucket_cold_storage_task():
    """Garante que o bucket de cold storage (destino) exista antes da movimentação."""
    s3 = _get_minio_client()
    bucket_destino = "cold-storage-layer"
    try:
        s3.head_bucket(Bucket=bucket_destino)
        print(f"✔️ Bucket de cold storage '{bucket_destino}' já existe.")
    except ClientError as e:
        # Se o erro for 'Not Found', o bucket não existe e podemos criá-lo.
        if e.response['Error']['Code'] == '404':
            print(f"Bucket '{bucket_destino}' não encontrado. Criando...")
            s3.create_bucket(Bucket=bucket_destino)
            print(f"🧊 Bucket de cold storage '{bucket_destino}' criado com sucesso.")
        else:
            # Propaga outros erros (ex: permissão negada)
            print(f"❌ Erro inesperado ao checar o bucket: {e}")
            raise

@task
def mover_arquivos_antigos_task():
    """Verifica e move arquivos antigos do bucket 'hot' para o 'cold' storage."""
    s3 = _get_minio_client()
    bucket_origem = "bronze-layer"
    bucket_destino = "cold-storage-layer"
    limite_dias = 30
    hoje = datetime.now()

    print(f"🔎 Verificando arquivos no bucket '{bucket_origem}' com mais de {limite_dias} dias...")
    
    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_origem)
        arquivos_movidos = 0

        for page in pages:
            if 'Contents' not in page:
                continue

            for objeto in page['Contents']:
                data_modificacao = objeto['LastModified'].replace(tzinfo=None)
                nome_ficheiro = objeto['Key']
                
                if (hoje - data_modificacao) > timedelta(days=limite_dias):
                    print(f"   -> 🥶 Arquivo '{nome_ficheiro}' é antigo. Movendo para cold storage...")
                    try:
                        copy_source = {'Bucket': bucket_origem, 'Key': nome_ficheiro}
                        s3.copy_object(Bucket=bucket_destino, CopySource=copy_source, Key=nome_ficheiro)
                        s3.delete_object(Bucket=bucket_origem, Key=nome_ficheiro)
                        print(f"      -> ✅ Movido e removido da origem com sucesso.")
                        arquivos_movidos += 1
                    except Exception as e:
                        print(f"      -> ❌ Erro ao mover o arquivo '{nome_ficheiro}': {e}")
                else:
                    print(f"   -> 🔥 Arquivo '{nome_ficheiro}' é recente. Nenhuma ação necessária.")
        
        if arquivos_movidos == 0:
            print("✅ Nenhum arquivo antigo encontrado para mover.")

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"⚠️ O bucket de origem '{bucket_origem}' não existe. Nada a fazer.")
        else:
            print(f"❌ Erro inesperado ao listar arquivos: {e}")
            raise


with DAG(
    dag_id='dag_gerenciamento_lifecycle_v1',
    start_date=pendulum.datetime(2025, 6, 10, tz="UTC"),
    schedule_interval='@daily',
    catchup=False,
    doc_md="### Gerenciamento de Lifecycle\nSimula política de arquivamento movendo dados antigos da camada 'hot' para 'cold'.",
    tags=['lifecycle', 'minio', 'storage', 'LGC'],
) as dag:

    criar_bucket_task = criar_bucket_cold_storage_task()
    mover_arquivos_task = mover_arquivos_antigos_task()

    criar_bucket_task >> mover_arquivos_task