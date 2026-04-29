"""RAI guardrail (6-stage bot pipeline, DEC-019).

Pillar: Stable Core
Phase: R
Purpose: RAI guardrail (6-stage bot pipeline, DEC-019).
Documented in: docs/rai-policy.md
"""

import re

from app.infrastructure.rai.errors import BotPipelineError

# Curated seed terms — astronomy / planetary science / MAIVE module topics.
# Lexical baseline; embedding-distance variant slot in via `score()` later.
_SEED_TERMS = frozenset(
    {
        "planet", "planeta", "moon", "luna", "star", "estrella", "sun", "sol",
        "orbit", "orbita", "gravity", "gravedad", "mass", "masa",
        "atmosphere", "atmosfera", "crater", "crater", "mars", "marte",
        "venus", "mercury", "mercurio", "earth", "tierra", "jupiter",
        "saturn", "saturno", "uranus", "urano", "neptune", "neptuno",
        "pluto", "pluton", "asteroid", "asteroide", "comet", "cometa",
        "galaxy", "galaxia", "solar", "system", "sistema", "telescope",
        "telescopio", "satellite", "satelite", "rover", "nasa", "iss",
        "mission", "mision", "rocket", "cohete", "spacecraft", "nave",
        "constellation", "constelacion", "eclipse", "tide", "marea",
        "rotation", "rotacion", "revolution", "revolucion", "axis", "eje",
        "light-year", "parsec", "nebula", "supernova", "black hole",
        "agujero negro", "habitable", "exoplanet", "exoplaneta", "phase",
        "fase", "season", "estacion", "meteor", "meteorito",
    }
)

# Soft threshold: at least one seed term hit OR length-normalised score above this.
MIN_SCORE = 0.05

_TOKEN_RE = re.compile(r"[a-záéíóúñ0-9\-]+", re.IGNORECASE)


def score(text: str) -> float:
    """Return a 0..1 astronomy-relevance score (lexical baseline)."""
    if not text:
        return 0.0
    tokens = _TOKEN_RE.findall(text.lower())
    if not tokens:
        return 0.0
    hits = sum(1 for t in tokens if t in _SEED_TERMS)
    # Bigram check for two-word seeds
    for a, b in zip(tokens, tokens[1:]):
        if f"{a} {b}" in _SEED_TERMS:
            hits += 1
    return min(1.0, hits / max(1, len(tokens)))


def check(text: str) -> float:
    """Return the score; raise BotPipelineError if below threshold."""
    s = score(text)
    if s < MIN_SCORE:
        raise BotPipelineError(
            stage="topic_gate",
            reason=f"off_topic:score={s:.3f}",
            http_status=422,
            public_detail="off_topic",
        )
    return s
