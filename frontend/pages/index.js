import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  Settings, 
  MessageCircle, 
  FileText, 
  Activity,
  Bot,
  Users,
  Database,
  Globe,
  History,
  User
} from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalSessions: 0,
    knowledgeBaseFiles: 0,
    curatedWebsites: 4,
    activeAgents: 4
  });

  const loadStats = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://medical-ai-chatbot-backend.onrender.com';
      const response = await fetch(`${API_URL}/api/projects/main/stats`);
      if (response.ok) {
        const data = await response.json();
        console.log('Stats loaded:', data); // Debug log
        setStats({
          totalUsers: data.total_users || 0,
          totalSessions: data.total_sessions || 0,
          knowledgeBaseFiles: data.knowledge_base_files || 0,
          curatedWebsites: data.curated_websites || 0,
          activeAgents: data.active_agents || 4
        });
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  useEffect(() => {
    // Load stats from API
    loadStats();
    
    // Reload stats when the page becomes visible (e.g., returning from admin panel)
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        loadStats();
      }
    };
    
    // Listen for messages from admin panel
    const handleMessage = (event) => {
      if (event.data === 'configUpdated') {
        loadStats();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('message', handleMessage);
    
    // Also reload every 30 seconds for real-time updates
    const interval = setInterval(loadStats, 30000);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('message', handleMessage);
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-600 rounded-lg">
                <Bot className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Medical AI Assistant</h1>
                <p className="text-gray-600">Your intelligent healthcare chatbot service</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-3 py-2 bg-green-100 text-green-800 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">Active</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center">
              <Users className="h-10 w-10 text-blue-600" />
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{stats.totalUsers}</p>
                <p className="text-gray-600">Total Users</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center">
              <MessageCircle className="h-10 w-10 text-green-600" />
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{stats.totalSessions}</p>
                <p className="text-gray-600">Chat Sessions</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center">
              <Database className="h-10 w-10 text-purple-600" />
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{stats.knowledgeBaseFiles}</p>
                <p className="text-gray-600">Knowledge Base Files</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center">
              <Globe className="h-10 w-10 text-orange-600" />
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{stats.curatedWebsites}</p>
                <p className="text-gray-600">Curated Websites</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center">
              <Activity className="h-10 w-10 text-red-600" />
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{stats.activeAgents}</p>
                <p className="text-gray-600">Active Agents</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bot Configuration Section */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Your chatbot configuration</h2>
              <p className="text-gray-600">Manage your medical AI assistant settings and knowledge base</p>
            </div>
            <div className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-800 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="font-medium">Active</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Database className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Knowledge Base</h3>
              <p className="text-gray-600 mb-4">Upload and manage medical documents and information</p>
              <p className="text-2xl font-bold text-blue-600">{stats.knowledgeBaseFiles} files</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Web Sources</h3>
              <p className="text-gray-600 mb-4">Curated medical websites for real-time information</p>
              <p className="text-2xl font-bold text-purple-600">{stats.curatedWebsites} sites</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Bot className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Agents</h3>
              <p className="text-gray-600 mb-4">Specialized agents for different medical queries</p>
              <p className="text-2xl font-bold text-green-600">{stats.activeAgents} agents</p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <button
            onClick={() => router.push('/register')}
            className="bg-green-600 hover:bg-green-700 text-white rounded-xl p-8 text-center transition-colors group"
          >
            <User className="h-12 w-12 mx-auto mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-bold mb-2">New User</h3>
            <p className="text-green-100">Register to access medical AI assistant</p>
          </button>

          <button
            onClick={() => router.push('/login')}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl p-8 text-center transition-colors group"
          >
            <MessageCircle className="h-12 w-12 mx-auto mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-bold mb-2">User Login</h3>
            <p className="text-blue-100">Sign in to continue your medical chats</p>
          </button>

          <button
            onClick={() => router.push('/admin-login')}
            className="bg-red-600 hover:bg-red-700 text-white rounded-xl p-8 text-center transition-colors group"
          >
            <Settings className="h-12 w-12 mx-auto mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-bold mb-2">Admin Login</h3>
            <p className="text-red-100">Access admin panel and user management</p>
          </button>

          <button
            onClick={() => router.push('/chat-history')}
            className="bg-purple-600 hover:bg-purple-700 text-white rounded-xl p-8 text-center transition-colors group"
          >
            <History className="h-12 w-12 mx-auto mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-bold mb-2">Chat History</h3>
            <p className="text-purple-100">View public conversation sessions</p>
          </button>
        </div>
      </main>
    </div>
  );
}
