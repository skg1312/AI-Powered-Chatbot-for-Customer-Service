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
  Trash2
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
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat/main', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          conversation_id: 'playground-' + Date.now()
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const botMessage = { 
          role: 'assistant', 
          content: data.response,
          agent: data.agent_used,
          timestamp: new Date() 
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error processing your request.',
          timestamp: new Date(),
          error: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I could not connect to the chat service.',
        timestamp: new Date(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
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
              <div className="p-2 bg-blue-600 rounded-lg">
                <MessageCircle className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Chat Playground</h1>
                <p className="text-sm text-gray-500">Test your medical AI assistant</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
              >
                <Settings className="h-6 w-6" />
              </button>
              <button
                onClick={clearChat}
                className="p-2 text-gray-600 hover:text-red-600 rounded-lg hover:bg-gray-100"
              >
                <Trash2 className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-white border-b shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Temperature
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => setSettings({...settings, temperature: parseFloat(e.target.value)})}
                  className="w-full"
                />
                <div className="text-xs text-gray-500">{settings.temperature}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Tokens
                </label>
                <input
                  type="number"
                  min="100"
                  max="2000"
                  value={settings.maxTokens}
                  onChange={(e) => setSettings({...settings, maxTokens: parseInt(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  System Prompt
                </label>
                <input
                  type="text"
                  value={settings.systemPrompt}
                  onChange={(e) => setSettings({...settings, systemPrompt: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Bot className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Start a conversation</h3>
              <p className="text-gray-500">Ask any medical question to test your AI assistant</p>
              <div className="mt-6 space-y-2">
                <div className="text-sm text-gray-400">Try asking:</div>
                <div className="flex flex-wrap justify-center gap-2">
                  {[
                    "What are the symptoms of diabetes?",
                    "How to treat a minor burn?",
                    "When should I see a doctor?",
                    "Book an appointment for next week"
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => setInput(suggestion)}
                      className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-600"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.error
                      ? 'bg-red-50 text-red-900 border border-red-200'
                      : 'bg-white text-gray-900 shadow-md border'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-full ${
                      message.role === 'user' 
                        ? 'bg-blue-500' 
                        : message.error
                        ? 'bg-red-200'
                        : 'bg-gray-100'
                    }`}>
                      {message.role === 'user' ? (
                        <User className="h-4 w-4 text-white" />
                      ) : (
                        <Bot className={`h-4 w-4 ${message.error ? 'text-red-600' : 'text-gray-600'}`} />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium">
                          {message.role === 'user' ? 'You' : 'Medical AI'}
                        </span>
                        {message.agent && (
                          <span className="text-xs px-2 py-1 bg-gray-200 text-gray-600 rounded-full">
                            {message.agent}
                          </span>
                        )}
                        <span className="text-xs opacity-70">
                          {formatTime(message.timestamp)}
                        </span>
                      </div>
                      <div className="prose prose-sm max-w-none">
                        {message.content}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 shadow-md border rounded-lg p-4 max-w-3xl">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-full bg-gray-100">
                    <Bot className="h-4 w-4 text-gray-600" />
                  </div>
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-gray-500">AI is thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="border-t bg-white p-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a medical question..."
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
