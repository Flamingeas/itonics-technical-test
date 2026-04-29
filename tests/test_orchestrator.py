"""Unit tests for orchestrator.py — keyword-based routing logic."""
import pytest
from agents.orchestrator import _is_element_task


class TestIsElementTask:
    @pytest.mark.parametrize("message", [
        "search for ideas",
        "find projects about AI",
        "create a new idea",
        "update the title of this element",
        "rename that task",
    ])
    def test_returns_true_for_element_messages(self, message: str) -> None:
        assert _is_element_task(message) is True

    @pytest.mark.parametrize("message", [
        "hello",
        "how are you?",
        "what can you do?",
        "thank you",
    ])
    def test_returns_false_for_general_messages(self, message: str) -> None:
        assert _is_element_task(message) is False

    def test_is_case_insensitive(self) -> None:
        assert _is_element_task("CREATE an IDEA") is True

    def test_empty_string_returns_false(self) -> None:
        assert _is_element_task("") is False
