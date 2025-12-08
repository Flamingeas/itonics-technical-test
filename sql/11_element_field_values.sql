CREATE TABLE IF NOT EXISTS public.element_field_values (
    uri TEXT PRIMARY KEY,
    element_uri TEXT NOT NULL REFERENCES public.elements(uri) ON DELETE CASCADE,
    field_uri TEXT NOT NULL REFERENCES public.fields(uri) ON DELETE CASCADE,
    value_text TEXT,
    value_number DOUBLE PRECISION,
    value_date BIGINT,
    value_boolean BOOLEAN,
    value_json JSONB,
    creation_date BIGINT NOT NULL,
    updated_date BIGINT NOT NULL,
    UNIQUE(element_uri, field_uri)
);

CREATE INDEX idx_element_field_values_element ON public.element_field_values(element_uri);
CREATE INDEX idx_element_field_values_field ON public.element_field_values(field_uri);
