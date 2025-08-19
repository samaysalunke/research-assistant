"""
Research-to-Insights Agent - FastAPI Application
Main entry point for the backend API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Import routers
from api.v1 import ingest, search, documents, conversation
from core.config import get_settings

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Research-to-Insights Agent API",
    description="AI-powered research assistant for processing and retrieving insights from digital content",
    version="0.1.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "research-insights-agent",
        "version": "0.1.0",
        "milestone": "3 - Enhanced Conversational Features"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Research-to-Insights Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "ingest": "/api/v1/ingest",
            "search": "/api/v1/search", 
            "documents": "/api/v1/documents",
            "conversation": "/api/v1/conversation"
        }
    }

# Include API routers
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(conversation.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=settings.workers
    )
