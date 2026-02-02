# PyLogic Frontend

Interface web para o demonstrador de equivalências lógicas PyLogic.

## Tecnologias

- **Next.js 14** - Framework React
- **Material-UI 5** - Componentes de UI
- **TypeScript** - Tipagem estática
- **Axios** - Cliente HTTP

## Funcionalidades

1. **Entrada de Proposições** - Dois campos para inserir proposições lógicas
2. **Seleção de Método** - Escolha entre métodos de prova (automático, direto, contrapositiva, absurdo, bidirecional)
3. **Configuração de Iterações** - Limite máximo de iterações (50, 100, 150, 300, 500)
4. **Opção Bidirecional** - Checkbox para permitir prova bidirecional
5. **Passos Completos** - Opção para visualizar todos os passos da demonstração
6. **Visualização Rica** - Proposições renderizadas com símbolos matemáticos

## Símbolos Suportados

| Entrada | Símbolo | Significado |
|---------|---------|-------------|
| `~`, `!` | ¬ | Negação |
| `^`, `&` | ∧ | Conjunção (E) |
| `v`, `\|` | ∨ | Disjunção (OU) |
| `->`, `=>` | → | Implicação |
| `T` | ⊤ | Verdadeiro |
| `F` | ⊥ | Falso |

## Desenvolvimento

```bash
# Instalar dependências
npm install

# Executar em modo de desenvolvimento
npm run dev

# Build para produção
npm run build

# Iniciar servidor de produção
npm start
```

## Docker

```bash
# Build da imagem
docker build -t pylogic-frontend .

# Executar container
docker run -p 3000:3000 pylogic-frontend

# Copiar build sem executar
docker create --name temp pylogic-frontend
docker cp temp:/app/.next ./build-copy/
docker rm temp
```

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `NEXT_PUBLIC_API_URL` | URL da API backend | `http://localhost:9000` |

## Estrutura

```
src/
├── app/                  # Next.js App Router
│   ├── layout.tsx        # Layout principal
│   └── page.tsx          # Página inicial
├── components/
│   └── prover/           # Componentes do demonstrador
│       ├── ProverForm.tsx
│       └── ProverResults.tsx
├── config/
│   └── theme.ts          # Tema Material-UI
├── services/
│   └── api.ts            # Cliente da API
├── styles/
│   └── globals.css       # Estilos globais
└── utils/
    └── propositionRenderer.tsx  # Renderização de proposições
```
