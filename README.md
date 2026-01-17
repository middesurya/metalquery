# MetalQuery - NLP-to-SQL + Multimodal RAG System

**MetalQuery** is a POC AI-powered chatbot for manufacturing KPI analysis. It converts natural language queries into SQL and retrieves information from BRD documents with multimodal support.

![Groq LLM](https://img.shields.io/badge/AI-Groq_LLM-blue) ![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue) ![React](https://img.shields.io/badge/Frontend-React-61DAFB) ![FastAPI](https://img.shields.io/badge/NLP-FastAPI-009688) ![Django](https://img.shields.io/badge/Backend-Django-092E20) ![Security](https://img.shields.io/badge/Security-IEC_62443-green)

---

## Core Principle: LLM Never Touches Database

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SECURITY ARCHITECTURE                                  │
│                                                                                  │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐              │
│   │    USER     │         │     LLM     │         │  DATABASE   │              │
│   │   Query     │         │   (Groq)    │         │ (PostgreSQL)│              │
│   └──────┬──────┘         └──────┬──────┘         └──────┬──────┘              │
│          │                       │                       │                      │
│          │                       │ Generates             │                      │
│          │                       │ SQL TEXT              │                      │
│          │                       │ only                  │                      │
│          │                       ▼                       │                      │
│          │              ┌─────────────────┐              │                      │
│          └─────────────►│     DJANGO      │◄─────────────┘                      │
│                         │   (Gatekeeper)  │                                     │
│                         │                 │                                     │
│                         │ • Validates SQL │                                     │
│                         │ • Checks RBAC   │                                     │
│                         │ • Executes query│                                     │
│                         │ • Owns DB conn  │                                     │
│                         └─────────────────┘                                     │
│                                                                                  │
│   KEY: LLM has NO database connection, NO credentials, NO direct access         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FULL SYSTEM FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

  User: "Show OEE by furnace"
        │
        ▼
┌───────────────────┐
│     FRONTEND      │  React (Port 5173)
│                   │  • Chat UI
│ localStorage:     │  • Auth token handling
│ authToken: xyz    │  • 401/403 error display
└─────────┬─────────┘
          │
          │  POST /api/chatbot/chat/
          │  Authorization: Bearer <token>
          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DJANGO BACKEND (Port 8000)                              │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ RBAC SERVICE                                                            │    │
│  │                                                                         │    │
│  │  Token ──► users_usertoken ──► users_user ──► users_userrole           │    │
│  │                                     │                                   │    │
│  │              ┌──────────────────────┴──────────────────────┐            │    │
│  │              ▼                                             ▼            │    │
│  │     users_rolepermission                          users_role_kpis      │    │
│  │     (function codes)                              (KPI metrics)        │    │
│  │              │                                             │            │    │
│  │              ▼                                             ▼            │    │
│  │     FUNCTION_TABLE_MAPPING                        KPI_TABLE_MAPPING    │    │
│  │     PLT_CFG → plant_plant                         OEE → kpi_oee        │    │
│  │     FUR_MNT → furnace_*                           YIELD → kpi_yield    │    │
│  │     LOG_BOOK → log_book_*                         DOWNTIME → kpi_*     │    │
│  │              │                                             │            │    │
│  │              └──────────────────┬──────────────────────────┘            │    │
│  │                                 ▼                                       │    │
│  │                          allowed_tables                                 │    │
│  │                    {"kpi_oee", "plant_plant", ...}                      │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                             │
│                                    │ POST {question, allowed_tables}            │
│                                    ▼                                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          NLP SERVICE (Port 8003)                                 │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ SECURITY LAYERS                                                         │    │
│  │ [1] Flipping Detector  - Jailbreak detection                           │    │
│  │ [2] Prompt Validator   - Injection signatures                          │    │
│  │ [3] Red Team Detector  - Attack patterns                               │    │
│  │ [4] Guardrails AI      - PII/profanity filtering                       │    │
│  │ [5] Query Guard        - Relevance + intent                            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                             │
│                                    ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ QUERY ROUTER                                                            │    │
│  │                                                                         │    │
│  │   "Show OEE..." ──► SQL Path    "What is EHS?" ──► BRD RAG Path        │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                             │
│                                    ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ SCHEMA FILTERING (prompts_v2.py)                                        │    │
│  │                                                                         │    │
│  │   Full TABLE_SCHEMA (29 tables)                                        │    │
│  │            │                                                            │    │
│  │            │  Filter by allowed_tables from RBAC                       │    │
│  │            ▼                                                            │    │
│  │   Filtered Schema ──► LLM only sees user's permitted tables            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                             │
│                                    ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ LLM (Groq llama-3.3-70b)                                                │    │
│  │                                                                         │    │
│  │   INPUT:  Filtered schema + user question                              │    │
│  │   OUTPUT: SQL query as TEXT string                                     │    │
│  │                                                                         │    │
│  │   ⚠️  NO database connection                                            │    │
│  │   ⚠️  NO credentials                                                    │    │
│  │   ⚠️  ONLY generates text                                               │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                    │                                             │
│                                    │ Returns: {sql: "SELECT...", type: "sql"}   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    DJANGO BACKEND - DEFENSE IN DEPTH                             │
│                                                                                  │
│  [1] SQLValidator    - Block DROP, DELETE, INSERT, UPDATE, GRANT, etc.          │
│  [2] Table Extractor - Parse tables from SQL                                     │
│  [3] RBAC Validator  - Verify tables ⊆ allowed_tables                           │
│  [4] Query Executor  - Django executes validated SQL                             │
│  [5] Audit Logger    - Log all queries with user context                         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              POSTGRESQL DATABASE                                 │
│                                                                                  │
│  29 Exposed Tables:                                                              │
│  • 20 KPI tables (kpi_oee, kpi_downtime, kpi_yield, etc.)                       │
│  • 3 Core process tables (core_process_tap_*)                                   │
│  • 3 Log book tables (log_book_*)                                               │
│  • 2 Furnace tables (furnace_*)                                                 │
│  • 1 Plant table (plant_plant)                                                  │
│                                                                                  │
│  Auth Tables (RBAC):                                                             │
│  • users_usertoken, users_user, users_userrole                                  │
│  • users_rolepermission, users_role_kpis                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Features

### SQL Generation
- Natural Language to SQL conversion
- Schema-aware prompts with 365+ few-shot examples
- Self-correction with confidence scoring
- 29 KPI tables supported

### Infographics/Charts (NEW)
- Automatic chart type detection from query patterns
- LIDA-inspired visualization pipeline
- Recharts-compatible JSON config generation
- Supported chart types:
  | Type | Use Case |
  |------|----------|
  | Bar | Comparisons (by furnace, by shift) |
  | Line | Trends (over time, last week) |
  | Pie | Distributions (breakdown, by reason) |
  | Progress Bar | Single OEE/yield percentage |
  | KPI Card | Single count/total value |

### Multimodal BRD RAG
- 33 PDF documents indexed
- 389 extracted images (screenshots, diagrams)
- Semantic search using ChromaDB
- LLM-powered answers with citations

### Query Routing
- Automatic SQL vs BRD detection
- `"Show OEE for furnace 1"` → SQL
- `"What is EHS?"` → BRD RAG

### RBAC (Role-Based Access Control)
- Token-based authentication
- Table-level access control
- Function code permissions (PLT_CFG, FUR_MNT, etc.)
- KPI metric permissions (OEE, YIELD, DOWNTIME, etc.)
- Defense-in-depth validation

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Groq API Key

### Start Services

```bash
# Terminal 1: Django Backend (Port 8000)
cd backend
python manage.py runserver 8000

# Terminal 2: NLP Service (Port 8003)
cd nlp_service
python main.py

# Terminal 3: Frontend (Port 5173)
cd frontend
npm install
npm start
```

### Open http://localhost:5173

---

## Security Layers (12 total)

| # | Layer | Location | Purpose |
|---|-------|----------|---------|
| 1 | Rate Limiter | Django | 30 req/min per IP |
| 2 | Token Validation | Django | Auth via users_usertoken |
| 3 | RBAC Service | Django | Token → allowed_tables |
| 4 | Flipping Detector | NLP | Jailbreak detection |
| 5 | Prompt Validator | NLP | Injection signatures |
| 6 | Red Team Detector | NLP | Attack patterns |
| 7 | Guardrails AI | NLP | PII/profanity filter |
| 8 | Query Guard | NLP | Relevance check |
| 9 | Schema Filter | NLP | Only allowed tables in prompt |
| 10 | SQL Validator | Django | Block dangerous SQL |
| 11 | Table Validator | Django | RBAC defense-in-depth |
| 12 | Audit Logger | Django | Full query logging |

---

## RBAC Permission Mappings

### Function Codes → Tables
| Code | Tables |
|------|--------|
| `PLT_CFG` | plant_plant |
| `FUR_MNT` | furnace_furnaceconfig, furnace_config_parameters |
| `LOG_BOOK` | log_book_* (3 tables) |
| `TAP_PROC` | core_process_tap_* (3 tables) |

### KPI Metrics → Tables
| Category | Codes | Tables |
|----------|-------|--------|
| Performance | OEE, YIELD, DEFECT, PROD_EFF | kpi_oee, kpi_yield, etc. |
| Maintenance | DOWNTIME, MTBF, MTTR, MTBS | kpi_downtime, kpi_mtbf, etc. |
| Energy | ENERGY_EFF, ENERGY_USE | kpi_energy_* |

---

## API Endpoints

### Django Backend (Port 8000)
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/chatbot/chat/` | POST | Bearer token | Main chat endpoint |
| `/api/chatbot/schema/` | GET | - | Database schema |
| `/api/chatbot/health/` | GET | - | Health check |

### NLP Service (Port 8003)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Hybrid chat (SQL + BRD) |
| `/api/v1/generate-sql` | POST | SQL generation only |
| `/health` | GET | Health check |

---

## Project Structure

```
poc_nlp_tosql/
├── backend/                    # Django REST API
│   ├── chatbot/
│   │   ├── views.py           # Chat endpoint + RBAC enforcement
│   │   └── services/
│   │       └── rbac_service.py # Token → allowed_tables
│   └── ignis/
│       └── schema/
│           └── exposed_tables.py  # Permission mappings
│
├── nlp_service/               # FastAPI NLP microservice
│   ├── main.py               # API + security layers + viz pipeline
│   ├── prompts_v2.py         # Schema filtering + LLM prompts
│   ├── query_router.py       # SQL vs BRD routing
│   ├── brd_rag.py            # Document retrieval
│   ├── visualization/        # LIDA-inspired chart generation
│   │   ├── viz_summarizer.py # Column classification
│   │   ├── viz_goal_finder.py # Chart type detection
│   │   └── viz_config_generator.py # Recharts config
│   └── security/             # Security modules
│
├── frontend/                  # React SPA
│   └── src/
│       ├── App.jsx           # Chat UI + auth handling
│       ├── config.js         # API configuration
│       └── components/
│           └── ChartRenderer.jsx # Dynamic Recharts rendering
│
└── docs/                      # Documentation
    ├── RBAC_WORKFLOW_DIAGRAM.md
    ├── RBAC_MANUAL_TESTING_GUIDE.md
    └── RBAC_QUICK_TEST_CHEATSHEET.md
```

---

## Testing

### Quick RBAC Test
```bash
# No token (expect 401)
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Show OEE"}'

# With token (expect data or 403 based on permissions)
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question": "Show OEE by furnace"}'
```

### Run Security Tests
```bash
cd backend
python test_rbac_defense.py    # RBAC tests
python test_sql_injection.py   # SQL injection tests (43 cases)
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [RBAC_WORKFLOW_DIAGRAM.md](./docs/RBAC_WORKFLOW_DIAGRAM.md) | Visual flow diagram |
| [RBAC_MANUAL_TESTING_GUIDE.md](./docs/RBAC_MANUAL_TESTING_GUIDE.md) | Complete testing guide |
| [RBAC_QUICK_TEST_CHEATSHEET.md](./docs/RBAC_QUICK_TEST_CHEATSHEET.md) | Quick reference |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design |
| [SECURITY.md](./SECURITY.md) | Security implementation |
| [CHANGES.md](./CHANGES.md) | Changelog |

---

## Test Results

| Test | Status |
|------|--------|
| No token → 401 | ✅ |
| Invalid token → 401 | ✅ |
| No permissions → 403 | ✅ |
| Superuser → 29 tables | ✅ |
| SQL injection (43 tests) | ✅ Blocked |
| Defense-in-depth | ✅ |
| Frontend → Backend | ✅ |
| Bar chart (comparison) | ✅ |
| Line chart (trend) | ✅ |
| Pie chart (distribution) | ✅ |
| Progress Bar (single OEE) | ✅ |
| KPI Card (single value) | ✅ |

---

## License

MIT License

---

**Last Updated:** 2026-01-16

### Recent Changes
- **2026-01-09**: Added infographics/charts (bar, line, pie, progress bar, KPI card)
- **2026-01-09**: Fixed SQL guardrails (comment stripping, REPLACE keyword)
- **2026-01-09**: Fixed column classification (METRIC_TIME_PATTERNS)
- **2026-01-06**: Added RBAC table-level access control
- **2026-01-06**: Added comprehensive RBAC documentation
- All security tests passing (43 SQL injection tests, 16 RBAC tests)
