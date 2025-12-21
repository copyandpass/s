import os
import pytest
import mysql.connector
from fastapi import HTTPException

import routers.submissions as submissions_module
from routers.submissions import upload_submission, get_submission_result


class MockCursor:
    def __init__(self, fetch_result=None, lastrowid=1, raise_on_execute=False):
        self._fetch_result = fetch_result
        self.lastrowid = lastrowid
        self._raise = raise_on_execute
        self.closed = False

    def execute(self, query, params=None):
        if self._raise:
            raise mysql.connector.Error("db error")

    def fetchone(self):
        return self._fetch_result

    def close(self):
        self.closed = True


class MockConn:
    def __init__(self, cursor_obj):
        self._cursor = cursor_obj
        self.committed = False

    def cursor(self, dictionary=True):
        return self._cursor

    def commit(self):
        self.committed = True


class FakeUploadFile:
    def __init__(self, data=b"abc"):
        self._data = data

    async def read(self):
        return self._data


@pytest.mark.asyncio
async def test_upload_submission_success(tmp_path, monkeypatch):
    # prepare tmp upload dir
    monkeypatch.setattr(submissions_module, "UPLOAD_DIRECTORY", str(tmp_path))

    # mock OCR service
    monkeypatch.setattr(submissions_module.ocr_service, "encode_image_to_base64", lambda p: "b64")
    monkeypatch.setattr(submissions_module.ocr_service, "get_text_from_image", lambda b: "print('hi')")
    monkeypatch.setattr(submissions_module.ocr_service, "compare_codes", lambda e, a: {
        "converted_code": "print('hi')",
        "accuracy": 100.0,
        "is_correct": True,
        "score": 100
    })

    # mock DB
    cursor = MockCursor(fetch_result={"answer_code": "print('hi')"}, lastrowid=42)
    conn = MockConn(cursor_obj=cursor)

    file = FakeUploadFile(b"imagebytes")

    res = await upload_submission(content_id=1, image=file, conn=conn)

    assert res["submission_id"] == 42
    assert res["message"].startswith("Submission")
    # ensure file was written
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert conn.committed is True


@pytest.mark.asyncio
async def test_upload_submission_content_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr(submissions_module, "UPLOAD_DIRECTORY", str(tmp_path))
    cursor = MockCursor(fetch_result=None)
    conn = MockConn(cursor_obj=cursor)

    file = FakeUploadFile(b"imagebytes")

    with pytest.raises(HTTPException) as exc:
        await upload_submission(content_id=999, image=file, conn=conn)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_upload_submission_ocr_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(submissions_module, "UPLOAD_DIRECTORY", str(tmp_path))

    monkeypatch.setattr(submissions_module.ocr_service, "encode_image_to_base64", lambda p: "b64")
    monkeypatch.setattr(submissions_module.ocr_service, "get_text_from_image", lambda b: None)

    cursor = MockCursor(fetch_result={"answer_code": "print('hi')"})
    conn = MockConn(cursor_obj=cursor)

    file = FakeUploadFile(b"imagebytes")

    with pytest.raises(HTTPException) as exc:
        await upload_submission(content_id=1, image=file, conn=conn)

    assert exc.value.status_code == 500


def test_get_submission_result_success():
    submission = {"submission_id": 1, "status": "COMPLETED"}
    cursor = MockCursor(fetch_result=submission)
    conn = MockConn(cursor_obj=cursor)

    res = get_submission_result(submission_id=1, conn=conn)
    assert res == submission
    assert cursor.closed is True


def test_get_submission_result_not_found():
    cursor = MockCursor(fetch_result=None)
    conn = MockConn(cursor_obj=cursor)

    with pytest.raises(HTTPException) as exc:
        get_submission_result(submission_id=999, conn=conn)
    assert exc.value.status_code == 404
    assert cursor.closed is True
