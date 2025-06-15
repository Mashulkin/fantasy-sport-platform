# Multi-stage Docker build for FastAPI backend application.

# Creates optimized Python environment with all dependencies
# and proper permissions for production deployment.

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    netcat-traditional \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and build tools for better package installation
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for Docker layer caching optimization
COPY requirements.txt .

# Install Python dependencies without cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/alembic/versions && \
    mkdir -p /app/scripts && \
    chmod -R 777 /app/alembic

# Copy and make entrypoint script executable
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Expose application port
EXPOSE 8000

# Set entrypoint and default command
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
