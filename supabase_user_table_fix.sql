-- Supabase Database Schema for Medical AI Chatbot
-- This script creates all necessary tables and indexes

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT,
    phone VARCHAR(50),
    age INTEGER,
    medical_conditions TEXT,
    emergency_contact TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW(),
    total_sessions INTEGER DEFAULT 0
);

-- 2. Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) REFERENCES users(user_id) ON DELETE CASCADE,
    project_id VARCHAR(255) DEFAULT 'main',
    title VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active',
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Project configurations table
CREATE TABLE IF NOT EXISTS project_configs (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(255) UNIQUE NOT NULL,
    bot_persona TEXT,
    curated_sites JSONB DEFAULT '[]',
    knowledge_base_files JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Knowledge base table (for future use)
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    project_id VARCHAR(255),
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    file_size INTEGER,
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. User activity logs (optional)
CREATE TABLE IF NOT EXISTS user_activity (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(user_id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    activity_type VARCHAR(100),
    details JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_project_id ON chat_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_project_configs_project_id ON project_configs(project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_project_id ON knowledge_base(project_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity(timestamp);

-- Enable Row Level Security (RLS) for data protection
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;

-- Create RLS policies

-- Users table policies
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage all users" ON users
    FOR ALL USING (auth.role() = 'service_role');

-- Chat sessions policies
CREATE POLICY "Users can view their own sessions" ON chat_sessions
    FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL OR auth.role() = 'service_role');

CREATE POLICY "Users can manage their own sessions" ON chat_sessions
    FOR ALL USING (auth.uid()::text = user_id OR user_id IS NULL OR auth.role() = 'service_role');

-- Project configs policies (allow all authenticated users to read, service role to write)
CREATE POLICY "Authenticated users can view project configs" ON project_configs
    FOR SELECT USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage project configs" ON project_configs
    FOR ALL USING (auth.role() = 'service_role');

-- Knowledge base policies
CREATE POLICY "Authenticated users can view knowledge base" ON knowledge_base
    FOR SELECT USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage knowledge base" ON knowledge_base
    FOR ALL USING (auth.role() = 'service_role');

-- User activity policies
CREATE POLICY "Users can view their own activity" ON user_activity
    FOR SELECT USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage all activity" ON user_activity
    FOR ALL USING (auth.role() = 'service_role');

-- Insert default project configuration
INSERT INTO project_configs (project_id, bot_persona, curated_sites, knowledge_base_files)
VALUES (
    'main',
    'You are a compassionate medical AI assistant that provides accurate health information while emphasizing the importance of consulting healthcare professionals.',
    '["mayoclinic.org", "webmd.com", "healthline.com", "medlineplus.gov"]',
    '[]'
) ON CONFLICT (project_id) DO NOTHING;

-- Create a function to automatically update total_sessions
CREATE OR REPLACE FUNCTION update_user_session_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.user_id IS NOT NULL THEN
        UPDATE users 
        SET total_sessions = total_sessions + 1,
            last_active = NOW()
        WHERE user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update session count automatically
DROP TRIGGER IF EXISTS trigger_update_user_session_count ON chat_sessions;
CREATE TRIGGER trigger_update_user_session_count
    AFTER INSERT ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_session_count();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated, service_role;

-- Success message
SELECT 'Database schema created successfully! All tables, indexes, and policies are in place.' AS result;
