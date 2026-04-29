import pytest

from app.infrastructure.rai import topic_gate
from app.infrastructure.rai.errors import BotPipelineError


@pytest.mark.parametrize(
    "text",
    [
        "What is the orbit of Mars?",
        "Why does the moon have phases?",
        "How big is Jupiter compared to Earth?",
        "What is a black hole?",
        "Tell me about the rover on Mars.",
    ],
)
def test_astronomy_passes(text):
    score = topic_gate.check(text)
    assert score >= topic_gate.MIN_SCORE


@pytest.mark.parametrize(
    "text",
    [
        "How do I bake a chocolate cake?",
        "What is the capital of France?",
        "Translate hello to German.",
        "Who won the world cup in 2022?",
        "Recommend a good detective novel.",
    ],
)
def test_off_topic_blocked(text):
    with pytest.raises(BotPipelineError) as exc:
        topic_gate.check(text)
    assert exc.value.stage == "topic_gate"
    assert exc.value.http_status == 422


def test_spanish_astronomy_passes():
    assert topic_gate.check("¿Cuál es la masa de Marte?") >= topic_gate.MIN_SCORE
