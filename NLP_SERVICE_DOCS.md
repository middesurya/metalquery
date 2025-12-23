# MetalQuery - NLP-to-SQL + BRD RAG Service Documentation

A hybrid natural language system for the IGNIS industrial furnace database. Converts questions to SQL queries or answers from BRD documents.

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    FRONTEND     │────▶│  DJANGO BACKEND │────▶│   NLP SERVICE   │
│    (React)      │     │   (Port 8000)   │     │   (Port 8003)   │
│    Port 3000    │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                        │
                               │                 ┌──────┴──────┐
                               ▼                 ▼             ▼
                        ┌─────────────┐   ┌───────────┐  ┌───────────┐
                        │  PostgreSQL │   │ Groq API  │  │ ChromaDB  │
                        │   Database  │   │ LLM Model │  │ (BRD RAG) │
                        └─────────────┘   └───────────┘  └───────────┘
```

### Security Boundary
- **Django** owns the database connection
- **NLP Service** only generates SQL, never executes it
- All SQL is validated before execution (defense in depth)

---

## 📁 Project Structure

```
metalquery/
├── .env                       # Environment variables (REQUIRED)
├── .env.example               # Template for .env
├── start_services.bat         # One-click startup script
│
├── backend/                   # Django Backend (Port 8000)
│   ├── chatbot/
│   │   ├── views.py          # Chat API, SQL validation & execution
│   │   ├── urls.py           # Routes (/chat/, /schema/, /health/)
│   │   └── relevant_models.py # Exposed tables whitelist
│   ├── ignis/
│   │   └── models.py         # Django ORM models for KPI tables
│   ├── config/
│   │   └── settings.py       # Django settings (reads from .env)
│   └── manage.py
│
├── nlp_service/               # FastAPI NLP Service (Port 8003)
│   ├── main.py               # FastAPI app, hybrid SQL+BRD routing
│   ├── config.py             # Loads GROQ_API_KEY from .env
│   ├── prompts_v2.py         # Schema-aware prompts (29 tables)
│   ├── diagnostic.py         # SQL validation diagnostics
│   ├── guardrails.py         # SQL security validation
│   ├── schema_loader.py      # Fetches schema from Django
│   ├── query_router.py       # Routes questions to SQL or BRD
│   ├── brd_rag.py            # BRD document retrieval
│   ├── brd_loader.py         # PDF ingestion for BRD
│   ├── brd/                   # BRD PDF documents
│   └── chroma_db/             # Vector database for BRD
│
└── frontend/                  # React Frontend (Port 3000)
    └── src/
        ├── App.jsx           # Main chat interface
        └── config.js         # API configuration
```

---

## ⚙️ Environment Configuration

### Required `.env` File

Copy `.env.example` to `.env` and fill in your values:

```env
# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password_here

# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

# NLP Service
NLP_SERVICE_HOST=localhost
NLP_SERVICE_PORT=8003
NLP_SERVICE_URL=http://localhost:8003

# LLM (REQUIRED - Get from https://console.groq.com/keys)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### Configuration Files

| File | Purpose |
|------|---------|
| `nlp_service/config.py` | Loads GROQ_API_KEY, validates on startup |
| `backend/config/settings.py` | Django settings, database connection |
| `frontend/src/config.js` | API URL configuration |

---

## 🚀 Quick Start

### Option 1: Use Startup Script
```powershell
cd metalquery
.\start_services.bat
```

### Option 2: Manual Start

**Terminal 1: Django Backend**
```bash
cd backend
..\venv\Scripts\activate
python manage.py runserver
# Runs on http://localhost:8000
```

**Terminal 2: NLP Service**
```bash
cd nlp_service
..\venv\Scripts\activate
python main.py
# Runs on http://localhost:8003
```

**Terminal 3: React Frontend**
```bash
cd frontend
npm start
# Runs on http://localhost:3000
```

---

## 📊 Supported Tables (29 Total)

### KPI Tables (20)

| Table | Description | Value Column | Aggregation |
|-------|-------------|--------------|-------------|
| `kpi_overall_equipment_efficiency_data` | OEE percentage | `oee_percentage` | AVG |
| `kpi_defect_rate_data` | Defect rate | `defect_rate` | AVG |
| `kpi_energy_efficiency_data` | kWh/ton | `energy_efficiency` | AVG |
| `kpi_energy_used_data` | Energy consumption | `energy_used` | SUM |
| `kpi_downtime_data` | Downtime hours | `downtime_hours` | SUM |
| `kpi_mean_time_between_failures_data` | MTBF | `mtbf_hours` | AVG |
| `kpi_mean_time_to_repair_data` | MTTR | `mttr_hours` | AVG |
| `kpi_mean_time_between_stoppages_data` | MTBS | `mtbs_hours` | AVG |
| `kpi_yield_data` | Yield % | `yield_percentage` | AVG |
| `kpi_first_pass_yield_data` | FPY % | `first_pass_yield` | AVG |
| `kpi_rework_rate_data` | Rework % | `rework_rate_percentage` | AVG |
| `kpi_resource_capacity_utilization_data` | Capacity % | `utilization_percentage` | AVG |
| `kpi_quantity_produced_data` | Units produced | `quantity_produced` | SUM |
| `kpi_output_rate_data` | Output rate | `output_rate_percentage` | AVG |
| `kpi_production_efficiency_data` | Production efficiency | `production_efficiency_percentage` | AVG |
| `kpi_on_time_delivery_data` | OTD % | `on_time_delivery_percentage` | AVG |
| `kpi_cycle_time_data` | Cycle time | `cycle_time` | AVG |
| `kpi_maintenance_compliance_data` | Compliance % | `compliance_percentage` | AVG |
| `kpi_planned_maintenance_data` | Planned maintenance | `planned_maintenance_percentage` | AVG |
| `kpi_safety_incidents_reported_data` | Safety incidents | `incidents_percentage` | AVG |

### Core Process Tables (3)

| Table | Description |
|-------|-------------|
| `core_process_tap_production` | Tap production with cast weights |
| `core_process_tap_process` | Tap tracking and status |
| `core_process_tap_grading` | Quality grading allocation |

### Master/Config Tables (6)

| Table | Description |
|-------|-------------|
| `furnace_furnaceconfig` | Furnace master data |
| `furnace_config_parameters` | Furnace configuration |
| `plant_plant` | Plant definitions |
| `log_book_furnace_down_time_event` | Downtime events |
| `log_book_reasons` | Reason codes |
| `log_book_downtime_type_master` | Downtime types |

---

## 🧠 SQL Generation Logic

### Query Routing (`query_router.py`)
The system automatically routes questions to:
- **SQL Path**: For data queries (OEE, downtime, production, etc.)
- **BRD Path**: For documentation/process questions

### Prompt Engineering (`prompts_v2.py`)

**Key Components:**
1. **TABLE_SCHEMA**: Complete mapping of 29 tables with columns, value columns, and aggregation types
2. **SYSTEM_PROMPT**: Comprehensive SQL generation rules
3. **FEW_SHOT_EXAMPLES**: 30+ example queries for pattern learning
4. **SchemaAnalyzer**: Finds best matching table for questions

### Aggregation Rules

| User Intent | Aggregation | Example |
|-------------|-------------|---------|
| "total", "sum" | SUM() | Total downtime last year |
| "average", "avg" | AVG() | Average OEE by furnace |
| "count", "how many" | COUNT() | How many events |
| "trend", "show" | NONE | Show OEE trend (raw data) |

### Critical SQL Rules

```
CRITICAL SQL RULES FOR AGGREGATION:
├─ If using aggregate functions (SUM, AVG, COUNT) WITHOUT GROUP BY:
│   └─ DO NOT use ORDER BY (single aggregate result)
├─ If using aggregate functions WITH GROUP BY:
│   └─ ORDER BY must use GROUP BY columns or aggregate expressions
├─ If NOT using aggregate functions:
│   └─ ORDER BY can use any column (e.g., ORDER BY date DESC)
```

---

## � Example Queries

### Simple Aggregations
```
✅ "Average OEE for Furnace 1 last month"
✅ "Total downtime by furnace"
✅ "Total downtime last year"
✅ "Which furnace has highest OEE?"
```

### Trend/Raw Data Queries
```
✅ "Show OEE trend for Furnace 2"
✅ "Recent tap production"
✅ "Defect rate trend for Furnace 2"
```

### Multi-Table JOINs
```
✅ "Average OEE by furnace with furnace names"
✅ "Downtime events with reasons for Furnace 1"
✅ "OEE by plant"
```

---

## � API Endpoints

### Django Backend (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chatbot/chat/` | POST | Hybrid chat (SQL + BRD) |
| `/api/chatbot/schema/` | GET | Get database schema |
| `/api/chatbot/health/` | GET | Health check |

### NLP Service (Port 8003)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Hybrid endpoint (routes SQL vs BRD) |
| `/api/v1/generate-sql` | POST | SQL generation only |
| `/api/v1/format-response` | POST | Format results as text |
| `/api/v1/routing-test` | GET | Test query routing |
| `/health` | GET | Health check |

---

## � Security Features

### SQL Guardrails (`guardrails.py`)
- ✅ Only SELECT queries allowed
- ✅ No dangerous keywords: DROP, DELETE, INSERT, UPDATE
- ✅ Table allowlist enforcement
- ✅ Single statement only (no semicolon injection)

### Django Validation (Defense in Depth)
- ✅ SQL validated again before execution
- ✅ Blocked patterns: `pg_`, `information_schema`, `--`
- ✅ Query timeout: 30 seconds
- ✅ Row limit: 100 rows

### Audit Logging
- All queries logged with IP, question, SQL, success/failure

---

## �🛠️ Development

### Add New KPI Table

1. **Add Django Model** (`backend/ignis/models.py`)
2. **Add to Whitelist** (`backend/chatbot/relevant_models.py`)
3. **Add to Schema** (`nlp_service/prompts_v2.py` → `TABLE_SCHEMA`)
4. **Add Keywords** for matching
5. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Modify Prompt Behavior

Edit `nlp_service/prompts_v2.py`:
- `SYSTEM_PROMPT`: Core SQL generation rules
- `FEW_SHOT_EXAMPLES`: Add pattern examples
- `TABLE_SCHEMA`: Table definitions and keywords
- `resolve_aggregation()`: Override aggregation logic

---

## � Troubleshooting

### "NLP service unavailable"
```bash
# Check if NLP service is running
curl http://localhost:8003/health

# Restart NLP service
cd nlp_service
python main.py
```

### "GROQ_API_KEY not set"
1. Ensure `.env` file exists in project root
2. Add: `GROQ_API_KEY=your_key_here`
3. Get free key from: https://console.groq.com/keys

### SQL Validation Errors
- Check generated SQL in terminal logs
- Verify column names match schema
- Use `furnace_no` not `furnace_id`

---

## �📌 Version History

| Version | Date | Changes |
|---------|------|---------|
| 5.0.0 | Dec 2024 | Hybrid SQL + BRD RAG, Query Router |
| 4.0.0 | Dec 2024 | Schema-aware prompts, Diagnostics |
| 3.0.0 | Dec 2024 | Multi-table JOINs support |
| 2.0.0 | Dec 2024 | Enhanced prompts, 29 tables |
| 1.0.0 | Dec 2024 | Initial release with Groq LLM |

---

## 📄 License

Internal Use Only - IGNIS Project
