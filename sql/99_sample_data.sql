-- Sample Data Generation Script
-- Generates thousands of elements with fields and values

-- =============================================================================
-- USERS (10 sample users)
-- =============================================================================
INSERT INTO public.users (uri, email, display_name) VALUES
    ('user:alice', 'alice@example.com', 'Alice Johnson'),
    ('user:bob', 'bob@example.com', 'Bob Smith'),
    ('user:charlie', 'charlie@example.com', 'Charlie Brown'),
    ('user:diana', 'diana@example.com', 'Diana Prince'),
    ('user:edward', 'edward@example.com', 'Edward Norton'),
    ('user:fiona', 'fiona@example.com', 'Fiona Green'),
    ('user:george', 'george@example.com', 'George Miller'),
    ('user:hannah', 'hannah@example.com', 'Hannah White'),
    ('user:ivan', 'ivan@example.com', 'Ivan Petrov'),
    ('user:julia', 'julia@example.com', 'Julia Roberts')
ON CONFLICT (uri) DO NOTHING;

-- =============================================================================
-- TENANTS (3 sample tenants)
-- =============================================================================
INSERT INTO public.tenants (uri, name, creation_date, status) VALUES
    ('tenant:acme', 'Acme Corporation', 1700000000000, 'active'),
    ('tenant:globex', 'Globex Industries', 1700100000000, 'active'),
    ('tenant:initech', 'Initech Solutions', 1700200000000, 'active')
ON CONFLICT (uri) DO NOTHING;

-- =============================================================================
-- PERMISSION VERBS
-- =============================================================================
INSERT INTO public.permission_verbs (uri, name, description) VALUES
    ('verb:read', 'read', 'Read access to resources'),
    ('verb:write', 'write', 'Write access to resources'),
    ('verb:delete', 'delete', 'Delete access to resources'),
    ('verb:admin', 'admin', 'Full administrative access')
ON CONFLICT (uri) DO NOTHING;

-- =============================================================================
-- SPACES (6 sample spaces - 2 per tenant)
-- =============================================================================
INSERT INTO public.spaces (uri, name, creation_date, tenant_uri) VALUES
    ('space:acme-projects', 'Projects', 1700010000000, 'tenant:acme'),
    ('space:acme-hr', 'Human Resources', 1700020000000, 'tenant:acme'),
    ('space:globex-products', 'Product Catalog', 1700110000000, 'tenant:globex'),
    ('space:globex-customers', 'Customer Database', 1700120000000, 'tenant:globex'),
    ('space:initech-tasks', 'Task Management', 1700210000000, 'tenant:initech'),
    ('space:initech-inventory', 'Inventory', 1700220000000, 'tenant:initech')
ON CONFLICT (uri) DO NOTHING;

-- =============================================================================
-- USER-TENANT ASSOCIATIONS
-- =============================================================================
INSERT INTO public.user_tenants (user_uri, tenant_uri) VALUES
    ('user:alice', 'tenant:acme'),
    ('user:bob', 'tenant:acme'),
    ('user:charlie', 'tenant:acme'),
    ('user:diana', 'tenant:globex'),
    ('user:edward', 'tenant:globex'),
    ('user:fiona', 'tenant:globex'),
    ('user:george', 'tenant:initech'),
    ('user:hannah', 'tenant:initech'),
    ('user:ivan', 'tenant:initech'),
    ('user:julia', 'tenant:initech')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- USER-SPACE ASSOCIATIONS
-- =============================================================================
INSERT INTO public.user_spaces (user_uri, space_uri) VALUES
    ('user:alice', 'space:acme-projects'),
    ('user:alice', 'space:acme-hr'),
    ('user:bob', 'space:acme-projects'),
    ('user:charlie', 'space:acme-hr'),
    ('user:diana', 'space:globex-products'),
    ('user:diana', 'space:globex-customers'),
    ('user:edward', 'space:globex-products'),
    ('user:fiona', 'space:globex-customers'),
    ('user:george', 'space:initech-tasks'),
    ('user:george', 'space:initech-inventory'),
    ('user:hannah', 'space:initech-tasks'),
    ('user:ivan', 'space:initech-inventory'),
    ('user:julia', 'space:initech-tasks'),
    ('user:julia', 'space:initech-inventory')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- TYPES (Different types for different use cases)
-- =============================================================================
INSERT INTO public.types (uri, name, space_uri, creation_date, author) VALUES
    -- Acme Projects types
    ('type:project', 'Project', 'space:acme-projects', 1700030000000, 'user:alice'),
    ('type:task', 'Task', 'space:acme-projects', 1700030100000, 'user:alice'),
    -- Acme HR types
    ('type:employee', 'Employee', 'space:acme-hr', 1700030200000, 'user:charlie'),
    ('type:department', 'Department', 'space:acme-hr', 1700030300000, 'user:charlie'),
    -- Globex Products types
    ('type:product', 'Product', 'space:globex-products', 1700130000000, 'user:diana'),
    ('type:category', 'Category', 'space:globex-products', 1700130100000, 'user:diana'),
    -- Globex Customers types
    ('type:customer', 'Customer', 'space:globex-customers', 1700130200000, 'user:fiona'),
    ('type:contact', 'Contact', 'space:globex-customers', 1700130300000, 'user:fiona'),
    -- Initech Tasks types
    ('type:ticket', 'Support Ticket', 'space:initech-tasks', 1700230000000, 'user:george'),
    ('type:bug', 'Bug Report', 'space:initech-tasks', 1700230100000, 'user:hannah'),
    -- Initech Inventory types
    ('type:item', 'Inventory Item', 'space:initech-inventory', 1700230200000, 'user:ivan'),
    ('type:supplier', 'Supplier', 'space:initech-inventory', 1700230300000, 'user:ivan')
ON CONFLICT (uri) DO NOTHING;

-- =============================================================================
-- FIELDS (Define fields for each type - AirTable-like structure)
-- =============================================================================

-- Project fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:project-name', 'Project Name', 'text', 'type:project', 1700040000000, 'user:alice', NULL, true),
    ('field:project-status', 'Status', 'select', 'type:project', 1700040001000, 'user:alice', '{"options": ["Planning", "In Progress", "On Hold", "Completed", "Cancelled"]}', true),
    ('field:project-budget', 'Budget', 'number', 'type:project', 1700040002000, 'user:alice', NULL, false),
    ('field:project-start', 'Start Date', 'date', 'type:project', 1700040003000, 'user:alice', NULL, false),
    ('field:project-end', 'End Date', 'date', 'type:project', 1700040004000, 'user:alice', NULL, false),
    ('field:project-active', 'Is Active', 'boolean', 'type:project', 1700040005000, 'user:alice', NULL, false),
    ('field:project-url', 'Project URL', 'url', 'type:project', 1700040006000, 'user:alice', NULL, false);

-- Task fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:task-title', 'Title', 'text', 'type:task', 1700040100000, 'user:alice', NULL, true),
    ('field:task-description', 'Description', 'text', 'type:task', 1700040101000, 'user:alice', NULL, false),
    ('field:task-priority', 'Priority', 'select', 'type:task', 1700040102000, 'user:alice', '{"options": ["Low", "Medium", "High", "Critical"]}', true),
    ('field:task-status', 'Status', 'select', 'type:task', 1700040103000, 'user:alice', '{"options": ["Todo", "In Progress", "Review", "Done"]}', true),
    ('field:task-due', 'Due Date', 'date', 'type:task', 1700040104000, 'user:alice', NULL, false),
    ('field:task-estimate', 'Estimate (hours)', 'number', 'type:task', 1700040105000, 'user:alice', NULL, false);

-- Employee fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:emp-name', 'Full Name', 'text', 'type:employee', 1700040200000, 'user:charlie', NULL, true),
    ('field:emp-email', 'Email', 'email', 'type:employee', 1700040201000, 'user:charlie', NULL, true),
    ('field:emp-hire-date', 'Hire Date', 'date', 'type:employee', 1700040202000, 'user:charlie', NULL, true),
    ('field:emp-salary', 'Salary', 'number', 'type:employee', 1700040203000, 'user:charlie', NULL, false),
    ('field:emp-active', 'Active', 'boolean', 'type:employee', 1700040204000, 'user:charlie', NULL, true),
    ('field:emp-department', 'Department', 'select', 'type:employee', 1700040205000, 'user:charlie', '{"options": ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]}', true);

-- Product fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:prod-name', 'Product Name', 'text', 'type:product', 1700140000000, 'user:diana', NULL, true),
    ('field:prod-sku', 'SKU', 'text', 'type:product', 1700140001000, 'user:diana', NULL, true),
    ('field:prod-price', 'Price', 'number', 'type:product', 1700140002000, 'user:diana', NULL, true),
    ('field:prod-stock', 'Stock Quantity', 'number', 'type:product', 1700140003000, 'user:diana', NULL, false),
    ('field:prod-available', 'Available', 'boolean', 'type:product', 1700140004000, 'user:diana', NULL, true),
    ('field:prod-category', 'Category', 'select', 'type:product', 1700140005000, 'user:diana', '{"options": ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys"]}', false),
    ('field:prod-url', 'Product URL', 'url', 'type:product', 1700140006000, 'user:diana', NULL, false);

-- Customer fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:cust-company', 'Company Name', 'text', 'type:customer', 1700140100000, 'user:fiona', NULL, true),
    ('field:cust-email', 'Email', 'email', 'type:customer', 1700140101000, 'user:fiona', NULL, true),
    ('field:cust-website', 'Website', 'url', 'type:customer', 1700140102000, 'user:fiona', NULL, false),
    ('field:cust-revenue', 'Annual Revenue', 'number', 'type:customer', 1700140103000, 'user:fiona', NULL, false),
    ('field:cust-active', 'Active Customer', 'boolean', 'type:customer', 1700140104000, 'user:fiona', NULL, true),
    ('field:cust-tier', 'Customer Tier', 'select', 'type:customer', 1700140105000, 'user:fiona', '{"options": ["Bronze", "Silver", "Gold", "Platinum"]}', false),
    ('field:cust-since', 'Customer Since', 'date', 'type:customer', 1700140106000, 'user:fiona', NULL, false);

-- Support Ticket fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:ticket-title', 'Title', 'text', 'type:ticket', 1700240000000, 'user:george', NULL, true),
    ('field:ticket-desc', 'Description', 'text', 'type:ticket', 1700240001000, 'user:george', NULL, true),
    ('field:ticket-priority', 'Priority', 'select', 'type:ticket', 1700240002000, 'user:george', '{"options": ["Low", "Medium", "High", "Urgent"]}', true),
    ('field:ticket-status', 'Status', 'select', 'type:ticket', 1700240003000, 'user:george', '{"options": ["Open", "In Progress", "Waiting", "Resolved", "Closed"]}', true),
    ('field:ticket-created', 'Created Date', 'date', 'type:ticket', 1700240004000, 'user:george', NULL, true);

-- Bug Report fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:bug-title', 'Bug Title', 'text', 'type:bug', 1700240100000, 'user:hannah', NULL, true),
    ('field:bug-steps', 'Steps to Reproduce', 'text', 'type:bug', 1700240101000, 'user:hannah', NULL, true),
    ('field:bug-severity', 'Severity', 'select', 'type:bug', 1700240102000, 'user:hannah', '{"options": ["Minor", "Major", "Critical", "Blocker"]}', true),
    ('field:bug-status', 'Status', 'select', 'type:bug', 1700240103000, 'user:hannah', '{"options": ["New", "Confirmed", "In Progress", "Fixed", "Verified", "Closed"]}', true),
    ('field:bug-reported', 'Reported Date', 'date', 'type:bug', 1700240104000, 'user:hannah', NULL, true),
    ('field:bug-resolved', 'Resolved Date', 'date', 'type:bug', 1700240105000, 'user:hannah', NULL, false);

-- Inventory Item fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:inv-name', 'Item Name', 'text', 'type:item', 1700240200000, 'user:ivan', NULL, true),
    ('field:inv-sku', 'SKU', 'text', 'type:item', 1700240201000, 'user:ivan', NULL, true),
    ('field:inv-quantity', 'Quantity', 'number', 'type:item', 1700240202000, 'user:ivan', NULL, true),
    ('field:inv-unit-cost', 'Unit Cost', 'number', 'type:item', 1700240203000, 'user:ivan', NULL, true),
    ('field:inv-reorder', 'Reorder Level', 'number', 'type:item', 1700240204000, 'user:ivan', NULL, false),
    ('field:inv-location', 'Location', 'select', 'type:item', 1700240205000, 'user:ivan', '{"options": ["Warehouse A", "Warehouse B", "Warehouse C", "Store Front"]}', false),
    ('field:inv-active', 'Active', 'boolean', 'type:item', 1700240206000, 'user:ivan', NULL, true);

-- Supplier fields
INSERT INTO public.fields (uri, name, field_type, type_uri, creation_date, author, options, required) VALUES
    ('field:sup-name', 'Supplier Name', 'text', 'type:supplier', 1700240300000, 'user:ivan', NULL, true),
    ('field:sup-email', 'Contact Email', 'email', 'type:supplier', 1700240301000, 'user:ivan', NULL, true),
    ('field:sup-website', 'Website', 'url', 'type:supplier', 1700240302000, 'user:ivan', NULL, false),
    ('field:sup-rating', 'Rating', 'select', 'type:supplier', 1700240303000, 'user:ivan', '{"options": ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"]}', false),
    ('field:sup-active', 'Active', 'boolean', 'type:supplier', 1700240304000, 'user:ivan', NULL, true);

-- =============================================================================
-- GENERATE THOUSANDS OF ELEMENTS AND FIELD VALUES
-- Using generate_series to create bulk data
-- =============================================================================

-- Generate 500 Projects
INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
SELECT
    'element:project-' || i,
    'Project ' || i || ': ' || (ARRAY['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega', 'Phoenix', 'Atlas', 'Nova', 'Titan', 'Apex'])[1 + (i % 10)],
    'type:project',
    'space:acme-projects',
    1700050000000 + (i * 1000),
    (ARRAY['user:alice', 'user:bob', 'user:charlie'])[1 + (i % 3)]
FROM generate_series(1, 500) AS i;

-- Generate field values for Projects
INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:project-' || i || '-name',
    'element:project-' || i,
    'field:project-name',
    'Project ' || i || ': ' || (ARRAY['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega', 'Phoenix', 'Atlas', 'Nova', 'Titan', 'Apex'])[1 + (i % 10)],
    NULL, NULL, NULL,
    1700050000000 + (i * 1000),
    1700050000000 + (i * 1000)
FROM generate_series(1, 500) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:project-' || i || '-status',
    'element:project-' || i,
    'field:project-status',
    (ARRAY['Planning', 'In Progress', 'On Hold', 'Completed', 'Cancelled'])[1 + (i % 5)],
    NULL, NULL, NULL,
    1700050000000 + (i * 1000),
    1700050000000 + (i * 1000)
FROM generate_series(1, 500) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:project-' || i || '-budget',
    'element:project-' || i,
    'field:project-budget',
    NULL,
    10000 + (i * 500) + (random() * 50000)::int,
    NULL, NULL,
    1700050000000 + (i * 1000),
    1700050000000 + (i * 1000)
FROM generate_series(1, 500) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:project-' || i || '-active',
    'element:project-' || i,
    'field:project-active',
    NULL, NULL, NULL,
    i % 4 != 0,
    1700050000000 + (i * 1000),
    1700050000000 + (i * 1000)
FROM generate_series(1, 500) AS i;

-- Generate 1000 Tasks
INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
SELECT
    'element:task-' || i,
    (ARRAY['Implement', 'Fix', 'Review', 'Update', 'Create', 'Design', 'Test', 'Deploy', 'Document', 'Refactor'])[1 + (i % 10)] || ' ' ||
    (ARRAY['feature', 'bug', 'module', 'component', 'service', 'API', 'database', 'UI', 'backend', 'frontend'])[1 + ((i / 10) % 10)] || ' ' || i,
    'type:task',
    'space:acme-projects',
    1700060000000 + (i * 500),
    (ARRAY['user:alice', 'user:bob', 'user:charlie'])[1 + (i % 3)]
FROM generate_series(1, 1000) AS i;

-- Generate field values for Tasks
INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:task-' || i || '-title',
    'element:task-' || i,
    'field:task-title',
    (ARRAY['Implement', 'Fix', 'Review', 'Update', 'Create', 'Design', 'Test', 'Deploy', 'Document', 'Refactor'])[1 + (i % 10)] || ' ' ||
    (ARRAY['feature', 'bug', 'module', 'component', 'service', 'API', 'database', 'UI', 'backend', 'frontend'])[1 + ((i / 10) % 10)] || ' ' || i,
    NULL, NULL, NULL,
    1700060000000 + (i * 500),
    1700060000000 + (i * 500)
FROM generate_series(1, 1000) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:task-' || i || '-priority',
    'element:task-' || i,
    'field:task-priority',
    (ARRAY['Low', 'Medium', 'High', 'Critical'])[1 + (i % 4)],
    NULL, NULL, NULL,
    1700060000000 + (i * 500),
    1700060000000 + (i * 500)
FROM generate_series(1, 1000) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:task-' || i || '-status',
    'element:task-' || i,
    'field:task-status',
    (ARRAY['Todo', 'In Progress', 'Review', 'Done'])[1 + (i % 4)],
    NULL, NULL, NULL,
    1700060000000 + (i * 500),
    1700060000000 + (i * 500)
FROM generate_series(1, 1000) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:task-' || i || '-estimate',
    'element:task-' || i,
    'field:task-estimate',
    NULL,
    1 + (i % 40),
    NULL, NULL,
    1700060000000 + (i * 500),
    1700060000000 + (i * 500)
FROM generate_series(1, 1000) AS i;

-- Generate 300 Employees
INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
SELECT
    'element:employee-' || i,
    (ARRAY['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Emma', 'Robert', 'Olivia'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'])[1 + ((i / 10) % 10)],
    'type:employee',
    'space:acme-hr',
    1700070000000 + (i * 1000),
    'user:charlie'
FROM generate_series(1, 300) AS i;

-- Generate field values for Employees
INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:employee-' || i || '-name',
    'element:employee-' || i,
    'field:emp-name',
    (ARRAY['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Emma', 'Robert', 'Olivia'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'])[1 + ((i / 10) % 10)],
    NULL, NULL, NULL,
    1700070000000 + (i * 1000),
    1700070000000 + (i * 1000)
FROM generate_series(1, 300) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:employee-' || i || '-email',
    'element:employee-' || i,
    'field:emp-email',
    lower((ARRAY['john', 'jane', 'michael', 'sarah', 'david', 'emily', 'james', 'emma', 'robert', 'olivia'])[1 + (i % 10)]) || '.' ||
    lower((ARRAY['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis', 'rodriguez', 'martinez'])[1 + ((i / 10) % 10)]) || i || '@acme.com',
    NULL, NULL, NULL,
    1700070000000 + (i * 1000),
    1700070000000 + (i * 1000)
FROM generate_series(1, 300) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:employee-' || i || '-salary',
    'element:employee-' || i,
    'field:emp-salary',
    NULL,
    45000 + (i * 200) + (random() * 30000)::int,
    NULL, NULL,
    1700070000000 + (i * 1000),
    1700070000000 + (i * 1000)
FROM generate_series(1, 300) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:employee-' || i || '-department',
    'element:employee-' || i,
    'field:emp-department',
    (ARRAY['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations'])[1 + (i % 6)],
    NULL, NULL, NULL,
    1700070000000 + (i * 1000),
    1700070000000 + (i * 1000)
FROM generate_series(1, 300) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:employee-' || i || '-active',
    'element:employee-' || i,
    'field:emp-active',
    NULL, NULL, NULL,
    i % 10 != 0,
    1700070000000 + (i * 1000),
    1700070000000 + (i * 1000)
FROM generate_series(1, 300) AS i;

-- Generate 800 Products
INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
SELECT
    'element:product-' || i,
    (ARRAY['Premium', 'Basic', 'Pro', 'Elite', 'Standard', 'Deluxe', 'Ultra', 'Mini', 'Max', 'Lite'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Widget', 'Gadget', 'Device', 'Tool', 'Kit', 'System', 'Module', 'Unit', 'Pack', 'Set'])[1 + ((i / 10) % 10)] || ' ' ||
    (ARRAY['X', 'Y', 'Z', 'Alpha', 'Beta', 'Pro', 'Plus', 'Air', 'Max', 'One'])[1 + ((i / 100) % 10)],
    'type:product',
    'space:globex-products',
    1700150000000 + (i * 500),
    (ARRAY['user:diana', 'user:edward'])[1 + (i % 2)]
FROM generate_series(1, 800) AS i;

-- Generate field values for Products
INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:product-' || i || '-name',
    'element:product-' || i,
    'field:prod-name',
    (ARRAY['Premium', 'Basic', 'Pro', 'Elite', 'Standard', 'Deluxe', 'Ultra', 'Mini', 'Max', 'Lite'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Widget', 'Gadget', 'Device', 'Tool', 'Kit', 'System', 'Module', 'Unit', 'Pack', 'Set'])[1 + ((i / 10) % 10)] || ' ' ||
    (ARRAY['X', 'Y', 'Z', 'Alpha', 'Beta', 'Pro', 'Plus', 'Air', 'Max', 'One'])[1 + ((i / 100) % 10)],
    NULL, NULL, NULL,
    1700150000000 + (i * 500),
    1700150000000 + (i * 500)
FROM generate_series(1, 800) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:product-' || i || '-sku',
    'element:product-' || i,
    'field:prod-sku',
    'SKU-' || lpad(i::text, 6, '0'),
    NULL, NULL, NULL,
    1700150000000 + (i * 500),
    1700150000000 + (i * 500)
FROM generate_series(1, 800) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:product-' || i || '-price',
    'element:product-' || i,
    'field:prod-price',
    NULL,
    9.99 + (i % 100) * 10 + (random() * 100)::int,
    NULL, NULL,
    1700150000000 + (i * 500),
    1700150000000 + (i * 500)
FROM generate_series(1, 800) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:product-' || i || '-stock',
    'element:product-' || i,
    'field:prod-stock',
    NULL,
    (random() * 1000)::int,
    NULL, NULL,
    1700150000000 + (i * 500),
    1700150000000 + (i * 500)
FROM generate_series(1, 800) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:product-' || i || '-available',
    'element:product-' || i,
    'field:prod-available',
    NULL, NULL, NULL,
    i % 5 != 0,
    1700150000000 + (i * 500),
    1700150000000 + (i * 500)
FROM generate_series(1, 800) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:product-' || i || '-category',
    'element:product-' || i,
    'field:prod-category',
    (ARRAY['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys'])[1 + (i % 6)],
    NULL, NULL, NULL,
    1700150000000 + (i * 500),
    1700150000000 + (i * 500)
FROM generate_series(1, 800) AS i;

-- Generate 400 Customers
INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
SELECT
    'element:customer-' || i,
    (ARRAY['Acme', 'Global', 'Prime', 'Metro', 'Alpha', 'Omega', 'Summit', 'Peak', 'Core', 'Edge'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Industries', 'Solutions', 'Systems', 'Technologies', 'Enterprises', 'Group', 'Corp', 'Inc', 'LLC', 'Partners'])[1 + ((i / 10) % 10)],
    'type:customer',
    'space:globex-customers',
    1700160000000 + (i * 1000),
    'user:fiona'
FROM generate_series(1, 400) AS i;

-- Generate field values for Customers
INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:customer-' || i || '-company',
    'element:customer-' || i,
    'field:cust-company',
    (ARRAY['Acme', 'Global', 'Prime', 'Metro', 'Alpha', 'Omega', 'Summit', 'Peak', 'Core', 'Edge'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Industries', 'Solutions', 'Systems', 'Technologies', 'Enterprises', 'Group', 'Corp', 'Inc', 'LLC', 'Partners'])[1 + ((i / 10) % 10)],
    NULL, NULL, NULL,
    1700160000000 + (i * 1000),
    1700160000000 + (i * 1000)
FROM generate_series(1, 400) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:customer-' || i || '-email',
    'element:customer-' || i,
    'field:cust-email',
    'contact@' || lower((ARRAY['acme', 'global', 'prime', 'metro', 'alpha', 'omega', 'summit', 'peak', 'core', 'edge'])[1 + (i % 10)]) || i || '.com',
    NULL, NULL, NULL,
    1700160000000 + (i * 1000),
    1700160000000 + (i * 1000)
FROM generate_series(1, 400) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:customer-' || i || '-revenue',
    'element:customer-' || i,
    'field:cust-revenue',
    NULL,
    100000 + (i * 5000) + (random() * 1000000)::int,
    NULL, NULL,
    1700160000000 + (i * 1000),
    1700160000000 + (i * 1000)
FROM generate_series(1, 400) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:customer-' || i || '-tier',
    'element:customer-' || i,
    'field:cust-tier',
    (ARRAY['Bronze', 'Silver', 'Gold', 'Platinum'])[1 + (i % 4)],
    NULL, NULL, NULL,
    1700160000000 + (i * 1000),
    1700160000000 + (i * 1000)
FROM generate_series(1, 400) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:customer-' || i || '-active',
    'element:customer-' || i,
    'field:cust-active',
    NULL, NULL, NULL,
    i % 8 != 0,
    1700160000000 + (i * 1000),
    1700160000000 + (i * 1000)
FROM generate_series(1, 400) AS i;

-- Generate 600 Support Tickets
INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
SELECT
    'element:ticket-' || i,
    (ARRAY['Cannot', 'Unable to', 'Issue with', 'Problem:', 'Error in', 'Bug:', 'Request:', 'Help with', 'Question about', 'Need'])[1 + (i % 10)] || ' ' ||
    (ARRAY['login', 'access', 'export', 'import', 'sync', 'update', 'install', 'configure', 'connect', 'load'])[1 + ((i / 10) % 10)] || ' ' ||
    (ARRAY['feature', 'module', 'report', 'dashboard', 'API', 'integration', 'settings', 'account', 'data', 'service'])[1 + ((i / 100) % 10)],
    'type:ticket',
    'space:initech-tasks',
    1700250000000 + (i * 500),
    (ARRAY['user:george', 'user:hannah', 'user:julia'])[1 + (i % 3)]
FROM generate_series(1, 600) AS i;

-- Generate field values for Tickets
INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:ticket-' || i || '-title',
    'element:ticket-' || i,
    'field:ticket-title',
    (ARRAY['Cannot', 'Unable to', 'Issue with', 'Problem:', 'Error in', 'Bug:', 'Request:', 'Help with', 'Question about', 'Need'])[1 + (i % 10)] || ' ' ||
    (ARRAY['login', 'access', 'export', 'import', 'sync', 'update', 'install', 'configure', 'connect', 'load'])[1 + ((i / 10) % 10)] || ' ' ||
    (ARRAY['feature', 'module', 'report', 'dashboard', 'API', 'integration', 'settings', 'account', 'data', 'service'])[1 + ((i / 100) % 10)],
    NULL, NULL, NULL,
    1700250000000 + (i * 500),
    1700250000000 + (i * 500)
FROM generate_series(1, 600) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:ticket-' || i || '-desc',
    'element:ticket-' || i,
    'field:ticket-desc',
    'User reported an issue with ' ||
    (ARRAY['the system', 'their account', 'a feature', 'the application', 'loading data'])[1 + (i % 5)] ||
    '. Steps to reproduce: 1. Open the application 2. Navigate to ' ||
    (ARRAY['dashboard', 'settings', 'reports', 'profile', 'admin panel'])[1 + ((i / 5) % 5)] ||
    ' 3. Observe the issue.',
    NULL, NULL, NULL,
    1700250000000 + (i * 500),
    1700250000000 + (i * 500)
FROM generate_series(1, 600) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:ticket-' || i || '-priority',
    'element:ticket-' || i,
    'field:ticket-priority',
    (ARRAY['Low', 'Medium', 'High', 'Urgent'])[1 + (i % 4)],
    NULL, NULL, NULL,
    1700250000000 + (i * 500),
    1700250000000 + (i * 500)
FROM generate_series(1, 600) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:ticket-' || i || '-status',
    'element:ticket-' || i,
    'field:ticket-status',
    (ARRAY['Open', 'In Progress', 'Waiting', 'Resolved', 'Closed'])[1 + (i % 5)],
    NULL, NULL, NULL,
    1700250000000 + (i * 500),
    1700250000000 + (i * 500)
FROM generate_series(1, 600) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, value_json, creation_date, updated_date)
SELECT
    'efv:ticket-' || i || '-created',
    'element:ticket-' || i,
    'field:ticket-created',
    NULL, NULL,
    1700250000000 + (i * 500),
    NULL, NULL,
    1700250000000 + (i * 500),
    1700250000000 + (i * 500)
FROM generate_series(1, 600) AS i;

-- Generate 500 Inventory Items
INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
SELECT
    'element:inventory-' || i,
    (ARRAY['Steel', 'Copper', 'Aluminum', 'Plastic', 'Rubber', 'Glass', 'Wood', 'Carbon', 'Silicon', 'Titanium'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Rod', 'Sheet', 'Tube', 'Wire', 'Plate', 'Block', 'Strip', 'Bar', 'Coil', 'Panel'])[1 + ((i / 10) % 10)] || ' ' ||
    (ARRAY['10mm', '20mm', '50mm', '100mm', '5mm', '15mm', '25mm', '75mm', '1m', '2m'])[1 + ((i / 100) % 10)],
    'type:item',
    'space:initech-inventory',
    1700260000000 + (i * 500),
    'user:ivan'
FROM generate_series(1, 500) AS i;

-- Generate field values for Inventory Items
INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:inventory-' || i || '-name',
    'element:inventory-' || i,
    'field:inv-name',
    (ARRAY['Steel', 'Copper', 'Aluminum', 'Plastic', 'Rubber', 'Glass', 'Wood', 'Carbon', 'Silicon', 'Titanium'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Rod', 'Sheet', 'Tube', 'Wire', 'Plate', 'Block', 'Strip', 'Bar', 'Coil', 'Panel'])[1 + ((i / 10) % 10)] || ' ' ||
    (ARRAY['10mm', '20mm', '50mm', '100mm', '5mm', '15mm', '25mm', '75mm', '1m', '2m'])[1 + ((i / 100) % 10)],
    NULL, NULL, NULL,
    1700260000000 + (i * 500),
    1700260000000 + (i * 500)
FROM generate_series(1, 500) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:inventory-' || i || '-sku',
    'element:inventory-' || i,
    'field:inv-sku',
    'INV-' || lpad(i::text, 6, '0'),
    NULL, NULL, NULL,
    1700260000000 + (i * 500),
    1700260000000 + (i * 500)
FROM generate_series(1, 500) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:inventory-' || i || '-quantity',
    'element:inventory-' || i,
    'field:inv-quantity',
    NULL,
    (random() * 10000)::int,
    NULL, NULL,
    1700260000000 + (i * 500),
    1700260000000 + (i * 500)
FROM generate_series(1, 500) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:inventory-' || i || '-unit-cost',
    'element:inventory-' || i,
    'field:inv-unit-cost',
    NULL,
    0.5 + (random() * 100)::numeric(10,2),
    NULL, NULL,
    1700260000000 + (i * 500),
    1700260000000 + (i * 500)
FROM generate_series(1, 500) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:inventory-' || i || '-location',
    'element:inventory-' || i,
    'field:inv-location',
    (ARRAY['Warehouse A', 'Warehouse B', 'Warehouse C', 'Store Front'])[1 + (i % 4)],
    NULL, NULL, NULL,
    1700260000000 + (i * 500),
    1700260000000 + (i * 500)
FROM generate_series(1, 500) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:inventory-' || i || '-active',
    'element:inventory-' || i,
    'field:inv-active',
    NULL, NULL, NULL,
    i % 6 != 0,
    1700260000000 + (i * 500),
    1700260000000 + (i * 500)
FROM generate_series(1, 500) AS i;

-- Generate 100 Suppliers
INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
SELECT
    'element:supplier-' || i,
    (ARRAY['Global', 'Premier', 'Quality', 'Express', 'Direct', 'Prime', 'Elite', 'Pro', 'Master', 'First'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Supply', 'Materials', 'Trading', 'Distribution', 'Wholesale', 'Imports', 'Exports', 'Logistics', 'Commerce', 'Sourcing'])[1 + ((i / 10) % 10)] || ' Co.',
    'type:supplier',
    'space:initech-inventory',
    1700270000000 + (i * 1000),
    'user:ivan'
FROM generate_series(1, 100) AS i;

-- Generate field values for Suppliers
INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:supplier-' || i || '-name',
    'element:supplier-' || i,
    'field:sup-name',
    (ARRAY['Global', 'Premier', 'Quality', 'Express', 'Direct', 'Prime', 'Elite', 'Pro', 'Master', 'First'])[1 + (i % 10)] || ' ' ||
    (ARRAY['Supply', 'Materials', 'Trading', 'Distribution', 'Wholesale', 'Imports', 'Exports', 'Logistics', 'Commerce', 'Sourcing'])[1 + ((i / 10) % 10)] || ' Co.',
    NULL, NULL, NULL,
    1700270000000 + (i * 1000),
    1700270000000 + (i * 1000)
FROM generate_series(1, 100) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:supplier-' || i || '-email',
    'element:supplier-' || i,
    'field:sup-email',
    'sales@' || lower((ARRAY['global', 'premier', 'quality', 'express', 'direct', 'prime', 'elite', 'pro', 'master', 'first'])[1 + (i % 10)]) || 'supply' || i || '.com',
    NULL, NULL, NULL,
    1700270000000 + (i * 1000),
    1700270000000 + (i * 1000)
FROM generate_series(1, 100) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:supplier-' || i || '-rating',
    'element:supplier-' || i,
    'field:sup-rating',
    (ARRAY['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'])[1 + (i % 5)],
    NULL, NULL, NULL,
    1700270000000 + (i * 1000),
    1700270000000 + (i * 1000)
FROM generate_series(1, 100) AS i;

INSERT INTO public.element_field_values (uri, element_uri, field_uri, value_text, value_number, value_date, value_boolean, creation_date, updated_date)
SELECT
    'efv:supplier-' || i || '-active',
    'element:supplier-' || i,
    'field:sup-active',
    NULL, NULL, NULL,
    i % 5 != 0,
    1700270000000 + (i * 1000),
    1700270000000 + (i * 1000)
FROM generate_series(1, 100) AS i;

-- =============================================================================
-- SUMMARY: Total generated data
-- - 10 Users
-- - 3 Tenants
-- - 4 Permission Verbs
-- - 6 Spaces
-- - 12 Types
-- - 54 Fields
-- - 3,700 Elements (500 projects + 1000 tasks + 300 employees + 800 products + 400 customers + 600 tickets + 500 inventory items + 100 suppliers)
-- - ~18,500 Element Field Values
-- =============================================================================
