-- Migration: Add conversation tables for enhanced conversational search
-- This migration creates tables for managing conversation sessions and messages

-- Create conversation_sessions table
CREATE TABLE IF NOT EXISTS conversation_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    context_documents TEXT[] DEFAULT '{}',
    conversation_summary TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Create conversation_messages table
CREATE TABLE IF NOT EXISTS conversation_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sources_used JSONB DEFAULT '[]',
    confidence FLOAT DEFAULT 0.0,
    query_intent TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_created_at ON conversation_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_last_activity ON conversation_sessions(last_activity);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_timestamp ON conversation_messages(timestamp);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_context_documents ON conversation_sessions USING GIN(context_documents);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_metadata ON conversation_sessions USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_sources_used ON conversation_messages USING GIN(sources_used);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_metadata ON conversation_messages USING GIN(metadata);

-- Add constraints
ALTER TABLE conversation_sessions 
ADD CONSTRAINT conversation_sessions_message_count_check 
CHECK (message_count >= 0);

ALTER TABLE conversation_messages 
ADD CONSTRAINT conversation_messages_confidence_check 
CHECK (confidence >= 0.0 AND confidence <= 1.0);

-- Create function to increment message count
CREATE OR REPLACE FUNCTION increment_message_count(session_uuid UUID)
RETURNS INTEGER AS $$
BEGIN
    UPDATE conversation_sessions 
    SET message_count = message_count + 1 
    WHERE session_id = session_uuid;
    
    RETURN (SELECT message_count FROM conversation_sessions WHERE session_id = session_uuid);
END;
$$ LANGUAGE plpgsql;

-- Create function to clean up old sessions
CREATE OR REPLACE FUNCTION cleanup_old_conversations(hours_old INTEGER DEFAULT 24)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM conversation_sessions 
    WHERE last_activity < NOW() - INTERVAL '1 hour' * hours_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security
ALTER TABLE conversation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for conversation_sessions
CREATE POLICY "Users can view their own conversation sessions" ON conversation_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own conversation sessions" ON conversation_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own conversation sessions" ON conversation_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own conversation sessions" ON conversation_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Create RLS policies for conversation_messages
CREATE POLICY "Users can view messages from their sessions" ON conversation_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversation_sessions 
            WHERE session_id = conversation_messages.session_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages to their sessions" ON conversation_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversation_sessions 
            WHERE session_id = conversation_messages.session_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update messages from their sessions" ON conversation_messages
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM conversation_sessions 
            WHERE session_id = conversation_messages.session_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete messages from their sessions" ON conversation_messages
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM conversation_sessions 
            WHERE session_id = conversation_messages.session_id 
            AND user_id = auth.uid()
        )
    );

-- Create service role policies (for backend operations)
CREATE POLICY "Service role can manage all conversation sessions" ON conversation_sessions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all conversation messages" ON conversation_messages
    FOR ALL USING (auth.role() = 'service_role');

-- Create view for conversation analytics
CREATE OR REPLACE VIEW conversation_analytics AS
SELECT 
    cs.session_id,
    cs.user_id,
    cs.created_at,
    cs.last_activity,
    cs.message_count,
    cs.conversation_summary,
    COUNT(cm.message_id) as total_messages,
    AVG(cm.confidence) as avg_confidence,
    MIN(cm.timestamp) as first_message,
    MAX(cm.timestamp) as last_message,
    EXTRACT(EPOCH FROM (MAX(cm.timestamp) - MIN(cm.timestamp))) as conversation_duration_seconds
FROM conversation_sessions cs
LEFT JOIN conversation_messages cm ON cs.session_id = cm.session_id
GROUP BY cs.session_id, cs.user_id, cs.created_at, cs.last_activity, cs.message_count, cs.conversation_summary;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON conversation_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON conversation_messages TO authenticated;
GRANT SELECT ON conversation_analytics TO authenticated;

-- Grant permissions to service role
GRANT ALL ON conversation_sessions TO service_role;
GRANT ALL ON conversation_messages TO service_role;
GRANT SELECT ON conversation_analytics TO service_role;

-- Create trigger to update last_activity when messages are added
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation_sessions 
    SET last_activity = NOW() 
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_activity
    AFTER INSERT ON conversation_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();
