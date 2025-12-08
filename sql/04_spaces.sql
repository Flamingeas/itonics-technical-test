CREATE TABLE IF NOT EXISTS public.spaces (
    uri TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    creation_date BIGINT NOT NULL,
    tenant_uri TEXT NOT NULL REFERENCES public.tenants(uri)
);
