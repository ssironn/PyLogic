#!/bin/bash
# ============================================================
# Script para copiar dependências dos containers do agente-ia
# ============================================================
#
# Uso:
#   ./copy-deps.sh <BOT_API_CONTAINER_ID> <BOT_APP_CONTAINER_ID>
#
# Exemplo:
#   ./copy-deps.sh abc123 def456
#
# ============================================================

set -e

BOT_API_ID=${1:-""}
BOT_APP_ID=${2:-""}

if [ -z "$BOT_API_ID" ] || [ -z "$BOT_APP_ID" ]; then
    echo "Uso: ./copy-deps.sh <BOT_API_CONTAINER_ID> <BOT_APP_CONTAINER_ID>"
    echo ""
    echo "Para encontrar os IDs dos containers:"
    echo "  docker ps -a | grep bot-api"
    echo "  docker ps -a | grep bot-app"
    exit 1
fi

echo "============================================"
echo "Copiando dependências do backend (bot-api)..."
echo "============================================"

mkdir -p backend/deps

echo "-> Copiando site-packages..."
docker cp "$BOT_API_ID":/usr/local/lib/python3.11/site-packages backend/deps/site-packages

echo "-> Copiando binários..."
docker cp "$BOT_API_ID":/usr/local/bin backend/deps/bin

echo "Backend OK!"
echo ""

echo "============================================"
echo "Copiando dependências do frontend (bot-app)..."
echo "============================================"

echo "-> Copiando node_modules..."
docker cp "$BOT_APP_ID":/app/node_modules frontend/node_modules

echo "Frontend OK!"
echo ""

echo "============================================"
echo "PRONTO! Agora você pode buildar as imagens:"
echo "============================================"
echo ""
echo "  docker build -t pylogic-backend ./backend"
echo "  docker build -t pylogic-frontend ./frontend"
echo ""
echo "Ou usar docker-compose:"
echo ""
echo "  docker-compose up --build"
echo ""
