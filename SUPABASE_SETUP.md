# Supabase Setup Guide for Medical AI Chatbot

This guide will help you set up Supabase as the database backend for your Medical AI Chatbot service.

## 🚀 Quick Setup Steps

### 1. Create Supabase Account and Project

1. **Go to Supabase**: Visit [https://app.supabase.com/](https://app.supabase.com/)
2. **Sign up/Login**: Create account or sign in with GitHub/Google
3. **Create New Project**: 
   - Click "New Project"
   - Choose your organization
   - Enter project name: `medical-ai-chatbot`
   - Enter database password (save this!)
   - Select region closest to you
   - Click "Create new project"

### 2. Get Your API Keys

1. **Go to Project Settings**: 
   - Click on your project
   - Navigate to "Settings" → "API"

2. **Copy Required Keys**:
   - **Project URL**: Copy the "Project URL" (starts with `https://`)
   - **anon/public key**: Copy the "anon public" key
   - **service_role key**: Copy the "service_role" key (keep this secret!)

### 3. Update Environment Variables

Open your `.env` file in the backend folder and update these values:

```env
# Supabase Database Configuration
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_ANON_KEY="your-anon-key-here"
SUPABASE_SERVICE_KEY="your-service-role-key-here"

# Set database type to use Supabase
DATABASE_TYPE="supabase"
```

**Replace the placeholder values with your actual Supabase credentials:**

- `your-project-id`: Your unique project identifier
- `your-anon-key-here`: The anon/public key from step 2
- `your-service-role-key-here`: The service_role key from step 2

### 4. Create Database Schema

1. **Open SQL Editor**: 
   - In your Supabase dashboard, go to "SQL Editor"
   - Click "New query"

2. **Execute Schema**: 
   - Copy the entire content from `backend/database_schema.sql`
   - Paste it in the SQL Editor
   - Click "Run" to execute

This will create all necessary tables, indexes, and security policies.

### 5. Verify Database Setup

Check if tables were created successfully:
1. Go to "Table Editor" in your Supabase dashboard
2. You should see these tables:
   - `users` - User profiles and registration data
   - `chat_sessions` - Chat conversation history
   - `project_configs` - Bot configuration settings
   - `knowledge_base` - File metadata (for future use)
   - `user_activity` - User activity logs (optional)

## 🔧 Required API Keys Summary

You need these 3 keys from Supabase:

| Key Name | Description | Where to Find | Environment Variable |
|----------|-------------|---------------|---------------------|
| **Project URL** | Your Supabase project endpoint | Settings → API → Project URL | `SUPABASE_URL` |
| **anon public** | Public key for client-side operations | Settings → API → anon public | `SUPABASE_ANON_KEY` |
| **service_role** | Server-side key with full access | Settings → API → service_role | `SUPABASE_SERVICE_KEY` |

## 🛡️ Security Notes

- **Keep `service_role` key secret** - Never expose it in frontend code
- **Use `anon` key for client operations** - Safe for frontend use with RLS
- **Row Level Security (RLS)** is enabled automatically for data protection

## 🔄 Migration from File Storage

When you switch to Supabase:

1. **Backup your data**: Save copies of your JSON files
2. **Update `.env`**: Set `DATABASE_TYPE="supabase"`
3. **Restart server**: The app will automatically use Supabase
4. **Migrate data** (optional): Re-register users to populate Supabase

## 🧪 Testing Your Setup

1. **Start your backend server**:
   ```bash
   cd backend
   python -m app.main
   ```

2. **Check logs**: Look for "✅ Supabase client initialized successfully"

3. **Test API**: Visit `http://localhost:8000/api/projects/main/stats`
   - Should return statistics from Supabase

4. **Register a user**: Use the registration API to test database writes

## 🆘 Troubleshooting

### Common Issues:

1. **"SUPABASE_URL must be set"**
   - Check your `.env` file has correct Supabase URL
   - Restart your server after updating `.env`

2. **Connection errors**
   - Verify your API keys are correct
   - Check if your Supabase project is active
   - Ensure no trailing spaces in `.env` values

3. **Permission errors**
   - Verify RLS policies are set up (run the schema SQL)
   - Check you're using the correct API key for operations

4. **Tables not found**
   - Run the complete `database_schema.sql` in Supabase SQL Editor
   - Check "Table Editor" to verify tables exist

## 📊 Database Schema Overview

The schema includes:

- **users**: User profiles with medical information
- **chat_sessions**: Conversation history with JSON message storage
- **project_configs**: Bot personality and configuration
- **Row Level Security**: Automatic data protection
- **Triggers**: Auto-update timestamps and user session counts
- **Views**: Optimized queries for statistics

## 🎯 Next Steps

After setup:
1. Test user registration and login
2. Create chat sessions
3. Configure bot personality in admin panel
4. Monitor usage through Supabase dashboard

Your Medical AI Chatbot is now running on a scalable, production-ready database! 🎉
