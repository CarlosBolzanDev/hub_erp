create extension if not exists pgcrypto;

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  auth_user_id uuid unique not null references auth.users(id) on delete cascade,
  name text,
  email text,
  avatar_url text,
  role text not null default 'operator' check (role in ('admin', 'operator')),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists users_auth_user_id_idx on public.users(auth_user_id);
create index if not exists users_email_idx on public.users(email);
create index if not exists users_role_idx on public.users(role);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_users_updated_at on public.users;
create trigger set_users_updated_at
before update on public.users
for each row execute function public.set_updated_at();

alter table public.users enable row level security;

create policy "Users can read own profile"
on public.users
for select
to authenticated
using (auth.uid() = auth_user_id);

-- Administradores serão gerenciados futuramente via server-side com SUPABASE_SECRET_KEY.
-- Nesta etapa, clientes autenticados recebem apenas permissão de leitura do próprio perfil.

create or replace function public.handle_new_auth_user()
returns trigger
security definer
set search_path = public
language plpgsql
as $$
begin
  insert into public.users (auth_user_id, name, email, avatar_url, role, is_active)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'name', new.raw_user_meta_data ->> 'full_name'),
    new.email,
    new.raw_user_meta_data ->> 'avatar_url',
    'operator',
    true
  )
  on conflict (auth_user_id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_auth_user();
