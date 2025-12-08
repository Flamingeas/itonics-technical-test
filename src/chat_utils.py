"""Utility functions for sending messages to the chat interface."""

import time
import uuid

from chat_context import get_conversation_history, get_shared_broker
from message_broker import ChatMessage


def generate_interaction_id() -> str:
    """
    Generate a unique interaction ID.
    """
    return str(uuid.uuid4())


def send_message(role: str, content: str, interaction_id: str) -> None:
    """
    Send a message to the chat interface.

    Args:
        role: Either "user" or "assistant"
        content: The message content to display
        interaction_id: Unique ID linking related messages together
    """
    broker = get_shared_broker()
    message = ChatMessage(
        role=role,
        content=content,
        timestamp=time.time(),
        interaction_id=interaction_id,
    )
    broker.send(message)


def send_user_message(content: str, interaction_id: str) -> None:
    """
    Send a user message to the chat interface.

    Args:
        content: The message text
        interaction_id: Unique ID linking this message with its response
    """
    send_message("user", content, interaction_id)


def send_assistant_message(content: str, interaction_id: str) -> None:
    """
    Send an assistant message to the chat interface.

    Args:
        content: The message text
        interaction_id: Unique ID linking this message with its prompt
    """
    send_message("assistant", content, interaction_id)


def stream_assistant_response(
    content: str, interaction_id: str, chunk_size: int = 3, delay: float = 0.15
) -> None:
    """
    Stream an assistant response in chunks to simulate LLM token streaming.

    Args:
        content: The full response text to stream
        interaction_id: Unique ID linking this response with its user prompt
        chunk_size: Number of characters per chunk
        delay: Delay in seconds between chunks
    """
    for i in range(0, len(content), chunk_size):
        chunk = content[i : i + chunk_size]
        send_assistant_message(chunk, interaction_id)
        time.sleep(delay)


def get_chat_history() -> list[ChatMessage]:
    """
    Get the conversation history.

    Use this to access previous messages and maintain context across interactions.
    This is useful for building context-aware chatbots that remember previous exchanges.
    """
    return get_conversation_history()
