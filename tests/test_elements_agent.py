"""Unit tests for elements_agent.py — tools output, error handling, and context cache."""
from unittest.mock import patch
import time
import pytest

import agents.elements_agent as ea
from agents.elements_agent import (
    search_elements_tool,
    create_element_tool,
    update_element_title_tool,
    _build_context,
    _context_cache,
    _CACHE_TTL,
)

_USER = "user:bob"
_SPACE = "space:acme"


# ── search_elements_tool
class TestSearchElementsTool:
    def test_formats_results(self) -> None:
        rows = [{"uri": "element:acme:1", "title": "Cool Idea"},
                {"uri": "element:acme:2", "title": "Better Idea"}]
        with patch("db.search_elements", return_value=rows):
            result = search_elements_tool.invoke({"space_uri": _SPACE, "query": "idea"})
        assert "Cool Idea" in result
        assert "Better Idea" in result

    def test_returns_no_results_message(self) -> None:
        with patch("db.search_elements", return_value=[]):
            result = search_elements_tool.invoke({"space_uri": _SPACE, "query": "nothing"})
        assert "No elements found" in result

    def test_returns_error_message_on_db_failure(self) -> None:
        with patch("db.search_elements", side_effect=Exception("connection lost")):
            result = search_elements_tool.invoke({"space_uri": _SPACE, "query": "x"})
        assert "Database error" in result

    def test_rejects_invalid_space_uri(self) -> None:
        result = search_elements_tool.invoke({"space_uri": "hr:all", "query": ""})
        assert "Invalid space_uri" in result

    def test_default_query_is_empty_string(self) -> None:
        with patch("db.search_elements", return_value=[]) as mock:
            search_elements_tool.invoke({"space_uri": _SPACE})
        mock.assert_called_once_with(_SPACE, "", limit=10)

    def test_limit_param_is_passed_to_db(self) -> None:
        rows = [{"uri": "element:acme:1", "title": "Latest"}]
        with patch("db.search_elements", return_value=rows) as mock:
            search_elements_tool.invoke({"space_uri": _SPACE, "query": "", "limit": 1})
        mock.assert_called_once_with(_SPACE, "", limit=1)


# ── create_element_tool
class TestCreateElementTool:
    def test_returns_success_message(self) -> None:
        element = {"uri": "element:acme:abc", "title": "New Idea"}
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.create_element", return_value=element):
                result = create_element_tool.invoke(
                    {"space_uri": _SPACE, "type_uri": "type:idea", "title": "New Idea"}
                )
        assert "Created element" in result
        assert "New Idea" in result

    def test_returns_permission_denied_message(self) -> None:
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.create_element", side_effect=PermissionError("no write access")):
                result = create_element_tool.invoke(
                    {"space_uri": _SPACE, "type_uri": "type:idea", "title": "Blocked"}
                )
        assert "Permission denied" in result

    def test_returns_error_message_on_db_failure(self) -> None:
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.create_element", side_effect=Exception("timeout")):
                result = create_element_tool.invoke(
                    {"space_uri": _SPACE, "type_uri": "type:idea", "title": "Fail"}
                )
        assert "Database error" in result

    def test_rejects_invalid_space_uri(self) -> None:
        result = create_element_tool.invoke(
            {"space_uri": "hr:all", "type_uri": "type:idea", "title": "Test"}
        )
        assert "Invalid space_uri" in result

    def test_rejects_invalid_type_uri(self) -> None:
        result = create_element_tool.invoke(
            {"space_uri": _SPACE, "type_uri": "idea", "title": "Test"}
        )
        assert "Invalid type_uri" in result


# ── update_element_title_tool
class TestUpdateElementTitleTool:
    def test_returns_success_message(self) -> None:
        element = {"uri": "element:acme:abc", "title": "Updated Title"}
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.update_element_title", return_value=element):
                result = update_element_title_tool.invoke(
                    {"element_uri": "element:acme:abc", "new_title": "Updated Title"}
                )
        assert "Updated element" in result
        assert "Updated Title" in result

    def test_returns_permission_denied_message(self) -> None:
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.update_element_title", side_effect=PermissionError("no access")):
                result = update_element_title_tool.invoke(
                    {"element_uri": "element:acme:abc", "new_title": "X"}
                )
        assert "Permission denied" in result

    def test_returns_not_found_message(self) -> None:
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.update_element_title", side_effect=ValueError("not found")):
                result = update_element_title_tool.invoke(
                    {"element_uri": "element:acme:missing", "new_title": "X"}
                )
        assert "Element not found" in result


# ── _build_context cache

class TestBuildContextCache:
    def setup_method(self) -> None:
        _context_cache.clear()

    def test_caches_result_on_first_call(self) -> None:
        spaces = [{"uri": _SPACE, "name": "Acme", "tenant_uri": "t:acme", "can_write": False}]
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.list_user_spaces", return_value=spaces) as mock_spaces:
                _build_context()
                _build_context()  # normally this should fail
        assert mock_spaces.call_count == 1

    def test_cache_expires_after_ttl(self) -> None:
        spaces = [{"uri": _SPACE, "name": "Acme", "tenant_uri": "t:acme", "can_write": False}]
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.list_user_spaces", return_value=spaces) as mock_spaces:
                _build_context()
                # expiring the cache artificially
                _context_cache[_USER] = (_context_cache[_USER][0], time.time() - _CACHE_TTL - 1)
                _build_context()  # should hit DB again
        assert mock_spaces.call_count == 2

    def test_returns_no_spaces_message_when_empty(self) -> None:
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.list_user_spaces", return_value=[]):
                result = _build_context()
        assert "No spaces available" in result

    def test_returns_error_message_on_db_failure(self) -> None:
        with patch("agents.elements_agent.CURRENT_USER", _USER):
            with patch("db.list_user_spaces", side_effect=Exception("DB down")):
                result = _build_context()
        assert "Could not load spaces" in result
