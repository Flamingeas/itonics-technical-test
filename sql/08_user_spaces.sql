CREATE TABLE IF NOT EXISTS public.user_spaces (
    user_uri TEXT NOT NULL REFERENCES public.users(uri),
    space_uri TEXT NOT NULL REFERENCES public.spaces(uri),
    PRIMARY KEY (user_uri, space_uri)
);
