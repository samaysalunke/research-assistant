"""
Shared utilities for Vercel serverless functions
"""

import json
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

def create_response(status_code: int, data: dict, headers: dict = None):
    """Create a standardized HTTP response"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(data)
    }

def handle_cors_preflight():
    """Handle CORS preflight requests"""
    return create_response(200, {})

def get_bearer_token(authorization_header: str) -> str:
    """Extract bearer token from Authorization header"""
    if not authorization_header:
        raise ValueError("Authorization header missing")
    
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Invalid authorization header format")
    
    return authorization_header[7:]  # Remove "Bearer " prefix

def parse_request_body(body: str) -> dict:
    """Parse JSON request body"""
    try:
        return json.loads(body) if body else {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in request body: {e}")

def get_query_params(event: dict) -> dict:
    """Extract query parameters from Vercel event"""
    return event.get('queryStringParameters', {}) or {}
