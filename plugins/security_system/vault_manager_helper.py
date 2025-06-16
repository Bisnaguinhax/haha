import os
import json
from cryptography.fernet import Fernet

class VaultManager:
    def __init__(self, vault_path=None, secret_key=None, logger=None):
        self.logger = logger if logger else type("SimpleLogger", (), {"info": lambda s, *a, **k: print(f"INFO: {a[0]}"), "error": lambda s, *a, **k: print(f"ERROR: {a[0]}"), "warning": lambda s, *a, **k: print(f"WARNING: {a[0]}")})()
        self.vault_path = vault_path or os.getenv("SECURITY_VAULT_PATH", '/opt/airflow/plugins/security_system/vault.json')
        self.secret_key = secret_key or os.getenv("SECURITY_VAULT_SECRET_KEY")
        if not self.secret_key: raise ValueError("A chave secreta (SECURITY_VAULT_SECRET_KEY) não está configurada.")
        self.fernet = Fernet(self.secret_key.encode())
        self.vault_data = self._load_vault()

    def _load_vault(self):
        try:
            if os.path.exists(self.vault_path) and os.path.getsize(self.vault_path) > 0:
                with open(self.vault_path, 'rb') as f: encrypted_data = f.read()
                return json.loads(self.fernet.decrypt(encrypted_data))
        except Exception as e: self.logger.error(f"Erro ao carregar o vault: {e}")
        return {}

    def _save_vault(self):
        with open(self.vault_path, 'wb') as f: f.write(self.fernet.encrypt(json.dumps(self.vault_data).encode()))

    def get_secret(self, key): return self.vault_data.get(key)

    def set_secret(self, key, value):
        self.vault_data[key] = value
        self._save_vault()