# =============================================================================
# ACREVIA Backend - Enterprise Production Dockerfile
# Multi-stage build targeting CPython 3.11 with unprivileged execution
# =============================================================================

# Stage 1: Build Dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime Environment
FROM python:3.11-slim AS runner

WORKDIR /app

# Install runtime shared libraries only (PostgreSQL client runtime, libglib for OpenCV/Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Create non-root application user
RUN groupadd -g 10001 acrevia && \
    useradd -u 10001 -g acrevia -s /bin/bash -m acrevia

# Create data directories with appropriate permissions
RUN mkdir -p /app/data/storage /app/logs && \
    chown -R acrevia:acrevia /app

# Copy application source code
COPY --chown=acrevia:acrevia backend /app/backend
COPY --chown=acrevia:acrevia ml /app/ml

USER acrevia

# Configuration environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
