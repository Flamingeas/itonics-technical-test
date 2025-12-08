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

from chat_utils import (
    generate_interaction_id,
    get_chat_history,
    send_user_message,
    stream_assistant_response,
)


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
    pass
