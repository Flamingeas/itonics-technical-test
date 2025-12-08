import os
import threading
import time
from typing import TypeAlias

import streamlit as st

from chat_context import get_shared_broker, set_conversation_history
from message_broker import ChatMessage, MessageBroker

ChatHistory: TypeAlias = list[ChatMessage]

STREAMING_KEY = "is_streaming"
CHAT_MODE = os.getenv("CHAT_MODE", "example")  # example or solution


def init_chat_history() -> ChatHistory:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history


def is_streaming() -> bool:
    return st.session_state.get(STREAMING_KEY, False)


def set_streaming(value: bool) -> None:
    st.session_state[STREAMING_KEY] = value


def render_history(history: ChatHistory) -> None:
    for message in history:
        st.chat_message(message.role).write(message.content)


def merge_consecutive_messages(history: ChatHistory) -> None:
    """Merge consecutive messages from the same role (for streaming)."""
    if len(history) < 2:
        return

    merged: ChatHistory = []
    for message in history:
        if merged and merged[-1].role == message.role:
            # Update the last message with concatenated content
            last_msg = merged[-1]
            merged[-1] = last_msg.model_copy(
                update={"content": last_msg.content + message.content}
            )
        else:
            merged.append(message)

    history.clear()
    history.extend(merged)


def hydrate_history_from_broker(history: ChatHistory, broker: MessageBroker) -> None:
    new_messages = broker.receive_all()
    history.extend(new_messages)
    merge_consecutive_messages(history)


def process_user_input(user_input: str, history: ChatHistory) -> None:
    """Process user input by delegating to main.py in a background thread."""

    # Import here to avoid circular imports
    if CHAT_MODE == "example":
        from main_example import handle_user_input
    elif CHAT_MODE == "solution":
        from main import handle_user_input
    else:
        raise ValueError(
            f"Invalid mode: {CHAT_MODE}. Valid modes are: example, solution"
        )

    def run_handler() -> None:
        try:
            # Sync conversation history to shared context before processing
            set_conversation_history(history)
            handle_user_input(user_input)
        finally:
            set_streaming(False)

    set_streaming(True)
    thread = threading.Thread(target=run_handler, daemon=True)
    thread.start()


def render_chat_interface() -> None:
    st.set_page_config(page_title="Chat UI", page_icon="💬")
    st.title(f"Chat UI:  ({CHAT_MODE})")
    broker = get_shared_broker()
    history = init_chat_history()
    hydrate_history_from_broker(history, broker)

    prompt = st.chat_input("Send a message")
    if prompt:
        process_user_input(prompt, history)

    render_history(history)

    # Auto-refresh while streaming to show incremental updates
    if is_streaming():
        time.sleep(0.1)
        st.rerun()


if __name__ == "__main__":
    render_chat_interface()
