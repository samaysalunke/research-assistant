# Research-to-Insights Agent

Transform how knowledge workers capture, process, and retrieve insights from digital content by automating the journey from raw URLs/text to structured, queryable knowledge.

## 🎯 Vision

Build a lightweight AI agent that eliminates the friction between consuming content and accessing insights later, turning every piece of content into a structured, searchable knowledge asset.

## 🏗️ Architecture

```
Content Input → AI Processing → Structured Storage → Intelligent Retrieval
```

### Key Components
- **Content Ingestion Engine**: URL processing, text extraction, multi-format support
- **AI Processing Pipeline**: GPT-4 powered insight extraction and summarization
- **Structured Storage System**: Supabase with pgvector for semantic search
- **Semantic Search & Chat Interface**: Natural language querying with source attribution

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: OpenAI GPT-4 for content processing
- **Database**: Supabase (PostgreSQL + pgvector)
- **Authentication**: Supabase Auth
- **Real-time**: Supabase real-time subscriptions

### Frontend
- **Framework**: React with TypeScript
- **UI Library**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand or React Query
- **Build Tool**: Vite

## 📁 Project Structure

```
research-insights-agent/
├── backend/
│   ├── api/           # FastAPI routes
│   ├── core/          # Business logic
│   ├── models/        # Pydantic models
│   ├── services/      # External integrations (OpenAI, scraping)
│   ├── database/      # Supabase client and operations
│   └── auth/          # Authentication middleware
├── frontend/
│   ├── components/    # React components
│   ├── pages/         # Page components
│   ├── hooks/         # Custom React hooks
│   ├── services/      # Supabase client and API calls
│   ├── contexts/      # Auth and app contexts
│   └── utils/         # Helper functions
├── database/
│   ├── migrations/    # Supabase migrations
│   ├── seeds/         # Initial data
│   └── types/         # Generated TypeScript types
└── shared/
    ├── types/         # Shared TypeScript types
    └── schemas/       # Data validation schemas
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git
- Supabase account
- OpenAI API key

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/samaysalunke/research-assistant.git
   cd research-assistant
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Install dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

4. **Start development servers**
   ```bash
   # Backend (from backend directory)
   uvicorn main:app --reload --port 8000
   
   # Frontend (from frontend directory)
   npm run dev
   ```

## 📋 Development Phases

This project follows a milestone-based development approach:

- **Phase 1**: Foundation & Infrastructure (Weeks 1-2)
- **Phase 2**: Core Backend API (Weeks 3-4)
- **Phase 3**: Content Processing Engine (Weeks 5-6)
- **Phase 4**: Advanced Search & Retrieval (Weeks 7-8)
- **Phase 5**: Frontend User Interface (Weeks 9-10)
- **Phase 6**: Multi-Format Support (Weeks 11-12)
- **Phase 7**: Performance & Optimization (Weeks 13-14)
- **Phase 8**: Testing & Quality Assurance (Weeks 15-16)
- **Phase 9**: Deployment & Production (Weeks 17-18)
- **Phase 10**: Documentation & Launch (Weeks 19-20)

For detailed implementation plan, see [project-plan.md](./project-plan.md).

## 🔧 Environment Variables

Create a `.env` file with the following variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# JWT Configuration
JWT_SECRET=your_jwt_secret_here

# Application Configuration
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📊 Success Metrics

- **Processing Success Rate**: >95% for supported formats
- **Search Response Time**: <1 second for vector similarity search
- **User Retention**: 70% weekly active users
- **System Uptime**: 99.5% availability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Check the [documentation](./docs/)
- Review the [project plan](./project-plan.md)

---

**Repository**: [https://github.com/samaysalunke/research-assistant.git](https://github.com/samaysalunke/research-assistant.git)
