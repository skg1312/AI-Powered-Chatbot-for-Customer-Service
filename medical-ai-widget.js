/**
 * Medical AI Chat Widget
 * Embeddable chat widget for any website
 * Version: 1.0.0
 */
(function() {
  'use strict';

  // Widget configuration (can be overridden)
  const defaultConfig = {
    apiUrl: window.location.hostname === 'https://medical-ai-chatbot-backend.onrender.com',
    theme: 'blue',
    position: 'bottom-right',
    greeting: 'Hello! I\'m your Medical AI Assistant. How can I help you today?',
    title: 'Medical AI Assistant',
    placeholder: 'Ask me about your health...',
    width: '350px',
    height: '500px',
    // Add test mode for local development
    testMode: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:'
  };

  // Merge with user config if provided
  const config = window.MedicalAIWidgetConfig ? 
    {...defaultConfig, ...window.MedicalAIWidgetConfig} : 
    defaultConfig;

  // Widget state
  let isOpen = false;
  let isMinimized = false;
  let isLoading = false;
  let messages = [
    {
      role: 'assistant',
      content: config.greeting,
      timestamp: new Date().toISOString()
    }
  ];
  let sessionId = 'widget_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  let userId = 'anonymous'; // Use consistent anonymous user tracking

  // Create widget container
  const widgetContainer = document.createElement('div');
  widgetContainer.id = 'medical-ai-chat-widget';
  
  // Position styles
  const positions = {
    'bottom-right': 'bottom: 20px; right: 20px;',
    'bottom-left': 'bottom: 20px; left: 20px;',
    'top-right': 'top: 20px; right: 20px;',
    'top-left': 'top: 20px; left: 20px;'
  };

  widgetContainer.style.cssText = `
    position: fixed;
    ${positions[config.position] || positions['bottom-right']}
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `;

  // Add widget to page
  document.body.appendChild(widgetContainer);

  // Styles
  const styles = `
    #medical-ai-chat-widget .widget-button {
      background: ${config.theme === 'green' ? '#059669' : config.theme === 'purple' ? '#7c3aed' : config.theme === 'dark' ? '#1f2937' : '#2563eb'};
      color: white;
      border: none;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
    }
    #medical-ai-chat-widget .widget-button:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
    #medical-ai-chat-widget .widget-chat {
      background: white;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.12);
      width: ${config.width};
      height: ${config.height};
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border: 1px solid #e5e7eb;
    }
    #medical-ai-chat-widget .widget-chat.minimized {
      height: 60px;
    }
    #medical-ai-chat-widget .widget-header {
      background: ${config.theme === 'green' ? '#059669' : config.theme === 'purple' ? '#7c3aed' : config.theme === 'dark' ? '#1f2937' : '#2563eb'};
      color: white;
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
    }
    #medical-ai-chat-widget .widget-body {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    #medical-ai-chat-widget .widget-messages {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      background: #fafafa;
    }
    #medical-ai-chat-widget .widget-input {
      border-top: 1px solid #e5e7eb;
      padding: 16px;
      background: white;
      flex-shrink: 0;
    }
    #medical-ai-chat-widget .widget-input-container {
      display: flex;
      gap: 8px;
      align-items: flex-end;
    }
    #medical-ai-chat-widget .widget-textarea {
      flex: 1;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      padding: 8px 12px;
      resize: none;
      font-size: 14px;
      outline: none;
      min-height: 36px;
      max-height: 100px;
    }
    #medical-ai-chat-widget .widget-textarea:focus {
      border-color: ${config.theme === 'green' ? '#059669' : config.theme === 'purple' ? '#7c3aed' : config.theme === 'dark' ? '#1f2937' : '#2563eb'};
      box-shadow: 0 0 0 3px ${config.theme === 'green' ? 'rgba(5, 150, 105, 0.1)' : config.theme === 'purple' ? 'rgba(124, 58, 237, 0.1)' : config.theme === 'dark' ? 'rgba(31, 41, 55, 0.1)' : 'rgba(37, 99, 235, 0.1)'};
    }
    #medical-ai-chat-widget .widget-send {
      background: ${config.theme === 'green' ? '#059669' : config.theme === 'purple' ? '#7c3aed' : config.theme === 'dark' ? '#1f2937' : '#2563eb'};
      color: white;
      border: none;
      border-radius: 8px;
      padding: 8px 16px;
      cursor: pointer;
      font-size: 14px;
      height: 36px;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: background-color 0.2s;
    }
    #medical-ai-chat-widget .widget-send:hover:not(:disabled) {
      background: ${config.theme === 'green' ? '#047857' : config.theme === 'purple' ? '#6d28d9' : config.theme === 'dark' ? '#111827' : '#1d4ed8'};
    }
    #medical-ai-chat-widget .widget-send:disabled {
      background: #9ca3af;
      cursor: not-allowed;
    }
    #medical-ai-chat-widget .message {
      margin-bottom: 16px;
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }
    #medical-ai-chat-widget .message.user {
      flex-direction: row-reverse;
    }
    #medical-ai-chat-widget .message-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      flex-shrink: 0;
    }
    #medical-ai-chat-widget .message.user .message-avatar {
      background: ${config.theme === 'green' ? '#059669' : config.theme === 'purple' ? '#7c3aed' : config.theme === 'dark' ? '#1f2937' : '#2563eb'};
      color: white;
    }
    #medical-ai-chat-widget .message.assistant .message-avatar {
      background: #f3f4f6;
      color: #6b7280;
    }
    #medical-ai-chat-widget .message-content {
      max-width: 80%;
      padding: 12px 16px;
      border-radius: 18px;
      font-size: 14px;
      line-height: 1.4;
    }
    #medical-ai-chat-widget .message.user .message-content {
      background: ${config.theme === 'green' ? '#059669' : config.theme === 'purple' ? '#7c3aed' : config.theme === 'dark' ? '#1f2937' : '#2563eb'};
      color: white;
    }
    #medical-ai-chat-widget .message.assistant .message-content {
      background: white;
      color: #1f2937;
      border: 1px solid #e5e7eb;
    }
    #medical-ai-chat-widget .message-content h1, 
    #medical-ai-chat-widget .message-content h2, 
    #medical-ai-chat-widget .message-content h3 {
      margin: 8px 0 4px 0;
      font-weight: 600;
      line-height: 1.2;
    }
    #medical-ai-chat-widget .message-content h1 { font-size: 18px; }
    #medical-ai-chat-widget .message-content h2 { font-size: 16px; }
    #medical-ai-chat-widget .message-content h3 { font-size: 14px; }
    #medical-ai-chat-widget .message-content p {
      margin: 4px 0;
      line-height: 1.5;
    }
    #medical-ai-chat-widget .message-content ul, 
    #medical-ai-chat-widget .message-content ol {
      margin: 8px 0;
      padding-left: 20px;
    }
    #medical-ai-chat-widget .message-content li {
      margin: 2px 0;
      line-height: 1.4;
    }
    #medical-ai-chat-widget .message-content strong {
      font-weight: 600;
      color: #111827;
    }
    #medical-ai-chat-widget .message-content em {
      font-style: italic;
      color: #374151;
    }
    #medical-ai-chat-widget .message-content code {
      background: #f3f4f6;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      color: #dc2626;
    }
    #medical-ai-chat-widget .message-content pre {
      background: #1f2937;
      color: #f9fafb;
      padding: 12px;
      border-radius: 8px;
      margin: 8px 0;
      overflow-x: auto;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      line-height: 1.4;
    }
    #medical-ai-chat-widget .message-content pre code {
      background: none;
      padding: 0;
      color: inherit;
    }
    #medical-ai-chat-widget .message-time {
      font-size: 11px;
      opacity: 0.7;
      margin-top: 4px;
    }
    #medical-ai-chat-widget .widget-controls {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    #medical-ai-chat-widget .widget-control-btn {
      background: none;
      border: none;
      color: white;
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      opacity: 0.8;
      transition: opacity 0.2s;
    }
    #medical-ai-chat-widget .widget-control-btn:hover {
      opacity: 1;
      background: rgba(255,255,255,0.1);
    }
    #medical-ai-chat-widget .loading-message {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 18px;
      font-size: 14px;
      color: #6b7280;
    }
    #medical-ai-chat-widget .loading-dots {
      display: flex;
      gap: 4px;
    }
    #medical-ai-chat-widget .loading-dot {
      width: 6px;
      height: 6px;
      background: #9ca3af;
      border-radius: 50%;
      animation: bounce 1.4s ease-in-out infinite both;
    }
    #medical-ai-chat-widget .loading-dot:nth-child(1) { animation-delay: -0.32s; }
    #medical-ai-chat-widget .loading-dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }
    #medical-ai-chat-widget .widget-footer {
      padding: 8px 16px;
      background: #f9fafb;
      border-top: 1px solid #e5e7eb;
      text-align: center;
    }
    #medical-ai-chat-widget .widget-footer-text {
      font-size: 11px;
      color: #6b7280;
    }
    @media (max-width: 480px) {
      #medical-ai-chat-widget .widget-chat {
        width: calc(100vw - 40px);
        height: calc(100vh - 40px);
        max-width: 400px;
        max-height: 600px;
      }
    }
  `;

  // Add styles to page
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);

  // Utility functions
  function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  function scrollToBottom() {
    setTimeout(() => {
      const messagesEl = widgetContainer.querySelector('.widget-messages');
      if (messagesEl) {
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }
    }, 100);
  }

  // Markdown parsing function
  function parseMarkdown(text) {
    if (!text) return '';
    
    // Convert markdown to HTML
    let html = text
      // Headers
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.*?)__/g, '<strong>$1</strong>')
      
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/_(.*?)_/g, '<em>$1</em>')
      
      // Code blocks
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      
      // Lists
      .replace(/^\* (.*$)/gim, '<li>$1</li>')
      .replace(/^- (.*$)/gim, '<li>$1</li>')
      .replace(/^\+ (.*$)/gim, '<li>$1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
      
      // Line breaks
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');
    
    // Wrap lists in ul tags
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Wrap in paragraphs if not already wrapped
    if (!html.includes('<h1>') && !html.includes('<h2>') && !html.includes('<h3>') && !html.includes('<ul>') && !html.includes('<pre>')) {
      html = '<p>' + html + '</p>';
    }
    
    return html;
  }

  // Render functions
  function renderButton() {
    return `
      <button class="widget-button" onclick="MedicalAIWidget.open()">
        💬
      </button>
    `;
  }

  function renderChat() {
    const messagesHtml = messages.map(msg => `
      <div class="message ${msg.role}">
        <div class="message-avatar">
          ${msg.role === 'user' ? '👤' : '🤖'}
        </div>
        <div class="message-content">
          ${msg.role === 'assistant' ? parseMarkdown(msg.content) : msg.content}
          <div class="message-time">
            ${formatTime(msg.timestamp)}
          </div>
        </div>
      </div>
    `).join('');

    const loadingHtml = isLoading ? `
      <div class="message assistant">
        <div class="message-avatar">🤖</div>
        <div class="loading-message">
          <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
          </div>
          Thinking...
        </div>
      </div>
    ` : '';

    return `
      <div class="widget-chat ${isMinimized ? 'minimized' : ''}">
        <div class="widget-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 18px;">🏥</span>
            <span style="font-weight: 600;">${config.title}</span>
          </div>
          <div class="widget-controls">
            <button class="widget-control-btn" onclick="MedicalAIWidget.minimize()" title="${isMinimized ? 'Expand' : 'Minimize'}">
              ${isMinimized ? '⬆️' : '⬇️'}
            </button>
            <button class="widget-control-btn" onclick="MedicalAIWidget.reset()" title="Reset Chat">
              🔄
            </button>
            <button class="widget-control-btn" onclick="MedicalAIWidget.close()" title="Close">
              ✖️
            </button>
          </div>
        </div>
        ${!isMinimized ? `
          <div class="widget-body">
            <div class="widget-messages">
              ${messagesHtml}
              ${loadingHtml}
            </div>
            <div class="widget-input">
              <div class="widget-input-container">
                <textarea 
                  class="widget-textarea" 
                  id="widget-input-${sessionId}" 
                  placeholder="${config.placeholder}"
                  rows="1"
                  onkeypress="MedicalAIWidget.handleKeyPress(event)"
                  oninput="MedicalAIWidget.autoResize(this)"
                ></textarea>
                <button 
                  class="widget-send" 
                  onclick="MedicalAIWidget.sendMessage()" 
                  id="send-button-${sessionId}"
                  ${isLoading ? 'disabled' : ''}
                >
                  📤
                </button>
              </div>
            </div>
          </div>
          <div class="widget-footer">
            <div class="widget-footer-text">
              Press Enter to send • Powered by Medical AI
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }

  function render() {
    widgetContainer.innerHTML = isOpen ? renderChat() : renderButton();
    if (isOpen && !isMinimized) {
      scrollToBottom();
    }
  }

  // API functions
  async function sendMessage() {
    const input = document.getElementById(`widget-input-${sessionId}`);
    if (!input) return;

    const message = input.value.trim();
    if (!message || isLoading) return;

    // Add user message
    messages.push({
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    });

    input.value = '';
    input.style.height = 'auto';
    isLoading = true;
    render();

    try {
      console.log('Widget: Sending request to:', `${config.apiUrl}/api/chat/widget-default`);
      const response = await fetch(`${config.apiUrl}/api/chat/widget-default`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          conversation_id: sessionId,
          user_id: userId,
          context: { source: 'embed-widget', widget_session: true }
        })
      });

      console.log('Widget: Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Widget: Received response:', data);
      messages.push({
        role: 'assistant',
        content: data.response || 'I apologize, but I couldn\'t process your request properly.',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Widget API Error:', error);
      console.error('Widget: Full error details:', {
        message: error.message,
        stack: error.stack,
        apiUrl: config.apiUrl
      });
      messages.push({
        role: 'assistant',
        content: `I apologize, but I'm having trouble connecting right now. Error: ${error.message}. Please try again later or consult a healthcare professional for urgent medical concerns.`,
        timestamp: new Date().toISOString()
      });
    }

    isLoading = false;
    render();
  }

  // Global widget API
  window.MedicalAIWidget = {
    open: function() {
      isOpen = true;
      isMinimized = false;
      render();
    },
    close: function() {
      isOpen = false;
      render();
    },
    minimize: function() {
      isMinimized = !isMinimized;
      render();
    },
    reset: function() {
      messages = [
        {
          role: 'assistant',
          content: config.greeting,
          timestamp: new Date().toISOString()
        }
      ];
      sessionId = 'widget_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      render();
    },
    sendMessage: sendMessage,
    handleKeyPress: function(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    },
    autoResize: function(textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    },
    configure: function(newConfig) {
      Object.assign(config, newConfig);
      render();
    }
  };

  // Initial render
  render();

  // Auto-open after delay (optional)
  if (config.autoOpen) {
    setTimeout(() => {
      window.MedicalAIWidget.open();
    }, config.autoOpenDelay || 3000);
  }

})();
