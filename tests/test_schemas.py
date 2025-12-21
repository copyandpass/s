import pytest
from pydantic import ValidationError
from schemas.content_schema import Content, ContentBase
from schemas.submission_schema import SubmissionResult, SubmissionCreateResponse
from datetime import datetime


def test_content_model_valid():
    data = {"content_id": 1, "title": "Test", "description": "d", "difficulty": "easy", "answer_code": "print(1)"}
    c = Content(**data)
    assert c.content_id == 1
    assert c.title == "Test"


def test_content_model_invalid():
    # title must be a string
    with pytest.raises(ValidationError):
        ContentBase(title=123)


def test_submission_models():
    now = datetime.utcnow()
    s = SubmissionResult(submission_id=1, status="COMPLETED", image_path="/tmp/x.jpg", submitted_at=now)
    assert s.submission_id == 1

    r = SubmissionCreateResponse(submission_id=2)
    assert r.submission_id == 2
    assert isinstance(r.message, str)
