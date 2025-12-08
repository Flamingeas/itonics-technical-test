CREATE TABLE IF NOT EXISTS public.tenants (
    uri TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    creation_date BIGINT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'inactive'))
);
