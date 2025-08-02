-- Add missing messages table to the database schema
-- This table stores individual messages separately from sessions

-- 6. Messages table (stores individual chat messages)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    user_id VARCHAR(255) REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    message_order INTEGER DEFAULT 0
);

-- Create indexes for the messages table
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_message_id ON messages(message_id);

-- Enable RLS for messages table
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for messages
CREATE POLICY "Users can view their own messages" ON messages
    FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL OR auth.role() = 'service_role');

CREATE POLICY "Users can manage their own messages" ON messages
    FOR ALL USING (auth.uid()::text = user_id OR user_id IS NULL OR auth.role() = 'service_role');

-- Grant permissions for messages table
GRANT SELECT, INSERT, UPDATE, DELETE ON messages TO authenticated;
GRANT ALL ON messages TO service_role;
GRANT USAGE, SELECT ON SEQUENCE messages_id_seq TO authenticated, service_role;

-- Create a function to automatically update message count in sessions
CREATE OR REPLACE FUNCTION update_session_message_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE chat_sessions 
        SET updated_at = NOW()
        WHERE session_id = NEW.session_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE chat_sessions 
        SET updated_at = NOW()
        WHERE session_id = OLD.session_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update session timestamp when messages are added/removed
DROP TRIGGER IF EXISTS trigger_update_session_message_count ON messages;
CREATE TRIGGER trigger_update_session_message_count
    AFTER INSERT OR DELETE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_session_message_count();

-- Add message_count column to chat_sessions if it doesn't exist
ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS message_count INTEGER DEFAULT 0;

-- Create a function to calculate and update message counts
CREATE OR REPLACE FUNCTION sync_session_message_counts()
RETURNS VOID AS $$
BEGIN
    UPDATE chat_sessions 
    SET message_count = (
        SELECT COUNT(*) 
        FROM messages 
        WHERE messages.session_id = chat_sessions.session_id
    );
END;
$$ LANGUAGE plpgsql;

-- Run the sync function to update existing session message counts
SELECT sync_session_message_counts();

SELECT 'Messages table created successfully and message counts synchronized!' AS result;
