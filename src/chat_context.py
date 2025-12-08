"""Shared chat context for communication between main.py and dashboard.py."""

from message_broker import ChatMessage, MessageBroker

# Singleton broker instance shared across the application
_broker_instance: MessageBroker | None = None
_conversation_history: list[ChatMessage] = []


def get_shared_broker() -> MessageBroker:
    """Get the shared message broker instance."""
    global _broker_instance
    if _broker_instance is None:
        _broker_instance = MessageBroker()
    return _broker_instance


def get_conversation_history() -> list[ChatMessage]:
    """
    Get the current conversation history.

    Returns:
        List of all messages in the conversation so far.
    """
    return _conversation_history.copy()


def set_conversation_history(history: list[ChatMessage]) -> None:
    """Update the conversation history (called by dashboard)."""
    global _conversation_history
    _conversation_history = history.copy()
