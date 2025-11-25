FROM python:3.11-slim

WORKDIR /app

# Install build dependencies (split into separate RUN to avoid resource issues)
RUN apt-get update -qq
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gcc python3-dev

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies to reduce image size
RUN apt-get remove -y gcc python3-dev
RUN apt-get autoremove -y
RUN rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

EXPOSE 8000

# Railway provides PORT as environment variable
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

