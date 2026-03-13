FROM python:3.12-slim AS base
ARG BUILDKIT_INLINE_CACHE=1

WORKDIR /project

## Install uv

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# ------------------------
# Dev target
# ------------------------

FROM base AS dev

COPY services/ecom-backend/pyproject.toml /project/services/ecom-backend/pyproject.toml

WORKDIR /project/services/ecom-backend

RUN uv pip install --system --no-cache-dir -e . --group dev

EXPOSE 8000


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod

COPY services/ecom-backend/pyproject.toml /project/services/ecom-backend/pyproject.toml

WORKDIR /project/services/ecom-backend

COPY services/ecom-backend /project/services/ecom-backend

# Ref: https://www.reddit.com/r/learnpython/comments/1hspt62/installing_dependencies_with_uv_sync_systemwide/
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --locked --no-dev --no-cache-dir



CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
