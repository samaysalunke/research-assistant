# Developer Guide - Research-to-Insights Agent

A comprehensive guide for developers contributing to or integrating with the Research-to-Insights Agent.

## 🏗️ Architecture Overview

### **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (Supabase)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI Services   │
                       │  (Claude/OpenAI)│
                       └─────────────────┘
```

### **Core Components**

1. **Frontend**: React 18 + TypeScript + Tailwind CSS
2. **Backend**: FastAPI + Python 3.11+
3. **Database**: Supabase (PostgreSQL + pgvector)
4. **AI Services**: Anthropic Claude + OpenAI Embeddings
5. **Content Processing**: Playwright + newspaper3k

## 📁 Project Structure

```
research-insights-agent/
├── backend/
│   ├── api/                    # FastAPI routes
│   │   ├── v1/
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── documents.py   # Document management
│   │   │   ├── ingest.py      # Content ingestion
│   │   │   └── search.py      # Search endpoints
│   │   └── dependencies.py    # Shared dependencies
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings management
│   │   └── logging.py         # Logging configuration
│   ├── services/               # Business logic services
│   │   ├── content_processor.py    # Main content processing
│   │   ├── ai_processor.py         # AI analysis service
│   │   ├── text_processor.py       # Text processing
│   │   ├── web_scraper.py          # Web scraping
│   │   ├── processing_pipeline.py  # Processing pipeline
│   │   └── enhanced_search.py      # Search service
│   ├── models/                 # Pydantic models
│   │   └── schemas.py          # API request/response models
│   ├── database/               # Database operations
│   │   ├── client.py           # Supabase client
│   │   └── migrations/         # Database migrations
│   ├── auth/                   # Authentication
│   │   └── middleware.py       # Auth middleware
│   └── main.py                 # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API services
│   │   ├── contexts/           # React contexts
│   │   ├── utils/              # Utility functions
│   │   └── types/              # TypeScript types
│   ├── public/                 # Static assets
│   └── package.json            # Dependencies
├── database/
│   └── migrations/             # SQL migrations
├── docs/                       # Documentation
└── README.md                   # Project overview
```

## 🚀 Development Setup

### **Prerequisites**

- Python 3.11+
- Node.js 18+
- Git
- Supabase CLI (optional)

### **Local Development**

1. **Clone Repository**
   ```bash
   git clone https://github.com/samaysalunke/research-assistant.git
   cd research-assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and Supabase credentials
   ```

5. **Database Setup**
   ```bash
   cd backend
   # Apply migrations
   python -m database.migrations
   ```

6. **Start Development Servers**
   ```bash
   # Backend (from backend directory)
   uvicorn main:app --reload --port 8000
   
   # Frontend (from frontend directory)
   npm run dev
   ```

## 🔧 Core Services

### **Content Processing Pipeline**

The content processing pipeline consists of several stages:

1. **Content Extraction** (`web_scraper.py`)
2. **Text Processing** (`text_processor.py`)
3. **AI Analysis** (`ai_processor.py`)
4. **Embedding Generation** (`content_processor.py`)
5. **Database Storage** (`processing_pipeline.py`)

#### **Example: Adding a New Processing Stage**

```python
# In services/processing_pipeline.py
async def _custom_processing_stage(self, task: ProcessingTask, content: str):
    """Custom processing stage"""
    try:
        # Your custom processing logic
        processed_content = await self.custom_processor.process(content)
        
        # Update task progress
        await self._update_task_progress(task, ProcessingStage.CUSTOM, 0.85)
        
        return processed_content
        
    except Exception as e:
        raise Exception(f"Custom processing failed: {str(e)}")
```

### **Enhanced Search Service**

The search service supports multiple search types:

```python
# In services/enhanced_search.py
async def search(self, query: str, user_id: str, 
                search_type: SearchType = SearchType.HYBRID,
                filters: Dict[str, Any] = None,
                sort_by: SortType = SortType.RELEVANCE,
                limit: int = 20, offset: int = 0):
    """Enhanced search with multiple search types and filtering"""
```

#### **Adding a New Search Type**

```python
# Add new search type enum
class SearchType(Enum):
    CUSTOM = "custom"

# Implement search method
async def _custom_search(self, query: str, base_query, limit: int, offset: int):
    """Custom search implementation"""
    # Your custom search logic
    pass
```

### **AI Processing Service**

The AI service uses content-aware processing strategies:

```python
# In services/ai_processor.py
class ProcessingStrategy(Enum):
    COMPREHENSIVE = "comprehensive"  # High-quality content
    STANDARD = "standard"           # Regular content
    LIGHT = "light"                 # Low-quality content
    TECHNICAL = "technical"         # Technical documentation
    ACADEMIC = "academic"           # Academic content
```

## 📊 Database Schema

### **Core Tables**

#### **documents**
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    source_url TEXT,
    title TEXT NOT NULL,
    summary TEXT,
    tags TEXT[],
    insights JSONB,
    action_items TEXT[],
    quotable_snippets JSONB,
    processing_status TEXT DEFAULT 'pending',
    content_type TEXT,
    quality TEXT,
    language TEXT DEFAULT 'en',
    word_count INTEGER,
    sentence_count INTEGER,
    paragraph_count INTEGER,
    reading_time_minutes INTEGER,
    complexity_score DECIMAL(3,2),
    key_phrases TEXT[],
    structure JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### **document_chunks**
```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### **processing_status**
```sql
CREATE TABLE processing_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID UNIQUE NOT NULL,
    url TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    status TEXT NOT NULL,
    stage TEXT NOT NULL,
    progress DECIMAL(3,2) DEFAULT 0.0,
    error_message TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    retry_count INTEGER DEFAULT 0,
    result JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **Database Functions**

#### **Vector Similarity Search**
```sql
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    document_id uuid,
    chunk_index int,
    content text,
    similarity float,
    metadata jsonb
);
```

#### **Hybrid Search**
```sql
CREATE OR REPLACE FUNCTION hybrid_search_documents(
    query_text text,
    query_embedding vector(1536),
    user_id uuid,
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 20
);
```

## 🔌 API Reference

### **Authentication**

All API endpoints require authentication via JWT tokens:

```http
Authorization: Bearer <jwt_token>
```

### **Content Ingestion**

#### **Process URL**
```http
POST /api/v1/ingest/
Content-Type: application/json

{
  "source_url": "https://example.com/article",
  "text_content": "Optional direct text input"
}
```

#### **Get Processing Status**
```http
GET /api/v1/ingest/{task_id}/status
```

### **Search**

#### **Enhanced Search**
```http
GET /api/v1/search/
  ?q=artificial intelligence
  &search_type=hybrid
  &content_type=technical
  &quality=excellent
  &sort_by=relevance
  &limit=20
```

#### **Search with Filters**
```http
POST /api/v1/search/
Content-Type: application/json

{
  "query": "machine learning",
  "search_type": "semantic",
  "filters": {
    "content_type": "technical",
    "quality": "excellent",
    "tags": ["python", "ai"]
  },
  "sort_by": "relevance",
  "limit": 10
}
```

### **Document Management**

#### **List Documents**
```http
GET /api/v1/documents/
  ?limit=20
  &offset=0
  &content_type=technical
```

#### **Get Document**
```http
GET /api/v1/documents/{document_id}
```

#### **Delete Document**
```http
DELETE /api/v1/documents/{document_id}
```

## 🧪 Testing

### **Backend Testing**

```bash
cd backend
python -m pytest tests/
```

#### **Test Structure**
```
backend/tests/
├── test_api/              # API endpoint tests
├── test_services/         # Service layer tests
├── test_database/         # Database tests
└── conftest.py           # Test configuration
```

#### **Example Test**
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_search_endpoint():
    response = client.get("/api/v1/search/?q=test")
    assert response.status_code == 200
    assert "results" in response.json()
```

### **Frontend Testing**

```bash
cd frontend
npm test
```

#### **Component Testing**
```typescript
import { render, screen } from '@testing-library/react'
import SearchPage from '../pages/Search'

test('renders search input', () => {
  render(<SearchPage />)
  const searchInput = screen.getByPlaceholderText(/search/i)
  expect(searchInput).toBeInTheDocument()
})
```

## 🔧 Configuration

### **Environment Variables**

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AI Services
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key

# Application Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7

# Processing Settings
MAX_RETRIES=3
PROCESSING_TIMEOUT=300
BATCH_SIZE=10
```

### **Processing Configuration**

```python
# In core/config.py
class Settings(BaseSettings):
    # Content processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    vector_dimension: int = 1536
    similarity_threshold: float = 0.7
    
    # AI processing
    max_tokens: int = 4000
    temperature: float = 0.3
    
    # Processing pipeline
    max_retries: int = 3
    processing_timeout: int = 300
    batch_size: int = 10
```

## 🚀 Deployment

### **Production Setup**

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   export ENVIRONMENT=production
   export DEBUG=false
   ```

2. **Database Migration**
   ```bash
   cd backend
   python -m database.migrations
   ```

3. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

4. **Deploy Backend**
   ```bash
   # Using uvicorn
   uvicorn main:app --host 0.0.0.0 --port 8000
   
   # Using gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### **Docker Deployment**

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

## 🔍 Monitoring & Logging

### **Logging Configuration**

```python
# In core/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### **Performance Monitoring**

```python
# In services/processing_pipeline.py
async def get_processing_metrics(self) -> Dict[str, Any]:
    """Get processing pipeline metrics"""
    return {
        "total_processed": self.metrics["total_processed"],
        "successful": self.metrics["successful"],
        "failed": self.metrics["failed"],
        "average_processing_time": self.metrics["average_processing_time"],
        "success_rate": self.metrics["success_rate"]
    }
```

## 🤝 Contributing

### **Development Workflow**

1. **Fork Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**
4. **Add Tests**
5. **Run Test Suite**
   ```bash
   # Backend tests
   cd backend && python -m pytest
   
   # Frontend tests
   cd frontend && npm test
   ```
6. **Submit Pull Request**

### **Code Standards**

- **Python**: Follow PEP 8 style guide
- **TypeScript**: Use strict mode and proper typing
- **Testing**: Maintain >80% test coverage
- **Documentation**: Update docs for new features

### **Commit Convention**

```
feat: add new search type
fix: resolve processing timeout issue
docs: update API documentation
test: add tests for enhanced search
refactor: improve content processing pipeline
```

## 🆘 Troubleshooting

### **Common Issues**

#### **Database Connection Issues**
```bash
# Check Supabase connection
python -c "from database.client import get_supabase_client; print('Connected')"
```

#### **AI Service Issues**
```bash
# Test AI service connectivity
python -c "from services.ai_processor import EnhancedAIProcessor; print('AI service ready')"
```

#### **Processing Pipeline Issues**
```bash
# Check processing status
curl -X GET "http://localhost:8000/api/v1/ingest/{task_id}/status"
```

### **Debug Mode**

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start with debug mode
uvicorn main:app --reload --log-level debug
```

## 📚 Additional Resources

- **API Documentation**: `/docs` endpoint when running backend
- **Supabase Documentation**: https://supabase.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **TypeScript Documentation**: https://www.typescriptlang.org/docs/

---

**For technical support or questions, create an issue in the repository or contact the development team.**
