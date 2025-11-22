# Build stage
FROM python:3.13-slim-bookworm AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 755 /install.sh && /install.sh && rm /install.sh

ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only dependency files first (for Docker layer caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies in a virtual environment
RUN uv sync --frozen --no-install-project

# Runtime stage
FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:${PATH}"

# Create non-root user for security
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Run FastAPI application (no --reload for production)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]