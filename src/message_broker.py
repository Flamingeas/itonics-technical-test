from queue import Empty, Queue

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    Represents a single message in the chat conversation.

    Attributes:
        role: The sender of the message, either "user" or "assistant"
        content: The text content of the message
        timestamp: Unix timestamp (seconds since epoch) when the message was created
        interaction_id: Unique identifier linking user message with assistant response
    """

    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="The message text content")
    timestamp: float = Field(..., description="Unix timestamp when message was sent")
    interaction_id: str = Field(
        ..., description="Unique ID linking related messages together"
    )


class MessageBroker:
    """Thread-safe message broker for chat communication."""

    def __init__(self) -> None:
        self._queue: Queue[ChatMessage] = Queue()

    def send(self, message: ChatMessage) -> None:
        """Push a message into the broker."""
        self._queue.put(message)

    def receive_all(self) -> list[ChatMessage]:
        """Pull all available messages from the broker."""
        messages: list[ChatMessage] = []
        while True:
            try:
                messages.append(self._queue.get_nowait())
            except Empty:
                break
        return messages
