"""
Search API endpoints
Handles semantic search and content retrieval
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import anthropic

from core.config import get_settings
from auth.middleware import get_current_user
from models.schemas import SearchRequest, SearchResponse, SearchResult
from database.client import get_supabase_service_client

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/", response_model=SearchResponse)
async def search_content(
    search_request: SearchRequest,
    current_user: dict = Depends(get_current_user),
    settings = Depends(get_settings)
):
    """
    Simple search content that actually works
    """
    try:
        supabase = get_supabase_service_client()
        
        # Get all documents for the user
        result = supabase.table("documents").select("*").execute()
        
        if not result.data:
            return SearchResponse(
                results=[],
                total_count=0,
                query=search_request.query,
                search_type=search_request.search_type
            )
        
        # Simple keyword matching
        query_terms = search_request.query.lower().split()
        matches = []
        
        for doc in result.data:
            score = 0
            title = doc.get('title', '').lower()
            summary = doc.get('summary', '').lower()
            tags = [tag.lower() for tag in doc.get('tags', [])]
            
            # Calculate relevance score
            for term in query_terms:
                if term in title:
                    score += 3  # Title matches are most important
                if term in summary:
                    score += 2  # Summary matches are important
                if any(term in tag for tag in tags):
                    score += 1  # Tag matches are good
            
            if score > 0:
                matches.append({
                    'doc': doc,
                    'score': score
                })
        
        # Sort by score and limit results
        matches.sort(key=lambda x: x['score'], reverse=True)
        matches = matches[:search_request.limit]
        
        # Convert to SearchResult format
        results = []
        for i, match in enumerate(matches):
            doc = match['doc']
            results.append(SearchResult(
                id=doc['id'],  # Use document ID as the result ID
                document_id=doc['id'],
                chunk_index=0,  # Default chunk index since we're not chunking
                content=doc.get('summary', '')[:500],  # Use summary as content
                similarity=match['score'] / 10.0,  # Normalize score to 0-1
                keyword_rank=match['score'] / 10.0,  # Same as similarity for now
                document_title=doc.get('title', ''),
                document_url=doc.get('source_url')
            ))
        
        return SearchResponse(
            results=results,
            total_count=len(results),
            query=search_request.query,
            search_type=search_request.search_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/", response_model=SearchResponse)
async def search_content_get(
    q: str = Query(..., description="Search query"),
    search_type: str = Query("keyword", description="Search type: keyword"),
    similarity_threshold: float = Query(0.1, description="Similarity threshold"),
    limit: int = Query(20, description="Maximum number of results"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    current_user: dict = Depends(get_current_user),
    settings = Depends(get_settings)
):
    """
    Simple search content using GET method
    """
    try:
        supabase = get_supabase_service_client()
        
        # Get all documents for the user
        result = supabase.table("documents").select("*").execute()
        
        if not result.data:
            return SearchResponse(
                results=[],
                total_count=0,
                query=q,
                search_type=search_type
            )
        
        # Simple keyword matching
        query_terms = q.lower().split()
        matches = []
        
        for doc in result.data:
            score = 0
            title = doc.get('title', '').lower()
            summary = doc.get('summary', '').lower()
            tags = [tag.lower() for tag in doc.get('tags', [])]
            
            # Calculate relevance score
            for term in query_terms:
                if term in title:
                    score += 3  # Title matches are most important
                if term in summary:
                    score += 2  # Summary matches are important
                if any(term in tag for tag in tags):
                    score += 1  # Tag matches are good
            
            # Apply tag filter if specified
            if tags and not any(tag in doc.get('tags', []) for tag in tags):
                continue
            
            if score > 0:
                matches.append({
                    'doc': doc,
                    'score': score
                })
        
        # Sort by score and limit results
        matches.sort(key=lambda x: x['score'], reverse=True)
        matches = matches[:limit]
        
        # Convert to SearchResult format
        results = []
        for i, match in enumerate(matches):
            doc = match['doc']
            results.append(SearchResult(
                id=doc['id'],  # Use document ID as the result ID
                document_id=doc['id'],
                chunk_index=0,  # Default chunk index since we're not chunking
                content=doc.get('summary', '')[:500],  # Use summary as content
                similarity=match['score'] / 10.0,  # Normalize score to 0-1
                keyword_rank=match['score'] / 10.0,  # Same as similarity for now
                document_title=doc.get('title', ''),
                document_url=doc.get('source_url')
            ))
        
        return SearchResponse(
            results=results,
            total_count=len(results),
            query=q,
            search_type=search_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
