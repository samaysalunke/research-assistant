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

4. **Start the application**
   ```bash
   # Backend (from backend directory)
   uvicorn main:app --reload --port 8000
   
   # Frontend (from frontend directory)
   npm run dev
   ```

### **Using the Application**

#### **Content Ingestion**
1. **Upload PDFs**: Drag and drop PDF files or use the file picker
2. **Add URLs**: Enter web URLs to extract and analyze content
3. **Direct Text**: Paste text content directly for processing
4. **Monitor Progress**: Track processing status in real-time

#### **Conversational Search**
1. **Ask Questions**: Use natural language queries like "What is the connection between reading and writing?"
2. **Get AI Responses**: Receive comprehensive, synthesized answers
3. **Explore Sources**: View the documents that informed the response
4. **Follow-up Suggestions**: Get intelligent suggestions for related questions

#### **Advanced Search**
1. **Multiple Search Types**: Choose from semantic, keyword, hybrid, tag, or content-type search
2. **Smart Filtering**: Filter results by quality, language, tags, or date ranges
3. **Sorting Options**: Sort by relevance, date, quality, or reading time
4. **Export Results**: Save and share search results

## 🔧 Configuration

### **Environment Variables**
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI Services
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Application Settings
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:5173
```

### **Database Setup**
1. Create a Supabase project
2. Enable the `pgvector` extension
3. Run the provided migration scripts
4. Configure Row Level Security policies

## 📊 Performance

### **Processing Capabilities**
- **PDF Processing**: Up to 50MB files, multi-page support
- **Web Scraping**: Intelligent content extraction with fallback mechanisms
- **AI Processing**: Parallel processing with background tasks
- **Search Performance**: Sub-second response times with vector indexing

### **Scalability**
- **Horizontal Scaling**: Stateless backend design
- **Database Optimization**: Efficient indexing and query optimization
- **Caching**: Intelligent caching for frequently accessed content
- **Background Processing**: Non-blocking content processing

## 🔒 Security

### **Data Protection**
- **Row Level Security**: User data isolation
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive input sanitization
- **File Upload Security**: Secure PDF processing with validation

### **Privacy**
- **Local Processing**: Content processed on your infrastructure
- **No Data Sharing**: Your data stays private
- **Configurable Retention**: Control data retention policies

## 🧪 Testing

### **API Testing**
```bash
# Test the API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/search/conversational?q=test
```

### **Frontend Testing**
```bash
cd frontend
npm run test
npm run build
```

## 📚 Documentation

- **[User Guide](docs/USER_GUIDE.md)**: Complete user documentation
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Development setup and guidelines
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: Production deployment instructions

## 🚀 Deployment

### **Quick Deploy Options**
- **Railway**: One-click deployment with automatic scaling
- **Render**: Free tier available with easy setup
- **Vercel**: Frontend deployment with serverless functions

### **Production Setup**
- **Docker**: Containerized deployment
- **Cloud Platforms**: AWS, GCP, Azure support
- **Monitoring**: Built-in health checks and logging
- **SSL/TLS**: Automatic HTTPS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### **Development Guidelines**
- Follow TypeScript best practices
- Use conventional commits
- Add comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Comprehensive guides and tutorials
- **Examples**: Sample queries and use cases

## 🗺️ Roadmap

### **Upcoming Features**
- **Video Processing**: YouTube and video content analysis
- **Multi-language Support**: Internationalization and translation
- **Collaborative Features**: Team workspaces and sharing
- **Advanced Analytics**: Usage insights and content metrics
- **Mobile App**: Native iOS and Android applications

### **Enhancements**
- **Voice Search**: Speech-to-text search capabilities
- **Export Options**: Multiple format export (PDF, Word, Markdown)
- **Integration APIs**: Third-party service integrations
- **Advanced AI Models**: Support for additional AI providers

---

**Built with ❤️ using modern web technologies and AI**
