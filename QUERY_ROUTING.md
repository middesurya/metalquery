# BRD vs SQL Query Routing Reference

## Routing Rules

### Routes to **SQL** (Database Queries)
Questions asking for **actual data/metrics/numbers**:
- "Show OEE for furnace 1"
- "What is the downtime for last week"
- "Get production data for January"
- "Compare yield across furnaces"

**KPI Metrics (always SQL when asking for data):**
- OEE, efficiency, yield, downtime, MTBF, MTTR, MTBS
- Production, energy, defect, output, cycle time
- Maintenance compliance, capacity utilization

---

### Routes to **BRD** (Documentation Queries)
Questions asking **how something works** or **what something is**:

| BRD Document | Topics that Route to BRD |
|--------------|-------------------------|
| **S013 - EHS** | ehs, incident reporting, safety, environment health |
| **S03 - System Config** | plant config, furnace config, user access, roles, users |
| **S04 - Master Data** | raw materials, additives, byproducts, WIP, grading plan, material maintenance |
| **S05 - Core Process** | core process, core process production |
| **S06 - Reports** | report format, report structure, consumption report |
| **S08 - Lab Analysis** | lab analysis, spout analysis, tap analysis, raw material analysis |
| **S09 - Log Book** | log book, tap hole log, furnace bed log, downtime log |

---

## Example Queries

| User Question | Routes To | Reason |
|---------------|-----------|--------|
| "What is raw material analysis" | **BRD** | Asking for definition/process |
| "Show raw material consumption" | **SQL** | Asking for actual data |
| "What is EHS" | **BRD** | Asking for definition |
| "What is the OEE for furnace 1" | **SQL** | Asking for metric data |
| "How to configure user roles" | **BRD** | Asking how to do something |
| "What is lab analysis" | **BRD** | Asking for definition |
| "Show tap analysis data" | **SQL** | Asking for actual data |

---

## Files Updated
- `query_router.py` - Routing logic with 33 BRD topics
- `query_guard.py` - Domain keywords to allow BRD queries
