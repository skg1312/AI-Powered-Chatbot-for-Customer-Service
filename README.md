# 🏥 AI-Powered Multi-Agent Medical Chatbot Service

A comprehensive multi-agent medical AI chatbot platform with an advanced admin panel. Built with **FastAPI** backend and **Next.js** frontend, featuring intelligent routing, RAG capabilities, real-time web search, and safety guardrails.

## 🚀 **Core Features**

### **Multi-Agent Architecture**
- **🔀 Router Agent**: Intelligent query classification using Groq Llama 3.3 70B
- **📚 RAG Agent**: Knowledge base search with Pinecone + HuggingFace embeddings
- **🌐 Web Search Agent**: Real-time medical information via Tavily AI
- **📅 Appointment Agent**: Appointment management (placeholder)
- **📍 Logistics Agent**: Clinic information (placeholder)
- **🛡️ Safety Guard**: Content moderation with Llama Guard

### **Admin Panel Features**
- **⚙️ Bot Configuration**: Customize personality and behavior
- **📁 Knowledge Base Management**: Upload and manage medical documents
- **🔗 Curated Sources**: Configure trusted medical websites
- **💬 Live Testing**: Real-time chat playground with agent visibility
- **📊 Multi-Project Support**: Manage multiple chatbot projects

### **Technical Excellence**
- **🔒 Safety First**: Llama Guard content moderation
- **⚡ High Performance**: Groq API for fast responses
- **🎯 Accurate Routing**: Context-aware agent selection
- **📱 Responsive Design**: Modern UI with Tailwind CSS
- **🔧 Easy Configuration**: Environment-based setup

---

## 📋 **Tech Stack**

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.9+ with FastAPI |
| **Frontend** | Next.js 14 with React 18 |
| **Generation LLM** | Groq API (llama-3.3-70b-versatile) |
| **Safety LLM** | Groq API (llama-guard-3-8b) |
| **Vector Database** | Pinecone |
| **Embeddings** | HuggingFace (nomic-embed-text-v1.5) |
| **Web Search** | Tavily AI |
| **Styling** | Tailwind CSS |
| **Icons** | Lucide React |

---

## 🛠️ **Quick Setup**

### **Prerequisites**
- Python 3.9+
- Node.js 18+
- API Keys for: Groq, Pinecone, HuggingFace, Tavily

### **1. Clone Repository**
```bash
git clone https://github.com/your-username/AI-Powered-Chatbot-for-Customer-Service.git
cd AI-Powered-Chatbot-for-Customer-Service
```

### **2. Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### **3. Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### **4. Start Services**
```bash
# Terminal 1: Backend API
cd backend
python -m app.main

# Terminal 2: Frontend (in another terminal)
cd frontend
npm run dev
```

### **5. Access Application**
- **Admin Panel**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ⚙️ **Configuration**

### **Environment Variables (.env)**
```env
# Groq API
GROQ_API_KEY="gsk_your_groq_api_key_here"

# Pinecone Vector Database
PINECONE_API_KEY="your_pinecone_api_key_here"
PINECONE_ENVIRONMENT="your_pinecone_environment"
PINECONE_INDEX_NAME="medical-chatbot-index"

# HuggingFace
HF_TOKEN="hf_your_huggingface_token_here"

# Tavily AI Search
TAVILY_API_KEY="tvly_your_tavily_api_key_here"

# Application Settings
ENVIRONMENT="development"
DEBUG=True
API_HOST="0.0.0.0"
API_PORT=8000
```

### **Getting API Keys**

1. **Groq API** (Free tier available)
   - Visit: https://console.groq.com
   - Create account and get API key
   - Used for: LLM generation and safety checking

2. **Pinecone** (Free tier: 1 index, 100MB)
   - Visit: https://www.pinecone.io
   - Create account and get API key
   - Used for: Vector database storage

3. **HuggingFace** (Free)
   - Visit: https://huggingface.co
   - Create account and get access token
   - Used for: Text embeddings

4. **Tavily AI** (Free tier available)
   - Visit: https://tavily.com
   - Create account and get API key
   - Used for: Real-time web search

---

## 🏗️ **Project Structure**

```
my-medical-bot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── agents/
│   │   │   ├── router.py        # Query routing logic
│   │   │   ├── rag_agent.py     # Knowledge base search
│   │   │   └── web_search_agent.py # Web search functionality
│   │   └── core/
│   │       └── config.py        # Configuration management
│   ├── .env.example            # Environment template
│   └── requirements.txt        # Python dependencies
└── frontend/
    ├── pages/
    │   ├── index.js             # Project dashboard
    │   └── projects/
    │       └── [id].js          # Project management page
    ├── components/
    │   ├── AdminControls.js     # Configuration panel
    │   └── ChatPlayground.js    # Live chat testing
    ├── package.json            # Node.js dependencies
    └── tailwind.config.js      # Styling configuration
```

---

## 💡 **How It Works**

### **1. Query Processing Flow**
```
User Input → Router Agent → Selected Agent → Context Retrieval → Response Generation → Safety Check → Final Response
```

### **2. Agent Selection Logic**
- **RAG Agent**: Internal policies, procedures, medical protocols
- **Web Search**: Recent news, public health updates, real-time info
- **Appointment Agent**: Booking, canceling, scheduling queries
- **Logistics Agent**: Hours, location, contact information

### **3. Safety Pipeline**
- All responses processed through Llama Guard
- Content moderation for medical safety
- Automatic fallback for unsafe content

---

## 🎯 **Usage Guide**

### **Creating a New Project**
1. Open admin panel at http://localhost:3000
2. Click "Create New Project"
3. Configure bot persona and settings
4. Upload knowledge base files
5. Test in live playground

### **Configuring Bot Persona**
```
Example Persona:
"You are a compassionate medical AI assistant specializing in general health information. You provide accurate, evidence-based responses while emphasizing the importance of consulting healthcare professionals for personalized advice. Maintain a professional yet caring tone, and always include appropriate medical disclaimers."
```

### **Adding Knowledge Base**
- Upload .txt files with medical information
- Files are automatically processed and indexed
- RAG agent uses this for internal queries

### **Setting Curated Sources**
Add trusted medical websites:
- who.int
- cdc.gov
- mayoclinic.org
- webmd.com
- healthline.com

---

## 🧪 **Testing Examples**

### **RAG Agent Queries**
```
"What is our policy on patient confidentiality?"
"What are the treatment protocols for hypertension?"
"How do we handle emergency situations?"
```

### **Web Search Queries**
```
"What's the latest COVID-19 guidance?"
"Recent breakthrough in cancer treatment"
"Current flu vaccination recommendations"
```

### **Appointment Queries**
```
"I need to book an appointment"
"Cancel my appointment for tomorrow"
"What appointments do I have next week?"
```

### **Logistics Queries**
```
"What are your clinic hours?"
"Where is the clinic located?"
"How can I contact the clinic?"
```

---

## 🚀 **API Endpoints**

### **Chat Endpoint**
```http
POST /api/chat/{project_id}
Content-Type: application/json

{
  "message": "What are the symptoms of diabetes?",
  "project_id": "project-1"
}
```

### **Configuration Endpoints**
```http
# Get project config
GET /api/projects/{project_id}/config

# Update project config
POST /api/projects/{project_id}/config

# Upload knowledge base
POST /api/projects/{project_id}/upload-knowledge
```

### **Health Check**
```http
GET /health
```

---

## 🔧 **Development**

### **Running in Development Mode**
```bash
# Backend with auto-reload
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend with hot reload
cd frontend
npm run dev
```

### **Adding New Agents**
1. Create agent file in `backend/app/agents/`
2. Implement required methods
3. Update router logic
4. Add to main application

### **Customizing Frontend**
- Modify components in `frontend/components/`
- Update styling in `tailwind.config.js`
- Add new pages in `frontend/pages/`

---

## 📈 **Production Deployment**

### **Backend Deployment**
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Frontend Deployment**
```bash
# Build for production
npm run build

# Start production server
npm start
```

### **Environment Considerations**
- Use production API keys
- Set `DEBUG=False`
- Configure proper CORS origins
- Set up monitoring and logging

---

## 🛡️ **Security Features**

- **Content Moderation**: Llama Guard safety checking
- **API Rate Limiting**: Configurable request limits
- **Input Validation**: Pydantic models for data validation
- **CORS Protection**: Configured for frontend domain
- **Environment Isolation**: Separate configs for dev/prod

---

## 📚 **Documentation**

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Health Status**: http://localhost:8000/health

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 🆘 **Support**

- **Issues**: GitHub Issues
- **Documentation**: Check `/docs` folder
- **API Reference**: http://localhost:8000/docs

---

## 🎉 **What's Next?**

- [ ] Implement appointment scheduling system
- [ ] Add user authentication
- [ ] Create analytics dashboard
- [ ] Add voice interface
- [ ] Implement conversation memory
- [ ] Add multi-language support

**Ready to revolutionize medical AI assistance!** 🏥✨
