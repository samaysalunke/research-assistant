# Research-to-Insights Agent

A powerful AI-driven research assistant that transforms digital content into structured, queryable knowledge with conversational search capabilities.

## 🚀 Key Features

### 📚 **Multi-Format Content Ingestion**
- **URL Processing**: Extract and analyze web content from any URL
- **PDF Upload**: Upload and process PDF documents with text extraction
- **Direct Text Input**: Process raw text content directly
- **Batch Processing**: Handle multiple documents simultaneously

### 🤖 **AI-Powered Content Analysis**
- **Intelligent Summarization**: Generate comprehensive summaries using Claude 3.5 Sonnet
- **Insight Extraction**: Identify key insights and actionable items
- **Tag Generation**: Automatic topic tagging and categorization
- **Content Quality Assessment**: Evaluate document quality and complexity
- **Quotable Snippets**: Extract memorable quotes and key passages

### 🔍 **Advanced Search & Retrieval**
- **Conversational Search**: Ask questions in natural language and get AI-generated responses
- **Multi-Modal Search**: Semantic, keyword, hybrid, tag, and content-type search
- **Smart Filtering**: Filter by content type, quality, language, tags, and date ranges
- **Relevance Scoring**: Intelligent ranking based on multiple factors
- **Context-Aware Responses**: AI synthesizes information from multiple documents

### 📊 **Enhanced Metadata**
- **Content Classification**: Automatic categorization of document types
- **Reading Time Estimation**: Calculate time to read documents
- **Complexity Analysis**: Assess document difficulty and complexity
- **Language Detection**: Identify document language automatically
- **Structure Analysis**: Analyze document organization and formatting

## 🏗️ Architecture

### **Backend (FastAPI + Python)**
- **FastAPI**: High-performance async web framework
- **Supabase**: PostgreSQL database with real-time capabilities
- **Anthropic Claude**: Advanced AI processing and conversational responses
- **OpenAI Embeddings**: Vector embeddings for semantic search
- **PyPDF2**: PDF text extraction and processing

### **Frontend (React + TypeScript)**
- **React 18**: Modern UI framework with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Beautiful, accessible components
- **Vite**: Fast development and build tool

### **Database (PostgreSQL + pgvector)**
- **PostgreSQL**: Robust relational database
- **pgvector**: Vector similarity search
- **Row Level Security**: Multi-tenant data isolation
- **Real-time Subscriptions**: Live updates and notifications

## 🛠️ Technology Stack

### **Core Technologies**
- **Backend**: FastAPI, Python 3.13, Pydantic
- **Database**: PostgreSQL, Supabase, pgvector
- **AI/ML**: Anthropic Claude 3.5 Sonnet, OpenAI Embeddings
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Build Tools**: Vite, npm, Python venv

### **Key Libraries**
- **PDF Processing**: PyPDF2, python-multipart
- **Web Scraping**: BeautifulSoup4, Playwright, newspaper3k
- **Text Processing**: NLTK, langdetect
- **Authentication**: JWT, Supabase Auth
- **HTTP Client**: httpx, requests

## 📖 Usage

### **Getting Started**

1. **Clone the repository**
   ```bash
   git clone https://github.com/samaysalunke/research-assistant.git
   cd research-assistant
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

4. **Start the development servers**
   ```bash
   # Backend (in one terminal)
   cd backend
   uvicorn main:app --reload --port 8000
   
   # Frontend (in another terminal)
   cd frontend
   npm run dev
   ```

5. **Open your browser**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🚀 Deployment

### **Quick Deploy to Railway**

The easiest way to deploy this application is using Railway:

1. **Fork this repository** to your GitHub account
2. **Sign up for Railway** at [railway.app](https://railway.app)
3. **Create a new project** and connect your GitHub repository
4. **Configure environment variables** (see `RAILWAY_DEPLOYMENT.md`)
5. **Deploy!** Railway will automatically build and deploy your app

### **Manual Deployment**

For other platforms, see the detailed deployment guide in `RAILWAY_DEPLOYMENT.md`.

### **Environment Variables**

Set these environment variables in your deployment platform:

```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional (with defaults)
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_secure_random_key
CORS_ORIGINS=https://your-domain.com
```

## 📚 API Documentation

### **Core Endpoints**

- `POST /api/v1/ingest/` - Ingest content from URL or text
- `POST /api/v1/ingest/pdf` - Upload and process PDF files
- `GET /api/v1/search/` - Search documents
- `POST /api/v1/conversation/query` - Conversational search
- `GET /api/v1/documents/` - List user documents

### **Authentication**

All endpoints require JWT authentication via Supabase Auth.

## 🔧 Configuration

### **Database Setup**

1. Create a Supabase project
2. Apply all migrations in `database/migrations/`
3. Configure RLS policies
4. Set up authentication

### **AI Models**

- **Anthropic Claude 3.5 Sonnet**: For content analysis and conversational responses
- **OpenAI text-embedding-3-small**: For vector embeddings

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📈 Performance

- **Content Processing**: ~30-60 seconds per document
- **Search Response**: <2 seconds for most queries
- **Conversational AI**: <5 seconds for responses
- **PDF Processing**: ~10-30 seconds depending on file size

## 🔒 Security

- **Row Level Security**: Database-level access control
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configured for production domains
- **Input Validation**: Pydantic models for all inputs
- **Rate Limiting**: Built-in protection against abuse

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` folder
- **Issues**: Report bugs on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

**Built with ❤️ using FastAPI, React, and Claude AI**
