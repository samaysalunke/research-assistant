"""
Research-to-Insights Agent - FastAPI Application
Main entry point for the backend API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from pathlib import Path

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

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

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

# Root endpoint - serve frontend or API info
@app.get("/")
async def root():
    """Root endpoint - serves frontend in production, API info in development"""
    if os.getenv("ENVIRONMENT") == "production" and frontend_path.exists():
        index_path = frontend_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
    
    # Return API info in development
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

# Catch-all route for SPA routing
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Catch-all route to serve frontend for client-side routing"""
    if os.getenv("ENVIRONMENT") == "production" and frontend_path.exists():
        # Don't serve frontend for API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve index.html for all other routes (SPA routing)
        index_path = frontend_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
    
    raise HTTPException(status_code=404, detail="Not found")

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
    )
