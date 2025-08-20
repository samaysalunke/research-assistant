"""
Documents endpoint for Vercel deployment
Handles document listing and management
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from core.config import get_settings
from auth.middleware import verify_token
from models.schemas import DocumentResponse
from database.client import get_supabase_service_client
from api._utils import create_response, handle_cors_preflight, get_bearer_token


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle document listing requests"""
        try:
            # Get authorization token
            auth_header = self.headers.get('Authorization', '')
            token = get_bearer_token(auth_header)
            
            # Verify user authentication
            current_user = verify_token(token)
            if not current_user:
                response = create_response(401, {"error": "Unauthorized"})
                self._send_response(response)
                return
            
            # Get query parameters
            query_string = self.path.split('?', 1)[1] if '?' in self.path else ''
            query_params = {}
            if query_string:
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value
            
            # Parse pagination parameters
            limit = int(query_params.get('limit', '20'))
            offset = int(query_params.get('offset', '0'))
            status_filter = query_params.get('status')
            
            # Get documents
            result = self._get_documents(current_user, limit, offset, status_filter)
            response = create_response(200, result)
            self._send_response(response)
            
        except Exception as e:
            response = create_response(500, {"error": f"Internal server error: {str(e)}"})
            self._send_response(response)
    
    def do_DELETE(self):
        """Handle document deletion requests"""
        try:
            # Get document ID from path
            path_parts = self.path.split('/')
            if len(path_parts) < 4 or not path_parts[-1]:
                response = create_response(400, {"error": "Document ID required"})
                self._send_response(response)
                return
            
            document_id = path_parts[-1].split('?')[0]  # Remove query params
            
            # Get authorization token
            auth_header = self.headers.get('Authorization', '')
            token = get_bearer_token(auth_header)
            
            # Verify user authentication
            current_user = verify_token(token)
            if not current_user:
                response = create_response(401, {"error": "Unauthorized"})
                self._send_response(response)
                return
            
            # Delete document
            result = self._delete_document(document_id, current_user)
            response = create_response(200, result)
            self._send_response(response)
            
        except Exception as e:
            response = create_response(500, {"error": f"Internal server error: {str(e)}"})
            self._send_response(response)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        response = handle_cors_preflight()
        self._send_response(response)
    
    def _send_response(self, response_data):
        """Send HTTP response"""
        self.send_response(response_data['statusCode'])
        for key, value in response_data['headers'].items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response_data['body'].encode())
    
    def _get_documents(self, current_user: dict, limit: int, offset: int, status_filter: str = None) -> dict:
        """Get user documents with pagination"""
        try:
            supabase = get_supabase_service_client()
            
            # Build query
            query = supabase.table("documents").select(
                "id, title, source_url, content_type, processing_status, created_at, updated_at, metadata"
            ).eq("user_id", current_user.get('id'))
            
            # Apply status filter if provided
            if status_filter:
                query = query.eq("processing_status", status_filter)
            
            # Apply pagination and ordering
            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            
            # Execute query
            result = query.execute()
            
            if not result.data:
                return {
                    "documents": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset
                }
            
            # Get total count (for pagination)
            count_query = supabase.table("documents").select(
                "id", count="exact"
            ).eq("user_id", current_user.get('id'))
            
            if status_filter:
                count_query = count_query.eq("processing_status", status_filter)
            
            count_result = count_query.execute()
            total_count = len(count_result.data) if count_result.data else 0
            
            # Format documents
            documents = []
            for doc in result.data:
                # Calculate content preview
                content_preview = None
                if doc.get('metadata') and isinstance(doc['metadata'], dict):
                    content_preview = doc['metadata'].get('content_preview')
                
                document_response = {
                    "id": doc['id'],
                    "title": doc['title'],
                    "source_url": doc.get('source_url'),
                    "content_type": doc['content_type'],
                    "processing_status": doc['processing_status'],
                    "created_at": doc['created_at'],
                    "updated_at": doc.get('updated_at'),
                    "content_preview": content_preview,
                    "metadata": doc.get('metadata', {})
                }
                documents.append(document_response)
            
            return {
                "documents": documents,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            raise Exception(f"Failed to get documents: {str(e)}")
    
    def _delete_document(self, document_id: str, current_user: dict) -> dict:
        """Delete a user document"""
        try:
            supabase = get_supabase_service_client()
            
            # First, verify the document belongs to the user
            doc_check = supabase.table("documents").select("id").eq(
                "id", document_id
            ).eq("user_id", current_user.get('id')).execute()
            
            if not doc_check.data:
                raise Exception("Document not found or access denied")
            
            # Delete the document
            delete_result = supabase.table("documents").delete().eq(
                "id", document_id
            ).eq("user_id", current_user.get('id')).execute()
            
            if not delete_result.data:
                raise Exception("Failed to delete document")
            
            return {
                "message": "Document deleted successfully",
                "document_id": document_id
            }
            
        except Exception as e:
            raise Exception(f"Failed to delete document: {str(e)}")


def get_bearer_token(authorization_header: str) -> str:
    """Extract bearer token from Authorization header"""
    if not authorization_header:
        raise ValueError("Authorization header missing")
    
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Invalid authorization header format")
    
    return authorization_header[7:]  # Remove "Bearer " prefix
