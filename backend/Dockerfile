# Optimized multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Install only essential build dependencies
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Production image
FROM python:3.11-slim

WORKDIR /app

# Copy only Python packages from builder (smaller than copying entire site-packages)
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy user-installed packages
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy only application code (not docs, etc)
COPY backend/app ./app
COPY backend/requirements.txt ./requirements.txt

EXPOSE 8000

ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT

