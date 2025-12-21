import mysql.connector
import types
import pytest
from database.dependencies import get_db_connection


class DummyConn:
    def __init__(self):
        self.closed = False

    def is_connected(self):
        return True

    def close(self):
        self.closed = True


def test_get_db_connection_yields_and_closes(monkeypatch):
    dummy = DummyConn()

    def fake_connect(**kwargs):
        return dummy

    monkeypatch.setattr("database.dependencies.mysql.connector.connect", fake_connect)

    gen = get_db_connection()
    conn = next(gen)  # should yield dummy connection
    assert conn is dummy

    # closing generator should trigger finally and close the connection
    gen.close()
    assert dummy.closed is True
