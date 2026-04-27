create extension if not exists "uuid-ossp";
create extension if not exists vector;

create table if not exists users (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    created_at timestamptz not null default now()
);

create table if not exists goals (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    title text not null,
    description text not null default '',
    weight double precision not null check (weight >= 0 and weight <= 1),
    created_at timestamptz not null default now()
);

create unique index if not exists goals_user_title_idx on goals (user_id, lower(title));

create table if not exists user_constraints (
    user_id uuid primary key references users(id) on delete cascade,
    time_per_day double precision check (time_per_day is null or time_per_day >= 0),
    budget double precision check (budget is null or budget >= 0),
    energy_level double precision check (energy_level is null or (energy_level >= 0 and energy_level <= 1)),
    updated_at timestamptz not null default now()
);

create table if not exists behavioral_patterns (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    pattern text not null,
    confidence_score double precision not null check (confidence_score >= 0 and confidence_score <= 1),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists behavioral_patterns_user_pattern_idx
    on behavioral_patterns (user_id, lower(pattern));

create table if not exists decision_history (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    decision_text text not null,
    options jsonb not null,
    chosen_option text,
    reasoning text not null default '',
    version integer not null default 1,
    agent_breakdown jsonb not null default '{}'::jsonb,
    final_score double precision check (final_score is null or (final_score >= 0 and final_score <= 1)),
    timestamp timestamptz not null default now()
);

create table if not exists outcomes (
    id uuid primary key default uuid_generate_v4(),
    decision_id uuid not null references decision_history(id) on delete cascade,
    outcome_summary text not null,
    success_score double precision not null check (success_score >= 0 and success_score <= 1),
    reflection text not null default '',
    created_at timestamptz not null default now()
);

create table if not exists semantic_memories (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid not null references users(id) on delete cascade,
    content text not null,
    source_type text not null,
    source_id uuid,
    embedding vector(1536) not null,
    created_at timestamptz not null default now()
);

create index if not exists semantic_memories_embedding_idx
    on semantic_memories using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

create index if not exists semantic_memories_user_created_idx
    on semantic_memories (user_id, created_at desc);

create index if not exists decision_history_user_timestamp_idx
    on decision_history (user_id, timestamp desc);

create index if not exists behavioral_patterns_user_confidence_idx
    on behavioral_patterns (user_id, confidence_score desc);

insert into users (id, name)
values ('00000000-0000-0000-0000-000000000001', 'Default User')
on conflict (id) do nothing;

insert into goals (user_id, title, description, weight)
values
    ('00000000-0000-0000-0000-000000000001', 'Sustainable growth', 'Choose decisions that compound career, health, and financial stability.', 0.45),
    ('00000000-0000-0000-0000-000000000001', 'Execution consistency', 'Prefer options that can be executed reliably with available time and energy.', 0.35),
    ('00000000-0000-0000-0000-000000000001', 'Risk control', 'Avoid irreversible downside, unmanaged debt, and overcommitment.', 0.20)
on conflict do nothing;

insert into user_constraints (user_id, time_per_day, budget, energy_level)
values ('00000000-0000-0000-0000-000000000001', 2.0, 500.0, 0.7)
on conflict (user_id) do nothing;
