# Multi-stage Dockerfile for AI Wellness Vision System
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies with optimizations
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ffmpeg \
    libsndfile1 \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge && \
    find /usr/local/lib/python3.10 -name "*.pyc" -delete && \
    find /usr/local/lib/python3.10 -name "__pycache__" -type d -exec rm -rf {} + || true

# Development stage
FROM base as development
COPY . .
EXPOSE 8000 8501
CMD ["python", "streamlit_app.py"]

# Production stage
FROM base as production

# Create non-root user with specific UID/GID for security
RUN groupadd -r app --gid=1000 && \
    useradd -r -g app --uid=1000 --home-dir=/app --shell=/bin/bash app

# Copy application code with proper ownership
COPY --chown=app:app . .

# Remove unnecessary files and optimize
RUN rm -rf tests/ docs/ .git/ .github/ *.md .gitignore .dockerignore && \
    find . -name "*.pyc" -delete && \
    find . -name "__pycache__" -type d -exec rm -rf {} + || true

# Switch to non-root user
USER app

# Health check with improved configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 8501

# Optimized start command with better resource management
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "30", \
     "--keep-alive", "5", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "src.api.gateway:app"]

# Lightweight service-specific images
FROM base as api-service
COPY --chown=app:app src/ ./src/
COPY --chown=app:app config/ ./config/
RUN groupadd -r app --gid=1000 && \
    useradd -r -g app --uid=1000 --home-dir=/app --shell=/bin/bash app
USER app
EXPOSE 8000
CMD ["uvicorn", "src.api.gateway:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

FROM base as streamlit-service
COPY --chown=app:app src/ ./src/
COPY --chown=app:app streamlit_app.py ./
COPY --chown=app:app config/ ./config/
RUN groupadd -r app --gid=1000 && \
    useradd -r -g app --uid=1000 --home-dir=/app --shell=/bin/bash app
USER app
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

FROM base as worker-service
COPY --chown=app:app src/ ./src/
COPY --chown=app:app config/ ./config/
RUN groupadd -r app --gid=1000 && \
    useradd -r -g app --uid=1000 --home-dir=/app --shell=/bin/bash app
USER app
CMD ["python", "-m", "src.services.worker"]