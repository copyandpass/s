import mysql.connector
import pytest
from routers.contents import get_contents_list, get_content_by_id
from fastapi import HTTPException


class MockCursor:
    def __init__(self, fetch_result=None, raise_on_execute=False):
        self._fetch_result = fetch_result
        self.raise_on_execute = raise_on_execute
        self.closed = False

    def execute(self, query, params=None):
        if self.raise_on_execute:
            raise mysql.connector.Error("db error")

    def fetchall(self):
        return self._fetch_result

    def fetchone(self):
        return self._fetch_result

    def close(self):
        self.closed = True


class MockConn:
    def __init__(self, cursor_obj):
        self._cursor = cursor_obj

    def cursor(self, dictionary=True):
        return self._cursor


def test_get_contents_list_success():
    contents = [{"content_id": 1, "title": "a", "description": "d", "difficulty": "easy", "answer_code": "c"}]
    cursor = MockCursor(fetch_result=contents)
    conn = MockConn(cursor)

    res = get_contents_list(conn=conn)
    assert res == contents
    assert cursor.closed is True


def test_get_contents_list_db_error():
    cursor = MockCursor(fetch_result=None, raise_on_execute=True)
    conn = MockConn(cursor)

    with pytest.raises(HTTPException) as exc:
        get_contents_list(conn=conn)
    assert exc.value.status_code == 500
    assert cursor.closed is True


def test_get_content_by_id_success():
    content = {"content_id": 1, "title": "a", "description": "d", "difficulty": "easy", "answer_code": "c"}
    cursor = MockCursor(fetch_result=content)
    conn = MockConn(cursor)

    res = get_content_by_id(content_id=1, conn=conn)
    assert res == content
    assert cursor.closed is True


def test_get_content_by_id_not_found():
    cursor = MockCursor(fetch_result=None)
    conn = MockConn(cursor)

    with pytest.raises(HTTPException) as exc:
        get_content_by_id(content_id=999, conn=conn)
    assert exc.value.status_code == 404
    assert cursor.closed is True


def test_get_content_by_id_db_error():
    cursor = MockCursor(fetch_result=None, raise_on_execute=True)
    conn = MockConn(cursor)

    with pytest.raises(HTTPException) as exc:
        get_content_by_id(content_id=1, conn=conn)
    assert exc.value.status_code == 500
    assert cursor.closed is True
