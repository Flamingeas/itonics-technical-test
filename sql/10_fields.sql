CREATE TABLE IF NOT EXISTS public.fields (
    uri TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    field_type TEXT NOT NULL CHECK (field_type IN ('text', 'number', 'date', 'boolean', 'select', 'multi_select', 'url', 'email')),
    type_uri TEXT NOT NULL REFERENCES public.types(uri),
    creation_date BIGINT NOT NULL,
    author TEXT NOT NULL REFERENCES public.users(uri),
    options JSONB DEFAULT NULL,
    required BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_fields_type_uri ON public.fields(type_uri);
