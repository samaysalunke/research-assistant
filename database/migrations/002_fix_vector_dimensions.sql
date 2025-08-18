-- Migration: Fix vector dimensions for Claude embeddings
-- Date: 2025-01-19
-- Description: Update embeddings table to use 3072 dimensions for Claude's text-embedding-3-large

-- Drop existing indexes that depend on the embedding column
DROP INDEX IF EXISTS embeddings_embedding_idx;

-- Alter the embeddings table to change vector dimensions
ALTER TABLE embeddings 
ALTER COLUMN embedding TYPE VECTOR(3072);

-- Recreate the vector similarity index
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Update the semantic search function to handle 3072 dimensions
CREATE OR REPLACE FUNCTION semantic_search(
    query_embedding VECTOR(3072),
    similarity_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INTEGER,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.document_id,
        e.chunk_index,
        e.content,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM embeddings e
    WHERE 1 - (e.embedding <=> query_embedding) > similarity_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Update the hybrid search function
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding VECTOR(3072),
    similarity_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INTEGER,
    content TEXT,
    similarity FLOAT,
    rank_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.document_id,
        e.chunk_index,
        e.content,
        1 - (e.embedding <=> query_embedding) AS similarity,
        (1 - (e.embedding <=> query_embedding)) * 0.7 + 
        (CASE WHEN e.content ILIKE '%' || query_text || '%' THEN 0.3 ELSE 0.0 END) AS rank_score
    FROM embeddings e
    WHERE 1 - (e.embedding <=> query_embedding) > similarity_threshold
    ORDER BY rank_score DESC
    LIMIT match_count;
END;
$$;
