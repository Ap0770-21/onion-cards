-- Run in Supabase SQL editor. Auth/users table is managed by Supabase already.

create extension if not exists vector;

create table generation_batches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) not null,
  topic text not null,
  overview text,
  source_type text check (source_type in ('prompt', 'upload')) not null,
  chunk_ids uuid[],  -- populated only for source_type = 'upload'
  created_at timestamptz default now()
);

create table cards (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) not null,
  batch_id uuid references generation_batches(id) on delete cascade,
  question text not null,
  answer text not null,
  favorite boolean default false,
  created_at timestamptz default now()
);

-- Embedding dimension (768) matches many free-tier embedding models —
-- adjust to match whichever provider you wire up in services/embeddings.py.
create table document_chunks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) not null,
  document_name text not null,
  content text not null,
  embedding vector(768),
  created_at timestamptz default now()
);

create table subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) unique not null,
  status text check (status in ('active', 'inactive', 'cancelled')) default 'inactive',
  paystack_customer_code text,
  current_period_end timestamptz,
  created_at timestamptz default now()
);

-- pgvector cosine-similarity search, scoped per-user
create or replace function match_document_chunks(
  query_embedding vector(768),
  match_user_id uuid,
  match_count int default 5
)
returns table (id uuid, document_name text, content text, similarity float)
language sql stable
as $$
  select id, document_name, content, 1 - (embedding <=> query_embedding) as similarity
  from document_chunks
  where user_id = match_user_id
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- Row Level Security: users only see/edit their own rows
alter table cards enable row level security;
alter table generation_batches enable row level security;
alter table document_chunks enable row level security;
alter table subscriptions enable row level security;

create policy "own cards" on cards for all using (auth.uid() = user_id);
create policy "own batches" on generation_batches for all using (auth.uid() = user_id);
create policy "own chunks" on document_chunks for all using (auth.uid() = user_id);
create policy "own subscription" on subscriptions for all using (auth.uid() = user_id);
