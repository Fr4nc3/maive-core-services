import pytest

from app.infrastructure.rai import output_validator
from app.infrastructure.rai.errors import BotPipelineError


def test_clean_astronomy_output_passes():
    text = "Mars has two moons named Phobos and Deimos. Its gravity is weaker than Earth's."
    ok, reasons = output_validator.validate(text)
    assert ok and reasons == []


def test_blocks_email():
    ok, reasons = output_validator.validate(
        "Contact me at someone@example.com about Mars."
    )
    assert not ok and "pii_email" in reasons


def test_blocks_url():
    ok, reasons = output_validator.validate(
        "See https://example.com for more about the moon."
    )
    assert not ok and "url_leak" in reasons


def test_blocks_instruction_leak():
    ok, reasons = output_validator.validate(
        "My instructions say to only answer astronomy questions about Mars."
    )
    assert not ok and "instruction_leak" in reasons


def test_blocks_off_topic_output():
    ok, reasons = output_validator.validate("I love chocolate cake recipes.")
    assert not ok and "off_topic_output" in reasons


def test_check_raises_on_failure():
    with pytest.raises(BotPipelineError) as exc:
        output_validator.check("Email me at x@y.com")
    assert exc.value.http_status == 502
