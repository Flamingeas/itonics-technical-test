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

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from agents.elements_agent import CURRENT_USER
from agents.orchestrator import run_orchestrator
from chat_utils import (
    generate_interaction_id,
    get_chat_history,
    send_user_message,
    stream_assistant_response,
)
from message_broker import ChatMessage


def _build_history_messages(history: list[ChatMessage]) -> list[BaseMessage]:
    """Reconstruct full conversation turns from streamed chat history chunks."""
    if not history:
        return []
    result: list[BaseMessage] = []
    current_id = history[0].interaction_id
    current_role = history[0].role
    current_content = history[0].content
    for msg in history[1:]:
        if msg.interaction_id == current_id and msg.role == current_role:
            current_content += msg.content
        else:
            if current_role == "user":
                result.append(HumanMessage(content=current_content))
            elif current_role == "assistant":
                result.append(AIMessage(content=current_content))
            current_id = msg.interaction_id
            current_role = msg.role
            current_content = msg.content
    if current_role == "user":
        result.append(HumanMessage(content=current_content))
    elif current_role == "assistant":
        result.append(AIMessage(content=current_content))
    return result

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
    if not CURRENT_USER:
        stream_assistant_response("No user configured. Set the CURRENT_USER environment variable.", interaction_id)
        return
    history = _build_history_messages(get_chat_history())
    try:
        reply = run_orchestrator(user_input, history)
    except Exception as e:
        reply = f"Unexpected error: {e}"
    stream_assistant_response(reply, interaction_id, chunk_size=15, delay=0.03)
