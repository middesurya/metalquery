# MetalQuery - Architecture & Flow Documentation

## Table of Contents
1. [Overview](#overview)
2. [Core Principle](#core-principle)
3. [System Architecture](#system-architecture)
4. [RBAC Flow](#rbac-flow)
5. [Request Flow](#request-flow)
6. [Security Architecture](#security-architecture)
7. [File Structure](#file-structure)
8. [Configuration](#configuration)

---

## Overview

**MetalQuery** is a Natural Language to SQL (NL2SQL) chatbot system for industrial furnace KPI analysis. It also supports document-based Q&A from BRD PDFs.

### Key Capabilities
| Feature | Description |
|---------|-------------|
| NL-to-SQL | Convert questions to PostgreSQL queries |
| BRD RAG | Answer questions from PDF documents |
| Hybrid Routing | Auto-detect SQL vs BRD questions |
| RBAC | Table-level access control |
| Security | 12-layer defense system |

### Technology Stack
| Layer | Technology | Port |
|-------|------------|------|
| Frontend | React 18 | 5173 |
| Backend Gateway | Django 4.2 | 8000 |
| NLP Service | FastAPI + LangChain | 8003 |
| LLM Provider | Groq (llama-3.3-70b) | Cloud |
| Database | PostgreSQL | 5432 |
| Vector Store | ChromaDB (Multimodal) | Embedded |

---

## Core Principle

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     LLM NEVER TOUCHES DATABASE DIRECTLY                          │
├─────────────────────────────────────────────────────────────────────────────────┤
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
│                              USER INTERFACE                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        React Frontend (Port 5173)                        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │    │
│  │  │  Chat Input  │  │  Message     │  │  Results     │  │  SQL        │  │    │
│  │  │  Component   │  │  Display     │  │  Table       │  │  Viewer     │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │    │
│  │                                                                          │    │
│  │  localStorage: authToken (Bearer token for RBAC)                        │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP POST /api/chatbot/chat/
                                        │ Authorization: Bearer <token>
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DJANGO BACKEND (Port 8000)                             │
│                        ═══════════════════════════════                           │
│                         SECURITY GATEWAY - DB OWNER                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │    │
│  │  │ Rate Limiter │  │ RBAC Service │  │ SQL Validator│  │ Audit       │  │    │
│  │  │ (30 req/min) │  │ (Token →     │  │ (Defense in  │  │ Logger      │  │    │
│  │  │              │  │  Tables)     │  │  Depth)      │  │             │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
          │                                               │
          │ HTTP POST /api/v1/chat                        │ SQL Query
          │ {question, allowed_tables}                    │
          ▼                                               ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│   NLP MICROSERVICE (Port 8003)  │         │      POSTGRESQL DATABASE        │
│  ═══════════════════════════════│         │  ═══════════════════════════════│
│   AI BOUNDARY - NO DB ACCESS    │         │                                 │
│  ┌─────────────────────────────┐│         │  ┌─────────────────────────────┐│
│  │  Security Layers            ││         │  │  29 KPI Tables              ││
│  │  ├── Flipping Detector      ││         │  │  3 Core Process Tables      ││
│  │  ├── Prompt Validator       ││         │  │  6 Master/Config Tables     ││
│  │  ├── Red Team Detector      ││         │  │                             ││
│  │  ├── Guardrails AI          ││         │  │  Auth Tables (RBAC):        ││
│  │  └── Query Guard            ││         │  │  • users_usertoken          ││
│  └─────────────────────────────┘│         │  │  • users_user               ││
│  ┌─────────────────────────────┐│         │  │  • users_userrole           ││
│  │  Schema Filtering           ││         │  │  • users_rolepermission     ││
│  │  ├── Filter by allowed_tables│         │  │  • users_role_kpis          ││
│  │  └── LLM only sees permitted││         │  └─────────────────────────────┘│
│  └─────────────────────────────┘│         └─────────────────────────────────┘
│  ┌─────────────────────────────┐│
│  │  Groq LLM API               ││
│  │  (llama-3.3-70b-versatile)  ││
│  │  Generates SQL TEXT only    ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

---

## RBAC Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          RBAC TABLE ACCESS CONTROL                               │
└─────────────────────────────────────────────────────────────────────────────────┘

  Authorization: Bearer xyz123...
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Token Lookup                                                            │
│                                                                                  │
│  users_usertoken                    users_user                                   │
│  ┌─────────────────┐               ┌─────────────────┐                          │
│  │ key = "xyz123"  │──────────────►│ id = 42         │                          │
│  │ user_id = 42    │               │ is_superuser    │                          │
│  └─────────────────┘               └────────┬────────┘                          │
│                                             │                                    │
│                     ┌───────────────────────┴───────────────────────┐            │
│                     │                                               │            │
│                     ▼                                               ▼            │
│        ┌────────────────────┐                          ┌────────────────────┐    │
│        │ IF is_superuser    │                          │ IF regular user    │    │
│        │ Return ALL 29      │                          │ Continue to        │    │
│        │ tables             │                          │ permission lookup  │    │
│        └────────────────────┘                          └─────────┬──────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                                                   │
                                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: Role Lookup                                                             │
│                                                                                  │
│  users_userrole                                                                  │
│  ┌─────────────────┐                                                            │
│  │ user_id = 42    │                                                            │
│  │ role_id = 5     │─────────────────────────────────────────────┐              │
│  └─────────────────┘                                             │              │
│                                                                   │              │
│              ┌────────────────────────────────────────────────────┤              │
│              │                                                    │              │
│              ▼                                                    ▼              │
│  ┌─────────────────────────┐                      ┌─────────────────────────┐   │
│  │ users_rolepermission    │                      │ users_role_kpis         │   │
│  │ role_id = 5             │                      │ role_id = 5             │   │
│  │ function_master_id:     │                      │ kpi_metric_code:        │   │
│  │  • PLT_CFG (view=true)  │                      │  • OEE                  │   │
│  │  • FUR_MNT (view=true)  │                      │  • DOWNTIME             │   │
│  └───────────┬─────────────┘                      │  • YIELD                │   │
│              │                                     └───────────┬─────────────┘   │
│              ▼                                                 ▼                 │
│  ┌─────────────────────────┐                      ┌─────────────────────────┐   │
│  │ FUNCTION_TABLE_MAPPING  │                      │ KPI_TABLE_MAPPING       │   │
│  │                         │                      │                         │   │
│  │ PLT_CFG → plant_plant   │                      │ OEE → kpi_oee           │   │
│  │ FUR_MNT → furnace_*     │                      │ DOWNTIME → kpi_downtime │   │
│  └───────────┬─────────────┘                      │ YIELD → kpi_yield       │   │
│              │                                     └───────────┬─────────────┘   │
│              │                                                 │                 │
│              └─────────────────────┬───────────────────────────┘                 │
│                                    │                                             │
│                                    ▼                                             │
│                     ┌──────────────────────────────┐                             │
│                     │      allowed_tables          │                             │
│                     │                              │                             │
│                     │ {"plant_plant",              │                             │
│                     │  "furnace_furnaceconfig",    │                             │
│                     │  "furnace_config_parameters",│                             │
│                     │  "kpi_oee",                  │                             │
│                     │  "kpi_downtime",             │                             │
│                     │  "kpi_yield"}                │                             │
│                     └──────────────────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Permission Mappings

**Function Codes → Tables:**
| Code | Tables |
|------|--------|
| `PLT_CFG` | plant_plant |
| `FUR_MNT` | furnace_furnaceconfig, furnace_config_parameters |
| `LOG_BOOK` | log_book_furnace_down_time_event, log_book_reasons, log_book_downtime_type_master |
| `TAP_PROC` | core_process_tap_production, core_process_tap_process, core_process_tap_grading |

**KPI Metrics → Tables (21 total):**
| Category | Codes |
|----------|-------|
| Performance | OEE, YIELD, DEFECT, PROD_EFF, OUTPUT, QTY_PROD, CYCLE_TIME, FPY, REWORK |
| Maintenance | DOWNTIME, MTBF, MTTR, MTBS, MAINT_COMP, PLAN_MAINT |
| Energy | ENERGY_EFF, ENERGY_USE |
| Capacity | CAPACITY, OTD |
| Safety | SAFETY |

---

## Request Flow

```
┌──────────┐
│   USER   │
└────┬─────┘
     │ 1. Ask: "What is the total downtime for last year?"
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         REACT FRONTEND                                │
│  • Capture user input                                                 │
│  • Get authToken from localStorage                                    │
│  • Call Django API with Bearer token                                  │
└────┬─────────────────────────────────────────────────────────────────┘
     │ 2. POST /api/chatbot/chat/
     │    Headers: Authorization: Bearer <token>
     │    Body: { question: "..." }
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         DJANGO BACKEND                                │
│                                                                        │
│  Step 2a: Rate Limiting (30 req/min per IP)                           │
│                                                                        │
│  Step 2b: RBAC Token Resolution                                       │
│  ├── Extract token from Authorization header                          │
│  ├── Lookup user via users_usertoken                                  │
│  ├── Get role permissions (function codes + KPIs)                     │
│  └── Build allowed_tables whitelist                                   │
│                                                                        │
│  Step 2c: Forward to NLP Service with allowed_tables                  │
└────┬─────────────────────────────────────────────────────────────────┘
     │ 3. POST /api/v1/chat { question: "...", allowed_tables: [...] }
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       NLP MICROSERVICE                                │
│                                                                        │
│  Step 3a: Security Layers                                             │
│  ├── Flipping Detector (jailbreak detection)                          │
│  ├── Prompt Validator (injection signatures)                          │
│  ├── Red Team Detector (attack patterns)                              │
│  ├── Guardrails AI (PII/profanity)                                    │
│  └── Query Guard (relevance check)                                    │
│                                                                        │
│  Step 3b: Schema Filtering                                            │
│  ├── Filter TABLE_SCHEMA by allowed_tables                            │
│  └── LLM only sees user's permitted tables                            │
│                                                                        │
│  Step 3c: LLM Generation (Groq)                                       │
│  └── Generate SQL using filtered schema                               │
└────┬─────────────────────────────────────────────────────────────────┘
     │ 4. Return { sql: "SELECT...", type: "sql" }
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         DJANGO BACKEND                                │
│                                                                        │
│  Step 4a: SQL Validation (Defense in Depth)                           │
│  ├── Block dangerous keywords (DROP, DELETE, etc.)                    │
│  ├── Extract tables from SQL                                          │
│  └── Verify tables ⊆ allowed_tables                                   │
│                                                                        │
│  Step 4b: Execute Query (if validated)                                │
│  └── Django executes SQL on PostgreSQL                                │
│                                                                        │
│  Step 4c: Audit Logging                                               │
│  └── Log query with user context                                      │
└────┬─────────────────────────────────────────────────────────────────┘
     │ 5. Return results to frontend
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         REACT FRONTEND                                │
│  • Display bot message with natural language response                 │
│  • Show expandable SQL query                                          │
│  • Render results in formatted table                                  │
└────┬─────────────────────────────────────────────────────────────────┘
     │ 6. Display to user
     ▼
┌──────────┐
│   USER   │  ← Sees answer, SQL, and data table
└──────────┘
```

---

## Security Architecture

### 12-Layer Security Stack

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

### Defense in Depth

```
User Input: "Show all users; DROP TABLE materials;"
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Layer 4-8: NLP Service Security                                     │
│ ├── Flipping Detector: Check for jailbreak patterns                 │
│ ├── Prompt Validator: Check injection signatures                    │
│ └── Query Guard: Check relevance to allowed tables                  │
│                                                                      │
│ If passed → Generate SQL                                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Layer 10-11: Django Backend Validation                              │
│ ├── SQL Validator: Block DROP, DELETE, INSERT, UPDATE               │
│ ├── Table Validator: Extract tables, verify ⊆ allowed_tables        │
│ └── Result: Query REJECTED, logged for security review              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
metalquery/
├── backend/                      # Django (Port 8001)
│   ├── chatbot/
│   │   ├── views.py             # Chat API, RBAC enforcement, SQL execution
│   │   ├── urls.py              # /chat/, /schema/, /health/
│   │   └── services/
│   │       └── rbac_service.py  # Token → allowed_tables resolution
│   ├── ignis/
│   │   ├── models.py            # KPI Django models
│   │   └── schema/
│   │       └── exposed_tables.py # Permission mappings
│   ├── config/
│   │   ├── settings.py          # Django settings
│   │   └── urls.py              # Root URL config
│   └── manage.py
│
├── nlp_service/                  # FastAPI (Port 8003)
│   ├── main.py                  # Hybrid chat endpoint, security layers, viz pipeline
│   ├── config.py                # Groq API config
│   ├── prompts_v2.py            # Schema filtering, 29 tables
│   ├── query_router.py          # SQL vs BRD routing
│   ├── brd_rag.py               # BRD document handler
│   ├── guardrails.py            # SQL validation with comment stripping
│   ├── sql_guardrails.py        # SQL guardrails with table allowlist
│   ├── security/                # Security modules
│   │   ├── flipping_detector.py
│   │   ├── anomaly_detector.py
│   │   ├── audit_logger.py
│   │   └── sql_validator.py
│   ├── visualization/           # LIDA-inspired chart generation
│   │   ├── viz_summarizer.py    # Column classification
│   │   ├── viz_goal_finder.py   # Chart type detection rules
│   │   ├── viz_config_generator.py # Recharts config generation
│   │   └── viz_validator.py     # Config validation
│   └── brd/                     # BRD PDF documents
│
├── frontend/                     # React (Port 5173)
│   └── src/
│       ├── App.jsx              # Main chat component, auth handling
│       ├── config.js            # API configuration (port 8000)
│       └── components/
│           └── ChartRenderer.jsx # Dynamic Recharts rendering
│
└── docs/                         # Documentation
    ├── RBAC_WORKFLOW_DIAGRAM.md
    ├── RBAC_MANUAL_TESTING_GUIDE.md
    └── RBAC_QUICK_TEST_CHEATSHEET.md
```

---

## Configuration

### Environment Variables

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

# NLP Service
NLP_SERVICE_URL=http://localhost:8003

# LLM (REQUIRED)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

### Starting Services

```bash
# Terminal 1: Django Backend
cd backend
python manage.py runserver 8001

# Terminal 2: NLP Service
cd nlp_service
python main.py

# Terminal 3: React Frontend
cd frontend
npm start
```

---

## Infographics Pipeline

The system includes a LIDA-inspired visualization pipeline that automatically generates chart configurations based on query results.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        INFOGRAPHICS GENERATION FLOW                              │
└─────────────────────────────────────────────────────────────────────────────────┘

  SQL Results (from Django)
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  DataSummarizer (viz_summarizer.py)                                              │
│                                                                                  │
│  • Classifies columns: numeric vs categorical vs temporal                        │
│  • Detects query patterns: comparison, distribution, trend                       │
│  • Uses METRIC_TIME_PATTERNS to prevent misclassification                        │
│    (e.g., cycle_time is numeric, not temporal)                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  VizGoalFinder (viz_goal_finder.py)                                              │
│                                                                                  │
│  • Applies heuristic rules to determine chart type                               │
│  • Rule priority:                                                                │
│    1. Single value → gauge (OEE/yield) or kpi_card (counts)                     │
│    2. Multi-metric row → metric_grid                                            │
│    3. Time series data → line chart                                             │
│    4. Trend keywords detected → line chart                                       │
│    5. Distribution keywords → pie chart                                          │
│    6. Comparison keywords → bar chart                                            │
│    7. Default → table                                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  VizConfigGenerator (viz_config_generator.py)                                    │
│                                                                                  │
│  • Generates Recharts-compatible JSON config                                     │
│  • Applies DaVinci design system colors                                          │
│  • Formats labels and units (OEE→%, kWh, hours)                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  Chart Config JSON → Frontend ChartRenderer
```

### Chart Type Detection Keywords

| Chart Type | Keywords / Patterns |
|------------|---------------------|
| **Bar** | "compare", "versus", "by furnace", "by shift", "rank", "top", "which furnace" |
| **Line** | "trend", "over time", "last week", "last month", "daily", "history" |
| **Pie** | "breakdown", "distribution", "by reason", "by type", "proportion" |
| **Gauge** | Single row with OEE/yield/efficiency/rate percentage |
| **KPI Card** | Single row with count/total/quantity |

### Supported Chart Types

| Type | Component | Use Case |
|------|-----------|----------|
| `bar` | BarChart | Categorical comparisons (by furnace, by shift) |
| `line` | LineChart | Time series and trends |
| `pie` | PieChart | Distribution/breakdown (≤8 categories) |
| `gauge` | Gauge | Single percentage metric (OEE, yield) |
| `kpi_card` | Card | Single numeric value |
| `metric_grid` | Grid | Multiple KPIs in one row |
| `table` | Table | Complex data (>20 rows, fallback) |

---

## Summary

| Component | Responsibility | Database Access |
|-----------|---------------|-----------------|
| React Frontend | User interface, auth token, chart rendering | None |
| Django Backend | Security, RBAC, DB access, chart config passthrough | Yes (Owner) |
| NLP Service | SQL generation, schema filtering, chart config | None |
| Groq LLM | Natural language processing | None |
| PostgreSQL | Data storage | N/A (is the DB) |

**Key Principle:** The AI (NLP Service + Groq) never has direct database access. Django acts as the security gateway and is the sole owner of database credentials.

---

**Last Updated:** 2026-01-09
