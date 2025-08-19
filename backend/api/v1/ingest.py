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
from services.processing_pipeline import EnhancedProcessingPipeline
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
        # Use service client since we're filtering by user_id for security
        from database.client import get_supabase_service_client
        supabase = get_supabase_service_client()
        
        # Check for duplicate URL if source_url is provided
        if content.source_url:
            try:
                existing_doc = supabase.table("documents").select("id, title, processing_status").eq("user_id", current_user.get('id')).eq("source_url", str(content.source_url)).execute()
                
                if existing_doc.data and len(existing_doc.data) > 0:
                    existing = existing_doc.data[0]
                    if existing["processing_status"] == "pending":
                        return ProcessingStatus(
                            job_id=existing["id"],
                            status="pending",
                            message="Content is already being processed"
                        )
                    elif existing["processing_status"] == "processing":
                        return ProcessingStatus(
                            job_id=existing["id"],
                            status="processing",
                            message="Content is currently being processed"
                        )
                    elif existing["processing_status"] == "completed":
                        return ProcessingStatus(
                            job_id=existing["id"],
                            status="completed",
                            message="This URL has already been processed"
                        )
                    else:
                        # If failed, we can retry
                        pass
            except Exception as e:
                print(f"Error checking for duplicate URL: {str(e)}")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create initial document record
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
            # Check if it's a duplicate URL constraint violation
            if "duplicate key value violates unique constraint" in str(e).lower() or "unique_user_url" in str(e):
                # Try to get the existing document
                try:
                    existing_doc = supabase.table("documents").select("id, title, processing_status").eq("user_id", current_user.get('id')).eq("source_url", str(content.source_url)).single().execute()
                    existing = existing_doc.data
                    
                    if existing["processing_status"] == "completed":
                        return ProcessingStatus(
                            job_id=existing["id"],
                            status="completed",
                            message="This URL has already been processed"
                        )
                    elif existing["processing_status"] in ["pending", "processing"]:
                        return ProcessingStatus(
                            job_id=existing["id"],
                            status=existing["processing_status"],
                            message=f"Content is already {existing['processing_status']}"
                        )
                    else:
                        return ProcessingStatus(
                            job_id=existing["id"],
                            status=existing["processing_status"],
                            message="This URL has already been submitted"
                        )
                except Exception as lookup_error:
                    raise HTTPException(status_code=400, detail="This URL has already been submitted")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to create document record: {str(e)}")
        
        # Use enhanced processing pipeline for URL content
        if content.source_url:
            pipeline = EnhancedProcessingPipeline()
            task_id = await pipeline.process_url(str(content.source_url), current_user.get('id'))
            
            return ProcessingStatus(
                job_id=task_id,
                status="pending",
                message="Content processing started with enhanced pipeline"
            )
        else:
            # For text content, use the original processor
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
        # First try enhanced pipeline status
        pipeline = EnhancedProcessingPipeline()
        enhanced_status = await pipeline.get_task_status(job_id)
        
        if "error" not in enhanced_status:
            # Return enhanced status
            return ProcessingStatus(
                job_id=enhanced_status.get("task_id", job_id),
                status=enhanced_status.get("status", "unknown"),
                progress=enhanced_status.get("progress", 0.0),
                message=f"Stage: {enhanced_status.get('stage', 'unknown')}",
                result=enhanced_status.get("result")
            )
        
        # Fallback to original document status
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
