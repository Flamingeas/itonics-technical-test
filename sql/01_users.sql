CREATE TABLE IF NOT EXISTS public.users (
    uri TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL
);
