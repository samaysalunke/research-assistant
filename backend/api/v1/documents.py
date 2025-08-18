"""
Documents API endpoints
Handles document CRUD operations and management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from core.config import get_settings
from auth.middleware import get_current_user
from models.schemas import DocumentResponse, DocumentUpdate, PaginatedResponse
from database.client import get_supabase_client

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/", response_model=PaginatedResponse)
async def get_documents(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get paginated list of user's documents
    """
    try:
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("documents").select("*").eq("user_id", current_user.id)
        
        # Apply filters
        if tags:
            query = query.overlaps("tags", tags)
        if status:
            query = query.eq("processing_status", status)
        
        # Get total count
        count_result = query.execute()
        total = len(count_result.data) if count_result.data else 0
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
        
        result = query.execute()
        
        if result.error:
            raise HTTPException(status_code=500, detail="Failed to fetch documents")
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit
        has_next = page < pages
        has_prev = page > 1
        
        return PaginatedResponse(
            items=result.data,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific document by ID
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", current_user.id).single().execute()
        
        if result.error:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(**result.data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a document
    """
    try:
        supabase = get_supabase_client()
        
        # Verify document belongs to user
        doc_result = supabase.table("documents").select("id").eq("id", document_id).eq("user_id", current_user.id).single().execute()
        
        if doc_result.error:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Prepare update data
        update_data = document_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update document
        result = supabase.table("documents").update(update_data).eq("id", document_id).select().single().execute()
        
        if result.error:
            raise HTTPException(status_code=500, detail="Failed to update document")
        
        return DocumentResponse(**result.data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a document
    """
    try:
        supabase = get_supabase_client()
        
        # Verify document belongs to user
        doc_result = supabase.table("documents").select("id").eq("id", document_id).eq("user_id", current_user.id).single().execute()
        
        if doc_result.error:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document (embeddings will be deleted via CASCADE)
        result = supabase.table("documents").delete().eq("id", document_id).execute()
        
        if result.error:
            raise HTTPException(status_code=500, detail="Failed to delete document")
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get content chunks for a document
    """
    try:
        supabase = get_supabase_client()
        
        # Verify document belongs to user
        doc_result = supabase.table("documents").select("id").eq("id", document_id).eq("user_id", current_user.id).single().execute()
        
        if doc_result.error:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunks
        result = supabase.table("embeddings").select("chunk_index, content").eq("document_id", document_id).order("chunk_index").execute()
        
        if result.error:
            raise HTTPException(status_code=500, detail="Failed to fetch chunks")
        
        return {"chunks": result.data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")
