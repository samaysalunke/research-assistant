"""
Pydantic models for the Research-to-Insights Agent
Defines data validation schemas for API requests and responses
"""

from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Base Models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

# Authentication Models
class UserLogin(BaseModel):
    """User login request model"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserSignup(BaseModel):
    """User signup request model"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")
    full_name: Optional[str] = Field(None, description="User full name")

class UserResponse(BaseModel):
    """User response model"""
    id: UUID
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Document Models
class DocumentCreate(BaseModel):
    """Document creation request model"""
    source_url: Optional[HttpUrl] = Field(None, description="Source URL of the content")
    text: Optional[str] = Field(None, description="Direct text content")
    
    @validator('source_url', 'text')
    def validate_content_source(cls, v, values):
        """Ensure either URL or text is provided"""
        if 'source_url' not in values and 'text' not in values:
            if v is None:
                raise ValueError("Either source_url or text must be provided")
        return v

class DocumentResponse(BaseModel):
    """Document response model"""
    id: UUID
    user_id: UUID
    source_url: Optional[str] = None
    title: str
    summary: Optional[str] = None
    tags: List[str] = []
    insights: Optional[List[Dict[str, Any]]] = None
    action_items: List[str] = []
    quotable_snippets: Optional[List[Dict[str, Any]]] = None
    processing_status: str
    created_at: datetime
    updated_at: datetime

class DocumentUpdate(BaseModel):
    """Document update request model"""
    title: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    insights: Optional[List[Dict[str, Any]]] = None
    action_items: Optional[List[str]] = None
    quotable_snippets: Optional[List[Dict[str, Any]]] = None

# Search Models
class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, description="Search query")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold for vector search")
    search_type: str = Field("hybrid", pattern="^(semantic|keyword|hybrid)$", description="Search type")

class SearchResult(BaseModel):
    """Search result model"""
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    similarity: float
    keyword_rank: Optional[float] = None
    document_title: str
    document_url: Optional[str] = None

class SearchResponse(BaseModel):
    """Search response model"""
    results: List[SearchResult]
    total_count: int
    query: str
    search_type: str

# Chat Models
class ChatMessage(BaseModel):
    """Chat message model"""
    message: str = Field(..., min_length=1, description="Chat message")
    context: Optional[List[UUID]] = Field(None, description="Context document IDs")

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    sources: List[Dict[str, Any]]
    confidence: float = Field(..., ge=0.0, le=1.0)

# Processing Models
class ProcessingStatus(BaseModel):
    """Processing status model"""
    job_id: str
    status: str = Field(..., pattern="^(pending|processing|completed|failed)$")
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    message: Optional[str] = None
    result: Optional[DocumentResponse] = None
    error: Optional[str] = None

# Insight Models
class Insight(BaseModel):
    """Insight model"""
    text: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    context: Optional[str] = None
    category: Optional[str] = None

class QuotableSnippet(BaseModel):
    """Quotable snippet model"""
    quote: str
    context: str
    source_section: Optional[str] = None

# Pagination Models
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool

# API Response Models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Configuration Models
class AppConfig(BaseModel):
    """Application configuration model"""
    environment: str
    debug: bool
    version: str
    features: Dict[str, bool]
