# MetalQuery - Architecture & Flow Documentation

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

**MetalQuery** is a Natural Language to SQL (NL2SQL) chatbot that allows users to query a metallurgy materials database using plain English. The system uses GPT-4 to convert questions into SQL queries, executes them securely, and returns formatted responses.

### Key Capabilities
- Convert natural language questions to SQL
- Execute SQL queries against PostgreSQL
- Format results in human-readable responses
- Display data in interactive tables

### Technology Stack
| Layer | Technology |
|-------|------------|
| Frontend | React 18 |
| Backend Gateway | Django 4.2 |
| NLP Service | FastAPI + LangChain |
| LLM Provider | OpenAI GPT-4o-mini |
| Database | PostgreSQL |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        React Frontend (Port 3000)                        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │    │
│  │  │  Chat Input  │  │  Message     │  │  Results     │  │  SQL        │  │    │
│  │  │  Component   │  │  Display     │  │  Table       │  │  Viewer     │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP POST /api/chatbot/chat/
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DJANGO BACKEND (Port 8000)                             │
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
          │ HTTP POST /api/v1/format-response             │
          ▼                                               ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│   NLP MICROSERVICE (Port 8001)  │         │      POSTGRESQL DATABASE        │
│  ═══════════════════════════════│         │  ═══════════════════════════════│
│   🤖 AI BOUNDARY - NO DB ACCESS │         │                                 │
│  ┌─────────────────────────────┐│         │  ┌─────────────────────────────┐│
│  │  LangChain Agent            ││         │  │  materials (827 rows)       ││
│  │  ├── prompts.py             ││         │  │  material_properties        ││
│  │  ├── guardrails.py          ││         │  │  material_categories        ││
│  │  └── schema_loader.py       ││         │  │  material_standards         ││
│  └─────────────────────────────┘│         │  │  heat_treatments            ││
│               │                 │         │  │  material_full_info (VIEW)  ││
│               ▼                 │         │  └─────────────────────────────┘│
│  ┌─────────────────────────────┐│         └─────────────────────────────────┘
│  │  OpenAI GPT-4o-mini         ││
│  │  (External API)             ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

---

## Components

### 1. React Frontend (`/frontend`)

**Purpose:** User interface for the chatbot

**Key Files:**
```
frontend/
├── src/
│   ├── App.jsx          # Main application component
│   ├── App.css          # Styling (dark theme)
│   └── index.js         # Entry point
├── public/
│   └── index.html       # HTML template with fonts
└── package.json         # Dependencies
```

**Features:**
- Chat message display with user/bot avatars
- Results table with formatted values (MPa, kg/m³)
- SQL query viewer with copy button
- Suggestion chips for quick queries
- Loading states and error handling

### 2. Django Backend (`/backend`)

**Purpose:** Security gateway, database owner, request orchestration

**Key Files:**
```
backend/
├── chatbot/
│   ├── views.py         # Main chat endpoint with security
│   └── urls.py          # URL routing
├── config/
│   ├── settings.py      # Django configuration
│   └── urls.py          # Root URL config
└── requirements.txt     # Python dependencies
```

**Security Features:**
- **Rate Limiting:** 30 requests/minute per IP
- **SQL Validation:** Defense-in-depth validation
- **Audit Logging:** All queries logged
- **Query Timeout:** 10 second maximum
- **Row-Level Security:** Prepared for multi-tenancy

### 3. NLP Microservice (`/nlp_service`)

**Purpose:** Natural language to SQL conversion (NO database access)

**Key Files:**
```
nlp_service/
├── main.py              # FastAPI application
├── config.py            # Environment configuration
├── prompts.py           # LLM prompts for metallurgy domain
├── guardrails.py        # SQL security validation
├── schema_loader.py     # Database schema introspection
└── requirements.txt     # Python dependencies
```

**Endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/generate-sql` | POST | Convert question to SQL |
| `/api/v1/format-response` | POST | Format results to NL |
| `/api/v1/schema` | GET | Get database schema |
| `/health` | GET | Health check |

---

## Request Flow

### Complete Flow Diagram

```
┌──────────┐                                                              
│   USER   │                                                              
└────┬─────┘                                                              
     │ 1. Ask: "What steel has highest tensile strength?"                 
     ▼                                                                    
┌──────────────────────────────────────────────────────────────────────┐  
│                         REACT FRONTEND                                │  
│  • Capture user input                                                 │  
│  • Show loading state                                                 │  
│  • Call Django API                                                    │  
└────┬─────────────────────────────────────────────────────────────────┘  
     │ 2. POST /api/chatbot/chat/ { question: "..." }                    
     ▼                                                                    
┌──────────────────────────────────────────────────────────────────────┐  
│                         DJANGO BACKEND                                │  
│  Step 2a: Rate Limiting                                               │  
│  ├── Check IP request count                                           │  
│  └── Block if > 30/min                                                │  
│                                                                        │  
│  Step 2b: Forward to NLP Service ─────────────────────────────────────┼──┐
└──────────────────────────────────────────────────────────────────────┘  │
                                                                           │
     ┌─────────────────────────────────────────────────────────────────────┘
     │ 3. POST /api/v1/generate-sql { question: "..." }                    
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                       NLP MICROSERVICE                                │   
│  Step 3a: Load Schema Context                                         │   
│  ├── Get table definitions from cache                                 │   
│  └── Build schema description for LLM                                 │   
│                                                                        │   
│  Step 3b: Generate SQL via LLM ───────────────────────────────────────┼───┐
└──────────────────────────────────────────────────────────────────────┘   │
                                                                            │
     ┌──────────────────────────────────────────────────────────────────────┘
     │ 4. API Call to OpenAI                                               
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                         OPENAI GPT-4                                  │   
│  Input: System prompt + Schema + User question                        │   
│  Output: SQL Query                                                    │   
│                                                                        │   
│  "SELECT name, grade, ultimate_tensile_strength                       │   
│   FROM materials m                                                    │   
│   JOIN material_properties mp ON m.id = mp.material_id                │   
│   WHERE m.category_id = (SELECT id FROM material_categories           │   
│                          WHERE name ILIKE 'Steel')                    │   
│   ORDER BY mp.ultimate_tensile_strength DESC                          │   
│   LIMIT 10;"                                                          │   
└────┬─────────────────────────────────────────────────────────────────┘   
     │ 5. Return generated SQL                                             
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                       NLP MICROSERVICE                                │   
│  Step 5a: Validate SQL (Guardrails)                                   │   
│  ├── Must start with SELECT                                           │   
│  ├── No INSERT/UPDATE/DELETE/DROP                                     │   
│  └── Only allowed tables                                              │   
│                                                                        │   
│  Step 5b: Return validated SQL to Django                              │   
└────┬─────────────────────────────────────────────────────────────────┘   
     │ 6. Return { success: true, sql: "SELECT..." }                       
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                         DJANGO BACKEND                                │   
│  Step 6a: Validate SQL Again (Defense in Depth)                       │   
│  ├── Double-check for blocked keywords                                │   
│  ├── Check for SQL injection patterns                                 │   
│  └── Verify single statement                                          │   
│                                                                        │   
│  Step 6b: Execute Query Safely ───────────────────────────────────────┼───┐
└──────────────────────────────────────────────────────────────────────┘   │
                                                                            │
     ┌──────────────────────────────────────────────────────────────────────┘
     │ 7. Execute SQL Query                                                
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                       POSTGRESQL DATABASE                             │   
│  • Execute query with 10s timeout                                     │   
│  • Return result rows                                                 │   
│                                                                        │   
│  Results:                                                             │   
│  ┌─────────────────────────────────────────────────────────────────┐ │   
│  │ name              │ grade    │ ultimate_tensile_strength        │ │   
│  ├───────────────────┼──────────┼──────────────────────────────────┤ │   
│  │ Steel SAE 5160    │ SAE 5160 │ 2220.00                          │ │   
│  │ Steel SAE 9260    │ SAE 9260 │ 2103.00                          │ │   
│  └─────────────────────────────────────────────────────────────────┘ │   
└────┬─────────────────────────────────────────────────────────────────┘   
     │ 8. Return query results                                             
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                         DJANGO BACKEND                                │   
│  Step 8a: Log Query (Audit)                                           │   
│  ├── IP address                                                       │   
│  ├── Question                                                         │   
│  ├── SQL                                                              │   
│  └── Row count                                                        │   
│                                                                        │   
│  Step 8b: Format Response via NLP ────────────────────────────────────┼───┐
└──────────────────────────────────────────────────────────────────────┘   │
                                                                            │
     ┌──────────────────────────────────────────────────────────────────────┘
     │ 9. POST /api/v1/format-response { question, sql, results }          
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                       NLP MICROSERVICE                                │   
│  Call OpenAI to format results in natural language                    │   
│                                                                        │   
│  Output: "The steel with the highest tensile strength is             │   
│           Steel SAE 5160 with 2,220 MPa, followed by                 │   
│           Steel SAE 9260 with 2,103 MPa..."                          │   
└────┬─────────────────────────────────────────────────────────────────┘   
     │ 10. Return formatted response                                       
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                         DJANGO BACKEND                                │   
│  Build final response:                                                │   
│  {                                                                    │   
│    success: true,                                                     │   
│    response: "The steel with highest tensile strength...",           │   
│    sql: "SELECT name, grade...",                                      │   
│    results: [...],                                                    │   
│    row_count: 10                                                      │   
│  }                                                                    │   
└────┬─────────────────────────────────────────────────────────────────┘   
     │ 11. Return to React                                                 
     ▼                                                                     
┌──────────────────────────────────────────────────────────────────────┐   
│                         REACT FRONTEND                                │   
│  • Display bot message with natural language response                 │   
│  • Show expandable SQL query                                          │   
│  • Render results in formatted table                                  │   
│  • Add message to chat history                                        │   
└────┬─────────────────────────────────────────────────────────────────┘   
     │ 12. Display to user                                                 
     ▼                                                                     
┌──────────┐                                                              
│   USER   │  ← Sees answer, SQL, and data table                          
└──────────┘                                                              
```

---

## Security Architecture

### The Security Boundary

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRUSTED ZONE (Has DB Access)                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Django Backend                                                │  │
│  │  • Owns database connection                                    │  │
│  │  • Validates all SQL before execution                          │  │
│  │  • Rate limits requests                                        │  │
│  │  • Logs all queries for audit                                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Database                                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                               ▲
                               │
═══════════════════════════════╪═══════════════════════════════════════
           SECURITY BOUNDARY   │  AI NEVER CROSSES THIS LINE
═══════════════════════════════╪═══════════════════════════════════════
                               │
┌─────────────────────────────────────────────────────────────────────┐
│                  UNTRUSTED ZONE (No DB Access)                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  NLP Microservice                                              │  │
│  │  • ONLY generates SQL (never executes)                         │  │
│  │  • ONLY formats responses                                      │  │
│  │  • Has NO database credentials                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  OpenAI API (External)                                         │  │
│  │  • Generates SQL based on prompts                              │  │
│  │  • No knowledge of actual data                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Multi-Layer Validation

```
User Input: "Show me all users; DROP TABLE materials;"
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Layer 1: NLP Service (guardrails.py)                                │
│ ├── Check: SQL starts with SELECT? ✓                               │
│ ├── Check: Contains DROP keyword? ✗ BLOCKED                        │
│ └── Result: Returns error before reaching Django                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (If passed Layer 1)
┌─────────────────────────────────────────────────────────────────────┐
│ Layer 2: Django Backend (SQLValidator)                              │
│ ├── Check: SQL starts with SELECT? ✓                               │
│ ├── Check: Contains blocked keywords? ✗ BLOCKED                    │
│ ├── Check: Multiple statements (;)? ✗ BLOCKED                      │
│ └── Result: Query rejected, logged for security review             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (If passed Layer 2)
┌─────────────────────────────────────────────────────────────────────┐
│ Layer 3: PostgreSQL                                                 │
│ ├── Statement timeout: 10 seconds                                  │
│ ├── Connection: Read-only user (recommended)                       │
│ └── Results limited to 100 rows                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Code Walkthrough

### 1. User Sends Question (React)

```javascript
// frontend/src/App.jsx
const sendMessage = async (text = inputValue) => {
    // ...
    const response = await fetch(`${API_URL}/api/chatbot/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
    });
    // ...
};
```

### 2. Django Receives Request

```python
# backend/chatbot/views.py
@csrf_exempt
@require_http_methods(["POST"])
@rate_limit  # Check rate limiting
def chat(request):
    question = body.get('question', '').strip()
    
    # Step 1: Call NLP service for SQL generation
    nlp_response = requests.post(
        f"{NLP_SERVICE_URL}/api/v1/generate-sql",
        json={'question': question}
    )
```

### 3. NLP Service Generates SQL

```python
# nlp_service/main.py
@app.post("/api/v1/generate-sql")
async def generate_sql(request: GenerateSQLRequest):
    # Get schema context
    schema_context = schema_loader.get_schema_context()
    
    # Build prompt with schema
    system_prompt = get_sql_generation_prompt(schema_context)
    
    # Call LLM
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=request.question)
    ]
    response = llm.invoke(messages)
    generated_sql = response.content.strip()
    
    # Validate with guardrails
    is_valid, error = guardrails.validate(generated_sql)
```

### 4. Django Validates and Executes

```python
# backend/chatbot/views.py
# Validate SQL (defense in depth)
is_valid, error = SQLValidator.validate(sql)
if not is_valid:
    return JsonResponse({'success': False, 'error': error})

# Execute safely
results = execute_safe_query(sql)

# Format response via NLP
format_response = requests.post(
    f"{NLP_SERVICE_URL}/api/v1/format-response",
    json={'question': question, 'sql': sql, 'results': results}
)
```

---

## Database Schema

```sql
-- Main tables
CREATE TABLE material_standards (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE,     -- ANSI, ISO, DIN
    name VARCHAR(100)
);

CREATE TABLE material_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE     -- Steel, Aluminum, Copper, etc.
);

CREATE TABLE heat_treatments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE     -- annealed, tempered, normalized
);

CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(50) UNIQUE,
    standard_id INTEGER REFERENCES material_standards(id),
    category_id INTEGER REFERENCES material_categories(id),
    name VARCHAR(200),
    grade VARCHAR(100),
    heat_treatment_id INTEGER REFERENCES heat_treatments(id),
    description TEXT,
    is_stainless BOOLEAN,
    is_in_use BOOLEAN
);

CREATE TABLE material_properties (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(id),
    ultimate_tensile_strength NUMERIC(10,2),  -- MPa
    yield_strength NUMERIC(10,2),              -- MPa
    elastic_modulus NUMERIC(12,2),             -- MPa
    shear_modulus NUMERIC(12,2),               -- MPa
    poisson_ratio NUMERIC(4,3),
    density NUMERIC(10,2),                     -- kg/m³
    brinell_hardness NUMERIC(10,2),
    vickers_hardness NUMERIC(10,2),
    elongation NUMERIC(6,2)                    -- %
);

-- Convenient view for queries
CREATE VIEW material_full_info AS
SELECT 
    m.id, ms.code as standard, mc.name as category,
    m.name as material_name, m.grade, ht.name as heat_treatment,
    mp.ultimate_tensile_strength, mp.yield_strength,
    mp.elastic_modulus, mp.density, mp.brinell_hardness
FROM materials m
LEFT JOIN material_standards ms ON m.standard_id = ms.id
LEFT JOIN material_categories mc ON m.category_id = mc.id
LEFT JOIN heat_treatments ht ON m.heat_treatment_id = ht.id
LEFT JOIN material_properties mp ON mp.material_id = m.id;
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# PostgreSQL
DB_HOST=localhost
DB_PORT=5433
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# Services
NLP_SERVICE_HOST=localhost
NLP_SERVICE_PORT=8001
```

### Starting the Services

```bash
# Terminal 1: NLP Service
cd nlp_service
.\venv\Scripts\activate
python main.py
# Runs on http://localhost:8001

# Terminal 2: Django Backend
cd backend
.\venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
# Runs on http://localhost:8000

# Terminal 3: React Frontend
cd frontend
npm start
# Runs on http://localhost:3000
```

---

## Summary

| Component | Responsibility | Database Access |
|-----------|---------------|-----------------|
| React Frontend | User interface | ❌ None |
| Django Backend | Security, DB access, orchestration | ✅ Yes (Owner) |
| NLP Service | SQL generation, response formatting | ❌ None |
| OpenAI GPT-4 | Natural language processing | ❌ None |
| PostgreSQL | Data storage | N/A (is the DB) |

**Key Principle:** The AI (NLP Service + OpenAI) never has direct database access. Django acts as the security gateway and is the sole owner of database credentials and connections.
