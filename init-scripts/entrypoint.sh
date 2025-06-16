#!/bin/bash

# Função para verificar se a variável de ambiente da chave secreta foi definida
check_secret_key() {
    if [ -z "$SECURITY_VAULT_SECRET_KEY" ]; then
        echo "ERRO: A variável de ambiente SECURITY_VAULT_SECRET_KEY não está definida."
        echo "Por favor, defina-a no arquivo .env antes de iniciar o ambiente."
        exit 1
    fi
}

# Aguardar o banco de dados e o redis estarem prontos
wait_for_services() {
    echo "Aguardando o PostgreSQL iniciar..."
    while ! nc -z postgres_data_warehouse 5432; do
      sleep 1
    done
    echo "PostgreSQL iniciado."

    echo "Aguardando o Redis iniciar..."
    while ! nc -z redis_cache_layer 6379; do
      sleep 1
    done
    echo "Redis iniciado."
}

# Comandos a serem executados dependendo do serviço
case "$1" in
  webserver)
    check_secret_key
    wait_for_services
    echo "Inicializando o banco de dados do Airflow..."
    airflow db upgrade
    echo "Criando usuário admin do Airflow..."
    airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com || true
    echo "Iniciando o Webserver..."
    exec airflow webserver
    ;;
  scheduler)
    check_secret_key
    wait_for_services
    echo "Aguardando um pouco mais antes de iniciar o Scheduler..."
    sleep 10
    echo "Iniciando o Scheduler..."
    exec airflow scheduler
    ;;
  worker)
    check_secret_key
    wait_for_services
    echo "Aguardando um pouco mais antes de iniciar o Worker..."
    sleep 10
    echo "Iniciando o Worker..."
    exec airflow celery worker
    ;;
  flower)
    check_secret_key
    wait_for_services
    echo "Aguardando um pouco mais antes de iniciar o Flower..."
    sleep 10
    echo "Iniciando o Flower..."
    exec airflow celery flower
    ;;
  *)
    exec "$@"
    ;;
esac