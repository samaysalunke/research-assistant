"""
Configuration management for the Research-to-Insights Agent
Handles environment variables and application settings
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Research-to-Insights Agent"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Supabase Configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: Optional[str] = None
    database_url: Optional[str] = None
    
    # Anthropic Claude Configuration
    anthropic_api_key: str
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_embedding_model: str = "text-embedding-3-large"
    
    # OpenAI Configuration (fallback for embeddings)
    openai_api_key: Optional[str] = None
    
    # JWT Configuration
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    # Database Configuration
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    
    # Content Processing Configuration
    max_content_length: int = 1000000
    chunk_size: int = 1000
    chunk_overlap: int = 200
    processing_timeout: int = 300
    
    # Search Configuration
    search_limit: int = 20
    similarity_threshold: float = 0.7
    vector_dimension: int = 3072  # Claude's text-embedding-3-large
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Server Configuration
    workers: int = 1
    reload: bool = True
    
    class Config:
        extra = "ignore"
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings
