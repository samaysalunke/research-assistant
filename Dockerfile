# Use Python 3.11 for better compatibility
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy package files
COPY frontend/package*.json ./frontend/
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install Node.js dependencies (including dev dependencies for build)
WORKDIR /app/frontend
RUN npm ci

# Copy application code
WORKDIR /app
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm run build
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start command - run startup test first, then start the app
CMD python startup_test.py && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
