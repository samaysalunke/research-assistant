# Deployment Guide - Research-to-Insights Agent

A comprehensive guide for deploying the Research-to-Insights Agent to production environments.

## 🚀 Quick Deployment Options

### **Option 1: Railway (Recommended)**

Railway provides the easiest deployment experience with automatic scaling.

#### **Backend Deployment**
1. **Connect Repository**
   - Go to [Railway](https://railway.app)
   - Connect your GitHub repository
   - Select the repository

2. **Configure Environment**
   ```bash
   # Add environment variables in Railway dashboard
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_KEY=your_service_key
   ANTHROPIC_API_KEY=your_claude_key
   OPENAI_API_KEY=your_openai_key
   ENVIRONMENT=production
   ```

3. **Deploy**
   - Railway automatically detects FastAPI
   - Deploys from the `backend/` directory
   - Provides HTTPS endpoint

#### **Frontend Deployment**
1. **Create New Service**
   - Add new service in Railway
   - Select "Deploy from GitHub repo"
   - Set root directory to `frontend/`

2. **Configure Build**
   ```bash
   # Build command
   npm run build
   
   # Output directory
   dist
   ```

3. **Environment Variables**
   ```bash
   VITE_API_URL=https://your-backend-url.railway.app
   ```

### **Option 2: Render**

Render provides free hosting with automatic deployments.

#### **Backend Setup**
1. **Create Web Service**
   - Connect GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables**
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_KEY=your_service_key
   ANTHROPIC_API_KEY=your_claude_key
   OPENAI_API_KEY=your_openai_key
   ```

#### **Frontend Setup**
1. **Create Static Site**
   - Build command: `npm run build`
   - Publish directory: `dist`

2. **Environment Variables**
   ```bash
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

### **Option 3: Vercel + Supabase**

#### **Backend (Vercel Functions)**
1. **Create Vercel Project**
   ```bash
   npm i -g vercel
   vercel
   ```

2. **Configure API Routes**
   - Place FastAPI app in `api/` directory
   - Vercel automatically handles Python functions

#### **Frontend (Vercel)**
1. **Deploy Frontend**
   ```bash
   cd frontend
   vercel
   ```

2. **Environment Variables**
   ```bash
   VITE_API_URL=https://your-vercel-app.vercel.app/api
   ```

## 🐳 Docker Deployment

### **Multi-Stage Dockerfile**

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 8000

# Start backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy source code
COPY frontend/ .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### **Docker Compose**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: frontend.Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### **Deploy with Docker**

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ☁️ Cloud Platform Deployment

### **AWS Deployment**

#### **ECS Fargate Setup**
1. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name research-assistant
   ```

2. **Build and Push Images**
   ```bash
   # Build images
   docker build -f backend.Dockerfile -t research-assistant-backend .
   docker build -f frontend.Dockerfile -t research-assistant-frontend .

   # Tag and push
   docker tag research-assistant-backend:latest $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/research-assistant:backend
   docker tag research-assistant-frontend:latest $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/research-assistant:frontend
   
   docker push $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/research-assistant:backend
   docker push $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/research-assistant:frontend
   ```

3. **Create ECS Cluster and Services**
   - Use AWS Console or CloudFormation
   - Configure environment variables
   - Set up load balancer

#### **Lambda + API Gateway**
1. **Package Backend for Lambda**
   ```bash
   pip install -r requirements.txt -t package/
   cd package
   zip -r ../lambda-deployment.zip .
   ```

2. **Deploy Lambda Function**
   ```bash
   aws lambda create-function \
     --function-name research-assistant-api \
     --runtime python3.11 \
     --handler main.handler \
     --zip-file fileb://lambda-deployment.zip
   ```

### **Google Cloud Platform**

#### **Cloud Run Deployment**
```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT_ID/research-assistant-backend
gcloud run deploy research-assistant-backend \
  --image gcr.io/PROJECT_ID/research-assistant-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and deploy frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/research-assistant-frontend
gcloud run deploy research-assistant-frontend \
  --image gcr.io/PROJECT_ID/research-assistant-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### **Azure Deployment**

#### **Azure Container Instances**
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image research-assistant-backend .
az acr build --registry myregistry --image research-assistant-frontend .

# Deploy containers
az container create \
  --resource-group myResourceGroup \
  --name research-assistant-backend \
  --image myregistry.azurecr.io/research-assistant-backend:latest \
  --ports 8000
```

## 🔧 Production Configuration

### **Environment Variables**

```bash
# Required for production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
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

# Security
CORS_ORIGINS=https://your-frontend-domain.com
JWT_SECRET=your_jwt_secret
```

### **Database Migration**

```bash
# Apply migrations to production database
cd backend
python -m database.migrations

# Verify migration status
python -c "from database.client import get_supabase_client; print('Database ready')"
```

### **SSL/TLS Configuration**

#### **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring & Logging

### **Application Monitoring**

#### **Health Check Endpoint**
```python
# Add to backend/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

#### **Logging Configuration**
```python
# In core/logging.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
```

### **Performance Monitoring**

#### **Add Metrics Endpoint**
```python
@app.get("/metrics")
async def get_metrics():
    return {
        "uptime": time.time() - start_time,
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent()
    }
```

## 🔒 Security Configuration

### **CORS Settings**
```python
# In backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Rate Limiting**
```python
# Add rate limiting middleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### **Security Headers**
```python
# Add security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-domain.com"])
```

## 🚀 Deployment Checklist

### **Pre-Deployment**
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] Monitoring setup

### **Deployment**
- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Database connection verified
- [ ] API endpoints responding
- [ ] Search functionality working
- [ ] Content processing tested

### **Post-Deployment**
- [ ] Performance monitoring active
- [ ] Error logging configured
- [ ] Backup strategy implemented
- [ ] Documentation updated
- [ ] Team access configured

## 🔄 CI/CD Pipeline

### **GitHub Actions**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python -m pytest

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railway/deploy@v1
        with:
          service: backend
          token: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          working-directory: ./frontend
```

## 🆘 Troubleshooting

### **Common Issues**

#### **Database Connection**
```bash
# Test database connection
curl -X GET "https://your-api.com/health"
```

#### **CORS Issues**
```bash
# Check CORS configuration
curl -H "Origin: https://your-frontend.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS https://your-api.com/api/v1/ingest/
```

#### **Memory Issues**
```bash
# Monitor memory usage
docker stats
# or
kubectl top pods
```

### **Debug Mode**
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart services
docker-compose restart
```

---

**For deployment support, check the troubleshooting section or create an issue in the repository.**
