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
    Search content using semantic similarity
    """
    try:
        # Generate embedding for search query using OpenAI
        try:
            import openai
            openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            embedding_response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=search_request.query
            )
            query_embedding = embedding_response.data[0].embedding
        except Exception as e:
            # Fallback: hash-based embedding
            import hashlib
            hash_obj = hashlib.md5(search_request.query.encode())
            hash_bytes = hash_obj.digest()
            query_embedding = [float(b) / 255.0 for b in hash_bytes] * 48  # 32 * 48 = 1536
            query_embedding = query_embedding[:1536]
        
        # Perform semantic search
        supabase = get_supabase_service_client()
        
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
        # Try to use the semantic_search function from database
        try:
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
        except Exception as rpc_error:
            # Fallback: direct vector search if RPC function doesn't exist
            print(f"RPC function not available, using direct search: {str(rpc_error)}")
            result = supabase.table("embeddings").select("*").execute()
            
                    # Simple vector similarity search
        results = []
        for row in result.data:
            if row.get("embedding"):
                # Parse embedding from JSON string
                import json
                try:
                    embedding = json.loads(row["embedding"]) if isinstance(row["embedding"], str) else row["embedding"]
                    
                    # Calculate cosine similarity
                    import numpy as np
                    vec1 = np.array(query_embedding)
                    vec2 = np.array(embedding)
                    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    
                    if similarity > threshold:
                        results.append({
                            "id": row["id"],
                            "document_id": row["document_id"],
                            "chunk_index": row["chunk_index"],
                            "content": row["content"],
                            "similarity": float(similarity)
                        })
                except Exception as e:
                    print(f"Error processing embedding: {str(e)}")
                    continue
            
            # Sort by similarity and limit
            results.sort(key=lambda x: x["similarity"], reverse=True)
            result.data = results[:limit]
        
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
