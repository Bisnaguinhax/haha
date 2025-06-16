# Arquivo: plugins/security_system/list_minio.py (CORRIGIDO)
import os
# CORREÇÃO: Usar importação absoluta
from plugins.security_system.secure_connection_pool import SecureConnectionPool

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def list_minio_objects():
    print("Tentando listar objetos no bucket MinIO...")
    try:
        pool = SecureConnectionPool()
        minio_client = pool.get_minio_client()

        # O nome do bucket deve ser genérico ou configurável
        bucket_name = "bronze" 
        print(f"Verificando bucket: {bucket_name}")

        if not minio_client.bucket_exists(bucket_name):
            print(f"AVISO: O bucket '{bucket_name}' não existe no MinIO.")
            return

        objects = minio_client.list_objects(bucket_name, recursive=True)

        found_objects = False
        print(f"\nObjetos encontrados no bucket '{bucket_name}':")
        for obj in objects:
            print(f"- {obj.object_name}")
            found_objects = True

        if not found_objects:
            print("Nenhum objeto encontrado neste bucket.")

    except Exception as e:
        print(f"ERRO ao listar objetos do MinIO: {e}")

if __name__ == "__main__":
    list_minio_objects()