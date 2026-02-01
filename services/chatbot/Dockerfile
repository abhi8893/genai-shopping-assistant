FROM python:3.12-slim AS base

WORKDIR /project

# ------------------------
# Install uv
# ------------------------

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

# ======================================================
# Dev target
# ======================================================

FROM base AS dev

# ---- Copy dependency manifests only (for caching) ----
COPY services/chatbot/requirements.txt /project/service/requirements.txt
COPY packages/chatbot/pyproject.toml /project/packages/chatbot/pyproject.toml

# ---- Copy full package + service (needed for install) ----
# These will be overridden by volume mounts in dev
COPY packages/chatbot /project/packages/chatbot
COPY services/chatbot /project/service

# ---- Install deps + editable install ----
RUN uv pip install --system --no-cache-dir \
    -r /project/service/requirements.txt && \
    uv pip install --system --no-cache-dir -e /project/packages/chatbot
    
WORKDIR /project/service

EXPOSE 8010

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010", "--reload"]

# ======================================================
# Prod target
# ======================================================

FROM base AS prod

# Copy everything needed
COPY services/chatbot /project/service
COPY packages/chatbot /project/packages/chatbot

# Install deps (non-editable)
RUN uv pip install --system --no-cache-dir \
    -r /project/service/requirements.txt && \
    uv pip install --system --no-cache-dir /project/packages/chatbot

WORKDIR /project/service

EXPOSE 8010

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
