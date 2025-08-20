"""
Content ingestion endpoint for Vercel deployment
Handles URL, text, and PDF content submission for processing
"""

from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from core.config import get_settings
from auth.middleware import verify_token
from models.schemas import DocumentCreate, ProcessingStatus
from services.content_processor import ContentProcessor
from services.processing_pipeline import EnhancedProcessingPipeline
from database.client import get_supabase_service_client
from api._utils import create_response, handle_cors_preflight, get_bearer_token, parse_request_body


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle content ingestion requests"""
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
                content = DocumentCreate(**request_data)
            except Exception as e:
                response = create_response(400, {"error": f"Invalid input: {str(e)}"})
                self._send_response(response)
                return
            
            # Process content ingestion
            result = self._ingest_content(content, current_user)
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
    
    def _ingest_content(self, content: DocumentCreate, current_user: dict) -> ProcessingStatus:
        """Process content ingestion"""
        try:
            supabase = get_supabase_service_client()
            
            # Check for duplicate URL if source_url is provided
            if content.source_url:
                existing_doc = supabase.table("documents").select(
                    "id, title, processing_status"
                ).eq("user_id", current_user.get('id')).eq(
                    "source_url", str(content.source_url)
                ).execute()
                
                if existing_doc.data and len(existing_doc.data) > 0:
                    existing = existing_doc.data[0]
                    if existing["processing_status"] in ["pending", "processing"]:
                        return ProcessingStatus(
                            job_id=existing["id"],
                            status=existing["processing_status"],
                            message="Content is already being processed"
                        )
            
            # Create new document record
            document_id = str(uuid.uuid4())
            
            # Determine document title
            title = content.title
            if not title:
                if content.source_url:
                    title = f"Document from {content.source_url}"
                else:
                    title = f"Text Document {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Insert document record
            doc_data = {
                "id": document_id,
                "user_id": current_user.get('id'),
                "title": title,
                "source_url": str(content.source_url) if content.source_url else None,
                "content_type": "url" if content.source_url else "text",
                "processing_status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "tags": content.tags or [],
                    "content_preview": content.content[:200] if content.content else None
                }
            }
            
            insert_result = supabase.table("documents").insert(doc_data).execute()
            
            if not insert_result.data:
                raise Exception("Failed to create document record")
            
            # Queue for background processing
            # Note: In Vercel, we'd need to use a queue service like Upstash or trigger another function
            # For now, we'll mark it as pending and rely on a separate processing service
            
            return ProcessingStatus(
                job_id=document_id,
                status="pending",
                message="Content queued for processing"
            )
            
        except Exception as e:
            raise Exception(f"Failed to ingest content: {str(e)}")


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
