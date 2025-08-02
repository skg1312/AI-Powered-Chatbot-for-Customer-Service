-- ===============================================
-- DATABASE RESET QUERIES - RUN IN SUPABASE SQL EDITOR
-- ===============================================
-- This will clean all data and reset the database to a fresh state

-- 1. DELETE ALL DATA FROM TABLES (but keep table structure)
-- ===============================================

-- Delete all messages first (due to foreign key constraints)
DELETE FROM messages;

-- Delete all chat sessions
DELETE FROM chat_sessions;

-- Delete all users (except if you want to keep some specific ones)
DELETE FROM users;

-- Delete all user activity logs
DELETE FROM user_activity;

-- Delete all knowledge base entries
DELETE FROM knowledge_base;

-- Reset the project configs to default only
DELETE FROM project_configs WHERE project_id != 'main';

-- 2. RESET AUTO-INCREMENT SEQUENCES
-- ===============================================

-- Reset all ID sequences to start from 1 again
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE chat_sessions_id_seq RESTART WITH 1;
ALTER SEQUENCE messages_id_seq RESTART WITH 1;
ALTER SEQUENCE user_activity_id_seq RESTART WITH 1;
ALTER SEQUENCE knowledge_base_id_seq RESTART WITH 1;
ALTER SEQUENCE project_configs_id_seq RESTART WITH 1;

-- 3. VERIFY CLEANUP
-- ===============================================

-- Check that all tables are empty
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'chat_sessions', COUNT(*) FROM chat_sessions
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'user_activity', COUNT(*) FROM user_activity
UNION ALL
SELECT 'knowledge_base', COUNT(*) FROM knowledge_base
UNION ALL
SELECT 'project_configs', COUNT(*) FROM project_configs;

-- 4. OPTIONAL: ALSO RESET THE PROJECT CONFIG TO DEFAULT
-- ===============================================

-- Ensure the main project config exists with default values
INSERT INTO project_configs (project_id, bot_persona, curated_sites, knowledge_base_files)
VALUES (
    'main',
    'You are a compassionate medical AI assistant that provides accurate health information while emphasizing the importance of consulting healthcare professionals.',
    '["mayoclinic.org", "webmd.com", "healthline.com", "medlineplus.gov"]',
    '[]'
) ON CONFLICT (project_id) DO UPDATE SET
    bot_persona = EXCLUDED.bot_persona,
    curated_sites = EXCLUDED.curated_sites,
    knowledge_base_files = EXCLUDED.knowledge_base_files,
    updated_at = NOW();

-- Success message
SELECT 'Database has been reset successfully! All user data, sessions, and messages have been cleared.' as result;
