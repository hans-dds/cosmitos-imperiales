FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ ./src/
COPY docker/entrypoint.sh ./docker/entrypoint.sh

# Instalación de dependencias vía UV
RUN uv sync --no-dev \
    && chmod +x ./docker/entrypoint.sh

EXPOSE 8501

CMD ["/app/docker/entrypoint.sh"]
