FROM python:3.12-slim AS base

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

# Copy only dependency manifest
COPY service/requirements.txt service/requirements.txt

# Copy whole package (even though we will later volume mount it, we need to copy it for install to work)
COPY pkg/ pkg/

# Install dependencies (note that these remain cached unless requirements.txt or pyproject.toml change)
RUN uv pip install --system --no-cache-dir -r service/requirements.txt

WORKDIR /project/service

EXPOSE 8010

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010", "--reload"]

# ------------------------
# Prod target
# ------------------------

FROM base AS prod
COPY . /project

# TODO: Create a separate requirements.txt for prod (as editable install is not needed, and is probably unsafe)
RUN uv pip install --system --no-cache-dir -r service/requirements.txt
WORKDIR /project/service
EXPOSE 8010

# TODO: Check if 0.0.0.0 is unsafe (hussein nasser ref video)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]