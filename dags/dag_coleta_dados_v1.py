# ===============================================================================
# DAG DE COLETA DE DADOS EXTERNOS - VERSÃO CORRIGIDA
# ===============================================================================
# Esta DAG orquestra a ingestão de dados externos (IPCA e Clima)
# demonstrando práticas seguras de engenharia de dados em ambiente Airflow.
#
# 🔐 ARQUITETURA DE SEGURANÇA:
# - Vault customizado para gestão de segredos sensíveis (API Keys).
# - Uso de XComs para transmissão segura entre tasks.
# - Estrutura modular e limpa (funções puras separadas da DAG).
# - Auditoria e logs segregados por componente.
# ===============================================================================

from __future__ import annotations
import pendulum
import os
import requests
import pandas as pd
from datetime import datetime

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

# ===============================================================================
# TASKS - Funções Puras e Desacopladas
# ===============================================================================

def _get_api_key_from_vault(**kwargs):
    """
    Task de segurança: acesso seguro ao vault para recuperar a chave da API.

    🛡️ Boa prática: Segregação da lógica de segurança da lógica de negócio.
    """
    # Importação localizada para isolar dependências ao escopo do Airflow
    from plugins.security_system.audit import AuditLogger
    from plugins.security_system.vault import AirflowSecurityManager

    print("🔐 Task de Segurança: acessando Vault...")

    # --- INÍCIO DO BLOCO CORRIGIDO ---
    
    # 1. Obter a chave secreta do ambiente. O Airflow garante que ela estará disponível na execução.
    SECRET_KEY = os.getenv('SECURITY_VAULT_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("ERRO CRÍTICO: A variável de ambiente 'SECURITY_VAULT_SECRET_KEY' não está definida no ambiente de execução.")

    # 2. Usar caminhos relativos ao AIRFLOW_HOME para portabilidade dentro do Docker.
    # A variável AIRFLOW_HOME é definida por padrão no ambiente Airflow.
    airflow_home = os.environ.get('AIRFLOW_HOME', '/opt/airflow')
    
    VAULT_PATH = os.path.join(airflow_home, 'plugins', 'security_system', 'vault.json')
    AUDIT_LOG_PATH = os.path.join(airflow_home, 'logs', 'security_audit', 'audit.csv')
    SYSTEM_LOG_PATH = os.path.join(airflow_home, 'logs', 'security_audit', 'system.log')

    # Cria o diretório de log de auditoria se não existir
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    
    # Inicialização dos componentes de segurança
    audit = AuditLogger(AUDIT_LOG_PATH, SYSTEM_LOG_PATH)
    sec_manager = AirflowSecurityManager(VAULT_PATH, SECRET_KEY, audit)

    # Acesso ao segredo no Vault
    api_key = sec_manager.get_secret("openweathermap_api_key")
    if not api_key:
        raise ValueError("Chave 'openweathermap_api_key' não encontrada no Vault.")

    print("✅ Chave da API recuperada com sucesso.")

    # Transfere a chave para a próxima task de forma segura via XCom
    kwargs['ti'].xcom_push(key='api_key', value=api_key)
    # --- FIM DO BLOCO CORRIGIDO ---

def _collect_and_save_data(**kwargs):
    """
    Task de negócio: coleta os dados do IPCA e Clima e persiste os arquivos.

    🔁 Padrão aplicado:
    - A chave é recebida via XCom (sem exposição no código).
    - Caminhos dinâmicos garantem portabilidade do fluxo.
    """
    print("\n📥 Task de Coleta: iniciando...")

    # Recupera a chave da API via XCom
    ti = kwargs['ti']
    api_key = ti.xcom_pull(key='api_key', task_ids='get_api_key')
    if not api_key:
        raise ValueError("❌ Não foi possível obter a chave da API via XCom.")

    # --- CORREÇÃO DO CAMINHO BASE ---
    airflow_home = os.environ.get('AIRFLOW_HOME', '/opt/airflow')
    base_path = os.path.join(airflow_home, 'data')
    # --- FIM DA CORREÇÃO ---

    # --- Etapa 1: Coleta de dados do IPCA ---
    try:
        print("📊 Coletando dados do IPCA (Banco Central)...")
        url_ipca = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
        response_ipca = requests.get(url_ipca, timeout=15)
        response_ipca.raise_for_status()

        df_ipca = pd.DataFrame(response_ipca.json())
        caminho_ipca = os.path.join(base_path, "indicadores")
        os.makedirs(caminho_ipca, exist_ok=True)
        df_ipca.to_csv(os.path.join(caminho_ipca, "ipca_coletado.csv"), index=False)

        print("✅ IPCA salvo com sucesso.")
    except Exception as e:
        print(f"❌ Erro na coleta do IPCA: {e}")
        raise

    # --- Etapa 2: Coleta de dados do clima (OpenWeather) ---
    try:
        print("\n🌦️ Coletando dados de Clima (OpenWeather)...")
        cidades = {"São Paulo": 3448439, "Rio de Janeiro": 3451190}
        dados_clima = []

        for cidade, codigo in cidades.items():
            url_clima = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?id={codigo}&appid={api_key}&lang=pt_br&units=metric"
            )
            response_clima = requests.get(url_clima, timeout=10)
            response_clima.raise_for_status()
            clima = response_clima.json()

            dados_clima.append({
                "cidade": cidade,
                "temperatura": clima["main"]["temp"],
                "condicao": clima["weather"][0]["description"],
                "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        caminho_clima = os.path.join(base_path, "clima")
        os.makedirs(caminho_clima, exist_ok=True)
        df_clima = pd.DataFrame(dados_clima)
        df_clima.to_csv(os.path.join(caminho_clima, "clima_coletado.csv"), index=False)

        print("✅ Clima salvo com sucesso.")
    except Exception as e:
        print(f"❌ Erro na coleta de clima: {e}")
        raise

# ===============================================================================
# DEFINIÇÃO DA DAG
# ===============================================================================
with DAG(
    dag_id="dag_coleta_dados_externos_v1",
    start_date=pendulum.datetime(2025, 6, 10, tz="UTC"),
    schedule=None,
    catchup=False,
    doc_md="""
    ### DAG de Coleta de Dados Externos

    Demonstra a coleta segura de dados do IPCA e Clima com arquitetura desacoplada e uso de Vault.

    Pontos:
    - Recuperação de secrets via sistema de segurança customizado.
    - Passagem de dados entre tasks via XCom.
    - Caminhos e estruturas compatíveis com múltiplos ambientes.
    """,
    tags=['dados', 'ingestao', 'api'],
) as dag:

    # Task 1: Recupera chave da API do Vault
    get_api_key_task = PythonOperator(
        task_id='get_api_key',
        python_callable=_get_api_key_from_vault,
    )

    # Task 2: Coleta os dados com a chave segura
    collect_data_task = PythonOperator(
        task_id='collect_and_save_data',
        python_callable=_collect_and_save_data,
    )

    # Ordem de execução: primeiro recupera o segredo, depois executa coleta
    get_api_key_task >> collect_data_task