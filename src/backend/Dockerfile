# Documented in: docs/RUNLOCAL.md, docs/deployment/runbook.md
# Multi-stage build for the MAIVE FastAPI backend.
# Builder uses uv to install locked deps into a project-local .venv;
# runtime stage copies the .venv into a slim image with a non-root user.

# ---------- Builder ----------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Install uv
RUN pip install --no-cache-dir uv==0.5.*

WORKDIR /app

# Copy lockfile + project descriptor first for max cache reuse.
COPY pyproject.toml uv.lock* ./

# Install dependencies (no project code yet).
RUN uv sync --frozen --no-install-project --no-dev

# Now copy the application source and install the project itself.
COPY app ./app
RUN uv sync --frozen --no-dev

# ---------- Runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Non-root user
RUN groupadd --system maive && useradd --system --gid maive --home /app maive

WORKDIR /app

# Copy the prepared virtualenv and the application code.
COPY --from=builder --chown=maive:maive /app/.venv /app/.venv
COPY --from=builder --chown=maive:maive /app/app /app/app

USER maive

EXPOSE 8000

# Healthcheck: composite /api/health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/health', timeout=3).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
