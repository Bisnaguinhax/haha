# Arquivo: plugins/security_system/vault.py (CORRIGIDO)
import os
import sys
import json
from cryptography.fernet import Fernet
from airflow.providers.fab.auth_manager.security_manager.override import FabAirflowSecurityManagerOverride

# Adiciona a pasta raiz de plugins ao path para garantir que a importação funcione
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from security_system.audit import AuditLogger

class AirflowSecurityManager(FabAirflowSecurityManagerOverride):
    """Classe de segurança customizada do Airflow."""
    def __init__(self, user_model=None):
        super(AirflowSecurityManager, self).__init__(user_model)
        # Inicialização simplificada para evitar dependências circulares