# NLP-to-SQL + RAG System - Changes Documentation

## Overview

This document details all changes made to implement the NLP-to-SQL + RAG system for IGNIS database integration following the provided implementation guide. **Docker was avoided** - all changes support local development.

---

## Recent Changes (2025-12-30)

### Dynamic Schema Keywords & Date Query Fix

**Problem 1:** Queries containing table-specific terms like "cycle time" were being blocked as "off-topic" because keywords were hardcoded.

**Solution:** Added dynamic keyword loading from database schema:
- `QueryGuard.load_schema_keywords()` extracts keywords from table and column names
- 289 keywords auto-loaded from 29 tables
- Supports compound terms (e.g., "cycle time", "production efficiency")

**Problem 2:** Date queries like "What is the cycle time for FURNACE on 2024-01-07?" were blocked as "math questions" because the date format (with hyphens) triggered math pattern detection.

**Solution:** Modified math patterns in `query_guard.py`:
- Removed subtraction (`-`) from math operator detection
- Date patterns (YYYY-MM-DD) no longer trigger math blocking

**Problem 3:** Frontend was using wrong port (8003 instead of 8004).

**Solution:** Updated `App.jsx` to use port 8004 for NLP service.

**Files Modified:**
- `nlp_service/query_guard.py` - Added `load_schema_keywords()` method, fixed math patterns
- `nlp_service/main.py` - Call `guard.load_schema_keywords(schema_dict)` on startup
- `frontend/src/App.jsx` - Changed NLP_URL port to 8004, removed duplicate image section

---

### BRD RAG Fix - ChromaDB Stale Reference Issue

**Problem:** BRD queries returned "I couldn't find relevant information" despite 961 text chunks and 389 images being indexed in ChromaDB.

**Root Cause:** The `search()` and `search_images()` functions in `brd_loader.py` were using stale `self.vectorstore` and `self.image_collection` references. When uvicorn reloaded or the server restarted, these cached references became invalid.

**Solution:** Modified both search functions to always get fresh ChromaDB client and collection references on every search call:

```python
def search(self, query: str, top_k: int = 5) -> List[Dict]:
    """Always gets a fresh collection reference from ChromaDB to avoid stale references."""
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    collection = client.get_collection("brd_documents")
    # ... rest of search logic
```

**Files Modified:**
- `nlp_service/brd_loader.py` - Fixed `search()` (lines 387-436) and `search_images()` (lines 438-494)
- `nlp_service/brd_rag.py` - Added logging for search results

### Multimodal RAG with Image Extraction

**Added:** Full multimodal support for BRD document search:
- Extracts images from PDFs with intelligent filtering (removes logos, icons)
- Stores image context in separate ChromaDB collection (`brd_images`)
- Returns both text chunks and relevant images in search results
- Frontend displays images with lightbox viewer

**Statistics:**
- 961 text chunks indexed
- 389 images extracted and indexed
- Image filtering removes images < 10KB, logo-shaped images, and repeated headers/footers

### Documentation Updates

- **README.md** - Complete rewrite with current architecture
- **skills.md** - Added "Future Extension Ideas" section with 10 categories
- **ARCHITECTURE.md** - Updated ports and multimodal info
- **NLP_SERVICE_DOCS.md** - Added multimodal RAG section

### New Debug Endpoint

Added `/api/v1/brd-debug` endpoint for diagnosing BRD RAG issues:
```bash
curl http://localhost:8003/api/v1/brd-debug
# Returns: text_chunks, image_count, initialized status, test search results
```

---

## Summary of Changes

| Category | Files Created | Files Modified |
|----------|---------------|----------------|
| Backend Django | 9 | 2 |
| NLP Service | 2 | 1 |
| Frontend | 4 | 1 |
| Configuration | 0 | 1 |
| **Total** | **15** | **5** |

---

## New Files Created (15)

### Backend - Chatbot Services

#### `backend/chatbot/services/__init__.py`
```python
# Services module initialization
# Exports: NLPServiceClient, RAGServiceClient, QueryRouter, ResponseFormatter
```

#### `backend/chatbot/services/nlp_service_client.py`
- **Purpose**: Client for calling NLP microservice
- **Key Methods**:
  - `generate_sql(question, schema)` - Generate SQL from natural language
  - `validate_sql(sql)` - Validate SQL against security rules
  - `check_health()` - Health check for NLP service
- **Config**: Uses `NLP_SERVICE_URL` from settings (default: `http://localhost:8003`)

#### `backend/chatbot/services/rag_service_client.py`
- **Purpose**: Client for calling RAG microservice for BRD documents
- **Key Methods**:
  - `query(question, top_k)` - Query BRD documents for answer
  - `search_documents(query, top_k)` - Search without generating answer
  - `get_indexed_documents()` - List indexed BRD documents
- **Config**: Uses `RAG_SERVICE_URL` from settings (default: `http://localhost:8004`)

#### `backend/chatbot/services/query_router.py`
- **Purpose**: Routes queries to NLP-SQL or RAG based on content
- **Keywords for SQL**: show, get, list, oee, efficiency, yield, downtime, mtbf, etc.
- **Keywords for RAG**: how to, what is, explain, procedure, configuration, etc.
- **Returns**: 'nlp-sql', 'rag', or 'hybrid'

#### `backend/chatbot/services/response_formatter.py`
- **Purpose**: Formats database results as natural language
- **Features**:
  - Auto-detects percentage, time, energy, weight columns
  - Adds proper units (%, hours, kWh, tons)
  - Creates ASCII tables for large result sets

#### `backend/chatbot/serializers.py`
- **Purpose**: DRF serializers for API endpoints
- **Serializers**:
  - `ChatRequestSerializer` - Chat request with mode
  - `ChatResponseSerializer` - Chat response with results
  - `DualQueryRequestSerializer` - Dual query endpoint
  - `SchemaResponseSerializer` - Schema info
  - `HealthResponseSerializer` - Health check

---

### Backend - IGNIS Schema Module

#### `backend/ignis/schema/__init__.py`
```python
# Schema module initialization
# Exports: EXPOSED_TABLES, TABLE_DESCRIPTIONS, get_schema_definitions
```

#### `backend/ignis/schema/exposed_tables.py`
- **Purpose**: Whitelist of all 29+ tables accessible via chatbot
- **Contents**:
  - `EXPOSED_TABLES` - Set of 29 table names
  - `TABLE_DESCRIPTIONS` - Human-readable descriptions
  - `KPI_COLUMN_MAPPINGS` - Maps keywords to (table, column)
  - `AGGREGATION_RULES` - AVG/SUM rules per column

**Tables Included**:
| Category | Count | Examples |
|----------|-------|----------|
| KPI Tables | 20 | `kpi_overall_equipment_efficiency_data`, `kpi_downtime_data` |
| Core Process | 3 | `core_process_tap_production`, `core_process_tap_grading` |
| Log Book | 1 | `log_book_furnace_down_time_event` |
| Configuration | 1 | `furnace_config_parameters` |
| Master Data | 4 | `furnace_furnaceconfig`, `plant_plant` |

#### `backend/ignis/schema/schema_definitions.py`
- **Purpose**: PostgreSQL schema introspection with caching
- **Key Functions**:
  - `get_schema_definitions(force_refresh)` - Get all table schemas
  - `get_schema_context_string(tables)` - Format for LLM prompts
  - `invalidate_schema_cache()` - Clear cache
- **Caching**: 1-hour cache using Django cache framework

---

### NLP Service

#### `nlp_service/nlp/__init__.py`
```python
# NLP module initialization
```

#### `nlp_service/nlp/response_formatter.py`
- **Purpose**: Format SQL results as natural language
- **Same functionality as Django version** for consistency

---

### Frontend

#### `frontend/src/config.js`
- **Purpose**: Centralized API configuration
- **Exports**:
  - `config` - API URL, endpoints, timeouts
  - `getEndpointUrl(endpoint)` - Build full URL
  - `apiRequest(endpoint, options)` - Make API request

#### `frontend/src/components/ModeToggle.jsx`
- **Purpose**: Toggle between Auto/Data/Docs modes
- **Props**: `mode`, `onModeChange`, `disabled`
- **Modes**:
  - 🔄 Auto - Auto-detect query type
  - 📊 Data - Force NLP-SQL mode
  - 📚 Docs - Force RAG mode

#### `frontend/src/components/ModeToggle.css`
- **Purpose**: Styling for mode toggle component
- **Features**: Gradient active state, responsive design

#### `frontend/src/components/hooks/useQuery.js`
- **Purpose**: Custom React hook for API queries
- **Returns**:
  - `isLoading`, `error`, `data` - State
  - `executeQuery(question, mode)` - Execute chat query
  - `executeDualQuery(question, forceMode)` - Execute dual query
  - `checkHealth()`, `fetchSchema()` - Utility functions

---

## Files Modified (5)

### `backend/config/settings.py`

**Changes**:
1. Added `rest_framework` to INSTALLED_APPS
2. Added `SecurityMiddleware` to MIDDLEWARE
3. Added NLP/RAG service URLs:
   ```python
   NLP_SERVICE_URL = os.getenv('NLP_SERVICE_URL', 'http://localhost:8003')
   RAG_SERVICE_URL = os.getenv('RAG_SERVICE_URL', 'http://localhost:8004')
   ```
4. Added CORS configuration:
   ```python
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:3000',
       'http://127.0.0.1:3000',
       'http://localhost:8000',
   ]
   CORS_ALLOW_CREDENTIALS = True
   ```
5. Added database connection pooling:
   ```python
   'CONN_MAX_AGE': 600,
   'OPTIONS': {
       'connect_timeout': 10,
       'options': '-c statement_timeout=30000'
   }
   ```
6. Added REST Framework config
7. Added local memory caching (1-hour timeout)
8. Added file-based logging to `logs/nlp_sql_rag.log`

---

### `backend/chatbot/views.py`

**Changes**:
1. **Fixed bug**: Replaced undefined `get_db_connection()` with Django's `connection.ensure_connection()`
   ```python
   # Before (broken):
   conn = get_db_connection()
   conn.close()
   
   # After (fixed):
   connection.ensure_connection()
   ```
2. Updated version to 3.0.0

---

### `nlp_service/guardrails.py`

**Changes**:
1. Added more blocked SQL keywords for enhanced security:
   ```python
   BLOCKED_KEYWORDS = {
       # ... existing ...
       "INTO", "COPY", "LOAD", "SET", "DECLARE",  # NEW
   }
   ```

---

### `frontend/src/App.jsx`

**Changes**:
1. Added imports:
   ```jsx
   import ModeToggle from './components/ModeToggle';
   import config from './config';
   ```
2. Added `queryMode` state:
   ```jsx
   const [queryMode, setQueryMode] = useState('auto');
   ```
3. Updated welcome message to IGNIS branding
4. Updated suggestions for furnace KPI queries:
   ```jsx
   const suggestions = [
       "Show OEE by furnace for last week",
       "What is the total downtime for Furnace 1?",
       "Compare yield percentage across all furnaces",
       "Show MTBF and MTTR trends",
       "What is the energy consumption by furnace?",
       "How to configure furnace parameters?",
       "What is EHS?",
       "Show production efficiency for January"
   ];
   ```
5. Added ModeToggle to header
6. Updated sidebar info (KPI Tables, Furnaces, BRD Docs)
7. Updated header text to "IGNIS Analytics Assistant"

---

### `.env.example`

**Complete rewrite** with all configuration options:
```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=davinci
DB_USER=davinci
DB_PASSWORD=your_password

# NLP Service
NLP_SERVICE_URL=http://localhost:8003

# RAG Service
RAG_SERVICE_URL=http://localhost:8004

# LLM (Groq)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# Optional: Redis, Ollama
```

---

## Architecture Compliance

✅ **Follows the NLP-to-SQL POC Implementation Workflow diagram exactly**:

| Diagram Component | Implementation |
|-------------------|----------------|
| React Frontend | `frontend/src/App.jsx` |
| Message Input | Input component in App.jsx |
| History Display | Messages state |
| Loading States | isLoading state |
| Django Backend | `backend/` |
| API Endpoint (views.py) | `/api/chatbot/chat/` |
| Query Validator | `SQLValidator` class |
| Safe SQL Executor | `execute_safe_query()` |
| Response Formatter | `response_formatter.py` |
| NLP Microservice | `nlp_service/` |
| LangChain Agent | `prompts.py`, `prompts_v2.py` |
| Security Guardrails | `guardrails.py` |
| Schema Metadata Cache | `schema_loader.py` |
| LLM Provider | Groq API |
| PostgreSQL Database | Configured in settings.py |

---

## Security Principles Implemented

| Principle | File | Implementation |
|-----------|------|----------------|
| Query Allowlist (SELECT only) | `views.py` L197 | Only SELECT allowed |
| Schema Restriction | `exposed_tables.py` | 29 table whitelist |
| Query Validation | `views.py`, `guardrails.py` | Double validation |
| Rate Limiting | `views.py` L38-104 | 30 requests/minute |
| Audit Logging | `views.py` L119-152 | All queries logged |
| Row-Level Security | `views.py` L252-279 | Organization filtering |

---

## Startup Commands (No Docker)

```bash
# Terminal 1: Django Backend
cd backend
.\venv\Scripts\activate
pip install djangorestframework  # If not installed
python manage.py runserver 0.0.0.0:8000

# Terminal 2: NLP Service
cd nlp_service
python main.py

# Terminal 3: Frontend
cd frontend
npm install
npm start
```

---

## Testing Commands

```bash
# Test schema endpoint
curl http://localhost:8000/api/chatbot/schema/

# Test chat endpoint
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Show OEE for last week"}'

# Test health
curl http://localhost:8000/api/chatbot/health/

# Run accuracy tests
cd nlp_service
python accuracy_tester.py
```

---

## File Structure After Changes

```
metalquery/
├── backend/
│   ├── chatbot/
│   │   ├── services/           # NEW FOLDER
│   │   │   ├── __init__.py
│   │   │   ├── nlp_service_client.py
│   │   │   ├── rag_service_client.py
│   │   │   ├── query_router.py
│   │   │   └── response_formatter.py
│   │   ├── serializers.py      # NEW
│   │   └── views.py            # MODIFIED
│   ├── config/
│   │   └── settings.py         # MODIFIED
│   └── ignis/
│       └── schema/             # NEW FOLDER
│           ├── __init__.py
│           ├── exposed_tables.py
│           └── schema_definitions.py
├── nlp_service/
│   ├── nlp/                    # NEW FOLDER
│   │   ├── __init__.py
│   │   └── response_formatter.py
│   └── guardrails.py           # MODIFIED
├── frontend/
│   └── src/
│       ├── config.js           # NEW
│       ├── App.jsx             # MODIFIED
│       └── components/
│           ├── ModeToggle.jsx  # NEW
│           ├── ModeToggle.css  # NEW
│           └── hooks/          # NEW FOLDER
│               └── useQuery.js
└── .env.example                # MODIFIED
```
