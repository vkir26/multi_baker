FROM python:3.13.3-slim
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations
RUN mkdir -p files
CMD alembic upgrade head && uvicorn web_baker:app --app-dir app --host 0.0.0.0 --port 8000
