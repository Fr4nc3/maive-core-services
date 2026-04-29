import pytest

from app.infrastructure.rai import input_validator
from app.infrastructure.rai.errors import BotPipelineError


def test_accepts_clean_query():
    assert input_validator.validate("What is Mars?", "en") == "What is Mars?"


def test_strips_control_chars():
    out = input_validator.validate("hi\x00there", "en")
    assert out == "hithere"


def test_normalises_unicode_nfc():
    # Composed vs decomposed "á"
    out = input_validator.validate("a\u0301strofísica", "es")
    assert "á" in out


def test_rejects_unknown_language():
    with pytest.raises(BotPipelineError) as exc:
        input_validator.validate("hi", "fr")
    assert exc.value.stage == "input_validator"
    assert "language_not_allowed" in exc.value.reason


def test_rejects_empty():
    with pytest.raises(BotPipelineError):
        input_validator.validate("   ", "en")


def test_rejects_too_long():
    with pytest.raises(BotPipelineError) as exc:
        input_validator.validate("x" * (input_validator.MAX_QUERY_LENGTH + 1), "en")
    assert "too_long" in exc.value.reason


def test_rejects_non_string():
    with pytest.raises(BotPipelineError):
        input_validator.validate(123, "en")  # type: ignore[arg-type]
