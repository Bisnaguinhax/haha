# Arquivo: scripts/examples/12-processa_vendas.py (VERSÃO FINAL COM INTEGRAÇÃO VAULT E IMPORTS)

import os # <-- ADICIONADO!
import sys # <-- ADICIONADO!
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, sum as _sum, avg as _avg
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# Importar o AirflowSecurityManager do seu plugin
# Note: o sys.path.insert é importante para encontrar plugins se este script for executado diretamente
# Mas dentro do contexto do Airflow, o plugin já deve estar disponível no PYTHONPATH
try:
    from plugins.security_system.vault import AirflowSecurityManager
except ImportError:
    # Fallback para execução local ou se o path não estiver configurado
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../plugins')))
    from security_system.vault import AirflowSecurityManager

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_spark_session(minio_endpoint, minio_access_key, minio_secret_key):
    """Inicializa e retorna uma sessão Spark configurada para acessar o MinIO."""
    logging.info("Iniciando a sessão Spark...")
    
    spark = (
        SparkSession.builder.appName("Processamento de Vendas Olist")
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        # As JARs agora são baixadas via Dockerfile e especificadas via spark-submit --jars
        # --- Configurações COMPLETAS para timeouts numéricos ---
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000")         # 60 segundos
        .config("spark.hadoop.fs.s3a.connection.establish.timeout", "5000") # 5 segundos para estabelecer a conexão
        .config("spark.hadoop.fs.s3a.socket.timeout", "60000")              # 60 segundos para timeout de socket
        .config("spark.hadoop.fs.s3a.read.timeout", "60000")                # 60 segundos para timeout de leitura
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .getOrCreate()
    )
    logging.info("Sessão Spark criada com sucesso.")
    return spark

def process_sales_data(spark, output_path_trusted, output_path_refined):
    """Cria um DataFrame de exemplo, processa e salva nas camadas Trusted e Refined."""
    try:
        logging.info("AVISO: Criando um DataFrame de exemplo para demonstração.")
        schema = StructType([
            StructField("product_category_name", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("order_item_id", IntegerType(), True),
        ])
        dummy_data = [
            ("informatica_acessorios", 150.50, 1), 
            ("beleza_saude", 75.20, 2),
            ("informatica_acessorios", 250.00, 1)
        ]
        df_vendas = spark.createDataFrame(dummy_data, schema=schema)
        logging.info("DataFrame de exemplo criado com sucesso.")

        logging.info("Processando para a camada Trusted (Silver)...")
        df_trusted = df_vendas.withColumn("receita_total", col("price") * col("order_item_id"))
        df_trusted.write.mode("overwrite").parquet(output_path_trusted)
        logging.info(f"Dados salvos na camada Trusted em: {output_path_trusted}")

        logging.info("Processando para a camada Refined (Gold)...")
        df_refined = df_trusted.groupBy("product_category_name").agg(
            _sum("receita_total").alias("receita_total_categoria"),
            _avg("price").alias("preco_medio_categoria")
        )
        df_refined.write.mode("overwrite").parquet(output_path_refined)
        logging.info(f"Dados agregados salvos na camada Refined em: {output_path_refined}")

    except Exception as e:
        logging.error(f"Erro durante o processamento: {e}", exc_info=True)
        raise

def main():
    """Função principal do pipeline de processamento Spark."""
    logging.info("=== Iniciando Pipeline de Processamento de Vendas ===")
    
    # -----------------------------------------------------------------------
    # Lógica para obter credenciais do Vault DENTRO DO SCRIPT SPARK
    # -----------------------------------------------------------------------
    SECRET_KEY = os.getenv('SECURITY_VAULT_SECRET_KEY')
    if not SECRET_KEY:
        logging.error("Erro Fatal: SECURITY_VAULT_SECRET_KEY não encontrada nas variáveis de ambiente.")
        return # Não pode prosseguir sem a chave do Vault

    VAULT_JSON_PATH = '/opt/airflow/plugins/security_system/vault.json'
    
    class SimpleLogger: # Classe de logger para evitar dependências complexas
        def info(self, *args, **kwargs): logging.info(args[0])
        def warning(self, *args, **kwargs): logging.warning(args[0])
        def error(self, *args, **kwargs): logging.error(args[0])

    try:
        sec_manager = AirflowSecurityManager(
            # O construtor do AirflowSecurityManager foi limpo em interações anteriores.
            # Se ainda houver um TypeError aqui, sua classe no vault.py pode precisar 
            # de um construtor vazio ou de argumentos específicos conforme seu design.
            # Por enquanto, assumimos que ela pode ser instanciada sem args no tempo de execução.
        )
        minio_creds = sec_manager.get_secret("minio_local_credentials")
        
        if not minio_creds or not isinstance(minio_creds, dict):
            logging.error("Erro Fatal: Credenciais 'minio_local_credentials' não encontradas ou inválidas no Vault.")
            return # Não pode prosseguir sem credenciais válidas
        
        minio_endpoint = minio_creds.get("endpoint_url")
        minio_access_key = minio_creds.get("access_key")
        minio_secret_key = minio_creds.get("secret_key")

        if not all([minio_endpoint, minio_access_key, minio_secret_key]):
            logging.error("Erro Fatal: Dados incompletos para credenciais do MinIO do Vault.")
            return

        logging.info("✅ Credenciais do MinIO recuperadas com sucesso do Vault para o job Spark.")

    except Exception as e:
        logging.error(f"Erro ao acessar o Vault ou credenciais: {e}", exc_info=True)
        return
    # -----------------------------------------------------------------------
    
    spark = None
    try:
        spark = get_spark_session(f"http://{minio_endpoint}", minio_access_key, minio_secret_key)
        
        caminho_trusted = "s3a://silver/vendas_olist/"
        caminho_refined = "s3a://gold/analytics_vendas_por_categoria/"
        
        process_sales_data(spark, caminho_trusted, caminho_refined)
        logging.info("Pipeline de Processamento de Vendas concluído com SUCESSO.")

    finally:
        if spark:
            logging.info("Sessão Spark encerrada.")
            spark.stop()

if __name__ == "__main__":
    main()
