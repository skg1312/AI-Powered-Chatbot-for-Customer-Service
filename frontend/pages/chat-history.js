import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  ArrowLeft, 
  MessageCircle, 
  User, 
  Bot, 
  Clock,
  Trash2,
  Search,
  Filter,
  Calendar,
  Play
} from 'lucide-react';

export default function ChatHistory() {
  const router = useRouter();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [userFilter, setUserFilter] = useState('');

  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/projects/main/chat-history');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this chat session?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/projects/main/chat-history/${sessionId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setSessions(sessions.filter(session => session.session_id !== sessionId));
        if (selectedSession?.session_id === sessionId) {
          setSelectedSession(null);
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const continueChat = (session) => {
    // Store the session data in localStorage to continue the conversation
    localStorage.setItem('continueSession', JSON.stringify({
      sessionId: session.session_id,
      userId: session.user_id,
      messages: session.messages
    }));
    
    // Navigate to playground with continue parameter
    router.push('/playground?continue=true');
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const filteredSessions = sessions.filter(session => {
    const matchesSearch = session.messages.some(msg => 
      msg.content.toLowerCase().includes(searchTerm.toLowerCase())
    );
    const matchesUser = !userFilter || session.user_id?.includes(userFilter);
    return matchesSearch && matchesUser;
  });

  const getSessionPreview = (session) => {
    const firstUserMessage = session.messages.find(msg => msg.role === 'user');
    return firstUserMessage ? firstUserMessage.content.substring(0, 100) + '...' : 'No messages';
  };

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
                <div className="p-3 bg-blue-600 rounded-lg">
                  <MessageCircle className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Chat History</h1>
                  <p className="text-gray-600">View and manage conversation sessions</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sessions List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Chat Sessions</h2>
                
                {/* Search and Filter */}
                <div className="space-y-3">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <input
                      type="text"
                      placeholder="Search messages..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div className="relative">
                    <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <input
                      type="text"
                      placeholder="Filter by user ID..."
                      value={userFilter}
                      onChange={(e) => setUserFilter(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {loading ? (
                  <div className="p-6 text-center text-gray-500">Loading sessions...</div>
                ) : filteredSessions.length === 0 ? (
                  <div className="p-6 text-center text-gray-500">No chat sessions found</div>
                ) : (
                  filteredSessions.map((session) => (
                    <div
                      key={session.session_id}
                      className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors ${
                        selectedSession?.session_id === session.session_id ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                      onClick={() => setSelectedSession(session)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <User className="h-4 w-4 text-gray-400" />
                            <span className="text-sm text-gray-600">
                              {session.user_id || 'Anonymous'}
                            </span>
                          </div>
                          <p className="text-sm text-gray-800 mb-2">
                            {getSessionPreview(session)}
                          </p>
                          <div className="flex items-center space-x-2 text-xs text-gray-500">
                            <Clock className="h-3 w-3" />
                            <span>{formatTimestamp(session.updated_at)}</span>
                            <span>•</span>
                            <span>{session.messages.length} messages</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              continueChat(session);
                            }}
                            className="p-1 hover:bg-green-100 rounded transition-colors"
                            title="Continue this conversation"
                          >
                            <Play className="h-4 w-4 text-green-600" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteSession(session.session_id);
                            }}
                            className="p-1 hover:bg-red-100 rounded transition-colors"
                            title="Delete this session"
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              {selectedSession ? (
                <>
                  <div className="p-6 border-b">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          Chat Session
                        </h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                          <span>User: {selectedSession.user_id || 'Anonymous'}</span>
                          <span>•</span>
                          <span>Started: {formatTimestamp(selectedSession.created_at)}</span>
                          <span>•</span>
                          <span>{selectedSession.messages.length} messages</span>
                        </div>
                      </div>
                      <button
                        onClick={() => continueChat(selectedSession)}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                      >
                        <Play className="h-4 w-4" />
                        <span>Continue Chat</span>
                      </button>
                    </div>
                  </div>

                  <div className="p-6 max-h-96 overflow-y-auto">
                    <div className="space-y-4">
                      {selectedSession.messages.map((message, index) => (
                        <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-2xl p-3 rounded-lg ${
                            message.role === 'user' 
                              ? 'bg-blue-600 text-white' 
                              : 'bg-gray-100 text-gray-900'
                          }`}>
                            <div className="flex items-center space-x-2 mb-1">
                              {message.role === 'user' ? (
                                <User className="h-4 w-4" />
                              ) : (
                                <Bot className="h-4 w-4" />
                              )}
                              <span className="text-sm font-medium">
                                {message.role === 'user' ? 'User' : 'Assistant'}
                              </span>
                              {message.agent_used && (
                                <span className="text-xs opacity-75">
                                  via {message.agent_used}
                                </span>
                              )}
                            </div>
                            <p className="whitespace-pre-wrap">{message.content}</p>
                            <div className="text-xs opacity-75 mt-2">
                              {formatTimestamp(message.timestamp)}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-12 text-center text-gray-500">
                  <MessageCircle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Session Selected</h3>
                  <p>Select a chat session from the list to view the conversation</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
