-- Ejecuta este script en Supabase SQL Editor antes de usar USE_SUPABASE=true.
-- Las tablas están separadas por historia de usuario para mantener claridad académica.

create table if not exists public.xp_role_rotation_sessions (
    id uuid primary key default gen_random_uuid(),
    developer_a text not null,
    developer_b text not null,
    interval_minutes integer not null check (interval_minutes > 0),
    current_piloto text not null,
    current_copiloto text not null,
    status text not null default 'configurada',
    remaining_seconds integer not null default 0,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.xp_role_rotation_history (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references public.xp_role_rotation_sessions(id) on delete cascade,
    piloto text not null,
    copiloto text not null,
    confirmed_by text[] not null default '{}',
    rotated_at timestamptz not null default now()
);

create table if not exists public.xp_code_reviews (
    id uuid primary key default gen_random_uuid(),
    programmer_name text not null,
    reviewer_name text not null,
    reviewed_task text not null,
    observations text not null default '',
    status text not null check (status in ('Aprobado', 'Con observaciones', 'Corregido')),
    review_date timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Para una entrega académica simple puedes dejar RLS desactivado.
-- Si activas RLS, crea políticas según autenticación de tu app.
