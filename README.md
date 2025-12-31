# MetalQuery - AI-Powered Industrial Analytics Platform

🔩 **MetalQuery** is a production-ready hybrid AI chatbot for industrial furnace analytics, combining Natural Language to SQL (NL2SQL) with multi-modal RAG for BRD document Q&A.

![MetalQuery Demo](https://img.shields.io/badge/AI-Groq_LLM-blue) ![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue) ![React](https://img.shields.io/badge/Frontend-React-61DAFB) ![FastAPI](https://img.shields.io/badge/NLP-FastAPI-009688) ![Django](https://img.shields.io/badge/Backend-Django-092E20) ![Security](https://img.shields.io/badge/Security-IEC_62443-green)

---

## 🏗️ Production Architecture

```
                             SECURITY BOUNDARY
                             AI never touches DB
                                    ↓
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐
│ React Frontend  │────▶│  Django Backend │────▶│ NLP Microservice│────▶│   Groq LLM   │
│   (Port 3000)   │     │   (Port 8000)   │     │   (Port 8003)   │     │ llama-3.3-70b│
└─────────────────┘     └────────┬────────┘     └────────┬────────┘     └──────────────┘
                                 │                       │
                                 ▼ Django ORM            ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │   ChromaDB      │
                        │  (29+ Tables)   │     │ (BRD Vectors)   │
                        └─────────────────┘     └─────────────────┘
```

### Key Security Principles (IEC 62443 SL-2/SL-3)
- **AI Never Touches Database** - NLP service ONLY generates SQL
- **4-Layer Defense** - Prompt flipping, injection, RBAC, anomaly detection
- **Rate Limiting** - Role-based (15-100 requests/minute)
- **Audit Logging** - All queries logged for compliance

---

## ✨ Features

### Core Capabilities
- 🤖 **Natural Language to SQL** - Ask questions in plain English, get data
- 📚 **BRD Document Q&A** - Multi-modal RAG with text + image retrieval
- 🔄 **Hybrid Routing** - Auto-detects SQL vs document queries
- 📊 **Rich Data Display** - Formatted tables with units
- 🖼️ **VLM Image Captioning** - Semantic captions for PDF images (Grok Vision)

### Security Features
- 🛡️ **Prompt Injection Defense** - 15+ attack pattern detection
- 🔁 **Flipping Attack Detection** - 4 reversal modes (FlipAttack research)
- 👤 **RBAC** - 4-tier access (Admin, Engineer, Operator, Viewer)
- 🔍 **Anomaly Detection** - Behavioral analysis for red team attacks
- 📝 **Comprehensive Audit Trail** - IEC 62443 compliant logging

---

## 📊 Database Content

| Category | Count |
|----------|-------|
| KPI Tables | 20 |
| Core Process Tables | 3 |
| Configuration Tables | 6 |
| Total Exposed Tables | 29+ |

### Key Metrics Available
- OEE (Overall Equipment Efficiency)
- Downtime Hours & MTBF/MTTR
- Energy & Power Consumption
- Yield Percentage & Scrap Rates
- Production Efficiency
- Furnace Parameters

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Groq API Key (for LLM)

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

   Required variables:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GROQ_MODEL=llama-3.3-70b-versatile
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=davinci
   DB_USER=davinci
   DB_PASSWORD=your_password
   ```

3. **Set up the NLP Service (Port 8003)**
   ```bash
   cd nlp_service
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   python main.py
   ```

4. **Set up the Django Backend (Port 8000)** (new terminal)
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py runserver
   ```

5. **Set up the React Frontend (Port 3000)** (new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   ```

6. **Open the application**
   - Frontend: http://localhost:3000
   - Django API: http://localhost:8000/api/chatbot/
   - NLP API Docs: http://localhost:8003/docs

### Quick Start (Windows)
```powershell
.\start_services.bat
```

---

## 💡 Example Queries

### SQL Queries (Data Mode)
| Question | Description |
|----------|-------------|
| "Show OEE by furnace for last week" | KPI data with date filtering |
| "What is the total downtime for Furnace 1?" | Aggregation query |
| "Compare yield percentage across all furnaces" | Multi-furnace comparison |
| "Show MTBF and MTTR trends" | Reliability metrics |
| "What is the energy consumption by furnace?" | Energy analysis |

### BRD Document Queries (Docs Mode)
| Question | Description |
|----------|-------------|
| "What is EHS?" | Definition from BRD docs |
| "How to configure furnace parameters?" | Procedure lookup |
| "Explain the grading process" | Process documentation |
| "What are the safety protocols?" | Compliance info |

---

## 🔒 Security Architecture

### 4-Layer Defense System

```
USER INPUT (Untrusted)
    ↓
[LAYER 1] NLP Service
    • Prompt flipping detection (4 modes)
    • Prompt signature validation (15+ patterns)
    • Schema boundary enforcement
    ↓
[LAYER 2] Django Backend
    • Rate limiting (role-based)
    • RBAC (4-tier access control)
    • SQL injection validation
    • Data masking (proprietary fields)
    ↓
[LAYER 3] PostgreSQL
    • RLS policies per role
    • Statement timeout (30s)
    • Connection limits
    ↓
[LAYER 4] Monitoring
    • Anomaly detection
    • Red team attack detection
    • Compliance reporting
```

### RBAC Tiers
| Role | Tables | Max Rows | Rate Limit |
|------|--------|----------|------------|
| Admin | All | 10,000 | 100 req/min |
| Engineer | 10 | 5,000 | 50 req/min |
| Operator | 5 | 1,000 | 30 req/min |
| Viewer | 3 | 500 | 15 req/min |

### Threats Defended
| Threat | Detection Method |
|--------|------------------|
| Prompt Injection | PromptSignatureValidator |
| Flipping Attacks | FlippingDetector (4 modes) |
| SQL Injection | Multi-layer validation |
| Red Team Attacks | AnomalyDetector |
| Data Exfiltration | RBAC + Data Masking |

---

## 📁 Project Structure

```
metalquery/
├── backend/                    # Django Backend (Port 8000)
│   ├── chatbot/
│   │   ├── views.py           # Chat API, SQL validation, execution
│   │   ├── services/          # Service clients
│   │   └── serializers.py     # API serializers
│   ├── ignis/
│   │   └── schema/            # Table whitelist & schema
│   └── config/
│       └── settings.py        # Django settings
│
├── nlp_service/               # FastAPI NLP Service (Port 8003)
│   ├── main.py               # Hybrid chat endpoint
│   ├── config.py             # Groq API configuration
│   ├── prompts_v2.py         # Schema-aware prompts (29 tables)
│   ├── query_router.py       # SQL vs BRD routing
│   ├── query_guard.py        # Input validation & guardrails
│   ├── brd_rag.py            # BRD document handler
│   ├── brd_loader.py         # PDF + image ingestion
│   ├── guardrails.py         # SQL security validation
│   ├── rate_limiter.py       # Token-aware rate limiting
│   ├── accuracy_tester.py    # SQL accuracy testing
│   ├── security/             # Security modules
│   │   ├── flipping_detector.py
│   │   ├── rbac.py
│   │   ├── sql_validator.py
│   │   ├── anomaly_detector.py
│   │   ├── audit_logger.py
│   │   └── red_team_simulator.py
│   ├── brd/                  # BRD PDF documents (33 files)
│   └── chroma_db/            # Vector embeddings
│
├── frontend/                  # React Frontend (Port 3000)
│   ├── src/
│   │   ├── App.jsx           # Main chat component
│   │   ├── config.js         # API configuration
│   │   └── components/       # UI components
│   └── package.json
│
├── ARCHITECTURE.md           # System architecture docs
├── SECURITY.md               # Security implementation docs
├── CHANGES.md                # Change log
├── start_services.bat        # Windows startup script
└── .env.example              # Environment template
```

---

## 🛠️ API Endpoints

### Django Backend (Port 8000)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chatbot/chat/` | POST | Main chat endpoint (hybrid) |
| `/api/chatbot/schema/` | GET | Get database schema |
| `/api/chatbot/health/` | GET | Health check |

### NLP Service (Port 8003)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Hybrid (SQL + BRD) endpoint |
| `/api/v1/generate-sql` | POST | SQL generation only |
| `/api/v1/format-response` | POST | Format results to NL |
| `/health` | GET | Health check |

---

## 🧪 Testing

### Run Accuracy Tests
```bash
cd nlp_service
python accuracy_tester.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/api/chatbot/health/

# SQL query
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Show OEE for last week"}'

# BRD query
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is EHS?"}'
```

### Security Test Suite
```python
from security import SecurityTestRunner

runner = SecurityTestRunner()
results = runner.run_full_test()
print(f"Block Rate: {results['block_rate']*100:.1f}%")
```

---

## 📚 Documentation

- [Architecture Guide](ARCHITECTURE.md) - System design & request flow
- [Security Documentation](SECURITY.md) - 4-layer security implementation
- [Change Log](CHANGES.md) - All modifications made
- [Query Routing](QUERY_ROUTING.md) - SQL vs BRD routing logic
- [Rate Limiting](RATE_LIMITING.md) - Token-aware rate limiting

---

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

- Groq for high-speed LLM inference (llama-3.3-70b-versatile)
- LangChain for LLM orchestration
- ChromaDB for vector storage
- FlipAttack research for flipping attack detection methods

---

## 📈 Key Metrics

| Metric | Target | Expected |
|--------|--------|----------|
| Attack Block Rate | >90% | 93-97% |
| False Positive Rate | <10% | <5% |
| Query Overhead | <100ms | 35-50ms |
| SQL Accuracy | >85% | 87-92% |
