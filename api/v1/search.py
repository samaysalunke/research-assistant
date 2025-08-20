"""
Search endpoint for Vercel deployment
Handles semantic search and content retrieval
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
from models.schemas import SearchRequest, SearchResponse, SearchResult
from database.client import get_supabase_service_client
from services.conversational_search import ConversationalSearchService
from api._utils import create_response, handle_cors_preflight, get_bearer_token, parse_request_body


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle search requests"""
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
            
            # Validate input
            try:
                search_request = SearchRequest(**request_data)
            except Exception as e:
                response = create_response(400, {"error": f"Invalid input: {str(e)}"})
                self._send_response(response)
                return
            
            # Perform search
            result = self._search_content(search_request, current_user)
            response = create_response(200, result.dict())
            self._send_response(response)
            
        except Exception as e:
            response = create_response(500, {"error": f"Internal server error: {str(e)}"})
            self._send_response(response)
    
    def do_GET(self):
        """Handle simple search with query parameters"""
        try:
            # Get query parameters
            query_string = self.path.split('?', 1)[1] if '?' in self.path else ''
            query_params = {}
            if query_string:
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value
            
            # Get authorization token
            auth_header = self.headers.get('Authorization', '')
            token = get_bearer_token(auth_header)
            
            # Verify user authentication
            current_user = verify_token(token)
            if not current_user:
                response = create_response(401, {"error": "Unauthorized"})
                self._send_response(response)
                return
            
            # Create search request from query params
            search_data = {
                "query": query_params.get('q', query_params.get('query', '')),
                "limit": int(query_params.get('limit', '10')),
                "threshold": float(query_params.get('threshold', '0.7'))
            }
            
            search_request = SearchRequest(**search_data)
            
            # Perform search
            result = self._search_content(search_request, current_user)
            response = create_response(200, result.dict())
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
    
    def _search_content(self, search_request: SearchRequest, current_user: dict) -> SearchResponse:
        """Perform content search"""
        try:
            supabase = get_supabase_service_client()
            
            # Get all documents for the user
            docs_response = supabase.table("documents").select(
                "id, title, content, source_url, created_at, metadata"
            ).eq("user_id", current_user.get('id')).eq(
                "processing_status", "completed"
            ).execute()
            
            if not docs_response.data:
                return SearchResponse(
                    query=search_request.query,
                    results=[],
                    total_results=0,
                    processing_time=0.0
                )
            
            # Simple text search for now (can be enhanced with vector search later)
            query_lower = search_request.query.lower()
            matching_docs = []
            
            for doc in docs_response.data:
                content = doc.get('content', '') or ''
                title = doc.get('title', '') or ''
                
                # Simple relevance scoring based on query term presence
                score = 0.0
                if query_lower in title.lower():
                    score += 0.5
                if query_lower in content.lower():
                    score += 0.3
                
                if score > 0:
                    # Extract relevant snippet
                    content_lower = content.lower()
                    query_pos = content_lower.find(query_lower)
                    
                    if query_pos != -1:
                        start = max(0, query_pos - 100)
                        end = min(len(content), query_pos + 200)
                        snippet = content[start:end]
                        if start > 0:
                            snippet = "..." + snippet
                        if end < len(content):
                            snippet = snippet + "..."
                    else:
                        snippet = content[:200] + "..." if len(content) > 200 else content
                    
                    search_result = SearchResult(
                        document_id=doc['id'],
                        title=doc['title'],
                        content_snippet=snippet,
                        source_url=doc.get('source_url'),
                        relevance_score=score,
                        metadata=doc.get('metadata', {})
                    )
                    matching_docs.append(search_result)
            
            # Sort by relevance score
            matching_docs.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Apply limit
            limited_results = matching_docs[:search_request.limit]
            
            return SearchResponse(
                query=search_request.query,
                results=limited_results,
                total_results=len(matching_docs),
                processing_time=0.1  # Placeholder
            )
            
        except Exception as e:
            raise Exception(f"Failed to search content: {str(e)}")


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
