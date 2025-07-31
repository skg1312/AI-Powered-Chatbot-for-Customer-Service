import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  ArrowLeft, 
  MessageSquare, 
  Calendar, 
  Clock,
  Plus,
  ExternalLink,
  User,
  LogOut,
  Search,
  Filter,
  Trash2,
  Eye
} from 'lucide-react';

export default function UserDashboard() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState(null);
  const [userSessions, setUserSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSession, setSelectedSession] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    const userData = localStorage.getItem('currentUser');
    if (!userData) {
      router.push('/login');
      return;
    }

    const user = JSON.parse(userData);
    setCurrentUser(user);
    loadUserSessions(user.user_id);
  }, []);

  const loadUserSessions = async (userId) => {
    try {
      const response = await fetch('http://localhost:8000/api/chat/history');
      if (response.ok) {
        const data = await response.json();
        // Filter sessions for current user
        const userSpecificSessions = data.sessions.filter(session => 
          session.user_id === userId
        );
        setUserSessions(userSpecificSessions);
      }
    } catch (error) {
      console.error('Failed to load user sessions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    router.push('/');
  };

  const startNewChat = () => {
    router.push('/playground');
  };

  const continueSession = (sessionId) => {
    router.push(`/playground?session=${sessionId}`);
  };

  const viewSessionDetails = async (session) => {
    setSelectedSession(session);
  };

  const deleteSession = async (sessionId) => {
    if (confirm('Are you sure you want to delete this chat session?')) {
      try {
        const response = await fetch(`http://localhost:8000/api/chat/session/${sessionId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          setUserSessions(prev => prev.filter(s => s.session_id !== sessionId));
          setSelectedSession(null);
        }
      } catch (error) {
        console.error('Failed to delete session:', error);
      }
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const filteredSessions = userSessions.filter(session =>
    session.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    session.session_id.includes(searchTerm)
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-6 w-6 text-gray-600" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-green-600 rounded-lg">
                  <User className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Welcome, {currentUser?.name}</h1>
                  <p className="text-gray-600">Your Medical Chat Assistant Dashboard</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={startNewChat}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <Plus className="h-4 w-4" />
                <span>New Chat</span>
              </button>
              <button
                onClick={handleLogout}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* User Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                <p className="text-2xl font-bold text-gray-900">{userSessions.length}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Sessions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {userSessions.filter(s => s.status === 'active').length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Last Chat</p>
                <p className="text-sm text-gray-900">
                  {userSessions.length > 0 
                    ? formatDate(userSessions[0].created_at)
                    : 'No chats yet'
                  }
                </p>
              </div>
              <Calendar className="h-8 w-8 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sessions List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-900">Your Chat Sessions</h2>
                  <div className="flex items-center space-x-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <input
                        type="text"
                        placeholder="Search sessions..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="divide-y">
                {filteredSessions.length === 0 ? (
                  <div className="p-8 text-center">
                    <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No chat sessions yet</h3>
                    <p className="text-gray-600 mb-4">Start your first conversation with our medical AI assistant</p>
                    <button
                      onClick={startNewChat}
                      className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2 mx-auto transition-colors"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Start New Chat</span>
                    </button>
                  </div>
                ) : (
                  filteredSessions.map((session) => (
                    <div key={session.session_id} className="p-6 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="font-medium text-gray-900">
                              {session.title || `Session ${session.session_id.slice(0, 8)}`}
                            </h3>
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              session.status === 'active' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {session.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">Session ID: {session.session_id}</p>
                          <p className="text-sm text-gray-500">
                            {session.messages?.length || 0} messages • {formatDate(session.created_at)}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => viewSessionDetails(session)}
                            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                            title="View Details"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => continueSession(session.session_id)}
                            className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors"
                            title="Continue Chat"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => deleteSession(session.session_id)}
                            className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete Session"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Session Details Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-6 sticky top-8">
              {selectedSession ? (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Details</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Session ID</label>
                      <p className="text-sm text-gray-900 break-all">{selectedSession.session_id}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Created</label>
                      <p className="text-sm text-gray-900">{formatDate(selectedSession.created_at)}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Status</label>
                      <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                        selectedSession.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {selectedSession.status}
                      </span>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Messages</label>
                      <p className="text-sm text-gray-900">{selectedSession.messages?.length || 0}</p>
                    </div>
                    <div className="pt-4 space-y-2">
                      <button
                        onClick={() => continueSession(selectedSession.session_id)}
                        className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg transition-colors"
                      >
                        Continue Chat
                      </button>
                      <button
                        onClick={() => deleteSession(selectedSession.session_id)}
                        className="w-full bg-red-600 hover:bg-red-700 text-white py-2 rounded-lg transition-colors"
                      >
                        Delete Session
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center">
                  <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Session</h3>
                  <p className="text-gray-600">Click on any session to view details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
