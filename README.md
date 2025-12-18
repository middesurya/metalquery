# MetalQuery - AI-Powered Metallurgy Materials Database

🔩 **MetalQuery** is a production-ready Natural Language to SQL chatbot that allows you to query a metallurgy materials database using plain English.

![MetalQuery Demo](https://img.shields.io/badge/AI-GPT--4-blue) ![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue) ![React](https://img.shields.io/badge/Frontend-React-61DAFB) ![FastAPI](https://img.shields.io/badge/NLP-FastAPI-009688) ![Django](https://img.shields.io/badge/Backend-Django-092E20)

## 🏗️ Production Architecture

```
                         SECURITY BOUNDARY
                         AI never touches DB
                                ↓
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐
│ React Frontend  │────▶│  Django Backend │────▶│ NLP Microservice│────▶│ LLM Provider │
│   (Port 3000)   │     │   (Port 8000)   │     │   (Port 8001)   │     │   (OpenAI)   │
└─────────────────┘     └────────┬────────┘     └─────────────────┘     └──────────────┘
                                 │
                                 ▼ Django ORM / Safe SQL
                        ┌─────────────────┐
                        │   PostgreSQL    │
                        │    Database     │
                        └─────────────────┘
```

### Key Security Principles:
- **AI Never Touches Database** - NLP service ONLY generates SQL
- **Django Owns the Database** - All queries go through Django
- **Defense in Depth** - SQL validated at both NLP and Django layers
- **Rate Limiting** - Prevents abuse (30 requests/minute per IP)
- **Audit Logging** - All queries logged for compliance

## ✨ Features

- 🤖 **Natural Language Queries** - Ask questions in plain English
- 🔒 **Multi-Layer Security** - AI isolation, SQL validation, rate limiting
- 📊 **Rich Data Display** - Beautiful tables with formatted values and units
- 🔍 **Query Transparency** - View generated SQL with copy functionality
- ⚡ **Real-time Results** - Instant query execution and response
- 🎨 **Production-Ready UI** - Modern, responsive dark-themed interface
- 📝 **Audit Trail** - Full logging for compliance

## 📊 Database Content

| Category | Count |
|----------|-------|
| Total Materials | 827 |
| Material Categories | 11 |
| Heat Treatments | 34 |
| Standards | ANSI, ISO, DIN |

### Material Properties Available:
- Ultimate Tensile Strength (MPa)
- Yield Strength (MPa)
- Elastic Modulus (MPa)
- Shear Modulus (MPa)
- Density (kg/m³)
- Hardness (Brinell & Vickers)
- Poisson's Ratio
- Elongation (%)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/middesurya/metalquery.git
   cd metalquery
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Install and Run Ollama**
   - Download Ollama from [ollama.com](https://ollama.com)
   - Pull the model:
     ```bash
     ollama pull qwen2.5-coder:1.5b
     ```

4. **Set up the NLP Service (Port 8003)**
   ```bash
   cd nlp_service
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   python main.py
   # Runs on http://127.0.0.1:8003
   ```

5. **Import metallurgy data**
   ```bash
   python import_metallurgy_data.py --host 127.0.0.1 --port 5433 --dbname postgres --user postgres --password YOUR_PASSWORD
   ```

6. **Set up the Django Backend (Port 8002)** (new terminal)
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py runserver 8002
   # Runs on http://127.0.0.1:8002
   ```

7. **Set up the React Frontend (Port 3000)** (new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   # Runs on http://localhost:3000
   ```

8. **Open the application**
   - Frontend: http://localhost:3000
   - Django API: http://127.0.0.1:8002/api/chatbot/
   - NLP API Docs: http://127.0.0.1:8003/docs

## 💡 Example Queries

| Question | Description |
|----------|-------------|
| "What steel has the highest tensile strength?" | Find strongest steel |
| "Show aluminum alloys with yield strength above 300 MPa" | Filter by property |
| "Compare properties of SAE 4140 steel" | Get specific material info |
| "Find lightweight materials with high strength" | Multi-criteria search |
| "List all stainless steels" | Category browsing |
| "What are the hardest materials?" | Sort by property |

## 🔒 Security Features

### Multi-Layer Architecture
| Layer | Security Function |
|-------|-------------------|
| **React Frontend** | User interface only |
| **Django Backend** | Rate limiting, SQL validation, DB access |
| **NLP Service** | SQL generation, initial validation |
| **Database** | Query timeout, connection limits |

### Implemented Protections
- ✅ **Read-only queries** - Only SELECT statements allowed
- ✅ **SQL injection prevention** - Multi-layer validation
- ✅ **Table restrictions** - Only allowed tables can be queried
- ✅ **Query limits** - Results capped at 100 rows
- ✅ **Rate limiting** - 30 requests/minute per IP
- ✅ **Audit logging** - All queries logged
- ✅ **Statement timeout** - 10 second max execution
- ✅ **AI isolation** - AI never touches database

## 📁 Project Structure

```
metalquery/
├── backend/               # Django backend (DB owner)
│   ├── chatbot/
│   │   ├── views.py       # Main chat endpoint with security
│   │   └── urls.py        # URL routing
│   ├── config/
│   │   └── settings.py    # Django settings
│   └── requirements.txt   # Python dependencies
│
├── nlp_service/           # NLP microservice (SQL generation only)
│   ├── main.py            # FastAPI application
│   ├── guardrails.py      # SQL validation
│   ├── schema_loader.py   # Schema introspection
│   ├── prompts.py         # LLM prompts
│   └── requirements.txt   # Python dependencies
│
├── frontend/              # React frontend
│   ├── src/
│   │   ├── App.jsx        # Main application
│   │   └── App.css        # Styles
│   └── package.json       # Node dependencies
│
├── .env.example           # Environment template
└── README.md              # This file
```

## 🛠️ API Endpoints

### Django Backend (Port 8000)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chatbot/chat/` | POST | Main chat endpoint |
| `/api/chatbot/schema/` | GET | Get database schema |
| `/api/chatbot/health/` | GET | Health check |

### NLP Service (Port 8001) - Internal Use
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/generate-sql` | POST | Generate SQL (no execution) |
| `/api/v1/format-response` | POST | Format results to NL |
| `/api/v1/schema` | GET | Schema info |
| `/health` | GET | Health check |

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

- Material properties data from engineering standards
- OpenAI for GPT-4 language model
- LangChain for LLM orchestration
