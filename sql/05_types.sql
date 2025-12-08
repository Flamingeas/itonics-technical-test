CREATE TABLE IF NOT EXISTS public.types (
    uri TEXT PRIMARY KEY,
    space_uri TEXT NOT NULL REFERENCES public.spaces(uri),
    name TEXT NOT NULL,
    creation_date BIGINT NOT NULL,
    author TEXT NOT NULL REFERENCES public.users(uri)
);
