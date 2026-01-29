# CHANGES.md - MetalQuery NLP-to-SQL Project

## [2026-01-29] Speech-to-Text & Export Features

### Overview
Added voice input capabilities using Faster-Whisper and export features for query results and charts.

### New Features
- **Speech-to-Text**: Voice input for natural language queries using Faster-Whisper
- **CSV Export**: Download query results as CSV files
- **Chart Export**: Download charts as PNG images using html2canvas
- **Gallery Export**: Download images from BRD RAG results
- **Collapsible SQL**: SQL query section is now collapsible for cleaner UI

### Files Created

| File | Purpose |
|------|---------|
| `nlp_service/stt_service.py` | Faster-Whisper STT service class |
| `frontend/src/utils/downloadHelper.js` | Export utilities (CSV, PNG, images) |

### Files Modified

| File | Changes |
|------|---------|
| `nlp_service/main.py` | Added `/api/v1/transcribe` endpoint, STT service initialization |
| `nlp_service/requirements.txt` | Added faster-whisper, ctranslate2, python-multipart |
| `backend/chatbot/views.py` | Added Django proxy endpoint for STT |
| `backend/chatbot/urls.py` | Added transcribe route |
| `frontend/src/App.jsx` | Added voice recording UI, export buttons |
| `frontend/src/components/Chatbot.jsx` | Added voice recording, download buttons |
| `frontend/src/components/charts/ChartRenderer.jsx` | Added chart export functionality |
| `frontend/package.json` | Added html2canvas dependency |

### Dependency Pinning (Windows Compatibility)

| Package | Version | Issue Fixed |
|---------|---------|-------------|
| `chromadb` | 0.5.3 | Rust bindings segfault in v1.x |
| `ctranslate2` | 4.4.0 | Segfaults with faster-whisper in v4.5+ |
| `onnxruntime` | 1.18.0 | DLL loading issues in v1.23+ |
| `numpy` | <2.0.0 | Breaks sentence-transformers |

### Security
- Audio transcription routed through Django proxy to maintain security boundary
- React → Django → NLP Service architecture preserved

---

## [2026-01-09] Infographics/Charts Implementation

### Overview
Implemented LIDA-inspired visualization pipeline for automatic chart generation from SQL query results.

### New Features
- **Bar Charts**: Comparison queries (by furnace, by shift, compare, rank)
- **Line Charts**: Trend/time series queries (trend, over time, last week)
- **Pie Charts**: Distribution queries (breakdown, by reason, by type)
- **Gauge**: Single percentage metrics (OEE, yield, efficiency)
- **KPI Card**: Single value totals (count, total)

### Files Created

| File | Purpose |
|------|---------|
| `nlp_service/visualization/viz_summarizer.py` | Column classification (numeric/categorical/temporal) |
| `nlp_service/visualization/viz_goal_finder.py` | Chart type detection using heuristic rules |
| `nlp_service/visualization/viz_config_generator.py` | Recharts-compatible JSON config generation |
| `nlp_service/visualization/viz_validator.py` | Config validation |
| `frontend/src/components/ChartRenderer.jsx` | Dynamic Recharts rendering |

### Files Modified

| File | Changes |
|------|---------|
| `nlp_service/main.py` | Added `/api/v1/generate-chart-config` endpoint, visualization pipeline |
| `nlp_service/guardrails.py` | Added SQL comment stripping before validation |
| `nlp_service/sql_guardrails.py` | Added comment stripping, removed REPLACE from blocked keywords |
| `backend/chatbot/views.py` | Added `convert_for_json()` for Decimal/date serialization |

### Bug Fixes

1. **"Object of type Decimal is not JSON serializable"**
   - Added `convert_for_json()` function to handle Decimal and date types

2. **"Blocked SQL operation detected: REPLACE"**
   - Removed REPLACE from BLOCKED_KEYWORDS (REPLACE() is a safe string function)

3. **"Blocked pattern: --" (SQL comments)**
   - Added comment stripping in guardrails.py before validation

4. **Metric columns classified as temporal (cycle_time, downtime_hours)**
   - Added METRIC_TIME_PATTERNS to exclude from temporal detection

5. **Bar chart instead of pie chart for "breakdown" queries**
   - Added `_detect_distribution()` method
   - Reordered rules so distribution-detected queries get pie charts before comparison

6. **total_production classified as categorical**
   - Fixed column classification order to check numeric values BEFORE categorical patterns

7. **"Chat failed:" error with no message**
   - HTTPException.detail was not being extracted properly
   - Added dedicated `except HTTPException as he:` handler in `main.py:868-876`
   - Now shows proper error messages like "Token limit exceeded. Please wait 45 seconds."

8. **Queries blocked as "spam" too aggressively**
   - Spam detection threshold was only 3 identical queries (shared across all users)
   - Increased threshold from 3 to 10 in `query_guard.py:59`

### Chart Detection Keywords (from FEW_SHOT_EXAMPLES.md)

**Bar Chart triggers:**
- `compare`, `versus`, `vs`, `between`
- `by furnace`, `by shift`, `by machine`, `by plant`
- `which furnace`, `rank`, `top`, `bottom`

**Line Chart triggers:**
- `trend`, `over time`, `history`
- `last week`, `last month`, `last 7 days`, `last 30 days`
- `daily`, `weekly`, `monthly`

**Pie Chart triggers:**
- `breakdown`, `distribution`, `proportion`
- `by reason`, `by type`, `by category`, `by cause`

### Testing Results (2026-01-09)

| Test | Status |
|------|--------|
| Bar chart (comparison) | ✅ PASS |
| Line chart (trend) | ✅ PASS |
| Pie chart (distribution) | ✅ PASS |
| Gauge (single OEE) | ✅ PASS |
| KPI Card (single value) | ✅ PASS |
| Empty results | ✅ PASS - Returns null |
| Multi-dimensional data | ✅ PASS |

---

## [2026-01-06] RBAC Table Access Control Implementation

### Overview
Implemented Role-Based Access Control (RBAC) for table-level access following Option A architecture: **Django as Single Source of Truth**.

### Architecture Decision
- Django owns ALL permission logic
- NLP service receives `allowed_tables` whitelist and simply filters
- Eliminates "dual RBAC systems" problem
- Defense-in-depth: SQL tables validated at both NLP and Django layers

### Files Created

| File | Purpose |
|------|---------|
| `backend/chatbot/services/__init__.py` | Services package init |
| `backend/chatbot/services/rbac_service.py` | Centralized RBAC service for token -> allowed_tables resolution |

### Files Modified

| File | Changes |
|------|---------|
| `backend/ignis/schema/exposed_tables.py` | Added `FUNCTION_TABLE_MAPPING` (5 function codes) and `KPI_METRIC_TABLE_MAPPING` (21 KPI codes) |
| `backend/chatbot/views.py` | Added RBAC enforcement: token extraction, RBACService integration, SQL table validation |
| `nlp_service/main.py` | Updated `HybridChatRequest` and `GenerateSQLRequest` to accept `allowed_tables` |
| `nlp_service/prompts_v2.py` | Added `find_best_table_filtered()`, updated `build_prompt_with_schema()` to filter TABLE_SCHEMA |
| `frontend/src/App.jsx` | Added Bearer token header, 401/403 error handling |

### Security Flow

```
REQUEST -> Django
    |
[1] Token validation (users_usertoken)
    |
[2] Role lookup (users_userrole)
    |
[3] Function permissions (users_rolepermission -> FUNCTION_TABLE_MAPPING)
    |
[4] KPI permissions (users_role_kpis -> KPI_METRIC_TABLE_MAPPING)
    |
[5] Send allowed_tables to NLP service
    |
[6] NLP filters TABLE_SCHEMA, generates SQL
    |
[7] Django validates SQL tables subset of allowed_tables (defense-in-depth)
    |
[8] Execute SQL -> Return results
```

### Database Tables Used (Existing)

| Table | Purpose |
|-------|---------|
| `users_usertoken` | Token -> user_id lookup |
| `users_user` | User details, is_superuser check |
| `users_userrole` | User -> role_id mapping |
| `users_rolepermission` | Role -> function_code permissions |
| `utils_function` | Function code definitions |
| `users_role_kpis` | Role -> KPI metric permissions |
| `users_kpi_metric_master` | KPI metric code definitions |

### Key Mappings Added

**Function Codes -> Tables:**
- `PLT_CFG` -> plant_plant
- `FUR_MNT` -> furnace_furnaceconfig, furnace_config_parameters
- `LOG_BOOK` -> log_book_furnace_down_time_event, log_book_reasons, log_book_downtime_type_master
- `TAP_PROC` -> core_process_tap_production, core_process_tap_process, core_process_tap_grading
- `KPI_VIEW` -> (empty, uses KPI_METRIC_TABLE_MAPPING)

**KPI Codes -> Tables (21 total):**
- Performance: OEE, YIELD, DEFECT, PROD_EFF, OUTPUT, QTY_PROD, CYCLE_TIME, FPY, REWORK
- Maintenance: DOWNTIME, MTBF, MTTR, MTBS, MAINT_COMP, PLAN_MAINT
- Energy: ENERGY_EFF, ENERGY_USE
- Capacity/Delivery: CAPACITY, OTD
- Safety: SAFETY

### Testing Results (2026-01-06)

- [x] No token -> 401 Unauthorized (PASS)
- [x] Invalid token -> 401 Unauthorized (PASS)
- [x] Valid token, no permissions -> 403 No permissions (PASS)
- [x] Superuser -> All 29 tables accessible (PASS)
- [x] User with specific permissions -> Only assigned tables accessible (PASS)
- [x] LLM generates unauthorized table -> Blocked at Django validation (PASS)
- [x] SQL injection attempt -> Blocked by existing SQLValidator (PASS)

**Defense-in-Depth Test Results (2026-01-06):**
- Unit tests: All 16 cases passed (extract_tables_from_sql + validate_sql_tables)
- Live API test with `testuser123` (only furnace/plant tables):
  - OEE query: 403 - Access denied to tables: furnace_performance ✓
  - Tap production: Redirected to BRD (no SQL generated) ✓
  - Invalid table name: 403 - Access denied to tables: furnaces ✓

**SQL Injection Test Results (2026-01-06): 43/43 PASSED**
- DROP/DELETE/UPDATE attacks: Blocked ✓
- Data modification (INSERT/UPDATE/DELETE): Blocked ✓
- System table access (pg_*, information_schema): Blocked ✓
- Comment injection (--,  /* */): Blocked ✓
- Multiple statement stacking: Blocked ✓
- Stored procedure execution (EXEC, CALL): Blocked ✓
- Privilege escalation (GRANT, REVOKE, CREATE USER): Blocked ✓
- Data exfiltration (COPY, LOAD, INTO OUTFILE): Blocked ✓
- Variable manipulation (SET, DECLARE): Blocked ✓
- Valid SELECT queries: Allowed ✓

**End-to-End API Test Results (2026-01-06):**
- Token validation: Working ✓
- Superuser gets all 29 tables: Working ✓
- RBACService token lookup: Working ✓
- Defense-in-depth blocks LLM hallucinated tables: Working ✓
- Invalid/missing token returns 401: Working ✓
- No permissions returns 403: Working ✓

**Schema Fix Applied:** Updated RBACService queries to match actual DB schema:
- `function_master_id` stores function_code directly (VARCHAR), not FK
- `kpi_metric_code` stored directly in users_role_kpis (VARCHAR), not via FK

### Breaking Changes

- **Authentication now required**: All chat requests must include `Authorization: Bearer <token>` header
- Frontend expects `authToken` in `localStorage` (set during login flow)

### Migration Notes

1. Ensure `users_role_kpis` table has KPI metric codes mapped for roles
2. Ensure `users_rolepermission` has function codes with `view=true` for roles
3. Frontend login flow must save token to `localStorage.setItem('authToken', token)`

---

## Previous Changes

### [2025-01-05] Hybrid SQL + BRD RAG System
- Implemented query router for SQL vs BRD document queries
- Added multimodal RAG with image support from BRD documents
- Integrated Guardrails AI for PII/profanity filtering

### [2025-01-04] Security Layers (IEC 62443)
- Added 4-layer security defense in NLP service
- Implemented prompt flipping detection
- Added SQL injection validator
- Added anomaly detector and red team detection
- Created comprehensive audit logging
