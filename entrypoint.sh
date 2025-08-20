#!/bin/bash

# Exit on any error
set -e

# Enable debug output
set -x

echo "=== Railway Deployment Startup ==="
echo "Timestamp: $(date)"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "Environment: ${ENVIRONMENT:-unknown}"
echo "Port: ${PORT:-8000}"
echo "Python version: $(python --version)"
echo "Uvicorn version: $(uvicorn --version)"

# List directory contents for debugging
echo "=== Directory Contents ==="
ls -la /app/
echo "=== Backend Directory Contents ==="
ls -la /app/backend/ || echo "Backend directory not found"

# Check if backend directory exists
if [ ! -d "/app/backend" ]; then
    echo "ERROR: Backend directory not found!"
    exit 1
fi

# Check if main.py exists
if [ ! -f "/app/backend/main.py" ]; then
    echo "ERROR: main.py not found in backend directory!"
    exit 1
fi

# Change to backend directory
echo "=== Changing to backend directory ==="
cd /app/backend

# Test Python import
echo "=== Testing Python imports ==="
python -c "
import sys
print(f'Python executable: {sys.executable}')
print(f'Python path: {sys.path}')

try:
    from main import app
    print('✓ Successfully imported FastAPI app')
    print(f'✓ App title: {app.title}')
    print(f'✓ App version: {app.version}')
except Exception as e:
    print(f'✗ Failed to import app: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# Check environment variables
echo "=== Environment Variables ==="
echo "Required environment variables check:"
for var in SUPABASE_URL SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY ANTHROPIC_API_KEY OPENAI_API_KEY; do
    if [ -z "${!var}" ]; then
        echo "WARNING: $var is not set"
    else
        echo "✓ $var is set"
    fi
done

# Start uvicorn with comprehensive logging
echo "=== Starting Uvicorn Server ==="
echo "Command: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info"

# Use exec to replace the shell process
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level info \
    --access-log \
    --use-colors \
    --loop uvloop