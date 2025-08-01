// API Configuration for frontend
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'https://medical-ai-chatbot-backend.onrender.com',
  ENDPOINTS: {
    // Auth endpoints
    REGISTER: '/api/users/register',
    LOGIN: '/api/users/login',
    USERS: '/api/users',
    
    // Project endpoints
    PROJECT_CONFIG: '/api/projects/main/config',
    PROJECT_STATS: '/api/projects/main/stats',
    
    // Chat endpoints
    CHAT: '/api/chat',
    CHAT_HISTORY: '/api/projects/main/chat-history',
    CHAT_SESSION: '/api/chat/session',
    
    // Health check
    HEALTH: '/health'
  }
};

// Helper function to build full URL
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Helper function for API calls with error handling
export const apiCall = async (endpoint, options = {}) => {
  const url = buildApiUrl(endpoint);
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
};

export default API_CONFIG;
