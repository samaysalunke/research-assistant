-- Migration: Enhanced Search Functionality
-- This migration adds enhanced search capabilities including semantic search function

-- Create function for matching document chunks using vector similarity
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    document_id uuid,
    chunk_index int,
    content text,
    similarity float,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.document_id,
        dc.chunk_index,
        dc.content,
        1 - (dc.embedding <=> query_embedding) as similarity,
        dc.metadata
    FROM document_chunks dc
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create function for hybrid search combining semantic and keyword search
CREATE OR REPLACE FUNCTION hybrid_search_documents(
    query_text text,
    query_embedding vector(1536),
    user_id uuid,
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 20
)
RETURNS TABLE (
    document_id uuid,
    title text,
    summary text,
    source_url text,
    similarity_score float,
    keyword_score float,
    combined_score float,
    tags text[],
    content_type text,
    quality text,
    created_at timestamptz
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH semantic_results AS (
        SELECT 
            dc.document_id,
            1 - (dc.embedding <=> query_embedding) as semantic_score
        FROM document_chunks dc
        WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
        GROUP BY dc.document_id
        ORDER BY AVG(1 - (dc.embedding <=> query_embedding)) DESC
        LIMIT match_count
    ),
    keyword_results AS (
        SELECT 
            d.id as document_id,
            CASE 
                WHEN d.title ILIKE '%' || query_text || '%' THEN 2.0
                WHEN d.summary ILIKE '%' || query_text || '%' THEN 1.0
                ELSE 0.0
            END as keyword_score
        FROM documents d
        WHERE d.user_id = hybrid_search_documents.user_id
        AND (d.title ILIKE '%' || query_text || '%' OR d.summary ILIKE '%' || query_text || '%')
    )
    SELECT 
        d.id as document_id,
        d.title,
        d.summary,
        d.source_url,
        COALESCE(sr.semantic_score, 0.0) as similarity_score,
        COALESCE(kr.keyword_score, 0.0) as keyword_score,
        COALESCE(sr.semantic_score, 0.0) * 0.7 + COALESCE(kr.keyword_score, 0.0) * 0.3 as combined_score,
        d.tags,
        d.content_type,
        d.quality,
        d.created_at
    FROM documents d
    LEFT JOIN semantic_results sr ON d.id = sr.document_id
    LEFT JOIN keyword_results kr ON d.id = kr.document_id
    WHERE d.user_id = hybrid_search_documents.user_id
    AND (sr.document_id IS NOT NULL OR kr.document_id IS NOT NULL)
    ORDER BY combined_score DESC, d.created_at DESC
    LIMIT match_count;
END;
$$;

-- Create function for advanced filtering
CREATE OR REPLACE FUNCTION filter_documents(
    user_id uuid,
    content_type_filter text[] DEFAULT NULL,
    quality_filter text[] DEFAULT NULL,
    language_filter text[] DEFAULT NULL,
    tag_filter text[] DEFAULT NULL,
    min_word_count int DEFAULT NULL,
    max_word_count int DEFAULT NULL,
    min_reading_time int DEFAULT NULL,
    max_reading_time int DEFAULT NULL,
    min_complexity float DEFAULT NULL,
    max_complexity float DEFAULT NULL,
    date_from timestamptz DEFAULT NULL,
    date_to timestamptz DEFAULT NULL,
    limit_count int DEFAULT 50,
    offset_count int DEFAULT 0
)
RETURNS TABLE (
    document_id uuid,
    title text,
    summary text,
    source_url text,
    tags text[],
    content_type text,
    quality text,
    language text,
    word_count int,
    reading_time_minutes int,
    complexity_score float,
    created_at timestamptz
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id as document_id,
        d.title,
        d.summary,
        d.source_url,
        d.tags,
        d.content_type,
        d.quality,
        d.language,
        d.word_count,
        d.reading_time_minutes,
        d.complexity_score,
        d.created_at
    FROM documents d
    WHERE d.user_id = filter_documents.user_id
    AND (content_type_filter IS NULL OR d.content_type = ANY(content_type_filter))
    AND (quality_filter IS NULL OR d.quality = ANY(quality_filter))
    AND (language_filter IS NULL OR d.language = ANY(language_filter))
    AND (tag_filter IS NULL OR d.tags && tag_filter)
    AND (min_word_count IS NULL OR d.word_count >= min_word_count)
    AND (max_word_count IS NULL OR d.word_count <= max_word_count)
    AND (min_reading_time IS NULL OR d.reading_time_minutes >= min_reading_time)
    AND (max_reading_time IS NULL OR d.reading_time_minutes <= max_reading_time)
    AND (min_complexity IS NULL OR d.complexity_score >= min_complexity)
    AND (max_complexity IS NULL OR d.complexity_score <= max_complexity)
    AND (date_from IS NULL OR d.created_at >= date_from)
    AND (date_to IS NULL OR d.created_at <= date_to)
    ORDER BY d.created_at DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$;

-- Create indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type);
CREATE INDEX IF NOT EXISTS idx_documents_quality ON documents(quality);
CREATE INDEX IF NOT EXISTS idx_documents_language ON documents(language);
CREATE INDEX IF NOT EXISTS idx_documents_word_count ON documents(word_count);
CREATE INDEX IF NOT EXISTS idx_documents_reading_time ON documents(reading_time_minutes);
CREATE INDEX IF NOT EXISTS idx_documents_complexity ON documents(complexity_score);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);

-- Create GIN index for tags array for faster tag searches
CREATE INDEX IF NOT EXISTS idx_documents_tags_gin ON documents USING GIN(tags);

-- Create full-text search index for title and summary
CREATE INDEX IF NOT EXISTS idx_documents_title_summary_fts ON documents USING GIN(to_tsvector('english', title || ' ' || COALESCE(summary, '')));

-- Add comments for documentation
COMMENT ON FUNCTION match_document_chunks IS 'Performs semantic search on document chunks using vector similarity';
COMMENT ON FUNCTION hybrid_search_documents IS 'Performs hybrid search combining semantic and keyword matching';
COMMENT ON FUNCTION filter_documents IS 'Advanced document filtering with multiple criteria';
