# Hub ERP

Projeto web moderno criado com Next.js App Router, TypeScript, TailwindCSS, ESLint e Supabase. A versão inicial entrega a estrutura escalável do projeto e uma interface básica de dashboard com sidebar fixa.

## Como instalar

```bash
npm install
```

## Como executar

```bash
npm run dev
```

Acesse `http://localhost:3000` no navegador.

## Scripts disponíveis

```bash
npm run dev        # inicia o servidor de desenvolvimento
npm run build      # gera o build de produção
npm run start      # executa o build de produção
npm run lint       # executa o ESLint
npm run typecheck  # valida os tipos TypeScript
```

## Estrutura de pastas

```text
src/
├── app/                  # Rotas, layouts e estilos globais do App Router
├── components/           # Componentes compartilhados de layout e UI
├── features/             # Módulos de domínio com arquitetura feature-based
│   └── itens/            # Domínio Itens preparado para CRUD futuro
├── lib/                  # Clientes, integrações e utilitários de infraestrutura
├── services/             # Serviços globais compartilhados entre domínios
├── hooks/                # Hooks globais reutilizáveis
├── types/                # Tipos globais e tipos gerados do Supabase
├── constants/            # Constantes compartilhadas do projeto
└── middleware.ts         # Middleware preparado para autenticação Supabase
```

## Como conectar ao Supabase

1. Crie um projeto no Supabase.
2. Copie a URL do projeto e as chaves em **Project Settings > API**.
3. Preencha o arquivo `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua-chave-anon
SUPABASE_SERVICE_ROLE_KEY=sua-chave-service-role
```

> Use `SUPABASE_SERVICE_ROLE_KEY` apenas em código server-side. Nunca exponha essa chave em componentes client-side.

Os clientes Supabase estão em:

- `src/lib/supabase/client.ts`: cliente browser-side.
- `src/lib/supabase/server.ts`: cliente server-side para Server Components, Server Actions e Route Handlers.

## Como criar novos módulos

Crie uma nova pasta em `src/features` seguindo o padrão do módulo `itens`:

```text
src/features/novo-modulo/
├── components/  # Componentes específicos do domínio
├── hooks/       # Hooks específicos do domínio
├── services/    # Regras de integração/API do domínio
├── types/       # Tipos e contratos do domínio
├── pages/       # Composições de tela do domínio
└── index.ts     # API pública do domínio
```

Recomendações:

- Exporte apenas a API pública do módulo pelo `index.ts`.
- Mantenha regras de negócio e acesso a dados dentro de `services`.
- Use `types` para contratos fortemente tipados.
- Reutilize componentes globais de `src/components/ui` quando possível.

## Preparação para evolução

A arquitetura já está organizada para adicionar:

- autenticação Supabase;
- CRUD de Itens;
- dashboard com métricas;
- controle de usuários;
- logs de auditoria;
- relatórios.
