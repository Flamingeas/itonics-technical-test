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

_llm = ChatOllama(model="llama3", base_url="http://ollama:11434")


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


_tools = [search_elements_tool]
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
