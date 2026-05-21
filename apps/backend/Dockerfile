FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PORT=8000

WORKDIR /app

# Copy uv from the official Astral image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies first to improve Docker layer caching.
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Copy application source code.
COPY app ./app

EXPOSE 8000

CMD ["sh", "-c", "uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]