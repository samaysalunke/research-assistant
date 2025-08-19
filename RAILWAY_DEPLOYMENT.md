# 🚀 Railway Deployment Guide

This guide will help you deploy the Research-to-Insights Agent to Railway.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Supabase Project**: Set up your Supabase project with all migrations applied
4. **API Keys**: Get your Anthropic and OpenAI API keys

## 🛠️ Deployment Steps

### 1. Connect to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository

### 2. Configure Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add these environment variables:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=1

# CORS (replace with your Railway URL)
CORS_ORIGINS=https://your-app.railway.app

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# AI Models
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Security (generate a secure random key)
SECRET_KEY=your_secure_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend (replace with your Railway URL)
VITE_API_URL=https://your-app.railway.app
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Deploy

1. Railway will automatically detect the `railway.json` configuration
2. The build process will:
   - Install Python dependencies
   - Install Node.js dependencies
   - Build the frontend
   - Start the FastAPI server
3. Your app will be available at the Railway URL

### 4. Verify Deployment

1. Check the deployment logs in Railway dashboard
2. Visit your Railway URL
3. Test the health endpoint: `https://your-app.railway.app/health`
4. Test the main application features

## 🔧 Configuration Details

### Railway Configuration (`railway.json`)

- **Builder**: Uses NIXPACKS for automatic dependency detection
- **Start Command**: Runs the FastAPI server with proper host/port
- **Health Check**: Monitors `/health` endpoint
- **Restart Policy**: Automatically restarts on failures

### Docker Configuration (`Dockerfile`)

- **Base Image**: Python 3.11 slim for optimal size
- **Multi-stage**: Installs both Python and Node.js dependencies
- **Security**: Runs as non-root user
- **Health Check**: Built-in health monitoring
- **Static Files**: Serves frontend build from FastAPI

### Frontend Build

- **Build Output**: `frontend/dist/` directory
- **Static Serving**: FastAPI serves static files
- **SPA Routing**: Catch-all route for client-side routing
- **Optimization**: Production minification and optimization

## 🚨 Important Notes

### Environment Variables

1. **Never commit sensitive keys** to your repository
2. **Use Railway's environment variables** for all secrets
3. **Update CORS origins** to include your Railway domain
4. **Generate a secure SECRET_KEY** for production

### Database Migrations

Ensure all database migrations are applied in Supabase:
- `001_initial_schema.sql`
- `002_fix_vector_dimensions.sql`
- `004_enhanced_metadata.sql`
- `005_processing_status.sql`
- `006_enhanced_search.sql`
- `007_conversation_tables.sql`

### CORS Configuration

Update `CORS_ORIGINS` to include:
- Your Railway app URL
- Any custom domains you set up
- Development URLs if needed

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Railway logs for dependency issues
   - Ensure all requirements are in `requirements.txt`
   - Verify Node.js dependencies in `package.json`

2. **Environment Variables**
   - Verify all required variables are set
   - Check for typos in variable names
   - Ensure API keys are valid

3. **Database Connection**
   - Verify Supabase URL and keys
   - Check if all migrations are applied
   - Test database connection from Railway

4. **Frontend Not Loading**
   - Check if frontend build completed
   - Verify static file serving configuration
   - Check browser console for errors

### Logs and Monitoring

- **Railway Logs**: View real-time logs in Railway dashboard
- **Health Check**: Monitor `/health` endpoint
- **Application Logs**: Check FastAPI logs for errors

## 🎯 Post-Deployment

### Testing Checklist

- [ ] Health endpoint responds
- [ ] Frontend loads correctly
- [ ] User authentication works
- [ ] Document ingestion works
- [ ] Search functionality works
- [ ] Conversational features work
- [ ] PDF upload works

### Performance Optimization

- **Database Indexes**: Ensure all indexes are created
- **Caching**: Consider adding Redis for caching
- **CDN**: Use Railway's CDN for static assets
- **Monitoring**: Set up Railway monitoring

## 📞 Support

If you encounter issues:

1. Check Railway documentation
2. Review application logs
3. Verify environment configuration
4. Test locally with production settings

## 🔄 Updates and Maintenance

### Updating the Application

1. Push changes to GitHub
2. Railway automatically redeploys
3. Monitor deployment logs
4. Test functionality after deployment

### Database Updates

1. Create new migration files
2. Apply migrations in Supabase
3. Update application code
4. Deploy and test

---

**Happy Deploying! 🚀**
