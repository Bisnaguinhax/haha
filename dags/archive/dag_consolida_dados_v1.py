# =================================================================================
# DAG DE CONSOLIDAÇÃO DE DADOS OLIST - VERSÃO CORRIGIDA E PORTÁTIL
# =================================================================================
# Esta DAG orquestra o processo de ETL sobre múltiplos datasets públicos da Olist,
# criando um CSV final consolidado e pronto para análises.
#
# PONTO DE ATENÇÃO:
# Esta DAG assume que os dados da Olist estão disponíveis dentro do contêiner
# no caminho `/opt/airflow/data/olist`.
# Garanta que o volume correspondente está montado no seu docker-compose.yml.
# =================================================================================

from __future__ import annotations

import pendulum
import pandas as pd

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator


# === 🔧 Função principal de consolidação de dados ===
def _consolidar_dados_olist():
    """
    Lê múltiplos arquivos CSV da Olist de um caminho relativo ao ambiente Airflow,
    executa joins e salva um dataset unificado.
    """
    # CORREÇÃO: Usar um caminho relativo ao ambiente Airflow, não um caminho local do Windows.
    # Este é o caminho onde os dados estarão DENTRO do contêiner Docker.
    base_path = '/opt/airflow/data/olist'
    print(f"📁 Lendo datasets a partir de: {base_path}")

    try:
        # 📦 Leitura dos arquivos de dados
        print("📦 Lendo arquivos CSV...")
        clientes = pd.read_csv(f'{base_path}/olist_customers_dataset.csv')
        pedidos = pd.read_csv(f'{base_path}/olist_orders_dataset.csv')
        pagamentos = pd.read_csv(f'{base_path}/olist_order_payments_dataset.csv')
        itens = pd.read_csv(f'{base_path}/olist_order_items_dataset.csv')
        reviews = pd.read_csv(f'{base_path}/olist_order_reviews_dataset.csv')
        produtos = pd.read_csv(f'{base_path}/olist_products_dataset.csv')
        print("👍 Arquivos lidos com sucesso.")
    except FileNotFoundError as e:
        print(f"❌ ERRO: Arquivo não encontrado. Verifique se o volume de dados está corretamente montado para '{base_path}' no seu docker-compose.yml.")
        raise e

    print("⚙️ Iniciando merges...")

    # === 🔗 Etapa 1: Clientes e Pedidos ===
    dados_clientes = pd.merge(
        clientes[['customer_id', 'customer_city', 'customer_state']],
        pedidos[['order_id', 'order_status', 'customer_id']],
        on='customer_id', how='outer'
    )

    # === 🔗 Etapa 2: Pagamentos, Itens e Reviews ===
    dados_pedidos = pd.merge(
        pagamentos[['order_id', 'payment_type', 'payment_value']],
        itens[['order_id', 'product_id', 'price', 'freight_value']],
        on='order_id', how='outer'
    )
    dados_pedidos = pd.merge(
        dados_pedidos,
        reviews[['order_id', 'review_score']],
        on='order_id', how='outer'
    )
    dados_pedidos = pd.merge(
        dados_pedidos,
        produtos[['product_id', 'product_category_name']],
        on='product_id', how='left'
    )

    # === 🔗 Etapa 3: União final com dados do cliente ===
    dados_consolidados = pd.merge(
        dados_pedidos,
        dados_clientes,
        on='order_id',
        how='outer',
        suffixes=('_pedido', '_cliente')
    )

    print(f"📊 Total de registros consolidados: {len(dados_consolidados)}")

    # === 💾 Salvando resultado final ===
    # O arquivo de saída também será salvo dentro da pasta de dados do contêiner.
    output_file = f'{base_path}/dados_consolidados.csv'
    dados_consolidados.to_csv(output_file, index=False)
    print(f"✅ Arquivo final salvo em: {output_file}")


# === 📅 Definição da DAG ===
with DAG(
    dag_id='dag_consolida_dados_olist_v1',
    start_date=pendulum.datetime(2025, 6, 10, tz="UTC"),
    schedule=None,  # Execução manual
    catchup=False,
    doc_md="""
### DAG de Consolidação Olist
Esta DAG realiza a união de múltiplos datasets públicos da Olist,
gerando um único arquivo `.csv` contendo os dados consolidados.
""",
    tags=['olist', 'etl', 'consolidacao']
) as dag:

    # === ▶️ Tarefa única de consolidação ===
    tarefa_consolidar_dados = PythonOperator(
        task_id='executar_consolidacao_olist',
        python_callable=_consolidar_dados_olist
    )