import os
import db
from agents.llm import _llm, run_react_loop
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

CURRENT_USER = os.getenv("CURRENT_USER")


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
def search_elements_tool(space_uri: str, query: str) -> str:
    """Search for elements whose title contains *query* inside *space_uri*.

    Args:
        space_uri: URI of the space to search in (e.g. 'space:acme-projects').
        query: Keyword to look for in element titles (case-insensitive).
               Use an empty string "" to list all elements in the space.
    """
    try:
        results = db.search_elements(space_uri, query)
    except Exception as e:
        return f"Database error while searching elements: {e}"
    if not results:
        return f"No elements found in {space_uri!r} matching {query!r}."
    lines = [f"- {r['uri']}: {r['title']}" for r in results]
    return "\n".join(lines)


@tool
def create_element_tool(space_uri: str, type_uri: str, title: str) -> str:
    """Create a new element in a space.

    Args:
        space_uri: URI of the space (e.g. 'space:acme-projects').
        type_uri: URI of the element type (e.g. 'type:project').
        title: Title for the new element.
    """
    try:
        element = db.create_element(CURRENT_USER, space_uri, type_uri, title)
    except PermissionError as e:
        return f"Permission denied: {e}"
    except Exception as e:
        return f"Database error while creating element: {e}"
    return f"Created element {element['uri']!r} with title {element['title']!r}."


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


_tools = [list_spaces_tool, list_types_tool, search_elements_tool, create_element_tool, update_element_title_tool]
_llm_with_tools = _llm.bind_tools(_tools)
_tool_map = {t.name: t for t in _tools}

_SYSTEM = SystemMessage(content=(
    "Elements agent. Use the provided context to call tools with correct URIs. "
    "For create/update: only use spaces with write=yes. "
    "All tool parameters are required — never omit them."
))

# Discovery tools need a follow-up LLM call; action tools return a final answer.
_ACTION_TOOLS = {"search_elements_tool", "create_element_tool", "update_element_title_tool"}


def _build_context() -> str:
    """Pre-load spaces and types so the LLM has all info before its first call."""
    try:
        spaces = db.list_user_spaces(CURRENT_USER)
    except Exception as e:
        return f"Could not load spaces: {e}"
    if not spaces:
        return "No spaces available for the current user."
    lines = ["Available spaces (write: yes = you can create/update here):"]
    for s in spaces:
        lines.append(f"  - {s['uri']}: {s['name']} (write: {'yes' if s['can_write'] else 'no'})")
        if s["can_write"]:
            try:
                types = db.list_types_in_space(s["uri"])
                for t in types:
                    lines.append(f"      type: {t['uri']} ({t['name']})")
            except Exception:
                pass
    return "\n".join(lines)


def run_elements_agent(user_message: str) -> str:
    context = _build_context()
    messages: list = [_SYSTEM, SystemMessage(content=context), HumanMessage(content=user_message)]
    return run_react_loop(messages, _llm_with_tools, _tool_map, stop_on=_ACTION_TOOLS)
