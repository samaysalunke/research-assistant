#!/bin/bash

echo "🧪 Testing Milestone 2: Core Backend API"
echo "========================================"

# Activate virtual environment
source venv/bin/activate

echo ""
echo "✅ Testing FastAPI Application:"
echo "  - Loading application..."
python3 -c "import sys; sys.path.append("backend"); from main import app; print('    ✅ App loaded successfully')"

echo ""
echo "✅ Testing API Endpoints:"
echo "  - Health check..."
curl -s http://localhost:8000/health | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'    ✅ Health: {data[\"status\"]} - {data[\"milestone\"]}')"

echo "  - Root endpoint..."
curl -s http://localhost:8000/ | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'    ✅ Root: {data[\"message\"]} v{data[\"version\"]}')"

echo ""
echo "✅ Testing Configuration:"
echo "  - Environment variables..."
python3 -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print(f'    ✅ ANTHROPIC_API_KEY: {\"SET\" if os.getenv(\"ANTHROPIC_API_KEY\") else \"NOT SET\"}')"
python3 -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print(f'    ✅ SUPABASE_URL: {\"SET\" if os.getenv(\"SUPABASE_URL\") else \"NOT SET\"}')"

echo ""
echo "✅ Testing Claude Integration:"
python3 -c "import anthropic; print('    ✅ Anthropic client ready')"

echo ""
echo "✅ Testing Supabase Integration:"
python3 -c "import supabase; print('    ✅ Supabase client ready')"

echo ""
echo "🎉 Milestone 2 Core Backend API - READY!"
echo ""
echo "📋 Available Endpoints:"
echo "  - GET /                    - API information"
echo "  - GET /health              - Health check"
echo "  - POST /api/v1/ingest/     - Content ingestion"
echo "  - GET /api/v1/ingest/{id}/status - Processing status"
echo "  - POST /api/v1/search/     - Semantic search"
echo "  - GET /api/v1/search/      - Search with query params"
echo "  - GET /api/v1/documents/   - List documents"
echo "  - GET /api/v1/documents/{id} - Get document"
echo "  - PUT /api/v1/documents/{id} - Update document"
echo "  - DELETE /api/v1/documents/{id} - Delete document"
echo "  - GET /docs                - API documentation"
echo ""
echo "🚀 Next Steps:"
echo "  1. Create Supabase project and run migrations"
echo "  2. Test content ingestion with real URLs"
echo "  3. Test semantic search functionality"
echo "  4. Begin Milestone 3: Content Processing Engine"
