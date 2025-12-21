import base64
import json
import Levenshtein
import pytest

from services.ocr_service import (
    encode_image_to_base64,
    get_text_from_image,
    compare_codes,
)


def test_encode_image_to_base64(tmp_path):
    data = b"\x00\x01\x02hello"
    p = tmp_path / "test.bin"
    p.write_bytes(data)

    encoded = encode_image_to_base64(str(p))
    assert encoded == base64.b64encode(data).decode('utf-8')


class MockResponse:
    def __init__(self, json_data=None, status_code=200, raise_exc=False):
        self._json = json_data or {}
        self.status_code = status_code
        self._raise = raise_exc

    def raise_for_status(self):
        if self._raise:
            raise Exception("HTTP error")

    def json(self):
        return self._json


def test_get_text_from_image_extracts_code_block(monkeypatch):
    text = "Some header\n```python\n1: print(\"hi\")\n2: print(\"bye\")\n```\nfooter"
    mock_json = {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    def fake_post(*args, **kwargs):
        return MockResponse(json_data=mock_json)

    monkeypatch.setattr("services.ocr_service.requests.post", fake_post)

    result = get_text_from_image("dummy_base64")
    assert result == "1: print(\"hi\")\n2: print(\"bye\")"


def test_get_text_from_image_returns_none_on_exception(monkeypatch):
    def fake_post(*args, **kwargs):
        raise Exception("network")

    monkeypatch.setattr("services.ocr_service.requests.post", fake_post)

    result = get_text_from_image("dummy_base64")
    assert result is None


def test_compare_codes_identical():
    extracted = "print('hi')\nprint('bye')\n"
    answer = "print('hi')\nprint('bye')\n"

    res = compare_codes(extracted, answer)

    assert res["converted_code"] == extracted
    assert res["accuracy"] == 100.0
    assert res["is_correct"] is True
    assert res["score"] == 100


def test_compare_codes_partial_mismatch():
    extracted = "print('hi')\nprint('bye')"
    answer = "print('hi')\nprint('world')"

    # compute expected accuracy using the same algorithm
    extracted_lines = [line.strip() for line in extracted.split('\n') if line.strip()]
    answer_lines = [line.strip() for line in answer.split('\n') if line.strip()]
    total_chars = sum(max(len(e), len(a)) for e, a in zip(extracted_lines, answer_lines))
    total_distance = sum(Levenshtein.distance(e, a) for e, a in zip(extracted_lines, answer_lines))
    expected_accuracy = round((1 - total_distance / total_chars) * 100, 2) if total_chars > 0 else 0.0

    res = compare_codes(extracted, answer)

    assert res["is_correct"] is False
    assert res["accuracy"] == expected_accuracy
    assert 0 <= res["score"] < 100


def test_compare_codes_empty_inputs():
    res = compare_codes("", "")
    assert res["accuracy"] == 0
    assert res["is_correct"] is False
    assert res["score"] == 0
