"""
Conversation endpoint for Vercel deployment
Handles conversational search and AI interactions
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
from models.schemas import ConversationRequest, ConversationResponse
from database.client import get_supabase_service_client
from services.conversational_search import ConversationalSearchService
from api._utils import create_response, handle_cors_preflight, get_bearer_token, parse_request_body


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle conversation requests"""
        try:
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            request_data = parse_request_body(body)
            
            # Get authorization token
            auth_header = self.headers.get('Authorization', '')
            token = get_bearer_token(auth_header)
            
            # Verify user authentication
            current_user = verify_token(token)
            if not current_user:
                response = create_response(401, {"error": "Unauthorized"})
                self._send_response(response)
                return
            
            # Handle different conversation endpoints based on path
            path_parts = self.path.split('/')
            if len(path_parts) >= 4:
                endpoint = path_parts[-1].split('?')[0]  # Remove query params
                
                if endpoint == "query":
                    result = self._handle_conversation_query(request_data, current_user)
                elif endpoint == "sessions":
                    result = self._handle_session_creation(request_data, current_user)
                else:
                    response = create_response(404, {"error": "Endpoint not found"})
                    self._send_response(response)
                    return
            else:
                response = create_response(400, {"error": "Invalid endpoint"})
                self._send_response(response)
                return
            
            response = create_response(200, result)
            self._send_response(response)
            
        except Exception as e:
            response = create_response(500, {"error": f"Internal server error: {str(e)}"})
            self._send_response(response)
    
    def do_GET(self):
        """Handle conversation history requests"""
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
            
            # Get conversation sessions
            result = self._get_conversation_sessions(current_user)
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
    
    def _handle_conversation_query(self, request_data: dict, current_user: dict) -> dict:
        """Handle conversational search query"""
        try:
            # Validate input
            conversation_request = ConversationRequest(**request_data)
            
            # Initialize conversational search service
            search_service = ConversationalSearchService()
            
            # Perform conversational search
            response = search_service.process_query(
                query=conversation_request.query,
                user_id=current_user.get('id'),
                session_id=conversation_request.session_id,
                context=conversation_request.context
            )
            
            return {
                "response": response.response,
                "sources": [source.dict() for source in response.sources],
                "session_id": response.session_id,
                "context": response.context
            }
            
        except Exception as e:
            raise Exception(f"Failed to process conversation query: {str(e)}")
    
    def _handle_session_creation(self, request_data: dict, current_user: dict) -> dict:
        """Handle conversation session creation"""
        try:
            supabase = get_supabase_service_client()
            
            # Create new conversation session
            session_data = {
                "user_id": current_user.get('id'),
                "title": request_data.get('title', 'New Conversation'),
                "created_at": "now()",
                "metadata": request_data.get('metadata', {})
            }
            
            result = supabase.table("conversation_sessions").insert(session_data).execute()
            
            if not result.data:
                raise Exception("Failed to create conversation session")
            
            return {
                "session_id": result.data[0]['id'],
                "message": "Conversation session created successfully"
            }
            
        except Exception as e:
            raise Exception(f"Failed to create conversation session: {str(e)}")
    
    def _get_conversation_sessions(self, current_user: dict) -> dict:
        """Get user's conversation sessions"""
        try:
            supabase = get_supabase_service_client()
            
            # Get conversation sessions for user
            result = supabase.table("conversation_sessions").select(
                "id, title, created_at, updated_at, metadata"
            ).eq("user_id", current_user.get('id')).order(
                "updated_at", desc=True
            ).execute()
            
            sessions = result.data if result.data else []
            
            return {
                "sessions": sessions,
                "total": len(sessions)
            }
            
        except Exception as e:
            raise Exception(f"Failed to get conversation sessions: {str(e)}")


def parse_request_body(body: str) -> dict:
    """Parse JSON request body"""
    try:
        return json.loads(body) if body else {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in request body: {e}")


def get_bearer_token(authorization_header: str) -> str:
    """Extract bearer token from Authorization header"""
    if not authorization_header:
        raise ValueError("Authorization header missing")
    
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Invalid authorization header format")
    
    return authorization_header[7:]  # Remove "Bearer " prefix
