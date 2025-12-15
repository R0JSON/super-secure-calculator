FROM python:3.10

# 1. CIS 5.7: Create a non-root user for the application
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# 2. CIS 4.6: Clean up package manager cache (This applies to the base Python image)
RUN rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app

# 3. CIS 5.3: Ensure copied files are owned by the non-root user (appuser:appgroup)
COPY --chown=appuser:appgroup ./scripts /app/scripts

COPY --chown=appuser:appgroup ./pyproject.toml ./uv.lock ./alembic.ini /app/

COPY --chown=appuser:appgroup ./app /app/app

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# 1. CIS 5.7: Switch to the non-root user for the final command execution
USER appuser

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
