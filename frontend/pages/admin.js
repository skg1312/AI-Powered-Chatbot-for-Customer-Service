import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  ArrowLeft, 
  Save, 
  Upload, 
  X, 
  Settings, 
  Database,
  Globe,
  Bot,
  Users,
  LogOut,
  Shield
} from 'lucide-react';

export default function AdminPanel() {
  const router = useRouter();
  const [config, setConfig] = useState({
    botPersona: '',
    curatedSites: [],
    knowledgeBaseFiles: []
  });
  const [newSite, setNewSite] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [adminSession, setAdminSession] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check admin authentication
    const session = localStorage.getItem('adminSession');
    if (!session) {
      router.push('/admin-login');
      return;
    }

    try {
      const sessionData = JSON.parse(session);
      if (sessionData.isAdmin) {
        setAdminSession(sessionData);
        setIsAuthenticated(true);
        loadConfiguration();
      } else {
        router.push('/admin-login');
      }
    } catch (error) {
      router.push('/admin-login');
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('adminSession');
    router.push('/');
  };

  const loadConfiguration = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://medical-ai-chatbot-backend.onrender.com';
      const response = await fetch(`${API_URL}/api/projects/main/config`);
      if (response.ok) {
        const data = await response.json();
        setConfig({
          botPersona: data.bot_persona || '',
          curatedSites: data.curated_sites || [],
          knowledgeBaseFiles: data.knowledge_base_files || []
        });
      }
    } catch (error) {
      console.error('Failed to load configuration:', error);
      // Keep the default state if loading fails
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://medical-ai-chatbot-backend.onrender.com';
      const response = await fetch(`${API_URL}/api/projects/main/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: 'main',
          bot_persona: config.botPersona,
          curated_sites: config.curatedSites,
          knowledge_base_files: config.knowledgeBaseFiles
        }),
      });

      if (response.ok) {
        setSaveMessage('Configuration saved successfully!');
        setTimeout(() => setSaveMessage(''), 3000);
        
        // Reload the configuration to ensure UI is in sync
        await loadConfiguration();
        
        // Notify parent window if opened from dashboard
        if (window.opener) {
          window.opener.postMessage('configUpdated', '*');
        }
      } else {
        const errorData = await response.json();
        setSaveMessage(`Failed to save configuration: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error saving configuration:', error);
      setSaveMessage('Error saving configuration: Network error');
    } finally {
      setIsSaving(false);
    }
  };

  const addCuratedSite = () => {
    if (newSite && !(config.curatedSites || []).includes(newSite)) {
      setConfig({
        ...config,
        curatedSites: [...(config.curatedSites || []), newSite]
      });
      setNewSite('');
    }
  };

  const removeCuratedSite = (site) => {
    setConfig({
      ...config,
      curatedSites: (config.curatedSites || []).filter(s => s !== site)
    });
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    const fileNames = files.map(file => file.name);
    setConfig({
      ...config,
      knowledgeBaseFiles: [...(config.knowledgeBaseFiles || []), ...fileNames]
    });
  };

  // Show loading screen while checking authentication
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => router.push('/')}
                className="p-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-6 w-6" />
              </button>
              <div className="p-2 bg-red-600 rounded-lg">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
                <p className="text-sm text-gray-500">
                  {adminSession ? `Welcome, ${adminSession.username}` : 'Configure your medical AI assistant'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => router.push('/chat-history')}
                className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
              >
                <Database className="h-5 w-5" />
                <span>Chat History</span>
              </button>
              <button
                onClick={() => router.push('/user-management')}
                className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
              >
                <Users className="h-5 w-5" />
                <span>Manage Users</span>
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg"
              >
                <LogOut className="h-5 w-5" />
                <span>Logout</span>
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
              >
                <Save className="h-5 w-5" />
                <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
              </button>
            </div>
          </div>
          {saveMessage && (
            <div className={`px-4 py-2 rounded-lg mb-4 ${
              saveMessage.includes('successfully') 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {saveMessage}
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Bot Persona Section */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
            <div className="flex items-center space-x-3 mb-6">
              <Bot className="h-8 w-8 text-blue-600" />
              <div>
                <h3 className="text-xl font-bold text-gray-900">Bot Persona</h3>
                <p className="text-gray-600">Define your bot's personality, tone, and behavior</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <textarea
                value={config.botPersona}
                onChange={(e) => setConfig({ ...config, botPersona: e.target.value })}
                placeholder="Example: You are a compassionate medical AI assistant that provides accurate health information while emphasizing the importance of consulting healthcare professionals..."
                className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-sm text-gray-500">
                This defines how your bot will behave and respond to users. Be specific about tone, expertise level, and disclaimers.
              </p>
            </div>
          </div>

          {/* Knowledge Base Section */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
            <div className="flex items-center space-x-3 mb-6">
              <Database className="h-8 w-8 text-green-600" />
              <div>
                <h3 className="text-xl font-bold text-gray-900">Knowledge Base Files</h3>
                <p className="text-gray-600">Upload knowledge base files</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <label className="cursor-pointer">
                  <span className="text-blue-600 hover:text-blue-800 font-medium">
                    Choose Files
                  </span>
                  <input
                    type="file"
                    multiple
                    accept=".txt,.pdf,.doc,.docx"
                    className="hidden"
                    onChange={handleFileUpload}
                  />
                </label>
                <p className="text-sm text-gray-500 mt-2">
                  Upload .txt files containing medical information, policies, or procedures
                </p>
              </div>

              {config.knowledgeBaseFiles && config.knowledgeBaseFiles.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900">Uploaded Files:</h4>
                  {config.knowledgeBaseFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-700">{file}</span>
                      <button
                        onClick={() => setConfig({
                          ...config,
                          knowledgeBaseFiles: (config.knowledgeBaseFiles || []).filter((_, i) => i !== index)
                        })}
                        className="text-red-600 hover:text-red-800"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Curated Websites Section */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
            <div className="flex items-center space-x-3 mb-6">
              <Globe className="h-8 w-8 text-purple-600" />
              <div>
                <h3 className="text-xl font-bold text-gray-900">Curated Search Websites</h3>
                <p className="text-gray-600">Add trusted medical websites for the web search agent to prioritize</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={newSite}
                  onChange={(e) => setNewSite(e.target.value)}
                  placeholder="e.g., mayoclinic.org"
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  onKeyPress={(e) => e.key === 'Enter' && addCuratedSite()}
                />
                <button
                  onClick={addCuratedSite}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg"
                >
                  Add
                </button>
              </div>

              {config.curatedSites && config.curatedSites.length > 0 ? (
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900">Curated Sites:</h4>
                  {config.curatedSites.map((site, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-700">{site}</span>
                      <button
                        onClick={() => removeCuratedSite(site)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No curated sites added yet
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
