CREATE TABLE IF NOT EXISTS public.elements (
    uri TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type_uri TEXT NOT NULL REFERENCES public.types(uri),
    space_uri TEXT NOT NULL REFERENCES public.spaces(uri),
    creation_date BIGINT NOT NULL,
    author TEXT NOT NULL REFERENCES public.users(uri)
);
