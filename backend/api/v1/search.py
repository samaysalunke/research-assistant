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
from database.client import get_supabase_client

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/", response_model=SearchResponse)
async def search_content(
    search_request: SearchRequest,
    current_user: dict = Depends(get_current_user),
    settings = Depends(get_settings)
):
    """
    Search content using semantic similarity
    """
    try:
        # Generate embedding for search query
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        
        embedding_response = client.embeddings.create(
            model=settings.claude_embedding_model,
            input=search_request.query
        )
        query_embedding = embedding_response.embeddings[0].embedding
        
        # Perform semantic search
        supabase = get_supabase_client()
        
        if search_request.search_type == "semantic":
            results = await _semantic_search(
                supabase, query_embedding, search_request.similarity_threshold, search_request.limit
            )
        elif search_request.search_type == "hybrid":
            results = await _hybrid_search(
                supabase, search_request.query, query_embedding, search_request.similarity_threshold, search_request.limit
            )
        else:
            results = await _keyword_search(
                supabase, search_request.query, search_request.limit
            )
        
        # Filter by tags if specified
        if search_request.tags:
            results = [r for r in results if any(tag in r.get("document_tags", []) for tag in search_request.tags)]
        
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
    search_type: str = Query("hybrid", description="Search type: semantic, keyword, or hybrid"),
    similarity_threshold: float = Query(0.7, description="Similarity threshold for semantic search"),
    limit: int = Query(20, description="Maximum number of results"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    current_user: dict = Depends(get_current_user),
    settings = Depends(get_settings)
):
    """
    Search content using GET method
    """
    search_request = SearchRequest(
        query=q,
        search_type=search_type,
        similarity_threshold=similarity_threshold,
        limit=limit,
        tags=tags
    )
    
    return await search_content(search_request, current_user, settings)

async def _semantic_search(supabase, query_embedding: List[float], threshold: float, limit: int) -> List[SearchResult]:
    """Perform semantic search using vector similarity"""
    try:
        # Use the semantic_search function from database
        result = supabase.rpc(
            "semantic_search",
            {
                "query_embedding": query_embedding,
                "similarity_threshold": threshold,
                "match_count": limit
            }
        ).execute()
        
        if result.error:
            raise Exception(f"Semantic search failed: {result.error}")
        
        # Get document details for results
        results = []
        for row in result.data:
            doc_result = supabase.table("documents").select("title, source_url").eq("id", row["document_id"]).single().execute()
            
            if doc_result.data:
                results.append(SearchResult(
                    id=row["id"],
                    document_id=row["document_id"],
                    chunk_index=row["chunk_index"],
                    content=row["content"],
                    similarity=row["similarity"],
                    document_title=doc_result.data["title"],
                    document_url=doc_result.data.get("source_url")
                ))
        
        return results
        
    except Exception as e:
        raise Exception(f"Semantic search error: {str(e)}")

async def _hybrid_search(supabase, query_text: str, query_embedding: List[float], threshold: float, limit: int) -> List[SearchResult]:
    """Perform hybrid search combining semantic and keyword search"""
    try:
        # Use the hybrid_search function from database
        result = supabase.rpc(
            "hybrid_search",
            {
                "query_text": query_text,
                "query_embedding": query_embedding,
                "similarity_threshold": threshold,
                "match_count": limit
            }
        ).execute()
        
        if result.error:
            raise Exception(f"Hybrid search failed: {result.error}")
        
        # Get document details for results
        results = []
        for row in result.data:
            doc_result = supabase.table("documents").select("title, source_url").eq("id", row["document_id"]).single().execute()
            
            if doc_result.data:
                results.append(SearchResult(
                    id=row["id"],
                    document_id=row["document_id"],
                    chunk_index=row["chunk_index"],
                    content=row["content"],
                    similarity=row["similarity"],
                    keyword_rank=row.get("keyword_rank"),
                    document_title=doc_result.data["title"],
                    document_url=doc_result.data.get("source_url")
                ))
        
        return results
        
    except Exception as e:
        raise Exception(f"Hybrid search error: {str(e)}")

async def _keyword_search(supabase, query_text: str, limit: int) -> List[SearchResult]:
    """Perform keyword-based search"""
    try:
        # Simple keyword search using PostgreSQL full-text search
        result = supabase.table("embeddings").select(
            "id, document_id, chunk_index, content"
        ).text_search("content", query_text).limit(limit).execute()
        
        if result.error:
            raise Exception(f"Keyword search failed: {result.error}")
        
        # Get document details for results
        results = []
        for row in result.data:
            doc_result = supabase.table("documents").select("title, source_url").eq("id", row["document_id"]).single().execute()
            
            if doc_result.data:
                results.append(SearchResult(
                    id=row["id"],
                    document_id=row["document_id"],
                    chunk_index=row["chunk_index"],
                    content=row["content"],
                    similarity=1.0,  # Default similarity for keyword search
                    document_title=doc_result.data["title"],
                    document_url=doc_result.data.get("source_url")
                ))
        
        return results
        
    except Exception as e:
        raise Exception(f"Keyword search error: {str(e)}")
