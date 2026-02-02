# PyLogic Backend Dockerfile
# ============================================================
# PASSO 1: COPIAR DEPENDÊNCIAS DO CONTAINER AGENTE-IA (bot-api)
# ============================================================
#
# Execute estes comandos ANTES de buildar esta imagem:
#
# 1. Encontre o container ID do bot-api:
#    docker ps -a | grep bot-api
#
# 2. Copie o ambiente Python do container:
#    docker cp 15a:/usr/local/lib/python3.11/site-packages ./deps/
#    docker cp 15a:/usr/local/bin ./deps/bin/
#
# 3. Agora você pode buildar esta imagem:
#    docker build -t pylogic-backend ./backend
#
# ============================================================

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Se existir a pasta deps/ com dependências copiadas do bot-api, use-as
COPY deps/ /usr/local/lib/python3.11/

# Instala apenas dependências que faltam (se deps não existir)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Remove a pasta deps se foi copiada (não precisa na imagem final)
RUN rm -rf /app/deps

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 5000

ENV FLASK_APP=api.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV DATABASE_HOST=mysql

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "api.py"]
