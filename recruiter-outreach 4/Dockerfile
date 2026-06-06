# ============================================================
# Dockerfile — WHY IT EXISTS
# ============================================================
# A Dockerfile is a recipe for building a Docker image.
# An image = a frozen, portable snapshot of your app + its dependencies.
# A container = a running instance of that image.
#
# Why Docker?
# "It works on my machine" is never a problem with Docker.
# The same image runs identically on your laptop, a friend's PC, or a server.
#
# This is a multi-stage build:
# Stage 1 (builder): installs all Python packages
# Stage 2 (final):   copies only what's needed → smaller final image
# ============================================================


# ── STAGE 1: Builder ────────────────────────────────────────────────────────
# FROM: which base image to start from
# python:3.12-slim = Python 3.12 on minimal Debian Linux (~50MB vs ~900MB full)
FROM python:3.12-slim AS builder

# WORKDIR: all subsequent commands run from this directory inside the container
# (like doing `cd /app` before every command)
WORKDIR /app

# ENV: sets environment variables inside the container
# PYTHONDONTWRITEBYTECODE=1 → don't create .pyc cache files (saves space)
# PYTHONUNBUFFERED=1        → print() and logs appear immediately (not buffered)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# COPY requirements first (before app code)
# WHY? Docker caches each layer. If requirements.txt hasn't changed,
# Docker skips reinstalling packages on rebuild. Huge time saver.
COPY requirements.txt .

# RUN: executes a shell command during image build
# --no-cache-dir: don't cache downloaded packages (saves space in image)
# --upgrade pip: always use latest pip
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ── STAGE 2: Final image ────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy installed Python packages from builder stage
# /usr/local/lib/python3.12/site-packages = where pip installs packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create /data directory — this is where SQLite database will be stored
# Docker volume is mounted here to persist data across container restarts
RUN mkdir -p /data && chmod 777 /data

# Copy application code
# COPY <source on your machine> <destination in container>
COPY app/ ./app/

# EXPOSE: documents which port the container listens on
# Doesn't actually open the port — that's done in docker-compose.yml
# Uvicorn will listen on port 8000 inside the container
EXPOSE 8000

# HEALTHCHECK: Docker periodically runs this to know if the container is healthy
# --interval=30s: check every 30 seconds
# --timeout=10s:  fail if no response within 10 seconds
# --retries=3:    mark unhealthy after 3 consecutive failures
# curl -f: returns non-zero exit code on HTTP error (fails healthcheck properly)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# CMD: the default command to run when the container starts
# uvicorn = ASGI server that runs FastAPI
# app.main:app = Python path to the FastAPI app object
# --host 0.0.0.0 = listen on ALL network interfaces (required in Docker)
#   (127.0.0.1 would only listen inside the container, unreachable from outside)
# --port 8000 = listen on port 8000
# --reload = auto-restart when code changes (development mode)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
