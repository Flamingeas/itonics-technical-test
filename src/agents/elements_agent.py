import os
import time
import db
from agents.llm import _llm, run_react_loop
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

CURRENT_USER = os.getenv("CURRENT_USER")

_context_cache: dict[str, tuple[str, float]] = {}  # user_uri -> context & timestamp
_user_spaces: dict[str, set[str]] = {}  # user_uri -> set of accessible space URIs
_CACHE_TTL = 300  # seconds; store for 4-5min


@tool
def list_spaces_tool() -> str:
    """List all spaces the current user has access to, with their URIs and tenant."""
    try:
        spaces = db.list_user_spaces(CURRENT_USER)
    except Exception as e:
        return f"Database error while listing spaces: {e}"
    if not spaces:
        return "No spaces found for the current user."
    lines = [
        f"- {s['uri']}: {s['name']} (tenant: {s['tenant_uri']}, write: {'yes' if s['can_write'] else 'no'})"
        for s in spaces
    ]
    return "\n".join(lines)


@tool
def list_types_tool(space_uri: str) -> str:
    """List all element types available in a space.

    Args:
        space_uri: URI of the space (e.g. 'space:acme-projects').
    """
    try:
        types = db.list_types_in_space(space_uri)
    except Exception as e:
        return f"Database error while listing types: {e}"
    if not types:
        return f"No types found in space {space_uri!r}."
    lines = [f"- {t['uri']}: {t['name']}" for t in types]
    return "\n".join(lines)


_GENERIC_QUERIES = {"all", "everything", "elements", "list", "show", "tasks", "items", "any", "every"}


@tool
def search_elements_tool(space_uri: str, query: str = "", limit: int = 10) -> str:
    """Search for elements in a space by title keyword.

    Args:
        space_uri: URI of the space to search in (e.g. 'space:acme-projects').
        query: Keyword to look for in element titles (case-insensitive).
               IMPORTANT: pass query="" (empty string) to list ALL elements.
               Never pass "all", "everything", or similar words as the query.
        limit: Max number of results to return. Use 1 for "latest" or "most recent".
               Default is 10 for keyword searches, use 20 for full listings.
    """
    if query.lower() in _GENERIC_QUERIES:
        query = ""
    if not space_uri.startswith("space:"):
        return f"Invalid space_uri {space_uri!r}. Use the exact space_uri from the context (e.g. 'space:acme-projects')."
    accessible = _user_spaces.get(CURRENT_USER, set()) if CURRENT_USER else set()
    if accessible and space_uri not in accessible:
        valid = ", ".join(f'"{s}"' for s in sorted(accessible))
        return f"Unknown space_uri {space_uri!r}. Valid spaces are: {valid}. Use one of these exactly."
    try:
        results = db.search_elements(space_uri, query, limit=limit)
    except Exception as e:
        return f"Database error while searching elements: {e}"
    if not results:
        return f"No elements found in {space_uri!r} matching {query!r}."
    lines = [f"- {r['uri']}: {r['title']}" for r in results]
    total_hint = f"\n(showing {len(results)} results)" if len(results) == limit and limit > 1 else ""
    return "\n".join(lines) + total_hint


@tool
def create_element_tool(space_uri: str, type_uri: str, title: str) -> str:
    """Create a new element in a space.

    Args:
        space_uri: URI of the space (e.g. 'space:acme-projects').
        type_uri: URI of the element type (e.g. 'type:project').
        title: Title for the new element.
    """
    if not space_uri.startswith("space:"):
        return f"Invalid space_uri {space_uri!r}. Use the exact space_uri from the context (e.g. 'space:acme-projects')."
    if CURRENT_USER and space_uri not in _user_spaces.get(CURRENT_USER, set()):
        return f"Space {space_uri!r} is not accessible to you. Use one of the spaces listed in the context."
    if not type_uri.startswith("type:"):
        return f"Invalid type_uri {type_uri!r}. Use the exact type_uri from the context (e.g. 'type:project')."
    try:
        element = db.create_element(CURRENT_USER, space_uri, type_uri, title)
    except PermissionError as e:
        return f"Permission denied: {e}"
    except Exception as e:
        return f"Database error while creating element: {e}"
    return f"Created \"{element['title']}\" successfully."



@tool
def update_element_title_tool(element_uri: str, new_title: str) -> str:
    """Update the title of an existing element.

    Args:
        element_uri: URI of the element to update (e.g. 'element:acme-projects:abc123').
        new_title: The new title to set.
    """
    try:
        element = db.update_element_title(CURRENT_USER, element_uri, new_title)
    except PermissionError as e:
        return f"Permission denied: {e}"
    except ValueError as e:
        return f"Element not found: {e}"
    except Exception as e:
        return f"Database error while updating element: {e}"
    return f"Updated title to \"{element['title']}\" successfully."


_tools = [list_spaces_tool, list_types_tool, search_elements_tool, create_element_tool, update_element_title_tool]
_llm_with_tools = _llm.bind_tools(_tools)
_tool_map = {t.name: t for t in _tools}

_SYSTEM = SystemMessage(content=(
    "You are a helpful assistant managing elements in a workspace.\n"
    "Rules:\n"
    "- NEVER show URIs, JSON, or technical field names. Use human-readable names only. Plain text only — no markdown links.\n"
    "- NEVER list elements from memory. Always call search_elements_tool to get live data.\n"
    "- Refer to results as 'elements' or by their type name (e.g. 'tickets'), never as 'ideas'.\n"
    "- For create/update: if the requested space is not in your context or is not writable, say so. NEVER redirect to a different space.\n"
    "- To update an element, ALWAYS call search_elements_tool first to get the exact URI.\n"
    "- If a piece of info is missing, ask ONE short question. Never ask for what the user already provided.\n"
    "- CRITICAL: always call the appropriate tool. Never confirm an action unless the tool succeeded. Report tool errors to the user."
))


def _build_context() -> str:
    """Pre-load spaces and types so the LLM has all info before its first call.

    Result is cached per user for _CACHE_TTL seconds to avoid redundant DB calls
    across consecutive messages within the same session.
    """
    now = time.time()
    if CURRENT_USER and CURRENT_USER in _context_cache:
        cached_context, cached_at = _context_cache[CURRENT_USER]
        if now - cached_at < _CACHE_TTL:
            return cached_context

    try:
        spaces = db.list_user_spaces(CURRENT_USER)
    except Exception as e:
        return f"Could not load spaces: {e}"
    if not spaces:
        return "No spaces available for the current user."
    lines = [
        "IMPORTANT: Always use the exact space_uri and type_uri values listed below.",
        "Never construct or guess URIs — copy them exactly as shown.",
        "",
        "Available spaces:",
    ]
    for s in spaces:
        can_write = s["can_write"]
        slug = s["uri"].split(":", 1)[-1]  # e.g. "space:initech-tasks" → "initech-tasks"
        lines.append(f'  Display name: "{s["name"]}" | also known as: "{slug}" | space_uri: "{s["uri"]}" | writable: {"yes" if can_write else "no"}')
        if can_write:
            try:
                types = db.list_types_in_space(s["uri"])
                for t in types:
                    lines.append(f'    Display name: "{t["name"]}" | type_uri: "{t["uri"]}"')
            except Exception:
                pass
    context = "\n".join(lines)
    if CURRENT_USER:
        _context_cache[CURRENT_USER] = (context, now)
        _user_spaces[CURRENT_USER] = {s["uri"] for s in spaces}
    return context


def run_elements_agent(user_message: str, history: list | None = None) -> str:
    context = _build_context()
    messages: list = [_SYSTEM, SystemMessage(content=context), *(history or []), HumanMessage(content=user_message)]
    return run_react_loop(messages, _llm_with_tools, _tool_map, stop_on=set())
