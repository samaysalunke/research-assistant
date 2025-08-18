"""
Supabase client configuration for the Research-to-Insights Agent
Handles database connections, authentication, and real-time subscriptions
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseManager:
    """Manages Supabase client and database operations"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        # Create Supabase client
        self.client: Client = create_client(self.supabase_url, self.supabase_anon_key)
        
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        return self.client
    
    def get_service_client(self) -> Client:
        """Get a Supabase client with service role key for admin operations"""
        if not self.supabase_service_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY must be set for admin operations")
        return create_client(self.supabase_url, self.supabase_service_key)
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user information"""
        try:
            # Use service client to verify token
            service_client = self.get_service_client()
            user = service_client.auth.get_user(token)
            return user.user if user.user else None
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by user ID"""
        try:
            service_client = self.get_service_client()
            response = service_client.auth.admin.get_user_by_id(user_id)
            return response.user if response.user else None
        except Exception as e:
            print(f"Failed to get user by ID: {e}")
            return None

# Global Supabase manager instance
supabase_manager = SupabaseManager()

def get_supabase_client() -> Client:
    """Get the default Supabase client"""
    return supabase_manager.get_client()

def get_supabase_service_client() -> Client:
    """Get the Supabase service client for admin operations"""
    return supabase_manager.get_service_client()

async def verify_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify authentication token and return user info"""
    return await supabase_manager.verify_token(token)
