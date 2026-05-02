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

---

# Solution (by Samyra Mangan Mben)

## Approach

The solution implements a two-agent architecture using **LangChain** (`0.3.14`) with **Ollama** (`qwen2.5:3b`) as the LLM backend.

### Agent design

```
handle_user_input()  (src/main.py)
        │
        ▼
  run_orchestrator()  (src/agents/orchestrator.py)
        │
        ├── keyword short-circuit (_is_element_task)
        │       └──► run_elements_agent()  (direct, no extra LLM call)
        │
        └── LLM call (casual / ambiguous)
                └──► call_elements_agent_tool  →  run_elements_agent()
```

**Orchestrator** — routes requests to the elements agent or responds directly to casual conversation. Common element-related keywords (search, create, update, find…) short-circuit the LLM routing step entirely, cutting latency roughly in half.

**Elements agent** — handles all DB operations through six LangChain tools:

| Tool | Operation |
|---|---|
| `list_spaces_tool` | Discover spaces the user can access |
| `list_types_tool` | Discover element types in a space |
| `search_elements_tool` | ILIKE search on element titles |
| `create_element_tool` | Insert a new element |
| `update_element_title_tool` | Rename an existing element |
| `delete_element_tool` | Permanently delete an element |

The agent runs a ReAct loop (`run_react_loop` in `src/agents/llm.py`) capped at 3 iterations. `stop_on=set()` lets the loop run until the LLM produces a natural language response — this is what allows the agent to confirm a write operation and immediately follow up with the updated element list, all in one reply.

### Context pre-loading

Before the first LLM call, `_build_context()` queries the user's accessible spaces and the types of each writable space, then injects an explicit `name → uri` mapping as a `SystemMessage`. The LLM uses this to resolve natural language ("Projects", "Task") to the correct URIs internally, without ever exposing them to the user. The result is cached per user for 5 minutes to reduce DB round-trips.

### Permission model

Permissions are enforced at the space level via `user_space_permissions`. `db.has_permission(user_uri, space_uri, "verb:write")` is called inside `create_element`, `update_element_title`, and `delete_element` before any write. `PermissionError` propagates to the tool layer where it is caught and returned as a user-friendly message. `create_element_tool` also validates the target space against a cached `_user_spaces` set, rejecting hallucinated URIs before they reach the DB.


### SQL safety

All queries use psycopg2 parameterized statements (`%s` placeholders). String interpolation in SQL is never used.

### Element URIs

Created elements get a human-readable URI derived from the title slug, suffixed with 6 hex chars for uniqueness. The update operation only supports changing the element title. Example of URI format :

```
"AI Assistant" → element:acme-projects:ai-assistant-a3f2b1
```

### Chat display

The dashboard shows a timestamp (UTC+2) under each message. Consecutive messages from the same user are kept separate (not merged). Conversation history survives page refreshes.


## Running the solution

To run unit tests:
```bash
docker compose up --build pytest
```

## Development process

The solution was built iteratively over several sessions, each focused on a specific layer or concern.

**Apr 23: Project setup & schema analysis**
Reviewed the full database schema (11 SQL files), mapped foreign key dependencies, and identified a gap in the sample data: `user_space_permissions` had no rows, making all write operations silently fail. Created a course notes document to track reasoning and decisions throughout the project.

**Apr 24: DB layer & first agent tool**
Built `db.py` with a `ThreadedConnectionPool` (thread-safe for Streamlit's background threads), a `get_cursor()` context manager, and parameterized queries throughout. Implemented the first LangChain tool (`search_elements_tool`) with a ReAct loop. Introduced 3-level error handling (tool → agent loop → `handle_user_input`) and switched `CURRENT_USER` to an environment variable to avoid hardcoded test users.

**Apr 25: Orchestrator & conversation history**
Built the orchestrator agent with `call_elements_agent_tool` as its single dispatch tool. Implemented `_build_history_messages()` to reconstruct full conversation turns from streamed `ChatMessage` chunks, giving the LLM proper multi-turn context. Added a system prompt to allow casual conversation without routing to an agent.

**Apr 28: Latency optimisation & bug fixes**
Identified that element tasks triggered 4 sequential LLM calls. Cut to 2 by returning tool results directly instead of re-summarising. Fixed a bug where the LLM passed `<nil>` as `space_uri` by adding a `list_spaces` discovery step. Improved streaming speed (3 chars / 0.15s → 15 chars / 0.03s).

**Apr 29: Refactor & context pre-loading**
Reorganised all agent code into `src/agents/` (llm.py, elements_agent.py, orchestrator.py). Added `_build_context()` to pre-inject a spaces/types mapping as a `SystemMessage`, removing the need for multi-step LLM discovery. Added `_is_element_task()` keyword short-circuit in the orchestrator, cutting latency from ~3m30s to ~1m46s. Extracted the shared `run_react_loop()`. Added a 5-minute context cache to avoid repeated DB queries.

**Apr 29: Unit tests & evaluation review**
Wrote a full unit test suite (48 tests across 5 files) covering the DB layer, tool output formatting, LLM tool call parsing, history reconstruction, and orchestrator routing. Added pytest infrastructure (pytest.ini, conftest.py with Ollama mock, Docker service).

**May 2: QA, UX & model tuning**
Ran end-to-end QA against all evaluation criteria. Fixed the missing write permissions in sample data. Switched LLM from `llama3.1` (~2 min/call on CPU) to `qwen2.5:3b` (faster, reliable tool calling). Fixed dashboard message merging (consecutive user messages were collapsed into one). Added UTC+2 timestamps and conversation persistence across page refreshes. Rewrote the elements agent system prompt to respond in plain language and hide URIs. Introduced human-readable element URIs built from title slugs. Added URI format validation in tools to allow the LLM to self-correct on bad inputs.

**May 3: Delete feature & UX polish**
Added `delete_element_tool` with `db.delete_element()` — raises `ValueError` if the element doesn't exist and `PermissionError` if the user lacks write access on its space. Switched the ReAct loop to `stop_on=set()` so that after any write operation the LLM can confirm success and show the updated element list in one reply, removing the need for the user to ask a follow-up. Added a `_GENERIC_QUERIES` sanitisation step in `search_elements_tool` that converts broad terms ("elements", "list", "show", "all") to `query=""`, preventing the LLM from triggering a no-match loop that would cause a multi-minute freeze. Added a `_warmup()` daemon thread in `main.py` that pre-loads the LLM model into VRAM and primes the context cache before the first user message arrives.


## Known limitations

- **Current user via env var** — there is no auth system in the dashboard. The active user is set through the `CURRENT_USER` environment variable (default: `user:alice`).
- **Model choice** — `qwen2.5:3b` was selected over larger models to prioritise response time, since low latency is critical for a conversational interface. It occasionally misroutes ambiguous requests, but the DB-level permission check always acts as the safety net for write operations.
