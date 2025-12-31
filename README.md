# MetalQuery - Hybrid NLP-to-SQL + Multimodal RAG System

🏭 **MetalQuery** is a production-ready AI-powered chatbot for manufacturing KPI analysis and BRD (Business Requirement Document) question-answering. It converts natural language queries into SQL and retrieves information from 33 PDF documents with **multimodal support (text + images)**.

![Groq](https://img.shields.io/badge/LLM-Groq_llama--3.3--70b-orange) ![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue) ![React](https://img.shields.io/badge/Frontend-React-61DAFB) ![FastAPI](https://img.shields.io/badge/NLP-FastAPI-009688) ![Django](https://img.shields.io/badge/Backend-Django-092E20) ![ChromaDB](https://img.shields.io/badge/Vector-ChromaDB-green)

## 🏗️ Architecture

```
                         SECURITY BOUNDARY
                         AI never touches DB
                                ↓
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐
│ React Frontend  │────▶│  Django Backend │────▶│ NLP Microservice│────▶│ Groq LLM API │
│   (Port 5173)   │     │   (Port 8000)   │     │   (Port 8004)   │     │(llama-3.3-70b)│
└─────────────────┘     └────────┬────────┘     └───────┬─────────┘     └──────────────┘
                                 │                      │
                                 ▼                      ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │    ChromaDB     │
                        │  (29 KPI tables)│     │ (961 chunks +   │
                        └─────────────────┘     │  389 images)    │
                                                └─────────────────┘
```

### Key Security Principles:
- **AI Never Touches Database** - NLP service ONLY generates SQL
- **Django Owns the Database** - All queries go through Django ORM
- **Defense in Depth** - SQL validated at both NLP and Django layers
- **Rate Limiting** - 30 requests/minute per IP
- **Query Guard** - Off-topic/harmful query detection

## ✨ Features

### SQL Generation
- 🤖 **Natural Language to SQL** - Ask questions about KPIs in plain English
- 📊 **29 KPI Tables** - OEE, Downtime, Yield, Defect Rate, MTBF, MTTR, etc.
- 🔄 **Self-Correction** - Active retry for low-quality SQL (up to 2 retries)
- ✅ **Confidence Scoring** - 90-100% accuracy with relevance scores

### Multimodal BRD RAG
- 📄 **33 PDF Documents** - Business Requirement Documents indexed
- 🖼️ **389 Extracted Images** - Screenshots, diagrams, flowcharts from PDFs
- 🔍 **Semantic Search** - Vector similarity using SentenceTransformers
- 💬 **LLM-Powered Answers** - Natural language responses with source citations
- 🌅 **Image Lightbox** - Click to view full-size images with navigation

### Query Routing
- 🚦 **Automatic Detection** - Routes SQL vs BRD queries automatically
- 📈 **"Show OEE for furnace 1"** → SQL generation
- 📖 **"What is EHS?"** → BRD RAG retrieval
- ⚙️ **Manual Override** - Force SQL or BRD mode

## 📊 Data Content

### KPI Tables (29 total)
| Category | Tables | Description |
|----------|--------|-------------|
| **Performance** | OEE, Production Efficiency | Overall equipment effectiveness |
| **Reliability** | MTBF, MTTR, Downtime | Equipment reliability metrics |
| **Quality** | Yield, Defect Rate | Production quality |
| **Energy** | Energy Used | Consumption tracking |
| **Process** | TAP Production, Grading | Core manufacturing processes |

### BRD Documents (33 PDFs)
- EHS Incident Reporting
- System Configuration (Plant, Furnace)
- User Access Control (Roles, Users)
- Material Maintenance (Raw Materials, Additives, Products)
- Reports (Consumption, Analysis, Quality)
- Lab Analysis
- Log Books

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Groq API Key (free tier available)

### Installation

1. **Clone and setup environment**
   ```bash
   git clone https://github.com/your-repo/poc_nlp_tosql.git
   cd poc_nlp_tosql
   cp .env.example .env
   # Edit .env with your GROQ_API_KEY and database credentials
   ```

2. **Start NLP Service (Port 8004)**
   ```bash
   cd nlp_service
   python -m venv venv
   source venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   python main.py
   # Wait for: ✓ BRD RAG initialized (961 chunks, 389 images)
   # ✓ Loaded 289 dynamic keywords from schema
   ```

3. **Start Django Backend (Port 8000)**
   ```bash
   cd backend
   source ../venv/Scripts/activate
   python manage.py runserver 0.0.0.0:8000
   ```

4. **Start React Frontend (Port 5173)**
   ```bash
   cd frontend
   npm install
   npm start
   ```

5. **Open http://localhost:5173**

## 💡 Example Queries

### SQL Queries
| Question | Description |
|----------|-------------|
| "Show OEE for furnace 1 last week" | Performance metrics |
| "What is the average yield across all furnaces?" | Aggregations |
| "Compare downtime between furnaces" | Cross-furnace analysis |
| "Show defect rate trend" | Time-series data |

### BRD Queries
| Question | Description |
|----------|-------------|
| "What is EHS?" | Definitions |
| "How do I configure a new furnace?" | Process steps |
| "Explain the grading plan process" | Documentation |
| "What are user roles?" | System configuration |

## 🔒 Security Features

| Layer | Protection |
|-------|------------|
| **Rate Limiting** | 30 req/min per IP |
| **Query Guard** | Off-topic/harmful query blocking |
| **SQL Guardrails** | SELECT only, table whitelist |
| **Django Validator** | Defense in depth |
| **Query Timeout** | 30 second limit |
| **Row Limit** | Max 100 rows |
| **Audit Logging** | Compliance tracking |

## 📁 Project Structure

```
poc_nlp_tosql/
├── backend/               # Django REST API
│   ├── chatbot/          # Main app (views, services)
│   ├── ignis/            # 150+ ORM models for KPI tables
│   └── config/           # Django settings
│
├── nlp_service/          # FastAPI NLP microservice
│   ├── brd/              # 33 PDF documents for RAG
│   ├── brd_images/       # 389 extracted images
│   ├── chroma_db/        # Vector database
│   ├── brd_loader.py     # PDF extraction + ChromaDB
│   ├── brd_rag.py        # RAG query handler
│   ├── query_router.py   # SQL vs BRD routing
│   └── guardrails.py     # SQL validation
│
├── frontend/             # React SPA
│   └── src/
│       └── App.jsx       # Chat interface + image lightbox
│
├── skills.md             # Full documentation + extension ideas
└── README.md             # This file
```

## 🛠️ API Endpoints

### Django Backend (Port 8000)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chatbot/chat/` | POST | Main chat endpoint |
| `/api/chatbot/schema/` | GET | Database schema |
| `/api/chatbot/health/` | GET | Health check |

### NLP Service (Port 8004)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Hybrid chat (SQL + BRD) |
| `/api/v1/generate-sql` | POST | SQL generation only |
| `/api/v1/routing-test` | GET | Test routing logic |
| `/api/v1/brd-debug` | GET | BRD system status |
| `/api/brd-images/{file}` | GET | Serve extracted images |

## 📈 Performance

- **SQL Query Response**: ~1-2 seconds
- **BRD Query Response**: ~2-3 seconds
- **First-time BRD Init**: ~2-3 minutes (downloads model)
- **Subsequent BRD Init**: ~10-20 seconds
- **Confidence Scores**: 90-100% average

## 📚 Documentation

- [skills.md](./skills.md) - Full architecture documentation + extension ideas
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed system design
- [NLP_SERVICE_DOCS.md](./NLP_SERVICE_DOCS.md) - NLP service documentation
- [QUERY_ROUTING.md](./QUERY_ROUTING.md) - Query routing logic
- [CHANGES.md](./CHANGES.md) - Changelog

## 📄 License

MIT License - See LICENSE file for details.

---

Last Updated: 2025-12-30
- Multimodal RAG with 389 images
- Image lightbox viewer
- BRD RAG search fix
- Dynamic schema keywords (289 keywords auto-loaded from 29 tables)
- Fixed date query blocking (e.g., 2024-01-07 no longer blocked as math)
- NLP service moved to port 8004
