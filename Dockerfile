# Arquivo: Dockerfile (VERSÃO FINAL E CORRIGIDA DEFINITIVA DO PATH DO SPARK-SUBMIT)

# Inicia a partir da imagem oficial do Airflow
FROM apache/airflow:2.9.2-python3.11

# Mudar para o usuário root para poder instalar pacotes e baixar JARs
USER root

# Instala o Java (dependência para o PySpark)
# Instala o netcat (para healthchecks)
# Instala o wget para baixar as JARs
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    wget \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configura a variável de ambiente JAVA_HOME que o Spark precisa
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Baixe as JARs do hadoop-aws e aws-java-sdk-bundle
# Estas versões são estáveis e conhecidas por funcionar com S3A/MinIO.
RUN mkdir -p /opt/airflow/jars/ && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.1/hadoop-aws-3.3.1.jar -P /opt/airflow/jars/ && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.901/aws-java-sdk-bundle-1.11.901.jar -P /opt/airflow/jars/

# Volta para o usuário padrão do Airflow para segurança
USER airflow

# ADICIONA O DIRETÓRIO DOS EXECUTÁVEIS DO PIP AO PATH
# Isso garante que `spark-submit` (instalado pelo PySpark via pip) seja encontrado.
ENV PATH="/home/airflow/.local/bin:${PATH}"

# Copia o arquivo de requerimentos para dentro da imagem
COPY requirements.txt /requirements.txt

# Instala os pacotes Python listados no arquivo
RUN pip install --no-cache-dir -r /requirements.txt