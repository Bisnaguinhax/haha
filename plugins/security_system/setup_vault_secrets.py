# Arquivo: scripts/setup_vault_secrets.py (VERSÃO FINAL E CORRIGIDA)

import sys
import os

# Adiciona o diretório raiz do projeto (/opt/airflow) ao path de busca do Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plugins.security_system.vault_manager_helper import VaultManager
from plugins.security_system.audit import AuditLogger

def setup_secrets():
    """Configura o vault com as credenciais iniciais necessárias."""
    SECRET_KEY = os.getenv('SECURITY_VAULT_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("A variável de ambiente SECURITY_VAULT_SECRET_KEY não está definida.")

    airflow_home = os.environ.get('AIRFLOW_HOME', '/opt/airflow')
    VAULT_PATH = os.path.join(airflow_home, 'plugins', 'security_system', 'vault.json')
    AUDIT_LOG_PATH = os.path.join(airflow_home, 'logs', 'security_audit', 'audit.csv')
    SYSTEM_LOG_PATH = os.path.join(airflow_home, 'logs', 'security_audit', 'system.log')

    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)

    logger = AuditLogger(AUDIT_LOG_PATH, SYSTEM_LOG_PATH)

    vault_manager = VaultManager(vault_path=VAULT_PATH, secret_key=SECRET_KEY, logger=logger)

    secrets_to_add = {
        "minio_local_credentials": {
            "endpoint_url": "minio:9000",
            "access_key": "admin",
            "secret_key": "minio_secure_2024"
        },
        "openweathermap_api_key": "SUA_CHAVE_DE_API_AQUI",
        "postgres_local_credentials": {
            "host": "postgres",
            "port": "5432",
            "database": "airflow_warehouse",
            "user": "airflow_user",
            "password": "secure_password_2024"
        }
    }

    for key, value in secrets_to_add.items():
        vault_manager.set_secret(key, value)
        print(f"Segredo '{key}' adicionado/atualizado no vault.")

    print("\nConfiguração de segredos do Vault concluída com sucesso!")

if __name__ == "__main__":
    setup_secrets()