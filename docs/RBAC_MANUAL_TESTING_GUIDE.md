# RBAC Manual Testing Guide

## Overview

This guide covers manual testing of the Role-Based Access Control (RBAC) implementation for the MetalQuery NLP-to-SQL system.

**Architecture**: Django as Single Source of Truth
- Django validates tokens and resolves user permissions
- NLP service receives `allowed_tables` whitelist
- Defense-in-depth: SQL validated at both layers

---

## Prerequisites

### 1. Start All Services

```bash
# Terminal 1: Django Backend (Port 8001)
cd backend
python manage.py runserver 8001

# Terminal 2: NLP Service (Port 8003)
cd nlp_service
python main.py

# Terminal 3: Frontend (Port 5173) - Optional for UI testing
cd frontend
npm start
```

### 2. Verify Services Running

```bash
# Check Django
curl http://localhost:8001/api/chatbot/chat/ -X POST -H "Content-Type: application/json" -d "{\"question\": \"test\"}"
# Expected: {"error": "Authentication required"} or 401

# Check NLP Service
curl http://localhost:8003/health
# Expected: {"status": "healthy"}
```

---

## Test Scenarios

### Test 1: No Authentication Token (401)

**Purpose**: Verify requests without token are rejected

```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Show OEE data"}'
```

**Expected Response**:
```json
{
  "error": "Authentication required"
}
```
**HTTP Status**: 401 Unauthorized

---

### Test 2: Invalid/Expired Token (401)

**Purpose**: Verify invalid tokens are rejected

```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token_12345" \
  -d '{"question": "Show OEE data"}'
```

**Expected Response**:
```json
{
  "error": "Invalid or expired token"
}
```
**HTTP Status**: 401 Unauthorized

---

### Test 3: Valid Token - Get User's Allowed Tables

**Purpose**: Verify token resolves to correct table permissions

First, get a valid token from the database:

```sql
-- Run in PostgreSQL
SELECT ut.key, uu.username, uu.is_superuser
FROM users_usertoken ut
JOIN users_user uu ON ut.user_id = uu.id
LIMIT 5;
```

Then test with the token:

```bash
# Replace YOUR_TOKEN with actual token from database
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question": "Show OEE data"}'
```

**Expected Responses**:

| User Type | Expected Behavior |
|-----------|-------------------|
| Superuser | Access to all 29 tables, query executes |
| User with OEE permission | Access to kpi_oee table, query executes |
| User without OEE permission | 403 or redirected to BRD |

---

### Test 4: Superuser Access (All 29 Tables)

**Purpose**: Verify superusers get full table access

```sql
-- Get superuser token
SELECT ut.key FROM users_usertoken ut
JOIN users_user uu ON ut.user_id = uu.id
WHERE uu.is_superuser = true
LIMIT 1;
```

```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SUPERUSER_TOKEN" \
  -d '{"question": "Show all furnace configurations"}'
```

**Expected**: Query executes successfully, returns data from `furnace_furnaceconfig` table.

---

### Test 5: User With Limited Permissions

**Purpose**: Verify non-superusers only access permitted tables

```sql
-- Find a non-superuser with specific permissions
SELECT ut.key, uu.username, ur.role_id
FROM users_usertoken ut
JOIN users_user uu ON ut.user_id = uu.id
JOIN users_userrole ur ON uu.id = ur.user_id
WHERE uu.is_superuser = false
LIMIT 1;

-- Check what function permissions this role has
SELECT rp.function_master_id
FROM users_rolepermission rp
WHERE rp.role_id = <ROLE_ID> AND rp.view = true;

-- Check what KPI permissions this role has
SELECT kpi_metric_code
FROM users_role_kpis
WHERE role_id = <ROLE_ID>;
```

```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer LIMITED_USER_TOKEN" \
  -d '{"question": "Show plant configuration"}'
```

**Expected**:
- If user has `PLT_CFG` permission: Returns plant data
- If user lacks `PLT_CFG` permission: 403 or BRD response

---

### Test 6: Defense-in-Depth (Block LLM Hallucination)

**Purpose**: Verify Django blocks SQL with unauthorized tables even if LLM generates them

This test requires modifying the NLP response temporarily or testing via unit tests.

**Unit Test** (run from project root):
```bash
cd backend
python -c "
from chatbot.views import extract_tables_from_sql, validate_sql_tables

# Simulate LLM generating unauthorized table
sql = 'SELECT * FROM kpi_oee JOIN secret_table ON id = id'
allowed = {'kpi_oee'}

tables = extract_tables_from_sql(sql)
print(f'Tables in SQL: {tables}')

is_valid, unauthorized = validate_sql_tables(sql, allowed)
print(f'Valid: {is_valid}')
print(f'Unauthorized tables: {unauthorized}')
"
```

**Expected Output**:
```
Tables in SQL: {'kpi_oee', 'secret_table'}
Valid: False
Unauthorized tables: {'secret_table'}
```

---

### Test 7: SQL Injection Prevention

**Purpose**: Verify dangerous SQL is blocked

```bash
# DROP TABLE attempt
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VALID_TOKEN" \
  -d '{"question": "DROP TABLE users; SELECT * FROM kpi_oee"}'

# DELETE attempt
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VALID_TOKEN" \
  -d '{"question": "DELETE FROM kpi_oee WHERE 1=1"}'

# System table access
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VALID_TOKEN" \
  -d '{"question": "Show all tables from pg_catalog"}'
```

**Expected**: All should return error or be blocked by security layers.

---

### Test 8: User With No Permissions (403)

**Purpose**: Verify users with valid token but no permissions get 403

```sql
-- Find/create a user with no role permissions
-- Or use a role that has no function codes or KPI codes assigned
```

```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer NO_PERMISSION_USER_TOKEN" \
  -d '{"question": "Show OEE data"}'
```

**Expected Response**:
```json
{
  "error": "No table access permissions. Contact administrator."
}
```
**HTTP Status**: 403 Forbidden

---

## Permission Mappings Reference

### Function Code → Tables

| Function Code | Tables Granted |
|---------------|----------------|
| `PLT_CFG` | plant_plant |
| `FUR_MNT` | furnace_furnaceconfig, furnace_config_parameters |
| `LOG_BOOK` | log_book_furnace_down_time_event, log_book_reasons, log_book_downtime_type_master |
| `TAP_PROC` | core_process_tap_production, core_process_tap_process, core_process_tap_grading |
| `KPI_VIEW` | (uses KPI metric mappings below) |

### KPI Metric Code → Tables

| KPI Code | Table |
|----------|-------|
| `OEE` | kpi_oee |
| `YIELD` | kpi_yield |
| `DOWNTIME` | kpi_downtime |
| `MTBF` | kpi_mtbf |
| `MTTR` | kpi_mttr |
| `MTBS` | kpi_mtbs |
| `ENERGY_EFF` | kpi_energy_efficiency |
| `ENERGY_USE` | kpi_energy_consumption |
| `DEFECT` | kpi_defect_rate |
| `PROD_EFF` | kpi_production_efficiency |
| `OUTPUT` | kpi_output |
| `QTY_PROD` | kpi_quantity_produced |
| `CYCLE_TIME` | kpi_cycle_time |
| `FPY` | kpi_first_pass_yield |
| `REWORK` | kpi_rework_rate |
| `CAPACITY` | kpi_capacity_utilization |
| `OTD` | kpi_on_time_delivery |
| `SAFETY` | kpi_safety_incidents |
| `MAINT_COMP` | kpi_maintenance_compliance |
| `PLAN_MAINT` | kpi_planned_maintenance |

---

## Frontend Testing

### Setup

1. Open browser to `http://localhost:5173`
2. Open Developer Tools → Application → Local Storage
3. Set `authToken` with a valid token from the database

### Test Cases

1. **No Token**: Clear localStorage, send query → "Session expired" message
2. **Valid Token**: Set valid token, send query → Data returned
3. **Expired Token**: Set old/invalid token → "Session expired" message

---

## Creating Test Users (Optional)

If you need to create test users with specific permissions:

```sql
-- 1. Create a test user
INSERT INTO users_user (username, email, password, is_superuser, is_active)
VALUES ('testuser_rbac', 'test@example.com', 'hashed_password', false, true)
RETURNING id;

-- 2. Create a role
INSERT INTO users_role (name, description)
VALUES ('Test RBAC Role', 'Role for testing RBAC')
RETURNING id;

-- 3. Assign user to role
INSERT INTO users_userrole (user_id, role_id)
VALUES (<USER_ID>, <ROLE_ID>);

-- 4. Grant function permissions
INSERT INTO users_rolepermission (role_id, function_master_id, view, create, edit, delete)
VALUES (<ROLE_ID>, 'FUR_MNT', true, false, false, false);

-- 5. Grant KPI permissions
INSERT INTO users_role_kpis (role_id, kpi_metric_code)
VALUES (<ROLE_ID>, 'OEE'), (<ROLE_ID>, 'DOWNTIME');

-- 6. Create auth token
INSERT INTO users_usertoken (key, user_id, created)
VALUES ('test_token_abc123', <USER_ID>, NOW())
RETURNING key;
```

---

## Automated Test Script

Run the comprehensive test script:

```bash
cd backend
python test_rbac_defense.py
```

This runs 43+ SQL injection tests and RBAC validation tests.

---

## Troubleshooting

### "Connection refused" errors
- Ensure Django is running on port 8001
- Ensure NLP service is running on port 8003

### "Invalid token" for known valid token
- Check token hasn't expired
- Verify token exists in `users_usertoken` table
- Check user is active (`is_active = true`)

### User gets 403 but should have access
- Verify user has role assigned (`users_userrole`)
- Verify role has permissions (`users_rolepermission` with `view = true`)
- Verify KPI permissions if querying KPI tables (`users_role_kpis`)

### Query returns BRD response instead of SQL
- The query may not match any allowed tables
- Check if user has permissions for the tables needed
- Query might be classified as documentation query by router

---

## Test Results Checklist

| Test | Expected | Actual | Pass/Fail |
|------|----------|--------|-----------|
| No token → 401 | 401 Unauthorized | | |
| Invalid token → 401 | 401 Unauthorized | | |
| No permissions → 403 | 403 Forbidden | | |
| Superuser → All tables | 29 tables accessible | | |
| Limited user → Filtered tables | Only permitted tables | | |
| SQL injection → Blocked | Error/Blocked | | |
| Defense-in-depth → Blocked | Unauthorized tables rejected | | |

---

## Contact

For issues with RBAC implementation, check:
- `backend/chatbot/services/rbac_service.py` - Token resolution logic
- `backend/chatbot/views.py` - RBAC enforcement
- `backend/ignis/schema/exposed_tables.py` - Table mappings
