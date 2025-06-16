# Arquivo: plugins/security_system/secure_connection_pool.py (CORRIGIDO)
import os
from minio import Minio
import psycopg2
import sys

# Adiciona a pasta raiz de plugins ao path para garantir que as importações funcionem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security_system.vault import AirflowSecurityManager
from security_system.audit import AuditLogger

class SecureConnectionPool:
    def __init__(self):
        # Caminhos relativos ao contêiner
        airflow_home = os.environ.get('AIRFLOW_HOME', '/opt/airflow')
        AUDIT_LOG_PATH = os.path.join(airflow_home, 'logs', 'security_audit', 'audit.csv')
        SYSTEM_LOG_PATH = os.path.join(airflow_home, 'logs', 'security_audit', 'system.log')
        VAULT_DB_PATH = os.path.join(airflow_home, 'data', 'security_vault.db') # Usando .db conforme o original
        SECRET_KEY = os.getenv('SECURITY_VAULT_SECRET_KEY')

        self.audit = AuditLogger(audit_file_path=AUDIT_LOG_PATH, system_log_file_path=SYSTEM_LOG_PATH)
        self.security_manager = AirflowSecurityManager(vault_db_path=VAULT_DB_PATH, secret_key=SECRET_KEY, audit_logger=self.audit)
        self.audit.log("SecureConnectionPool inicializado.", action="CONN_POOL_INIT")

    def get_minio_client(self):
        """Retorna um cliente MinIO seguro."""
        try:
            minio_endpoint = self.security_manager.get_secret("minio_endpoint")
            minio_access_key = self.security_manager.get_secret("minio_access_key")
            minio_secret_key = self.security_manager.get_secret("minio_secret_key")

            if not all([minio_endpoint, minio_access_key, minio_secret_key]):
                raise ValueError("Credenciais MinIO incompletas ou não encontradas.")

            # Assume-se que a URL do endpoint já inclui o 'http://' se necessário
            client = Minio(endpoint=minio_endpoint.replace("http://", ""), access_key=minio_access_key, secret_key=minio_secret_key, secure=False)
            self.audit.log("Cliente MinIO obtido com sucesso.", action="MINIO_CONN_SUCCESS")
            return client
        except Exception as e:
            self.audit.log(f"Erro ao obter cliente MinIO: {e}", level="CRITICAL", action="MINIO_CONN_FAIL")
            raise

    def get_postgresql_conn(self):
        """Retorna uma conexão PostgreSQL segura."""
        try:
            creds = {
                "host": self.security_manager.get_secret("postgresql_host"),
                "port": self.security_manager.get_secret("postgresql_port"),
                "database": self.security_manager.get_secret("postgresql_database"),
                "user": self.security_manager.get_secret("postgresql_user"),
                "password": self.security_manager.get_secret("postgresql_password")
            }
            if not all(creds.values()):
                raise ValueError("Credenciais PostgreSQL incompletas ou não encontradas.")
            
            conn = psycopg2.connect(**creds)
            self.audit.log("Conexão PostgreSQL obtida com sucesso.", action="PG_CONN_SUCCESS")
            return conn
        except Exception as e:
            self.audit.log(f"Erro ao obter conexão PostgreSQL: {e}", level="CRITICAL", action="PG_CONN_FAIL")
            raise