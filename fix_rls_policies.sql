-- Fix RLS policies for documents table
-- This script ensures that users can only access their own documents

-- Enable RLS on documents table if not already enabled
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own documents" ON documents;
DROP POLICY IF EXISTS "Users can insert their own documents" ON documents;
DROP POLICY IF EXISTS "Users can update their own documents" ON documents;
DROP POLICY IF EXISTS "Users can delete their own documents" ON documents;

-- Create RLS policies for documents
CREATE POLICY "Users can view their own documents" ON documents
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own documents" ON documents
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own documents" ON documents
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own documents" ON documents
    FOR DELETE USING (auth.uid() = user_id);

-- Also ensure embeddings table has proper RLS policies
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view embeddings for their documents" ON embeddings;
DROP POLICY IF EXISTS "Users can insert embeddings for their documents" ON embeddings;
DROP POLICY IF EXISTS "Users can update embeddings for their documents" ON embeddings;
DROP POLICY IF EXISTS "Users can delete embeddings for their documents" ON embeddings;

-- Create RLS policies for embeddings
CREATE POLICY "Users can view embeddings for their documents" ON embeddings
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM documents 
            WHERE documents.id = embeddings.document_id 
            AND documents.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert embeddings for their documents" ON embeddings
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM documents 
            WHERE documents.id = embeddings.document_id 
            AND documents.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update embeddings for their documents" ON embeddings
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM documents 
            WHERE documents.id = embeddings.document_id 
            AND documents.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete embeddings for their documents" ON embeddings
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM documents 
            WHERE documents.id = embeddings.document_id 
            AND documents.user_id = auth.uid()
        )
    );
