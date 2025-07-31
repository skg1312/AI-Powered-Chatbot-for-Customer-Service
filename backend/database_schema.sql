-- Medical AI Chatbot Database Schema for Supabase
-- Execute these SQL commands in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    age INTEGER,
    medical_conditions TEXT,
    emergency_contact VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW(),
    total_sessions INTEGER DEFAULT 0
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active DESC);

-- 2. Chat Sessions Table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) REFERENCES users(user_id) ON DELETE CASCADE,
    project_id VARCHAR(255) DEFAULT 'main',
    title VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active',
    messages JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for chat sessions
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_status ON chat_sessions(status);

-- 3. Project Configurations Table
CREATE TABLE IF NOT EXISTS project_configs (
    id BIGSERIAL PRIMARY KEY,
    project_id VARCHAR(255) UNIQUE NOT NULL,
    bot_persona TEXT,
    curated_sites JSONB DEFAULT '[]'::jsonb,
    knowledge_base_files JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for project configs
CREATE INDEX IF NOT EXISTS idx_project_configs_project_id ON project_configs(project_id);

-- 4. Knowledge Base Table (for future file storage metadata)
CREATE TABLE IF NOT EXISTS knowledge_base (
    id BIGSERIAL PRIMARY KEY,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    project_id VARCHAR(255) NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(100),
    file_size BIGINT,
    upload_date TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for knowledge base
CREATE INDEX IF NOT EXISTS idx_knowledge_base_file_id ON knowledge_base(file_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_project_id ON knowledge_base(project_id);

-- 5. User Activity Log (optional - for analytics)
CREATE TABLE IF NOT EXISTS user_activity (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for user activity
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON user_activity(created_at DESC);

-- 6. Create Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage users" ON users
    FOR ALL USING (auth.role() = 'service_role');

-- Chat sessions policies
CREATE POLICY "Users can view their own sessions" ON chat_sessions
    FOR SELECT USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage sessions" ON chat_sessions
    FOR ALL USING (auth.role() = 'service_role');

-- Project configs policies
CREATE POLICY "Service role can manage project configs" ON project_configs
    FOR ALL USING (auth.role() = 'service_role');

-- Knowledge base policies
CREATE POLICY "Service role can manage knowledge base" ON knowledge_base
    FOR ALL USING (auth.role() = 'service_role');

-- User activity policies
CREATE POLICY "Users can view their own activity" ON user_activity
    FOR SELECT USING (auth.uid()::text = user_id OR auth.role() = 'service_role');

CREATE POLICY "Service role can manage user activity" ON user_activity
    FOR ALL USING (auth.role() = 'service_role');

-- 7. Create Functions and Triggers

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_chat_sessions_updated_at
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_configs_updated_at
    BEFORE UPDATE ON project_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update user's total_sessions count
CREATE OR REPLACE FUNCTION update_user_session_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users 
        SET total_sessions = total_sessions + 1,
            last_active = NOW()
        WHERE user_id = NEW.user_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE users 
        SET total_sessions = GREATEST(total_sessions - 1, 0)
        WHERE user_id = OLD.user_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Trigger to automatically update user session count
CREATE TRIGGER update_user_session_count_trigger
    AFTER INSERT OR DELETE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_session_count();

-- 8. Insert default project configuration
INSERT INTO project_configs (project_id, bot_persona, curated_sites, knowledge_base_files)
VALUES (
    'main',
    'You are a helpful medical AI assistant. Provide accurate, evidence-based medical information while always recommending users consult with healthcare professionals for serious concerns.',
    '["https://www.mayoclinic.org", "https://www.webmd.com", "https://medlineplus.gov", "https://www.healthline.com"]'::jsonb,
    '[]'::jsonb
) ON CONFLICT (project_id) DO UPDATE SET
    updated_at = NOW();

-- 9. Create a view for user statistics
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.user_id,
    u.name,
    u.email,
    u.total_sessions,
    u.last_active,
    COUNT(cs.session_id) as actual_sessions,
    MAX(cs.created_at) as last_chat_date
FROM users u
LEFT JOIN chat_sessions cs ON u.user_id = cs.user_id
GROUP BY u.user_id, u.name, u.email, u.total_sessions, u.last_active;

-- 10. Create a view for system statistics
CREATE OR REPLACE VIEW system_stats AS
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM chat_sessions) as total_sessions,
    (SELECT COUNT(*) FROM chat_sessions WHERE status = 'active') as active_sessions,
    (SELECT COUNT(*) FROM knowledge_base) as knowledge_files,
    4 as active_agents;

-- Grant necessary permissions
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT SELECT ON user_stats, system_stats TO anon, authenticated;

-- Success message
SELECT 'Medical AI Chatbot database schema created successfully!' as message;
