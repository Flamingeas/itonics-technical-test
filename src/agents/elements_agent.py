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
    if not space_uri.startswith("space:"):
        return f"Invalid space_uri {space_uri!r}. Use the exact space_uri from the context (e.g. 'space:acme-projects')."
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
    return f"Created element {element['uri']!r} with title {element['title']!r}."


@tool
def delete_element_tool(element_uri: str) -> str:
    """Delete an element permanently.
    Args:
        element_uri: URI of the element to delete (e.g. 'element:acme-projects:ai-assistant-a3f2b1').
    """
    if not element_uri.startswith("element:"):
        return f"Invalid element_uri {element_uri!r}. Use the exact URI from a previous search result."
    try:
        db.delete_element(CURRENT_USER, element_uri)
    except PermissionError as e:
        return f"Permission denied: {e}"
    except ValueError as e:
        return f"Element not found: {e}"
    except Exception as e:
        return f"Database error while deleting element: {e}"
    return f"Element {element_uri!r} has been deleted."


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
    return f"Updated element {element['uri']!r} — new title: {element['title']!r}."


_tools = [list_spaces_tool, list_types_tool, search_elements_tool, create_element_tool, update_element_title_tool, delete_element_tool]
_llm_with_tools = _llm.bind_tools(_tools)
_tool_map = {t.name: t for t in _tools}

_SYSTEM = SystemMessage(content=(
    "You are a helpful assistant managing elements in a workspace.\n"
    "Rules:\n"
    "- NEVER show URIs, JSON, or technical field names to the user. Use human-readable names only.\n"
    "- Translate user language to URIs internally before calling tools.\n"
    "- For create/update: only use spaces where write=yes.\n"
    "- If the user's request is missing one piece of info (e.g. title), ask ONE short question.\n"
    "- When an operation succeeds, confirm it in plain language (e.g. 'Done! I created \"My idea\" in Projects.').\n"
    "- Only use the tools provided. Never invent tool names.\n"
    "- All tool parameters are required — never omit them."
))

# Discovery tools need a follow-up LLM call; action tools return a final answer.
_ACTION_TOOLS = {"search_elements_tool", "create_element_tool", "update_element_title_tool", "delete_element_tool"}


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
        lines.append(f'  Display name: "{s["name"]}" | space_uri: "{s["uri"]}" | writable: {"yes" if can_write else "no"}')
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
    return run_react_loop(messages, _llm_with_tools, _tool_map, stop_on=_ACTION_TOOLS)
