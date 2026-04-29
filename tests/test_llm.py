"""Unit tests for llm.py — llama3.1 native tool call parsing."""
import pytest

from agents.llm import _parse_python_tag_calls


class TestParsePythonTagCalls:
    def test_parses_single_valid_call(self) -> None:
        content = '<|python_tag|>{"name": "search_elements_tool", "parameters": {"space_uri": "space:acme", "query": "idea"}}'
        calls = _parse_python_tag_calls(content)
        assert len(calls) == 1
        assert calls[0]["name"] == "search_elements_tool"
        assert calls[0]["args"]["space_uri"] == "space:acme"
        assert calls[0]["args"]["query"] == "idea"

    def test_parses_multiple_calls(self) -> None:
        content = (
            '<|python_tag|>{"name": "tool_a", "parameters": {"x": 1}} '
            '<|python_tag|>{"name": "tool_b", "parameters": {"y": 2}}'
        )
        calls = _parse_python_tag_calls(content)
        assert len(calls) == 2
        assert calls[0]["name"] == "tool_a"
        assert calls[1]["name"] == "tool_b"

    def test_assigns_unique_ids(self) -> None:
        content = (
            '<|python_tag|>{"name": "tool_a", "parameters": {}} '
            '<|python_tag|>{"name": "tool_b", "parameters": {}}'
        )
        calls = _parse_python_tag_calls(content)
        assert calls[0]["id"] != calls[1]["id"]

    def test_returns_empty_list_when_no_tags(self) -> None:
        assert _parse_python_tag_calls("Just a plain response.") == []

    def test_skips_invalid_json(self) -> None:
        content = '<|python_tag|>{not valid json}'
        calls = _parse_python_tag_calls(content)
        assert calls == []

    def test_skips_entries_without_name(self) -> None:
        content = '<|python_tag|>{"parameters": {"x": 1}}'
        calls = _parse_python_tag_calls(content)
        assert calls == []

    def test_normalises_arguments_key(self) -> None:
        """Model may use 'arguments' instead of 'parameters'."""
        content = '<|python_tag|>{"name": "some_tool", "arguments": {"foo": "bar"}}'
        calls = _parse_python_tag_calls(content)
        assert calls[0]["args"]["foo"] == "bar"

    def test_normalises_args_key(self) -> None:
        """Model may use 'args' directly."""
        content = '<|python_tag|>{"name": "some_tool", "args": {"baz": 42}}'
        calls = _parse_python_tag_calls(content)
        assert calls[0]["args"]["baz"] == 42
