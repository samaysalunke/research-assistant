#!/bin/bash

# Exit on any error
set -e

echo "=== Railway Deployment Startup ==="
echo "Timestamp: $(date)"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "Environment: ${ENVIRONMENT:-unknown}"
echo "Port: ${PORT:-8000}"

# Change to backend directory
echo "=== Changing to backend directory ==="
cd /app/backend

# Test Python import
echo "=== Testing Python imports ==="
python -c "
import sys
print(f'Python executable: {sys.executable}')
try:
    from main import app
    print('✓ Successfully imported FastAPI app')
    print(f'✓ App title: {app.title}')
except Exception as e:
    print(f'✗ Failed to import app: {e}')
    sys.exit(1)
"

# Start uvicorn
echo "=== Starting Uvicorn Server ==="
echo "Command: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"

exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}