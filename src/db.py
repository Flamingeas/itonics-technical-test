import os
import threading
import uuid
import time
from contextlib import contextmanager
from typing import Any, Generator

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

WRITE_VERB = "verb:write"

_pool: ThreadedConnectionPool | None = None
_pool_lock = threading.Lock()


def _get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=5,
                    host=os.getenv("DB_HOST"),
                    port=int(os.getenv("DB_PORT", "5432")),
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                )
    return _pool


@contextmanager
def get_cursor() -> Generator[psycopg2.extras.RealDictCursor, None, None]:
    """Yield a RealDictCursor; auto-commit/rollback and return connection to pool."""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                yield cur
    finally:
        pool.putconn(conn)


def has_permission(user_uri: str, space_uri: str, verb: str) -> bool:
    """Return True if user holds the given verb on the space."""
    sql = """
        SELECT 1
        FROM public.user_space_permissions
        WHERE user_uri = %s
          AND space_uri = %s
          AND verb_uri  = %s
        LIMIT 1
    """
    with get_cursor() as cur:
        cur.execute(sql, (user_uri, space_uri, verb))
        return cur.fetchone() is not None


def search_elements(space_uri: str, query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Case-insensitive substring search on element titles within a space."""
    sql = """
        SELECT uri, title, type_uri, space_uri, creation_date, author
        FROM public.elements
        WHERE space_uri = %s
          AND title ILIKE %s
        ORDER BY creation_date DESC
        LIMIT %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (space_uri, f"%{query}%", limit))
        return [dict(row) for row in cur.fetchall()]


def get_element(element_uri: str) -> dict[str, Any] | None:
    """Fetch a single element by URI. Returns None if not found."""
    sql = """
        SELECT uri, title, type_uri, space_uri, creation_date, author
        FROM public.elements
        WHERE uri = %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (element_uri,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_element(user_uri: str, space_uri: str, type_uri: str, title: str) -> dict[str, Any]:
    """Create a new element. Raises PermissionError if user lacks write access."""
    if not has_permission(user_uri, space_uri, WRITE_VERB):
        raise PermissionError(
            f"User {user_uri!r} does not have write access to space {space_uri!r}."
        )

    element_uri = f"element:{space_uri.split(':')[-1]}:{uuid.uuid4().hex}"
    sql = """
        INSERT INTO public.elements (uri, title, type_uri, space_uri, creation_date, author)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING uri, title, type_uri, space_uri, creation_date, author
    """
    creation_date = int(time.time() * 1000)
    with get_cursor() as cur:
        cur.execute(sql, (element_uri, title, type_uri, space_uri, creation_date, user_uri))
        row = cur.fetchone()
        return dict(row)


def list_user_spaces(user_uri: str) -> list[dict[str, Any]]:
    """Return all spaces the user has access to."""
    sql = """
        SELECT s.uri, s.name, s.tenant_uri
        FROM public.spaces s
        JOIN public.user_spaces us ON us.space_uri = s.uri
        WHERE us.user_uri = %s
        ORDER BY s.uri
    """
    with get_cursor() as cur:
        cur.execute(sql, (user_uri,))
        return [dict(row) for row in cur.fetchall()]


def update_element_title(user_uri: str, element_uri: str, new_title: str) -> dict[str, Any]:
    """Update an element's title atomically. Raises ValueError if not found, PermissionError if unauthorized."""
    update_sql = """
        UPDATE public.elements e
        SET title = %s
        FROM public.user_space_permissions p
        WHERE e.uri = %s
          AND p.user_uri = %s
          AND p.space_uri = e.space_uri
          AND p.verb_uri = %s
        RETURNING e.uri, e.title, e.type_uri, e.space_uri, e.creation_date, e.author
    """
    check_sql = "SELECT space_uri FROM public.elements WHERE uri = %s"
    with get_cursor() as cur:
        cur.execute(update_sql, (new_title, element_uri, user_uri, WRITE_VERB))
        row = cur.fetchone()
        if row is not None:
            return dict(row)
        cur.execute(check_sql, (element_uri,))
        if cur.fetchone() is None:
            raise ValueError(f"Element {element_uri!r} not found.")
        raise PermissionError(
            f"User {user_uri!r} does not have write access to the element's space."
        )
