"""
Main module for chatbot implementation.

Implement your chatbot logic here. The dashboard will call `handle_user_input()`
whenever a user sends a message.

Available functions:
- generate_interaction_id(): Generate unique ID to link messages
- get_chat_history(): Get list of previous messages for context
- send_user_message(content, interaction_id): Send a user message
- stream_assistant_response(content, interaction_id): Stream an assistant response
"""

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

import os
import db
from chat_utils import (
    generate_interaction_id,
    get_chat_history,
    send_user_message,
    stream_assistant_response,
)

CURRENT_USER = os.getenv("CURRENT_USER", "user:alice")

_llm = ChatOllama(model="llama3.1", base_url="http://ollama:11434")


@tool
def search_elements_tool(space_uri: str, query: str) -> str:
    """Search for elements whose title contains *query* inside *space_uri*.

    Args:
        space_uri: URI of the space to search in (e.g. 'space:abc123').
        query: Keyword to look for in element titles (case-insensitive).
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


_tools = [search_elements_tool, create_element_tool, update_element_title_tool]
_llm_with_tools = _llm.bind_tools(_tools)
_tool_map = {t.name: t for t in _tools}


def _run_elements_agent(user_message: str) -> str:
    messages: list = [HumanMessage(content=user_message)]
    while True:
        try:
            response: AIMessage = _llm_with_tools.invoke(messages)
        except Exception as e:
            return f"The assistant is temporarily unavailable: {e}"
        messages.append(response)
        if not response.tool_calls:
            return str(response.content)
        for tc in response.tool_calls:
            result = _tool_map[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))


@tool
def call_elements_agent_tool(task: str) -> str:
    """Delegate element-related tasks to the elements agent.

    Use this for: searching elements, creating elements, updating element titles.
    Args:
        task: Natural language description of the task
              (e.g. 'search for ideas in space:acme-projects').
    """
    return _run_elements_agent(task)


_orchestrator_tools = [call_elements_agent_tool]
_orchestrator_llm_with_tools = _llm.bind_tools(_orchestrator_tools)
_orchestrator_tool_map = {t.name: t for t in _orchestrator_tools}


def _run_orchestrator(user_message: str) -> str:
    messages: list = [HumanMessage(content=user_message)]
    while True:
        try:
            response: AIMessage = _orchestrator_llm_with_tools.invoke(messages)
        except Exception as e:
            return f"The assistant is temporarily unavailable: {e}"
        messages.append(response)
        if not response.tool_calls:
            return str(response.content)
        for tc in response.tool_calls:
            result = _orchestrator_tool_map[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))


def handle_user_input(user_input: str) -> None:
    """
    Process user input and generate a response.

    TODO: Implement your chatbot logic here.

    Args:
        user_input: The user's message from the chat interface

    Example:
        # Generate interaction ID to link user message with response
        interaction_id = generate_interaction_id()

        # Get previous conversation for context
        history = get_chat_history()
        # Each message is a ChatMessage object with:
        # - role, content, timestamp, interaction_id

        # Send user message to chat
        send_user_message(user_input, interaction_id)

        # Generate response (use history for context-aware responses)
        response = "Your bot response here"

        # Stream response back with same interaction_id
        stream_assistant_response(response, interaction_id)
    """
    interaction_id = generate_interaction_id()
    send_user_message(user_input, interaction_id)
    try:
        reply = _run_elements_agent(user_input)
    except Exception as e:
        reply = f"Unexpected error: {e}"
    stream_assistant_response(reply, interaction_id)
