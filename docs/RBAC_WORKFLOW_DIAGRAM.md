# RBAC Workflow Diagram

## Complete Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              RBAC WORKFLOW DIAGRAM                               │
└─────────────────────────────────────────────────────────────────────────────────┘

  USER QUERY: "Show OEE by furnace"
        │
        ▼
┌───────────────────┐
│     FRONTEND      │
│   (React:5173)    │
│                   │
│ localStorage      │
│ ┌───────────────┐ │
│ │ authToken:xyz │ │
│ └───────────────┘ │
└─────────┬─────────┘
          │
          │  POST /api/chatbot/chat/
          │  Headers: Authorization: Bearer <token>
          │  Body: {"question": "Show OEE by furnace"}
          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DJANGO BACKEND (Port 8001)                              │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 1: Extract Token                                                      │ │
│  │         Authorization: Bearer xyz123... → token = "xyz123..."              │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 2: RBACService.get_allowed_tables(token)                              │ │
│  │                                                                            │ │
│  │   ┌──────────────────┐      ┌──────────────────┐                           │ │
│  │   │ users_usertoken  │ ───► │    users_user    │                           │ │
│  │   │ key = "xyz123"   │      │ id, is_superuser │                           │ │
│  │   └──────────────────┘      └────────┬─────────┘                           │ │
│  │                                      │                                      │ │
│  │              ┌───────────────────────┴───────────────────────┐              │ │
│  │              │                                               │              │ │
│  │              ▼                                               ▼              │ │
│  │   ┌─────────────────────┐                     ┌─────────────────────┐       │ │
│  │   │ IF is_superuser     │                     │ IF regular user     │       │ │
│  │   │ Return ALL 29 tables│                     │                     │       │ │
│  │   └─────────────────────┘                     └──────────┬──────────┘       │ │
│  │                                                          │                  │ │
│  │                                                          ▼                  │ │
│  │                                               ┌──────────────────┐          │ │
│  │                                               │  users_userrole  │          │ │
│  │                                               │  user → role_id  │          │ │
│  │                                               └────────┬─────────┘          │ │
│  │                                                        │                    │ │
│  │                              ┌─────────────────────────┴─────────────────┐  │ │
│  │                              │                                           │  │ │
│  │                              ▼                                           ▼  │ │
│  │                   ┌─────────────────────┐                 ┌──────────────────┐│
│  │                   │ users_rolepermission│                 │ users_role_kpis  ││
│  │                   │ role → function_code│                 │ role → kpi_code  ││
│  │                   │ (where view=true)   │                 │                  ││
│  │                   └──────────┬──────────┘                 └────────┬─────────┘│
│  │                              │                                     │         │ │
│  │                              ▼                                     ▼         │ │
│  │                   ┌─────────────────────┐                 ┌──────────────────┐│
│  │                   │FUNCTION_TABLE_MAPPING                 │KPI_TABLE_MAPPING ││
│  │                   │ PLT_CFG → plant_plant                 │ OEE → kpi_oee    ││
│  │                   │ FUR_MNT → furnace_*  │                │ YIELD → kpi_yield││
│  │                   │ LOG_BOOK → log_book_*│                │ DOWNTIME → ...   ││
│  │                   │ TAP_PROC → tap_*     │                │ (21 mappings)    ││
│  │                   └──────────┬──────────┘                 └────────┬─────────┘│
│  │                              │                                     │         │ │
│  │                              └──────────────┬──────────────────────┘         │ │
│  │                                             │                                │ │
│  │                                             ▼                                │ │
│  │                              ┌──────────────────────────────┐                │ │
│  │                              │      allowed_tables          │                │ │
│  │                              │ {"kpi_oee", "plant_plant",   │                │ │
│  │                              │  "furnace_furnaceconfig"}    │                │ │
│  │                              └──────────────────────────────┘                │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 3: Send to NLP Service                                                │ │
│  │         POST /api/v1/chat {question, allowed_tables}                       │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          NLP SERVICE (Port 8003)                                 │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ SECURITY LAYERS (5 checks)                                                 │ │
│  │ [1] Flipping Detector  → Jailbreak detection                               │ │
│  │ [2] Prompt Validator   → Injection signatures                              │ │
│  │ [3] Red Team Detector  → Attack patterns                                   │ │
│  │ [4] Guardrails AI      → PII/profanity                                     │ │
│  │ [5] Query Guard        → Relevance check                                   │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ SCHEMA FILTERING (prompts_v2.py)                                           │ │
│  │                                                                            │ │
│  │   Full TABLE_SCHEMA (29 tables)                                            │ │
│  │            │                                                               │ │
│  │            │  Filter by allowed_tables                                     │ │
│  │            ▼                                                               │ │
│  │   Filtered Schema (only user's tables)                                     │ │
│  │   ┌─────────────────────────────────┐                                      │ │
│  │   │ kpi_oee: furnace_id, oee_value  │  ◄── Only these shown to LLM        │ │
│  │   │ plant_plant: id, name           │                                      │ │
│  │   └─────────────────────────────────┘                                      │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ LLM (Groq llama-3.3-70b)                                                   │ │
│  │                                                                            │ │
│  │   Generates SQL using ONLY filtered schema                                 │ │
│  │   → SELECT AVG(oee_value) FROM kpi_oee GROUP BY furnace_id                │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ Returns: {sql: "SELECT...", type: "sql"}
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    DJANGO BACKEND - DEFENSE IN DEPTH                             │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 4: SQL Validation                                                     │ │
│  │                                                                            │ │
│  │   [1] SQLValidator - Block dangerous keywords                              │ │
│  │       (DROP, DELETE, INSERT, UPDATE, GRANT, etc.)                          │ │
│  │                                                                            │ │
│  │   [2] Table Validator - Extract tables from SQL                            │ │
│  │       SELECT * FROM kpi_oee → {"kpi_oee"}                                  │ │
│  │                                                                            │ │
│  │   [3] RBAC Check - Verify tables ⊆ allowed_tables                          │ │
│  │       {"kpi_oee"} ⊆ {"kpi_oee", "plant_plant"} → ✅ ALLOWED                │ │
│  │                                                                            │ │
│  │       If LLM hallucinated unauthorized table:                              │ │
│  │       {"kpi_oee", "secret_table"} ⊆ allowed → ❌ BLOCKED (403)             │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                           │
│                                      ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 5: Execute SQL on PostgreSQL                                          │ │
│  │         Returns query results                                              │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              RESPONSE TO USER                                    │
│                                                                                  │
│   {                                                                              │
│     "answer": "Here is the OEE data by furnace...",                             │
│     "data": [{"furnace_id": 1, "avg_oee": 85.2}, ...],                          │
│     "sql": "SELECT furnace_id, AVG(oee_value)..."                               │
│   }                                                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Simple Version

```
User Query
    │
    ▼
Frontend (React) ──► Token from localStorage
    │
    ▼
Django ──► [1] Validate Token
       ──► [2] Get User Roles
       ──► [3] Get Permissions (function codes + KPIs)
       ──► [4] Map to allowed_tables
    │
    ▼
NLP Service ──► Filter schema by allowed_tables
            ──► Generate SQL (LLM only sees allowed tables)
    │
    ▼
Django ──► [5] Validate SQL tables ⊆ allowed_tables
       ──► [6] Execute SQL
    │
    ▼
Response to User
```

---

## Error Scenarios

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ERROR SCENARIOS                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   No Token:          ──────────►  401 "Authentication required"                 │
│                                                                                  │
│   Invalid Token:     ──────────►  401 "Invalid or expired token"                │
│                                                                                  │
│   No Permissions:    ──────────►  403 "No table access permissions"             │
│                                                                                  │
│   Unauthorized       ──────────►  403 "Access denied to tables: xxx"            │
│   Table in SQL:                                                                  │
│                                                                                  │
│   SQL Injection:     ──────────►  Blocked by SQLValidator                       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Tables Used

### Authentication Flow

```
users_usertoken          users_user              users_userrole
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ key (token)     │────►│ id              │────►│ user_id         │
│ user_id         │     │ username        │     │ role_id         │
│ created         │     │ is_superuser    │     └────────┬────────┘
└─────────────────┘     └─────────────────┘              │
                                                         │
                        ┌────────────────────────────────┴────────────────────────┐
                        │                                                         │
                        ▼                                                         ▼
             users_rolepermission                                      users_role_kpis
             ┌─────────────────────┐                                  ┌─────────────────┐
             │ role_id             │                                  │ role_id         │
             │ function_master_id  │                                  │ kpi_metric_code │
             │ view (boolean)      │                                  └────────┬────────┘
             └──────────┬──────────┘                                           │
                        │                                                      │
                        ▼                                                      ▼
             FUNCTION_TABLE_MAPPING                                  KPI_TABLE_MAPPING
             ┌─────────────────────┐                                  ┌─────────────────┐
             │ PLT_CFG → plant_*   │                                  │ OEE → kpi_oee   │
             │ FUR_MNT → furnace_* │                                  │ YIELD → kpi_... │
             │ LOG_BOOK → log_*    │                                  │ (21 mappings)   │
             │ TAP_PROC → tap_*    │                                  └─────────────────┘
             └─────────────────────┘
```

---

## Security Layers

```
                              Request Flow
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 1: Rate Limiting                       │
│                     30 requests/min per IP                       │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 2: Token Validation                    │
│                     Django RBAC Service                          │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 3: NLP Security                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │  Flipping   │ │   Prompt    │ │  Red Team   │ │ Guardrails │ │
│  │  Detector   │ │  Validator  │ │  Detector   │ │     AI     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 4: Schema Filtering                    │
│                     Only allowed tables in LLM prompt            │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 5: SQL Validation                      │
│                     Block dangerous SQL + RBAC check             │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 6: Audit Logging                       │
│                     All queries logged with user context         │
└─────────────────────────────────────────────────────────────────┘
```
