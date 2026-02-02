# PyLogic Frontend Dockerfile
# ============================================================
# PASSO 1: COPIAR BUILD DO CONTAINER AGENTE-IA (bot-app)
# ============================================================
#
# Execute estes comandos ANTES de buildar esta imagem:
#
# 1. Encontre o container ID do bot-app:
#    docker ps -a | grep bot-app
#
# 2. Encontre o diretório de build dentro do container:
#    docker exec <CONTAINER_ID> find / -name "build" -type d 2>/dev/null
#    docker exec <CONTAINER_ID> find / -name ".next" -type d 2>/dev/null
#
# 3. Copie o node_modules do container (para não baixar de novo):
#    docker cp <CONTAINER_ID>:/app/node_modules ./node_modules/
#
# 4. Copie o .next build se existir:
#    docker cp c69:/app/.next ./.next/ 2>/dev/null || true
#
# 5. Agora você pode buildar esta imagem:
#    docker build -t pylogic-frontend ./frontend
#
# ============================================================

FROM node:20-alpine

WORKDIR /app

# Copia package.json primeiro
COPY package*.json ./

# Se node_modules foi copiado do bot-app, usa ele (evita npm install)
COPY node_modules/ ./node_modules/

# Instala dependências apenas se node_modules não existir ou estiver incompleto
RUN if [ ! -d "node_modules" ] || [ ! -d "node_modules/next" ]; then \
      npm ci; \
    fi

# Copia o código fonte
COPY . .

# Se .next foi copiado, não precisa buildar
# Caso contrário, faz o build
ARG NEXT_PUBLIC_API_URL=http://localhost:9000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN if [ ! -d ".next" ]; then \
      npm run build; \
    fi

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]
