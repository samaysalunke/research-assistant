# 🚀 Vercel Deployment Guide

This guide will help you deploy the Research-to-Insights Agent to Vercel with serverless functions.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Supabase Project**: Set up your Supabase project with all migrations applied
4. **API Keys**: Get your Anthropic and OpenAI API keys

## 🛠️ Deployment Steps

### 1. Import Project to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the configuration

### 2. Configure Environment Variables

In your Vercel project dashboard, go to "Settings" → "Environment Variables" and add:

```bash
# Application
ENVIRONMENT=production

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# AI Models
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Frontend Environment Variables
VITE_API_URL=https://your-vercel-app.vercel.app
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional
SECRET_KEY=your_secure_random_secret_key
```

### 3. Deploy

1. Vercel will automatically deploy on every push to main branch
2. The build process will:
   - Build the frontend React app
   - Deploy serverless functions from `/api` directory
   - Serve static files from global CDN
3. Your app will be available at your Vercel URL

### 4. Verify Deployment

1. Check the deployment logs in Vercel dashboard
2. Visit your Vercel URL
3. Test the health endpoint: `https://your-app.vercel.app/api/health`
4. Test the main application features

## 🔧 Configuration Details

### Vercel Configuration (`vercel.json`)

- **Frontend**: Built with Vite and served as static files
- **Backend**: Python serverless functions in `/api` directory
- **Routing**: Automatic routing for API endpoints and SPA
- **Environment**: Environment variables for both frontend and backend

### Serverless Functions

- **Runtime**: Python 3.11
- **Location**: `/api` directory
- **Endpoints**:
  - `GET /api/health` - Health check
  - `POST /api/v1/ingest` - Content ingestion
  - `GET/POST /api/v1/search` - Search functionality
  - `GET /api/v1/documents` - Document management
  - `POST /api/v1/conversation/query` - Conversational search

### Frontend Build

- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Output**: Static files served from CDN
- **SPA Routing**: Client-side routing with fallback

## 🚨 Important Notes

### Environment Variables

1. **Never commit sensitive keys** to your repository
2. **Use Vercel's environment variables** for all secrets
3. **Set both backend and frontend variables**
4. **Generate a secure SECRET_KEY** for production

### Database Migrations

Ensure all database migrations are applied in Supabase:
- `001_initial_schema.sql`
- `002_fix_vector_dimensions.sql`
- `004_enhanced_metadata.sql`
- `005_processing_status.sql`
- `006_enhanced_search.sql`
- `007_conversation_tables.sql`

### API Routes

Vercel serverless functions have some limitations:
- **Execution time**: 10 seconds for Hobby plan, 60 seconds for Pro
- **Memory**: 1024MB limit
- **Cold starts**: First request may be slower
- **Stateless**: No persistent storage between requests

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Vercel build logs for dependency issues
   - Ensure all requirements are in `api/requirements.txt`
   - Verify Node.js dependencies in `frontend/package.json`

2. **Environment Variables**
   - Verify all required variables are set in Vercel dashboard
   - Check for typos in variable names
   - Ensure API keys are valid

3. **Serverless Function Errors**
   - Check function logs in Vercel dashboard
   - Verify Python imports and dependencies
   - Ensure database connections work

4. **CORS Issues**
   - Verify CORS headers in API responses
   - Check that frontend URL matches Vercel domain

### Performance Optimization

1. **Frontend**
   - Vite automatically optimizes the build
   - Static files are served from global CDN
   - Enable compression and caching

2. **Backend**
   - Keep function code minimal
   - Use connection pooling for database
   - Implement proper error handling
   - Cache frequently accessed data

## 📈 Monitoring

Vercel provides built-in monitoring:
- **Analytics**: Page views and performance metrics
- **Function Logs**: Real-time serverless function logs
- **Deployment History**: Track all deployments
- **Domain Management**: Custom domains and SSL

## 🔄 Continuous Deployment

Vercel automatically deploys:
- **Production**: From main/master branch
- **Preview**: From pull requests and other branches
- **Rollback**: Easy rollback to previous deployments

## 💡 Best Practices

1. **Use Preview Deployments**: Test changes in preview environments
2. **Monitor Function Performance**: Keep an eye on execution times
3. **Optimize Bundle Size**: Use code splitting and tree shaking
4. **Handle Errors Gracefully**: Implement proper error boundaries
5. **Use Environment-Specific Configs**: Different settings for dev/prod
