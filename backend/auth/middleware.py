"""
Authentication middleware for FastAPI
Handles JWT token verification and user authentication
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from database.client import verify_auth_token

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Verify JWT token and return current user information
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Dict containing user information and access token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token with Supabase
    user = await verify_auth_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    
    # Add access token to user object for RLS operations
    if hasattr(user, 'dict'):
        user_dict = user.dict()
    elif hasattr(user, '__dict__'):
        user_dict = user.__dict__
    else:
        user_dict = dict(user) if user else {}
    
    user_dict['access_token'] = token
    
    return user_dict

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token and return current user information (optional)
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        
    Returns:
        Dict containing user information or None if no valid token
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    if not token:
        return None
    
    # Verify token with Supabase
    user = await verify_auth_token(token)
    return user

def require_auth():
    """Decorator to require authentication for endpoints"""
    return Depends(get_current_user)

def optional_auth():
    """Decorator to make authentication optional for endpoints"""
    return Depends(get_current_user_optional)
