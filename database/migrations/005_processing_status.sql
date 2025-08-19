-- Migration: Add processing status tracking table
-- This migration creates a table to track processing task status and progress

-- Create processing_status table
CREATE TABLE IF NOT EXISTS processing_status (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id UUID NOT NULL UNIQUE,
    url TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    stage TEXT NOT NULL CHECK (stage IN ('initialized', 'content_extraction', 'text_processing', 'ai_analysis', 'embedding_generation', 'database_storage', 'completed')),
    progress DECIMAL(3,2) DEFAULT 0.0 CHECK (progress >= 0.0 AND progress <= 1.0),
    error_message TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    retry_count INTEGER DEFAULT 0,
    result JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_processing_status_task_id ON processing_status(task_id);
CREATE INDEX IF NOT EXISTS idx_processing_status_user_id ON processing_status(user_id);
CREATE INDEX IF NOT EXISTS idx_processing_status_status ON processing_status(status);
CREATE INDEX IF NOT EXISTS idx_processing_status_created_at ON processing_status(created_at);

-- Add RLS policies
ALTER TABLE processing_status ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own processing status
CREATE POLICY "Users can view own processing status" ON processing_status
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own processing status
CREATE POLICY "Users can insert own processing status" ON processing_status
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own processing status
CREATE POLICY "Users can update own processing status" ON processing_status
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Service role can manage all processing status
CREATE POLICY "Service role can manage all processing status" ON processing_status
    FOR ALL USING (auth.role() = 'service_role');

-- Add comments for documentation
COMMENT ON TABLE processing_status IS 'Tracks the status and progress of content processing tasks';
COMMENT ON COLUMN processing_status.task_id IS 'Unique identifier for the processing task';
COMMENT ON COLUMN processing_status.url IS 'URL being processed';
COMMENT ON COLUMN processing_status.user_id IS 'User who initiated the processing';
COMMENT ON COLUMN processing_status.status IS 'Current status of the task (pending, processing, completed, failed, cancelled)';
COMMENT ON COLUMN processing_status.stage IS 'Current processing stage';
COMMENT ON COLUMN processing_status.progress IS 'Progress percentage (0.0 to 1.0)';
COMMENT ON COLUMN processing_status.error_message IS 'Error message if task failed';
COMMENT ON COLUMN processing_status.start_time IS 'When processing started';
COMMENT ON COLUMN processing_status.end_time IS 'When processing completed or failed';
COMMENT ON COLUMN processing_status.retry_count IS 'Number of retry attempts';
COMMENT ON COLUMN processing_status.result IS 'Processing results and metadata';

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_processing_status_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_update_processing_status_updated_at
    BEFORE UPDATE ON processing_status
    FOR EACH ROW
    EXECUTE FUNCTION update_processing_status_updated_at();
