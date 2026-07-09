# AI-First CRM HCP Module

An AI-first Customer Relationship Management (CRM) system designed for life sciences field representatives to manage interactions with Healthcare Professionals (HCPs). Built with LangGraph, Groq LLM, FastAPI, React, and MySQL.

## 🎯 Overview

This application provides field representatives with two flexible ways to log HCP interactions:
1. **Structured Form** - Traditional form-based data entry
2. **AI Chat Interface** - Conversational logging powered by LangGraph agent

The AI agent uses the `gemma2-9b-it` model via Groq for natural language processing, entity extraction, summarization, and intelligent routing of user requests to specialized tools.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Redux Store  │  InteractionForm  │  ChatInterface   │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────┐
│                     Backend (FastAPI)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Routers: HCPs │ Interactions │ Chat │ AI │ Accounts │  │
│  └───────────────────────────────────────────────────────┘  │
│                             │                                │
│  ┌──────────────────────────▼────────────────────────────┐  │
│  │              LangGraph AI Agent                       │  │
│  │  ┌─────────────┬──────────────┬────────────────────┐  │  │
│  │  │ Log         │ Edit         │ Search HCP         │  │  │
│  │  │ Interaction │ Interaction  │                    │  │  │
│  │  ├─────────────┼──────────────┼────────────────────┤  │  │
│  │  │ Create      │ Get          │ Get Interaction    │  │  │
│  │  │ Account     │ Insights     │ History            │  │  │
│  │  └─────────────┴──────────────┴────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                             │                                │
│  ┌──────────────────────────▼────────────────────────────┐  │
│  │              Groq LLM (gemma2-9b-it)                  │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ SQLAlchemy ORM
┌────────────────────────────▼────────────────────────────────┐
│                     Database (MySQL)                        │
│  ┌──────────┬─────────────┬──────────┬──────────────────┐  │
│  │ HCPs     │ Interactions│ Accounts │ Chat Sessions    │  │
│  └──────────┴─────────────┴──────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI library
- **Redux Toolkit** - State management
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Vite** - Build tool
- **Google Inter Font** - Typography

### Backend
- **FastAPI** - Python web framework
- **LangGraph** - AI agent framework
- **LangChain** - LLM integration
- **Groq** - LLM inference (gemma2-9b-it)
- **SQLAlchemy** - ORM
- **PyMySQL** - MySQL driver
- **Pydantic** - Data validation

### Database
- **MySQL 8.0+** - Relational database

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Groq API key ([Get one here](https://console.groq.com/keys))

## 🚀 Quick Start

### 1. Clone & Setup Database

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE crm_hcp_db;
EXIT;
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials and Groq API key

# Run the server
python -m app.main
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 🤖 LangGraph AI Agent

### Agent Role
The LangGraph agent serves as the intelligent layer between user input and CRM operations. It:
- Parses natural language from field reps
- Extracts entities (HCP names, products, topics, organizations)
- Routes requests to appropriate tools
- Generates AI-powered summaries and insights
- Maintains conversation context

### Agent Tools (6 Total)

#### 1. **Log Interaction** 📝
Captures and saves interaction data with AI enhancement:
- Identifies HCP from natural language
- Classifies interaction type (Call, Visit, Email, Meeting, etc.)
- Generates professional summary via LLM
- Extracts products and topics discussed
- Performs sentiment analysis
- Identifies action items and next steps
- Schedules follow-ups

**Example Input:**
```
"I had a great meeting with Dr. Sarah Johnson at Metro Hospital today. 
We discussed our new cardiology product CardioX and she seemed very 
interested in the clinical trial data. She wants to see the pricing 
information and we agreed to follow up next Tuesday."
```

**AI Processing:**
```json
{
  "hcp_name": "Dr. Sarah Johnson",
  "organization": "Metro Hospital",
  "interaction_type": "Meeting",
  "products": ["CardioX"],
  "topics": ["Clinical Trial Data", "Pricing"],
  "sentiment": "positive",
  "confidence": 0.92,
  "next_steps": ["Send pricing information", "Follow up next Tuesday"],
  "ai_summary": "Productive meeting with Dr. Johnson regarding CardioX..."
}
```

#### 2. **Edit Interaction** ✏️
Modifies existing logged interactions:
- Field-level updates (summary, details, status, dates)
- Audit trail tracking
- AI re-summarization when content changes
- Validation of updates

**Example Usage:**
```
"Update interaction #45 to change the follow-up date to January 20th 
and add 'Send clinical data packet' to next steps."
```

#### 3. **Search HCP** 🔍
Finds healthcare professionals by criteria:
- Name-based fuzzy search
- Specialty filtering
- Organization filtering
- Geographic filtering (city, state)
- NPI number lookup

**Example Usage:**
```
"Find all cardiologists at Metro Hospital in Boston"
```

#### 4. **Create Account** 💼
Creates sales opportunities from interactions:
- Links to HCP and interaction records
- Tracks product interest levels
- Estimates deal value
- Sets expected close dates
- Monitors opportunity status

**Example Usage:**
```
"Create an opportunity for Dr. Johnson for CardioX, estimated value 
$50,000, high interest, expected close in Q2."
```

#### 5. **Get Insights** 📊
Generates AI-powered analytics:
- Interaction frequency analysis
- Engagement trend identification
- Product interest patterns
- Sentiment analysis over time
- Recommended next actions
- Risk flags and opportunities

**Example Usage:**
```
"Show me engagement insights for Dr. Chen over the last 3 months"
```

#### 6. **Get Interaction History** 📋
Retrieves complete interaction history:
- Chronological interaction list
- Summary of past conversations
- Products discussed over time
- Follow-up tracking

**Example Usage:**
```
"What's my interaction history with Dr. Williams?"
```

## 📱 Features

### Log Interaction Screen
- **Dual Mode Interface**: Toggle between structured form and AI chat
- **Form Mode**: Traditional data entry with validation
- **Chat Mode**: Conversational AI logging with natural language
- **AI Enhancement**: Automatic entity extraction and summarization
- **Real-time Processing**: Instant feedback from AI agent

### Dashboard
- Key metrics overview
- Recent interactions list
- Quick action buttons
- Performance indicators

### HCP Management
- Search and filter HCPs
- Add new healthcare professionals
- View HCP details and history
- Track engagement metrics

### Interaction Tracking
- View all logged interactions
- Filter by type, status, date
- Edit existing records
- Track follow-ups

## 🗄️ Database Schema

### Tables
1. **hcps** - Healthcare Professional records
2. **interactions** - Interaction/encounter records
3. **accounts** - Sales opportunities
4. **chat_sessions** - Chat session tracking
5. **chat_messages** - Individual chat messages

### Key Relationships
- HCP → Interactions (1:N)
- HCP → Accounts (1:N)
- Interaction → Accounts (1:N)
- ChatSession → ChatMessages (1:N)

## 🔌 API Endpoints

### HCPs
- `GET /api/hcps/` - List all HCPs
- `GET /api/hcps/{id}` - Get HCP by ID
- `POST /api/hcps/` - Create new HCP
- `PUT /api/hcps/{id}` - Update HCP
- `DELETE /api/hcps/{id}` - Delete HCP

### Interactions
- `GET /api/interactions/` - List interactions
- `GET /api/interactions/{id}` - Get interaction
- `POST /api/interactions/` - Create interaction
- `PUT /api/interactions/{id}` - Update interaction
- `DELETE /api/interactions/{id}` - Delete interaction

### Chat
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions/{id}` - Get session
- `POST /api/chat/messages` - Send message
- `GET /api/chat/messages/{id}` - Get messages

### AI Agent
- `POST /api/ai/chat` - Chat with AI agent
- `POST /api/ai/extract` - Extract entities from text
- `POST /api/ai/log-interaction` - Log with AI enhancement

### Accounts
- `GET /api/accounts/` - List accounts
- `POST /api/accounts/` - Create account

## 🎨 UI Components

- **Sidebar** - Navigation menu
- **Header** - Page title and user info
- **InteractionForm** - Structured data entry
- **ChatInterface** - Conversational AI logging
- **Dashboard** - Overview and metrics
- **HCPList** - HCP management
- **InteractionList** - Interaction tracking

## 🔒 Security Considerations

- Environment variables for sensitive configuration
- CORS configuration for frontend-backend communication
- Input validation with Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- API key management for Groq service

## 📝 Environment Variables

### Backend (.env)
```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=crm_hcp_db

# Groq LLM
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=gemma2-9b-it
GROQ_CONTEXT_MODEL=llama-3.3-70b-versatile

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

## 🧪 Testing

```bash
# Backend tests (add pytest configuration)
cd backend
pytest

# Frontend tests (add vitest/jest configuration)
cd frontend
npm test
```

## 📦 Project Structure

```
poc/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── agent.py          # LangGraph AI agent
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── hcps.py       # HCP CRUD routes
│   │       ├── interactions.py # Interaction routes
│   │       ├── chat.py       # Chat routes
│   │       ├── ai.py         # AI agent routes
│   │       └── accounts.py   # Account routes
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx          # Entry point
│   │   ├── App.jsx           # Root component
│   │   ├── index.css         # Global styles
│   │   ├── store/
│   │   │   ├── index.js      # Redux store
│   │   │   └── slices/
│   │   │       ├── interactionSlice.js
│   │   │       ├── chatSlice.js
│   │   │       └── hcpSlice.js
│   │   ├── services/
│   │   │   └── api.js        # API client
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── InteractionForm.jsx
│   │   │   └── ChatInterface.jsx
│   │   └── pages/
│   │       ├── Dashboard.jsx
│   │       ├── LogInteraction.jsx
│   │       ├── HCPList.jsx
│   │       └── InteractionList.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🚀 Deployment

### Backend
```bash
# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
# Build for production
npm run build

# Serve with nginx or similar
```

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq Models](https://console.groq.com/docs/models)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)

## 📄 License

This project is a proof of concept for AI-first CRM in life sciences.

## 👥 Support

For questions or issues, please refer to the documentation or contact the development team.
