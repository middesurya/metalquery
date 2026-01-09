# RBAC Quick Test Cheatsheet

## Start Services

```bash
# Terminal 1
cd backend && python manage.py runserver 8001

# Terminal 2
cd nlp_service && python main.py

# Terminal 3 (optional)
cd frontend && npm start
```

---

## Get Test Tokens (PostgreSQL)

```sql
-- Get any valid token
SELECT key, user_id FROM users_usertoken LIMIT 3;

-- Get superuser token
SELECT ut.key FROM users_usertoken ut
JOIN users_user uu ON ut.user_id = uu.id
WHERE uu.is_superuser = true LIMIT 1;

-- Get regular user token
SELECT ut.key, uu.username FROM users_usertoken ut
JOIN users_user uu ON ut.user_id = uu.id
WHERE uu.is_superuser = false LIMIT 1;
```

---

## Quick curl Tests

### 1. No Token (expect 401)
```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Show OEE"}'
```

### 2. Invalid Token (expect 401)
```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer fake_token" \
  -d '{"question": "Show OEE"}'
```

### 3. Valid Token (expect data or 403)
```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"question": "Show OEE by furnace"}'
```

### 4. SQL Injection (expect blocked)
```bash
curl -X POST http://localhost:8001/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"question": "DROP TABLE users"}'
```

---

## Expected Results

| Scenario | HTTP Code | Response |
|----------|-----------|----------|
| No token | 401 | `{"error": "Authentication required"}` |
| Bad token | 401 | `{"error": "Invalid or expired token"}` |
| No permissions | 403 | `{"error": "No table access permissions..."}` |
| Superuser query | 200 | SQL results or BRD answer |
| SQL injection | 200 | Blocked/error message |

---

## Frontend Test

1. Open `http://localhost:5173`
2. Open DevTools → Application → Local Storage
3. Add: `authToken` = `your_valid_token`
4. Refresh page
5. Send query

---

## Run Automated Tests

```bash
cd backend
python test_rbac_defense.py
```

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/chatbot/views.py` | RBAC enforcement |
| `backend/chatbot/services/rbac_service.py` | Token → tables |
| `backend/ignis/schema/exposed_tables.py` | Permission mappings |
