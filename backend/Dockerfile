FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies only if needed
# Most Python packages have wheels, so we may not need gcc
RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Remove build tools after installation to reduce image size
RUN apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Use PORT environment variable (Railway provides this)
ENV PORT=8000

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

