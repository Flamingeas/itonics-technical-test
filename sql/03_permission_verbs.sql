CREATE TABLE IF NOT EXISTS public.permission_verbs (
    uri TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

