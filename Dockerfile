# ==============================================================================
# Multi-Stage Production Dockerfile for MoveSense Pedestrian Behaviour Pipeline
# Target: Production Inference & Batch Evaluation
# ==============================================================================

# ------------------------------------------------------------------------------
# STAGE 1: Builder (Compiles wheels in isolated environment)
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Copy project definitions and source code to build package wheels
COPY pyproject.toml .
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --wheel-dir=/build/wheels .

# ------------------------------------------------------------------------------
# STAGE 2: Production Runtime (Ultra-lightweight & Non-Root)
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="MoveSense Pedestrian Tracking & Behaviour Pipeline" \
      org.opencontainers.image.version="0.1.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Security: Create non-root user (UID 10001)
RUN groupadd -g 10001 movesense && \
    useradd -u 10001 -g movesense -m -s /bin/bash movesense

WORKDIR /app

# Copy compiled wheels from builder and install into minimal virtualenv
COPY --from=builder /build/wheels /wheels
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy configuration files
COPY --chown=movesense:movesense configs/ /app/configs/

# Drop root privileges permanently
USER 10001

# Entrypoint verification command
ENTRYPOINT ["python"]
CMD ["-c", "import movesense; print('MoveSense Production Container Ready!')"]
