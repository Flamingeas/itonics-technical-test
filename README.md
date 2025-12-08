# Instructions

The files on this directory contain tools to bootstrap a Postgres database
using docker and docker compose.

## Getting Started

### Prerequisites
- Docker and Docker Compose installed

### Starting the Database

Start the PostgreSQL database with sample data:
```bash
docker compose up postgres
```

The database will initialize with all tables and sample data from the `sql/` directory.


### Connecting to the Database

Connect to the database using psql:
```bash
docker exec -it postgres psql -U postgres -d technical_assessment
```

Useful commands to verify the database:
```sql
-- List all tables
\dt

-- Check sample users
SELECT * FROM users;

-- Check spaces and their tenants
SELECT s.name as space, t.name as tenant
FROM spaces s
JOIN tenants t ON s.tenant_uri = t.uri;

-- Exit psql
\q
```

# Tables and relations

The database contains multiple tables, all of them available on the `public` schema.

## Core Entities

### users
Represents system users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uri | TEXT | PRIMARY KEY | Unique user identifier |
| email | TEXT | NOT NULL, UNIQUE | User email address |
| display_name | TEXT | NOT NULL | User's display name |

### tenants
Top-level organization containers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uri | TEXT | PRIMARY KEY | Unique tenant identifier |
| name | TEXT | NOT NULL | Tenant name |
| creation_date | BIGINT | NOT NULL | Unix timestamp of creation |
| status | TEXT | NOT NULL, CHECK | Tenant status ('active' or 'inactive') |

### spaces
Workspaces within tenants where elements are organized.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uri | TEXT | PRIMARY KEY | Unique space identifier |
| name | TEXT | NOT NULL | Space name |
| creation_date | BIGINT | NOT NULL | Unix timestamp of creation |
| tenant_uri | TEXT | NOT NULL, FK → tenants(uri) | Parent tenant |

### types
Element type definitions within spaces.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uri | TEXT | PRIMARY KEY | Unique type identifier |
| space_uri | TEXT | NOT NULL, FK → spaces(uri) | Parent space |
| name | TEXT | NOT NULL | Type name |
| creation_date | BIGINT | NOT NULL | Unix timestamp of creation |
| author | TEXT | NOT NULL, FK → users(uri) | Creator user |

### elements
The main content entities (ideas, items, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uri | TEXT | PRIMARY KEY | Unique element identifier |
| title | TEXT | NOT NULL | Element title |
| type_uri | TEXT | NOT NULL, FK → types(uri) | Element type |
| space_uri | TEXT | NOT NULL, FK → spaces(uri) | Parent space |
| creation_date | BIGINT | NOT NULL | Unix timestamp of creation |
| author | TEXT | NOT NULL, FK → users(uri) | Creator user |

### fields
Custom field definitions for types.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uri | TEXT | PRIMARY KEY | Unique field identifier |
| name | TEXT | NOT NULL | Field name |
| field_type | TEXT | NOT NULL, CHECK | Field type ('text', 'number', 'date', 'boolean', 'select', 'multi_select', 'url', 'email') |
| type_uri | TEXT | NOT NULL, FK → types(uri) | Parent type |
| creation_date | BIGINT | NOT NULL | Unix timestamp of creation |
| author | TEXT | NOT NULL, FK → users(uri) | Creator user |
| options | JSONB | DEFAULT NULL | Options for select/multi_select fields |
| required | BOOLEAN | DEFAULT FALSE | Whether field is required |

**Indexes:** `idx_fields_type_uri` on `type_uri`

### element_field_values
Stores actual values for element fields.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uri | TEXT | PRIMARY KEY | Unique value identifier |
| element_uri | TEXT | NOT NULL, FK → elements(uri) ON DELETE CASCADE | Parent element |
| field_uri | TEXT | NOT NULL, FK → fields(uri) ON DELETE CASCADE | Field definition |
| value_text | TEXT | NULL | Text value storage |
| value_number | DOUBLE PRECISION | NULL | Numeric value storage |
| value_date | BIGINT | NULL | Date value storage (Unix timestamp) |
| value_boolean | BOOLEAN | NULL | Boolean value storage |
| value_json | JSONB | NULL | JSON value storage (for select/multi_select) |
| creation_date | BIGINT | NOT NULL | Unix timestamp of creation |
| updated_date | BIGINT | NOT NULL | Unix timestamp of last update |

**Constraints:** UNIQUE(element_uri, field_uri)
**Indexes:** `idx_element_field_values_element` on `element_uri`, `idx_element_field_values_field` on `field_uri`

## Permission & Access Tables

### permission_verbs
Defines available permission types.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| uri | TEXT | PRIMARY KEY | Unique permission verb identifier |
| name | TEXT | NOT NULL, UNIQUE | Permission name (e.g., 'read', 'write', 'delete') |
| description | TEXT | NULL | Permission description |

### user_tenants
Many-to-many relationship between users and tenants.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_uri | TEXT | NOT NULL, FK → users(uri) | User identifier |
| tenant_uri | TEXT | NOT NULL, FK → tenants(uri) | Tenant identifier |

**Constraints:** PRIMARY KEY (user_uri, tenant_uri)

### user_spaces
Many-to-many relationship between users and spaces.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_uri | TEXT | NOT NULL, FK → users(uri) | User identifier |
| space_uri | TEXT | NOT NULL, FK → spaces(uri) | Space identifier |

**Constraints:** PRIMARY KEY (user_uri, space_uri)

### user_space_permissions
Defines user permissions within specific spaces.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_uri | TEXT | NOT NULL, FK → users(uri) | User identifier |
| space_uri | TEXT | NOT NULL, FK → spaces(uri) | Space identifier |
| verb_uri | TEXT | NOT NULL, FK → permission_verbs(uri) | Permission type |

**Constraints:** PRIMARY KEY (user_uri, space_uri, verb_uri)

## Relationship Summary

```
users ──┬─── user_tenants ──── tenants
        │
        ├─── user_spaces ────┬─── spaces ─── types ─── fields
        │                    │                │
        └─── user_space_permissions          └─── elements ─── element_field_values
                             │
                             └─── permission_verbs
```

**Key Relationships:**
- Users can be part of multiple tenants and spaces (many-to-many)
- Tenants can have multiple spaces (one-to-many)
- A space belongs to exactly one tenant (many-to-one)
- An element belongs to exactly one space and one type (many-to-one)
- Types define the structure (fields) for elements
- Element field values store the actual data for each element's fields
- Permissions are granted at the space level for specific actions (verbs)

# Use case

Our customers are often faced with different challenges during their innovation
cycle:

- Generating new ideas that are in line with the market.
- Managing existing ideas.
- Making it easier for their users to use ITONICS.

Instead of making them always use a classic form interface, we want to leverage
LLMs and AI to provide support during this task. Essentially, we need to build
a chat-based solution that can help users do different actions such as:

- Reviewing and summarizing existing ideas.
- Creating new ideas and updating existing ones.
- Deleting those that are no longer relevant.

# Task

Build 2 AI Agents:

- Orchestrator agent: handles requests and dispatches work to other agents
- Elements agent: handles request related to elements. It should be able to:
    - Search elements.
    - Create elements.
    - Update elements: changing the title is enough.

Implement your solution logic in `src/main.py`. The dashboard will automatically call your `handle_user_input()` function when users send messages.

Available utilities are documented in `src/chat_utils.py` and example usage is in `src/main_example.py`.

The code can and should be organized in multiple files and modules, but `src/main.py` is the entrypoint
that is connected to the UI, so make sure the whole solution can be run from it.

## Chat UI

Just like in the real application, the UI part is already implemented. The solution
only needs to integrate with it.

### Starting the Chat Dashboard

The chat dashboard can run in two modes (configured via `.env` file):

**Example mode**:

Use this to verify that everything is working

```bash
# Create .env file with:
CHAT_MODE=example

# Start dashboard
docker compose up --build dashboard
```

**Solution mode**:
Use this to test and iterate over your solution

```bash
# Create .env file with:
CHAT_MODE=solution

# Start dashboard
docker compose up --build dashboard
```

Access the dashboard at: http://localhost:8501


# Evaluation

This is an open-ended use case, so there are no strictly right or wrong answers. However, we will evaluate your solution based on the following criteria:

## Functionality
- **Agent Implementation**: Both orchestrator and elements agents must be implemented and working
- **Required Operations**: Search, create, and update elements must function correctly
- **Chat Integration**: The solution integrates properly with the provided chat dashboard
- **Database Interaction**: Correct querying and manipulation of the database
- **Portability**: The solution runs successfully using the provided Docker setup without modifications

## Code Quality
- **Structure & Organization**: Clean, modular code with clear separation of concerns
- **Type Safety**: All code must be properly typed and pass `mypy==1.18.2` validation. This
can be tested with `docker compose up --build mypy`
- **Readability**: Code is self-documenting with appropriate naming and structure
- **Error Handling**: Graceful handling of edge cases and error conditions
- **Testing**: Unit tests covering key functionality

## Security
- **Permission Checks**: User permissions (user_space_permissions) are properly validated before operations
- **Input Validation**: User inputs are sanitized and validated
- **SQL Injection Prevention**: Safe database query practices

## Architecture & Design
- **Scalability**: Solution design considers future growth and additional agents
- **Performance**: Efficient database queries and resource usage
- **Agent Communication**: Clear interface between orchestrator and specialized agents
- **Extensibility**: Easy to add new agents or capabilities

## Development Practices
- **Version Control**: Meaningful git commits showing development progression
- **Documentation**: Clear explanation of approach, setup, and usage
- **Dependencies**: Appropriate use of libraries and dependencies

# Deliverable Format

The solution must be delivered in a Docker-friendly format:

- Builds and runs using Docker Compose with the provided setup
- All dependencies specified in `requirements.txt`
- Works immediately after cloning and running `docker compose up --build dashboard`
- Multiple containers can be used if needed for your architecture
- The existing `src/main.py` must remain as the entry point for the chat interface
