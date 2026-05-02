"""Unit tests for db.py """
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import db


def make_cursor(*fetchone_values: Any, fetchall: list[Any] | None = None) -> tuple[Any, Any]:
    """Return (context-manager factory, cursor mock).

    fetchone_values: successive return values for cursor.fetchone().
    fetchall: return value for cursor.fetchall().
    """
    cur = MagicMock()
    cur.fetchone.side_effect = list(fetchone_values) if fetchone_values else [None]
    cur.fetchall.return_value = fetchall or []

    @contextmanager
    def _ctx() -> Any:
        yield cur
    return _ctx, cur


# ── check if user has_permission
class TestHasPermission:
    def test_returns_true_when_row_found(self) -> None:
        ctx, _ = make_cursor({"1": 1})
        with patch("db.get_cursor", ctx):
            assert db.has_permission("user:bob", "space:acme", "verb:write") is True

    def test_returns_false_when_no_row(self) -> None:
        ctx, _ = make_cursor(None)
        with patch("db.get_cursor", ctx):
            assert db.has_permission("user:bob", "space:acme", "verb:write") is False


# ── search_elements
class TestSearchElements:
    def test_returns_list_of_dicts(self) -> None:
        rows = [{"uri": "element:acme:abc", "title": "Cool Idea", "type_uri": "type:idea",
                 "space_uri": "space:acme", "creation_date": 0, "author": "user:bob"}]
        ctx, _ = make_cursor(fetchall=rows)
        with patch("db.get_cursor", ctx):
            results = db.search_elements("space:acme", "cool")
        assert len(results) == 1
        assert results[0]["title"] == "Cool Idea"

    def test_returns_empty_list_when_no_match(self) -> None:
        ctx, _ = make_cursor(fetchall=[])
        with patch("db.get_cursor", ctx):
            assert db.search_elements("space:acme", "nothing") == []


# ── create_element
class TestCreateElement:
    def test_permission_error_when_no_write_access(self) -> None:
        with patch("db.has_permission", return_value=False):
            with pytest.raises(PermissionError):
                db.create_element("user:bob", "space:acme", "type:idea", "My Idea")

    def test_returns_element_dict_on_success(self) -> None:
        row = {"uri": "element:acme:abc123", "title": "My Idea", "type_uri": "type:idea",
               "space_uri": "space:acme", "creation_date": 0, "author": "user:bob"}
        ctx, _ = make_cursor(row)
        with patch("db.has_permission", return_value=True):
            with patch("db.get_cursor", ctx):
                result = db.create_element("user:bob", "space:acme", "type:idea", "My Idea")
        assert result["uri"] == "element:acme:abc123"
        assert result["title"] == "My Idea"

    def test_uri_slug_derived_from_title(self) -> None:
        row = {"uri": "element:acme:cool-idea-abc123", "title": "Cool Idea", "type_uri": "type:idea",
               "space_uri": "space:acme", "creation_date": 0, "author": "user:bob"}
        ctx, cur = make_cursor(row)
        with patch("db.has_permission", return_value=True):
            with patch("db.get_cursor", ctx):
                db.create_element("user:bob", "space:acme", "type:idea", "Cool Idea")
        inserted_uri: str = cur.execute.call_args[0][1][0]
        assert inserted_uri.startswith("element:acme:cool-idea-")

    def test_uri_slug_falls_back_for_special_char_title(self) -> None:
        row = {"uri": "element:acme:element-abc123", "title": "???", "type_uri": "type:idea",
               "space_uri": "space:acme", "creation_date": 0, "author": "user:bob"}
        ctx, cur = make_cursor(row)
        with patch("db.has_permission", return_value=True):
            with patch("db.get_cursor", ctx):
                db.create_element("user:bob", "space:acme", "type:idea", "???")
        inserted_uri: str = cur.execute.call_args[0][1][0]
        assert inserted_uri.startswith("element:acme:element-")


# ── update_element_title
class TestUpdateElementTitle:
    def test_returns_dict_on_success(self) -> None:
        row = {"uri": "element:acme:abc", "title": "New Title", "type_uri": "type:idea",
               "space_uri": "space:acme", "creation_date": 0, "author": "user:bob"}
        # 1st fetchone: success
        ctx, _ = make_cursor(row)
        with patch("db.get_cursor", ctx):
            result = db.update_element_title("user:bob", "element:acme:abc", "New Title")
        assert result["title"] == "New Title"

    def test_value_error_when_el_not_found(self) -> None:
        # UPDATE null, SELECT null -> el missing
        ctx, _ = make_cursor(None, None)
        with patch("db.get_cursor", ctx):
            with pytest.raises(ValueError, match="not found"):
                db.update_element_title("user:bob", "element:acme:missing", "X")

    def test_permission_error_when_no_access(self) -> None:
        # UPDATE null, SELECT ok -> el exists but user can't write
        ctx, _ = make_cursor(None, {"space_uri": "space:acme"})
        with patch("db.get_cursor", ctx):
            with pytest.raises(PermissionError):
                db.update_element_title("user:bob", "element:acme:abc", "X")


# ── list_user_spaces
class TestListUserSpaces:
    def test_returns_spaces_with_write_flag(self) -> None:
        rows = [{"uri": "space:acme", "name": "Acme", "tenant_uri": "tenant:acme", "can_write": True}]
        ctx, _ = make_cursor(fetchall=rows)
        with patch("db.get_cursor", ctx):
            spaces = db.list_user_spaces("user:bob")
        assert spaces[0]["can_write"] is True

    def test_returns_empty_list_when_no_spaces(self) -> None:
        ctx, _ = make_cursor(fetchall=[])
        with patch("db.get_cursor", ctx):
            assert db.list_user_spaces("user:bob") == []


# ── list_types_in_space
class TestListTypesInSpace:
    def test_returns_type_list(self) -> None:
        rows = [{"uri": "type:idea", "name": "Idea"}, {"uri": "type:project", "name": "Project"}]
        ctx, _ = make_cursor(fetchall=rows)
        with patch("db.get_cursor", ctx):
            types = db.list_types_in_space("space:acme")
        assert len(types) == 2
        assert types[0]["uri"] == "type:idea"
