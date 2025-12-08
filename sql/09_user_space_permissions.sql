CREATE TABLE IF NOT EXISTS public.user_space_permissions (
    user_uri TEXT NOT NULL REFERENCES public.users(uri),
    space_uri TEXT NOT NULL REFERENCES public.spaces(uri),
    verb_uri TEXT NOT NULL REFERENCES public.permission_verbs(uri),
    PRIMARY KEY (user_uri, space_uri, verb_uri)
);

