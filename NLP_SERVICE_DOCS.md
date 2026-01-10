# MetalQuery - NLP Service Documentation

A hybrid natural language system for the IGNIS industrial furnace database. Converts questions to SQL queries or answers from BRD documents.

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    FRONTEND     │────▶│  DJANGO BACKEND │────▶│   NLP SERVICE   │
│    (React)      │     │   (Port 8000)   │     │   (Port 8003)   │
│    Port 5173    │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                        │
                               │                 ┌──────┴──────┐
                               ▼                 ▼             ▼
                        ┌─────────────┐   ┌───────────┐  ┌───────────┐
                        │  PostgreSQL │   │ Groq API  │  │ ChromaDB  │
                        │   Database  │   │ LLM Model │  │(Multimodal│
                        └─────────────┘   └───────────┘  │ BRD RAG)  │
                                                         └───────────┘
```

### Key Principles
- **Django** owns the database connection
- **NLP Service** only generates SQL, never executes it
- **RBAC** filtering happens at Django, allowed_tables sent to NLP
- All SQL is validated before execution (defense in depth)

### Multimodal RAG Features
- **961 text chunks** from 33 BRD PDF documents
- **389 extracted images** (screenshots, diagrams, flowcharts)
- **Intelligent filtering** removes logos, icons, and repeated headers
- **Image lightbox** for full-size image viewing

---

## Project Structure

```
metalquery/
├── backend/                   # Django Backend (Port 8000)
│   ├── chatbot/
│   │   ├── views.py          # Chat API, RBAC enforcement, SQL execution
│   │   ├── urls.py           # Routes (/chat/, /schema/, /health/)
│   │   └── services/
│   │       └── rbac_service.py # Token → allowed_tables resolution
│   ├── ignis/
│   │   ├── models.py         # Django ORM models for KPI tables
│   │   └── schema/
│   │       └── exposed_tables.py # Permission mappings
│   └── config/
│       └── settings.py       # Django settings
│
├── nlp_service/               # FastAPI NLP Service (Port 8003)
│   ├── main.py               # FastAPI app, hybrid SQL+BRD routing, viz pipeline
│   ├── config.py             # Loads GROQ_API_KEY from .env
│   ├── prompts_v2.py         # Schema-aware prompts (29 tables)
│   ├── query_router.py       # Routes questions to SQL or BRD
│   ├── brd_rag.py            # BRD document retrieval
│   ├── guardrails.py         # SQL validation with comment stripping
│   ├── sql_guardrails.py     # SQL guardrails with table allowlist
│   ├── security/             # Security modules
│   │   ├── flipping_detector.py
│   │   ├── anomaly_detector.py
│   │   └── sql_validator.py
│   ├── visualization/        # LIDA-inspired chart generation
│   │   ├── viz_summarizer.py
│   │   ├── viz_goal_finder.py
│   │   └── viz_config_generator.py
│   ├── brd/                   # BRD PDF documents
│   └── chroma_db/             # Vector database for BRD
│
└── frontend/                  # React Frontend (Port 5173)
    └── src/
        ├── App.jsx           # Main chat interface
        └── config.js         # API configuration (port 8001)
```

---

## Quick Start

### Start Services

```bash
# Terminal 1: Django Backend (Port 8000)
cd backend
python manage.py runserver 0.0.0.0:8000

# Terminal 2: NLP Service (Port 8003)
cd nlp_service
python main.py
# Loads 289 dynamic keywords from schema
# Initializes BRD RAG (961 chunks, 389 images)

# Terminal 3: React Frontend (Port 5173)
cd frontend
npm start
```

---

## Supported Tables (29 Total)

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

## RBAC Integration

### How It Works

1. **Django receives request** with Bearer token
2. **RBACService** resolves token → user → roles → permissions
3. **allowed_tables** whitelist is built from:
   - Function code permissions (PLT_CFG, FUR_MNT, etc.)
   - KPI metric permissions (OEE, DOWNTIME, etc.)
4. **NLP Service** receives `{question, allowed_tables}`
5. **Schema filtering** in prompts_v2.py filters TABLE_SCHEMA
6. **LLM only sees** user's permitted tables

### Schema Filtering (prompts_v2.py)

```python
def build_prompt_with_schema(question: str, allowed_tables: list = None):
    """Build prompt with filtered schema based on RBAC permissions."""

    if allowed_tables:
        # Filter TABLE_SCHEMA to only include allowed tables
        filtered_schema = {
            table: info
            for table, info in TABLE_SCHEMA.items()
            if table in allowed_tables
        }
    else:
        filtered_schema = TABLE_SCHEMA

    # Build prompt with filtered schema
    schema_text = format_schema(filtered_schema)
    return f"{SYSTEM_PROMPT}\n\nAvailable tables:\n{schema_text}"
```

---

## Visualization Pipeline (LIDA-inspired)

The NLP service includes a LIDA-inspired visualization pipeline that automatically generates Recharts-compatible chart configurations.

### Pipeline Components

| Component | File | Purpose |
|-----------|------|---------|
| DataSummarizer | `viz_summarizer.py` | Column classification (numeric/categorical/temporal) |
| VizGoalFinder | `viz_goal_finder.py` | Chart type detection using heuristic rules |
| VizConfigGenerator | `viz_config_generator.py` | Recharts-compatible JSON config generation |
| VizValidator | `viz_validator.py` | Config validation |

### Chart Type Detection

| Query Pattern | Chart Type | Example |
|---------------|------------|---------|
| "by furnace", "compare", "rank" | Bar | "Compare OEE between furnaces" |
| "trend", "last week", "over time" | Line | "Show OEE trend last week" |
| "breakdown", "by reason", "distribution" | Pie | "Downtime by reason" |
| Single OEE/yield/percentage | Gauge | "Average OEE for all furnaces" |
| Single total/count | KPI Card | "Total production today" |

### Detection Keywords

**Bar Chart triggers:**
- `compare`, `versus`, `vs`, `between`
- `by furnace`, `by shift`, `by machine`, `by plant`
- `which furnace`, `which shift`, `rank`, `top`, `bottom`

**Line Chart triggers:**
- `trend`, `over time`, `history`
- `last week`, `last month`, `last 7 days`, `last 30 days`
- `daily`, `weekly`, `monthly`

**Pie Chart triggers:**
- `breakdown`, `distribution`, `proportion`
- `by reason`, `by type`, `by category`, `by cause`

**Gauge triggers (single row with percentage):**
- Column contains: `oee`, `yield`, `efficiency`, `rate`, `percent`

### Column Classification

The `DataSummarizer` classifies columns to determine chart axes:

```python
# Temporal patterns (for X-axis in line charts)
TEMPORAL_PATTERNS = ['date', 'timestamp', 'created_at', 'start_time', 'shift_date']

# Metric patterns that look temporal but are numeric values
METRIC_TIME_PATTERNS = ['cycle_time', 'downtime', 'mtbf', 'mttr', 'duration']

# Categorical patterns (for grouping/X-axis in bar/pie)
CATEGORICAL_PATTERNS = ['name', 'type', 'category', 'shift', 'furnace', 'reason']
```

### Generate Chart Config Endpoint

```http
POST /api/v1/generate-chart-config
Content-Type: application/json

{
  "question": "Show OEE by furnace",
  "results": [
    {"furnace_no": "F1", "avg_oee": 85.5},
    {"furnace_no": "F2", "avg_oee": 78.2}
  ]
}
```

**Response:**
```json
{
  "chart_config": {
    "type": "bar",
    "data": [...],
    "options": {
      "xAxis": {"dataKey": "furnace_no"},
      "bars": [{"dataKey": "avg_oee", "fill": "#3b82f6"}],
      "title": "OEE by furnace"
    }
  }
}
```

---

## SQL Generation Logic

### Query Routing (`query_router.py`)
The system automatically routes questions to:
- **SQL Path**: For data queries (OEE, downtime, production, etc.)
- **BRD Path**: For documentation/process questions

### Aggregation Rules

| User Intent | Aggregation | Example |
|-------------|-------------|---------|
| "total", "sum" | SUM() | Total downtime last year |
| "average", "avg" | AVG() | Average OEE by furnace |
| "count", "how many" | COUNT() | How many events |
| "trend", "show" | NONE | Show OEE trend (raw data) |

---

## API Endpoints

### Django Backend (Port 8000)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/chatbot/chat/` | POST | Bearer token | Main chat endpoint |
| `/api/chatbot/schema/` | GET | - | Get database schema |
| `/api/chatbot/health/` | GET | - | Health check |

### NLP Service (Port 8003)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Hybrid endpoint (routes SQL vs BRD) |
| `/api/v1/generate-sql` | POST | SQL generation only |
| `/api/v1/generate-chart-config` | POST | Chart config generation (Recharts) |
| `/api/v1/format-response` | POST | Format results as text |
| `/api/v1/brd-debug` | GET | BRD RAG debug info |
| `/api/brd-images/{file}` | GET | Serve extracted images |
| `/health` | GET | Health check |

### Request Format

```json
// POST /api/v1/chat
{
  "question": "Show OEE by furnace",
  "allowed_tables": ["kpi_oee", "furnace_furnaceconfig"]
}
```

### Response Format

```json
{
  "success": true,
  "type": "sql",
  "sql": "SELECT furnace_no, AVG(oee_percentage) FROM kpi_oee GROUP BY furnace_no",
  "confidence": 0.95
}
```

---

## Security Features

### NLP Service Security Layers

| Layer | Module | Purpose |
|-------|--------|---------|
| 1 | Flipping Detector | Jailbreak detection |
| 2 | Prompt Validator | Injection signatures |
| 3 | Red Team Detector | Attack patterns |
| 4 | Guardrails AI | PII/profanity filter |
| 5 | Query Guard | Relevance check |
| 6 | Schema Filter | Only allowed tables in prompt |

### SQL Guardrails

- Only SELECT queries allowed
- No dangerous keywords: DROP, DELETE, INSERT, UPDATE
- Table allowlist enforcement
- Single statement only (no semicolon injection)

---

## Example Queries

### SQL Queries
```
"Average OEE for Furnace 1 last month"
"Total downtime by furnace"
"Which furnace has highest OEE?"
"Show OEE trend for Furnace 2"
"Defect rate trend for Furnace 2"
```

### BRD Queries
```
"What is EHS?"
"How do I configure a new furnace?"
"Explain the grading plan process"
"What are user roles?"
```

---

## Troubleshooting

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

### "Unauthorized" errors
- Verify Bearer token is valid
- Check user has permissions for requested tables
- Superusers bypass RBAC (access all 29 tables)

---

**Last Updated:** 2026-01-09
