"""
Example implementation of chatbot logic.

This is a reference implementation showing how to use the chat utilities
to build a simple echo bot with streaming responses and conversation context.
"""

import time

from chat_utils import (
    generate_interaction_id,
    get_chat_history,
    send_user_message,
    stream_assistant_response,
)


def handle_user_input(user_input: str) -> None:
    """
    Process user input and generate a response.

    This example implementation:
    1. Generates an interaction ID to link user message with response
    2. Gets conversation history for context
    3. Echoes the user's message back to the chat
    4. Uses message timestamps and interaction_id to track interactions
    5. Streams the response in chunks to simulate LLM token streaming

    Args:
        user_input: The user's message from the chat interface
    """
    # Generate interaction ID to link this user message with its response
    interaction_id = generate_interaction_id()

    # Get conversation history to maintain context
    history = get_chat_history()
    message_count = len(history)

    # Display the user's message in the chat
    send_user_message(user_input, interaction_id)

    # Generate a context-aware response (in a real implementation, pass history to LLM)
    if message_count == 0:
        response = f"You said: {user_input} (This is the first message!)"
    else:
        # Each message is a ChatMessage object with: role, content, timestamp, interaction_id
        first_msg_time = history[0].timestamp
        current_time = time.time()
        elapsed = int(current_time - first_msg_time)
        response = f"You said: {user_input} (History: {message_count} msgs, {elapsed}s elapsed)"

    # Stream the response with same interaction_id to link it with the user message
    stream_assistant_response(response, interaction_id, chunk_size=3, delay=0.15)
