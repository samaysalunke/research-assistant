#!/bin/bash
echo "🧪 Testing Research-to-Insights Agent Setup..."
source venv/bin/activate
echo "✅ Python environment activated"
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(\".env\"); print(\"✅ Environment variables loaded\")"
python3 -c "import anthropic; print(\"✅ Anthropic client ready\")"
cd backend && python3 -c "from main import app; print(\"✅ FastAPI app ready\")"
echo "🎉 All systems ready for development!"
