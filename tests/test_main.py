"""Unit tests for main.py — conversation history reconstruction and message merging."""
from langchain_core.messages import HumanMessage, AIMessage

from main import _build_history_messages
from dashboard import merge_consecutive_messages
from message_broker import ChatMessage


def _msg(role: str, content: str, interaction_id: str = "id-1") -> ChatMessage:
    return ChatMessage(role=role, content=content, timestamp=0.0, interaction_id=interaction_id)


class TestBuildHistoryMessages:
    def test_empty_history_returns_empty_list(self) -> None:
        assert _build_history_messages([]) == []

    def test_single_user_message(self) -> None:
        history = [_msg("user", "Hello")]
        result = _build_history_messages(history)
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)
        assert result[0].content == "Hello"

    def test_single_assistant_message(self) -> None:
        history = [_msg("assistant", "Hi there")]
        result = _build_history_messages(history)
        assert len(result) == 1
        assert isinstance(result[0], AIMessage)

    def test_full_conversation_turn(self) -> None:
        history = [
            _msg("user", "Search for ideas", "id-1"),
            _msg("assistant", "Here are the results", "id-1"),
        ]
        result = _build_history_messages(history)
        assert len(result) == 2
        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)

    def test_streamed_chunks_are_merged(self) -> None:
        """Streamed assistant messages sharing the same interaction_id must be joined."""
        history = [
            _msg("user", "Tell me", "id-1"),
            _msg("assistant", "Part one. ", "id-1"),
            _msg("assistant", "Part two.", "id-1"),
        ]
        result = _build_history_messages(history)
        assert len(result) == 2
        assert result[1].content == "Part one. Part two."

    def test_multiple_turns_produce_correct_message_count(self) -> None:
        history = [
            _msg("user", "First question", "id-1"),
            _msg("assistant", "First answer", "id-1"),
            _msg("user", "Second question", "id-2"),
            _msg("assistant", "Second answer", "id-2"),
        ]
        result = _build_history_messages(history)
        assert len(result) == 4

    def test_unknown_roles_are_ignored(self) -> None:
        """Messages with unrecognised roles must not produce a LangChain message."""
        history = [
            _msg("system", "Internal note", "id-0"),
            _msg("user", "Real question", "id-1"),
        ]
        result = _build_history_messages(history)
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)


class TestMergeConsecutiveMessages:
    def test_same_role_same_id_are_merged(self) -> None:
        """Streaming chunks with the same interaction_id must be concatenated."""
        history = [
            _msg("assistant", "Hello ", "id-1"),
            _msg("assistant", "world", "id-1"),
        ]
        merge_consecutive_messages(history)
        assert len(history) == 1
        assert history[0].content == "Hello world"

    def test_same_role_different_id_are_not_merged(self) -> None:
        """Two user messages with different interaction_ids must stay separate."""
        history = [
            _msg("user", "First message", "id-1"),
            _msg("user", "Second message", "id-2"),
        ]
        merge_consecutive_messages(history)
        assert len(history) == 2
        assert history[0].content == "First message"
        assert history[1].content == "Second message"

    def test_alternating_roles_are_never_merged(self) -> None:
        history = [
            _msg("user", "Question", "id-1"),
            _msg("assistant", "Answer", "id-1"),
        ]
        merge_consecutive_messages(history)
        assert len(history) == 2
