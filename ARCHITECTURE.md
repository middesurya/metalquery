# ProcessQuery - Architecture & Flow Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Components](#components)
4. [Request Flow](#request-flow)
5. [Security Architecture](#security-architecture)
6. [Code Walkthrough](#code-walkthrough)
7. [Database Schema](#database-schema)
8. [Configuration](#configuration)

---

## Overview

**ProcessQuery** is a specialized AI Assistant for Smart Manufacturing. It enables plant managers and operators to query production data using natural language. The system differentiates between general domain questions (answered directly by the LLM) and data retrieval requests (converted to SQL), executing them securely against a manufacturing database.

### Key Capabilities
- **Hybrid Response System**: Distinguishes between General QA (text) and Data Queries (SQL).
- **Self-Correcting SQL**: Automatically retries and fixes malformed SQL queries using validator feedback.
- **Priority Schema Loading**: Optimizes context for large schemas by prioritizing KPI and Log tables.
- **Secure Execution**: Strict read-only access with multi-layer guardrails.

### Technology Stack
| Layer | Technology |
|-------|------------|
| Frontend | React 18 |
| Backend Gateway | Django 4.2 |
| NLP Service | FastAPI + LangChain |
| LLM Provider | Ollama (Local qwen2.5-coder:1.5b) |
| Database | PostgreSQL 16 |

---

## Architecture Diagram

```ascii
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        React Frontend (Port 3000)                        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │    │
│  │  │  Chat Input  │  │  Message     │  │  Results     │  │  SQL        │  │    │
│  │  │  Component   │  │  List        │  │  Table       │  │  Viewer     │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP POST /api/chatbot/chat/
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DJANGO BACKEND (Port 8002)                             │
│                        ═══════════════════════════════                           │
│                         🔒 SECURITY GATEWAY - DB OWNER                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │    │
│  │  │ Rate Limiter │  │ SQL Validator│  │ Query        │  │ Audit       │  │    │
│  │  │ (30 req/min) │  │ (Defense in  │  │ Executor     │  │ Logger      │  │    │
│  │  │              │  │  Depth)      │  │ (psycopg2)   │  │             │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
          │                                               │
          │ HTTP POST /api/v1/generate-sql                │ SQL Query
          │                                               ▼
          ▼                                     ┌─────────────────────────────────┐
┌─────────────────────────────────┐             │      POSTGRESQL DATABASE        │
│   NLP MICROSERVICE (Port 8003)  │             │  ═══════════════════════════════│
│  ═══════════════════════════════│             │                                 │
│   🤖 AI BOUNDARY - NO DB ACCESS │             │  ┌─────────────────────────────┐│
│  ┌─────────────────────────────┐│             │  │  log_book_tap_hole_log      ││
│  │  Self-Correction Loop       ││             │  │  core_process_tap_production││
│  │  (Max 3 Retries on Error)   ││             │  │  assistant_analysisresult   ││
│  ├─────────────────────────────┤│             │  │  kpi_energy_efficiency_data ││
│  │  Schema Priority Loader     ││             │  │  kpi_downtime_data          ││
│  │  (Full Cols for KPIs)       ││             │  └─────────────────────────────┘│
│  └─────────────────────────────┘│             └─────────────────────────────────┘
│               │                 │
│               ▼                 │
│  ┌─────────────────────────────┐│
│  │      Local LLM (Ollama)     ││
│  │     (qwen2.5-coder:1.5b)    ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

---

## Components

### 1. React Frontend (`/frontend`)
**Purpose:** User interface for the "ProcessQuery" assistant.
**Features:**
- Domain-specific branding (Manufacturing/Process Control).
- Intelligent suggestion chips (e.g., "How many process taps?").
- Dynamic rendering of text answers vs. data tables.

### 2. Django Backend (`/backend`)
**Purpose:** Security gateway and orchestration.
**Logic:**
- Receives NLP response.
- If `is_sql=False` (General QA): Returns text directly.
- If `is_sql=True` (Data Request): Validates SQL -> Executes -> Returns Rows.

### 3. NLP Microservice (`/nlp_service`)
**Purpose:** Intelligence layer (No DB credentials).
**Advanced Logic:**
- **Mode Selection**: Decides whether to generate SQL or answer with General Domain Knowledge.
- **Tables Priority**: Loads full schema for critical tables (KPIs, Logs) but compacts others to save tokens.
- **Self-Correction**: If generated SQL fails validation, it captures the error and re-prompts the LLM to fix it.

---

## Request Flow

### Scenario A: General Question ("What is the purpose of this system?")
1. **Frontend**: Sends question to Django.
2. **Django**: Forwards to NLP Service.
3. **NLP Service**:
   - LLM recognizes this as a "General Question" based on System Prompt.
   - LLM generates text response using embedded Domain Knowledge.
   - Returns `{ sql: null, explanation: "The system tracks..." }`.
4. **Django**: Sees `sql` is null, returns explanation directly.
5. **Frontend**: Displays text answer.

### Scenario B: Data Query - Self-Correction ("Errors in KPI tables")
1. **NLP Service**:
   - **Try 1**: LLM hallucinates `SELECT * FROM kpi_errors`.
   - **Validator**: Fails (Table `kpi_errors` does not exist).
   - **Retry Loop**: Captures error, adds to history: *"Error: Table kpi_errors not found. Available tables: kpi_cycle_time_data, ..."*.
   - **Try 2**: LLM Corrects: `SELECT * FROM kpi_cycle_time_data WHERE record_status = 'Error'`.
   - **Validator**: Passes.
2. **Django**: Receives valid SQL, executes, returns results.

---

## Database Schema (Manufacturing Domain)

### Core Production Tables
- `log_book_tap_hole_log`: Tracks status and maintenance of furnace tap holes.
- `core_process_tap_production`: Detailed metrics for each production "batch" (tap).
- `furnace_config_tap_hole`: Configuration and state of active tap holes.

### Quality & Analysis
- `assistant_analysisresult`: Lab results for chemical/physical properties.
- `assistant_clinkerimage`: Visual analysis metadata.

### KPI Tables (Full Schema Visible to LLM)
- `kpi_energy_efficiency_data`
- `kpi_downtime_data`
- `kpi_cycle_time_data`
- `kpi_defect_rate_data`
- ... (and 15+ others)

---

## Configuration

### Environment Variables (`.env`)
```bash
# LLM
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5-coder:1.5b

# PostgreSQL
DB_HOST=localhost
DB_PORT=5433
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# Validation thresholds
MAX_SQL_RETRIES=3
```

### Future Roadmap
- [ ] Add Vector Store (RAG) for searching PDF documentation (BRDs).
- [ ] Implement query caching for frequent KPI requests.
