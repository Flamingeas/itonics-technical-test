CREATE TABLE IF NOT EXISTS public.user_tenants (
    user_uri TEXT NOT NULL REFERENCES public.users(uri),
    tenant_uri TEXT NOT NULL REFERENCES public.tenants(uri),
    PRIMARY KEY (user_uri, tenant_uri)
);
