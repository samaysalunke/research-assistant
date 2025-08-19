-- Migration: Add enhanced metadata fields to documents table
-- This migration adds fields for advanced text processing results

-- Add new columns for enhanced metadata
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS content_type TEXT,
ADD COLUMN IF NOT EXISTS quality TEXT,
ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'en',
ADD COLUMN IF NOT EXISTS word_count INTEGER,
ADD COLUMN IF NOT EXISTS sentence_count INTEGER,
ADD COLUMN IF NOT EXISTS paragraph_count INTEGER,
ADD COLUMN IF NOT EXISTS reading_time_minutes INTEGER,
ADD COLUMN IF NOT EXISTS complexity_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS key_phrases TEXT[],
ADD COLUMN IF NOT EXISTS structure JSONB;

-- Add indexes for new fields
CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type);
CREATE INDEX IF NOT EXISTS idx_documents_quality ON documents(quality);
CREATE INDEX IF NOT EXISTS idx_documents_language ON documents(language);
CREATE INDEX IF NOT EXISTS idx_documents_complexity_score ON documents(complexity_score);
CREATE INDEX IF NOT EXISTS idx_documents_reading_time ON documents(reading_time_minutes);

-- Add constraints for quality field
ALTER TABLE documents 
ADD CONSTRAINT check_quality 
CHECK (quality IN ('excellent', 'good', 'fair', 'poor'));

-- Add constraints for content_type field
ALTER TABLE documents 
ADD CONSTRAINT check_content_type 
CHECK (content_type IN ('article', 'documentation', 'news', 'blog_post', 'technical', 'academic', 'general'));

-- Add constraints for complexity_score
ALTER TABLE documents 
ADD CONSTRAINT check_complexity_score 
CHECK (complexity_score >= 0 AND complexity_score <= 1);

-- Update existing documents with default values
UPDATE documents 
SET 
    content_type = 'general',
    quality = 'fair',
    language = 'en',
    word_count = 0,
    sentence_count = 0,
    paragraph_count = 0,
    reading_time_minutes = 1,
    complexity_score = 0.5,
    key_phrases = ARRAY[]::TEXT[],
    structure = '{}'::JSONB
WHERE content_type IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN documents.content_type IS 'Type of content (article, documentation, news, etc.)';
COMMENT ON COLUMN documents.quality IS 'Content quality assessment (excellent, good, fair, poor)';
COMMENT ON COLUMN documents.language IS 'Detected language code (en, es, fr, etc.)';
COMMENT ON COLUMN documents.word_count IS 'Total number of words in the document';
COMMENT ON COLUMN documents.sentence_count IS 'Total number of sentences in the document';
COMMENT ON COLUMN documents.paragraph_count IS 'Total number of paragraphs in the document';
COMMENT ON COLUMN documents.reading_time_minutes IS 'Estimated reading time in minutes';
COMMENT ON COLUMN documents.complexity_score IS 'Text complexity score (0-1)';
COMMENT ON COLUMN documents.key_phrases IS 'Extracted key phrases from the content';
COMMENT ON COLUMN documents.structure IS 'Document structure analysis (JSON)';
