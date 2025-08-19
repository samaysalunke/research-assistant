"""
Content ingestion API endpoints
Handles URL and text content submission for processing
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
import uuid
from datetime import datetime

from core.config import get_settings
from auth.middleware import get_current_user
from models.schemas import DocumentCreate, ProcessingStatus
from services.content_processor import ContentProcessor
from database.client import get_supabase_user_client

router = APIRouter(prefix="/ingest", tags=["Content Ingestion"])

@router.post("/", response_model=ProcessingStatus)
async def ingest_content(
    content: DocumentCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    settings = Depends(get_settings)
):
    """
    Ingest content from URL or direct text input
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        

        
        # Create initial document record
        # Use service client since we're filtering by user_id for security
        from database.client import get_supabase_service_client
        supabase = get_supabase_service_client()
        
        document_data = {
            "id": job_id,
            "user_id": current_user.get('id'),
            "source_url": str(content.source_url) if content.source_url else None,
            "title": "Processing...",
            "processing_status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert document record
        try:
            result = supabase.table("documents").insert(document_data).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create document record: {str(e)}")
        
        # Start background processing
        background_tasks.add_task(
            process_content_background,
            job_id=job_id,
            content=content,
            user_id=current_user.get('id')
        )
        
        return ProcessingStatus(
            job_id=job_id,
            status="pending",
            message="Content processing started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

@router.get("/{job_id}/status", response_model=ProcessingStatus)
async def get_processing_status(
    job_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get the processing status of a content ingestion job
    """
    try:
        # Use service client since we're filtering by user_id for security
        from database.client import get_supabase_service_client
        supabase = get_supabase_service_client()
        
        # Get document status
        try:
            result = supabase.table("documents").select("*").eq("id", job_id).eq("user_id", current_user.get('id')).single().execute()
            document = result.data
        except Exception as e:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return ProcessingStatus(
            job_id=job_id,
            status=document["processing_status"],
            message=f"Processing status: {document['processing_status']}",
            result=document if document["processing_status"] == "completed" else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

async def process_content_background(job_id: str, content: DocumentCreate, user_id: str):
    """
    Background task to process content
    """
    try:
        # Update status to processing
        # Note: Background tasks don't have access to the request context
        # So we need to use the service client for admin operations
        from database.client import get_supabase_service_client
        supabase = get_supabase_service_client()
        supabase.table("documents").update({"processing_status": "processing"}).eq("id", job_id).execute()
        
        # Initialize content processor
        processor = ContentProcessor()
        
        # Process content
        if content.source_url:
            # Process URL
            processed_content = await processor.process_url(str(content.source_url))
        else:
            # Process direct text
            processed_content = await processor.process_text(content.text)
        
        # Update document with processed content
        update_data = {
            "title": processed_content["title"],
            "summary": processed_content["summary"],
            "tags": processed_content["tags"],
            "insights": processed_content["insights"],
            "action_items": processed_content["action_items"],
            "quotable_snippets": processed_content["quotable_snippets"],
            "content_chunks": processed_content["chunks"],
            "processing_status": "completed",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("documents").update(update_data).eq("id", job_id).execute()
        
        # Generate embeddings for chunks
        await processor.generate_embeddings(job_id, processed_content["chunks"])
        
    except Exception as e:
        # Update status to failed
        supabase.table("documents").update({
            "processing_status": "failed",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", job_id).execute()
        
        print(f"Processing failed for job {job_id}: {str(e)}")
