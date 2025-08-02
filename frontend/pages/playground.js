import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  ArrowLeft, 
  Send, 
  Bot, 
  User, 
  MessageCircle,
  Loader2,
  Settings,
  Trash2,
  Clock,
  Hash,
  Home
} from 'lucide-react';

export default function Playground() {
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState({
    temperature: 0.7,
    maxTokens: 1000,
    systemPrompt: 'You are a helpful medical AI assistant.'
  });
  const [showSettings, setShowSettings] = useState(false);
  const [userId, setUserId] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const [conversationId, setConversationId] = useState('');
  const [isContinuedSession, setIsContinuedSession] = useState(false);
  const [sessionInfo, setSessionInfo] = useState(null);
  const messagesEndRef = useRef(null);

  // Initialize session data
  useEffect(() => {
    // Check if user is logged in (optional for playground)
    const userData = localStorage.getItem('currentUser');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        setCurrentUser(user);
        setUserId(user.user_id);
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    } else {
      // Anonymous user - generate a temporary user ID
      const tempUserId = 'anonymous_' + Math.random().toString(36).substr(2, 9);
      setUserId(tempUserId);
    }

    // Check for session continuation from URL params or localStorage
    const { session: sessionParam, continue: continueParam } = router.query;
    
    if (sessionParam) {
      // Load specific session by ID
      loadSessionById(sessionParam);
    } else if (continueParam === 'true') {
      // Load session from localStorage (continued from chat history)
      loadContinuedSession();
    } else {
      // Create new session
      setConversationId('conversation_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now());
    }
  }, [router.query]);

  const loadSessionById = async (sessionId) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://medical-ai-chatbot-backend.onrender.com';
      const response = await fetch(`${API_URL}/api/chat/session/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        const session = data.session;
        
        setConversationId(sessionId);
        setIsContinuedSession(true);
        setSessionInfo(session);
        
        // Convert previous messages to the format expected by the UI
        if (session.messages && session.messages.length > 0) {
          const formattedMessages = session.messages.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            agent: msg.agent_used
          }));
          setMessages(formattedMessages);
        }
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const loadContinuedSession = () => {
    try {
      const sessionData = localStorage.getItem('continueSession');
      if (sessionData) {
        const { sessionId, userId: sessionUserId, messages: sessionMessages } = JSON.parse(sessionData);
        
        setConversationId(sessionId);
        setIsContinuedSession(true);
        
        // Use the session's user ID if available
        if (sessionUserId) {
          setUserId(sessionUserId);
        }
        
        // Convert previous messages to the format expected by the UI
        if (sessionMessages && sessionMessages.length > 0) {
          const formattedMessages = sessionMessages.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            agent: msg.agent_used
          }));
          setMessages(formattedMessages);
        }
        
        // Clear the localStorage after loading
        localStorage.removeItem('continueSession');
      }
    } catch (error) {
      console.error('Failed to load continued session:', error);
    }
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInput('');

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://medical-ai-chatbot-backend.onrender.com';
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          user_id: userId,
          conversation_id: conversationId
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          agent: data.agent_used
        };

        setMessages(prev => [...prev, assistantMessage]);
        
        // Update conversation ID if it was generated by the backend
        if (data.conversation_id && data.conversation_id !== conversationId) {
          setConversationId(data.conversation_id);
        }
        
        setIsContinuedSession(true);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setConversationId('conversation_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now());
    setIsContinuedSession(false);
    setSessionInfo(null);
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push(currentUser ? '/user-dashboard' : '/')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title={currentUser ? "Back to Dashboard" : "Back to Home"}
              >
                <Home className="h-6 w-6 text-gray-600" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-green-600 rounded-lg">
                  <MessageCircle className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Medical AI Chat Playground</h1>
                  <p className="text-gray-600">
                    {currentUser ? `Welcome, ${currentUser.name}!` : 'Welcome! Start chatting with our AI assistant'}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {!currentUser && (
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => router.push('/register')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                  >
                    Register
                  </button>
                  <button
                    onClick={() => router.push('/login')}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                  >
                    Login
                  </button>
                </div>
              )}
              {sessionInfo && (
                <div className="text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4" />
                    <span>Started: {new Date(sessionInfo.created_at).toLocaleString()}</span>
                  </div>
                </div>
              )}
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Settings"
              >
                <Settings className="h-6 w-6 text-gray-600" />
              </button>
              <button
                onClick={clearChat}
                className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                title="Clear Chat"
              >
                <Trash2 className="h-6 w-6 text-red-600" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Session Info */}
        {isContinuedSession && sessionInfo && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Hash className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Continuing Session</span>
            </div>
            <p className="text-sm text-blue-700">
              Session ID: {conversationId}
            </p>
            <p className="text-sm text-blue-700">
              Messages: {messages.length} • 
              Started: {new Date(sessionInfo.created_at).toLocaleString()}
            </p>
          </div>
        )}

        {/* Settings Panel */}
        {showSettings && (
          <div className="mb-6 p-6 bg-white rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Chat Settings</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperature: {settings.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => setSettings(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Tokens: {settings.maxTokens}
                </label>
                <input
                  type="range"
                  min="100"
                  max="2000"
                  step="100"
                  value={settings.maxTokens}
                  onChange={(e) => setSettings(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        )}

        {/* Chat Messages */}
        <div className="bg-white rounded-lg shadow-sm border mb-6">
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Bot className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">Welcome to Medical AI Assistant</p>
                <p className="text-sm">Ask me anything about health and medical topics.</p>
                {currentUser ? (
                  <p className="text-sm mt-2 text-green-600">Hello, {currentUser.name}! How can I help you today?</p>
                ) : (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-800">
                      💡 <strong>Tip:</strong> Register for an account to save your conversations and access your chat history!
                    </p>
                  </div>
                )}
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex items-start space-x-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="p-2 bg-green-100 rounded-full">
                      <Bot className="h-5 w-5 text-green-600" />
                    </div>
                  )}
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-green-600 text-white'
                        : message.isError
                        ? 'bg-red-100 text-red-800 border border-red-200'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-xs opacity-70">
                        {formatTime(message.timestamp)}
                      </p>
                      {message.agent && (
                        <span className="text-xs opacity-70">
                          {message.agent}
                        </span>
                      )}
                    </div>
                  </div>
                  {message.role === 'user' && (
                    <div className="p-2 bg-green-100 rounded-full">
                      <User className="h-5 w-5 text-green-600" />
                    </div>
                  )}
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-green-100 rounded-full">
                  <Bot className="h-5 w-5 text-green-600" />
                </div>
                <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Message Input */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex space-x-4">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your health concerns..."
              className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
              rows="3"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg transition-colors flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span>Send</span>
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Press Enter to send • Shift+Enter for new line
            {conversationId && (
              <span className="ml-2">• Session: {conversationId.slice(-8)}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
