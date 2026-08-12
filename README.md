# Bibly

Bibly é um SaaS em Next.js para gerenciamento e conferência de pedidos de marketplaces. Esta primeira versão entrega autenticação com Supabase Auth, rotas protegidas, dashboard inicial, navegação responsiva e a base de banco para perfis de usuários.

## Instalação

```bash
npm install
```

## Configuração do `.env`

Copie `.env.example` para `.env` e preencha sem commitar valores reais:

```bash
cp .env.example .env
```

Variáveis esperadas:

```env
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=
SUPABASE_JWKS_URL=
```

`SUPABASE_SECRET_KEY` é usada somente em código server-side (`src/lib/supabase/admin.ts`) e nunca deve ser exposta ao navegador.

## Configuração do Supabase

1. Crie um projeto no Supabase.
2. Copie a URL do projeto para `SUPABASE_URL`.
3. Copie a publishable/anon key para `SUPABASE_PUBLISHABLE_KEY`.
4. Copie a service role key para `SUPABASE_SECRET_KEY` apenas no ambiente server-side.
5. Habilite o provedor Email/Password em Authentication.
6. Execute a migration inicial em `supabase/migrations/001_create_users.sql`.

## Migrations

Com Supabase CLI configurado, aplique a migration:

```bash
supabase db push
```

Ou execute o SQL de `supabase/migrations/001_create_users.sql` no SQL Editor do Supabase.

## Desenvolvimento

```bash
npm run dev
```

Abra `http://localhost:3000`.

## Build

```bash
npm run build
```

## Produção

```bash
npm run start
```

## Estrutura de pastas

```text
src/
  app/                 Rotas App Router, layouts e páginas
  components/          UI, layout, auth, dashboard e navegação
  config/              Configurações compartilhadas
  hooks/               Hooks reutilizáveis futuros
  lib/                 Clientes Supabase e helpers de autenticação
  services/            Casos de uso e integrações por domínio
  types/               Tipos TypeScript de domínio
  utils/               Utilitários compartilhados
supabase/migrations/   Migrations SQL do banco
```

## Autenticação

- Login usa `supabase.auth.signInWithPassword()` via Server Action.
- A sessão é persistida pelos cookies gerenciados pelo `@supabase/ssr`.
- `/dashboard`, `/pedidos` e `/usuarios` validam autenticação no servidor.
- Usuários sem sessão são redirecionados para `/login`.
- `/` redireciona para `/dashboard` quando autenticado e para `/login` quando não autenticado.
- Logout usa `supabase.auth.signOut()` e redireciona para `/login`.
- A tabela `public.users` referencia `auth.users` e não armazena senhas.
