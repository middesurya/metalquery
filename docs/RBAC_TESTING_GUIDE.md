# RBAC Manual Testing Guide

## Quick Start

### Step 1: Start Services
```bash
# Terminal 1 - Django Backend
cd backend && ..\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

# Terminal 2 - NLP Service
cd nlp_service && ..\.venv\Scripts\python.exe main.py

# Terminal 3 - Frontend
cd frontend && npm start
```

### Step 2: Open Browser
Go to: http://localhost:5173

---

## Available Test Users & Tokens

### SUPERUSER (Full Access - All Tables)

| User | Username | Token |
|------|----------|-------|
| Shrishail Karigar | skarigar | See below |

**skarigar Token (SUPERUSER):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ5NTM3ODQ2LCJpYXQiOjE3NDk0NTE0NDYsImp0aSI6ImZiZWFhN2ZlMTZmYjQxMWQ4N2UwNzJhNjU0ZDEzMmU4IiwidXNlcl9pZCI6NiwidXNlcl9kYXRhIjp7ImlkIjo2LCJmaXJzdF9uYW1lIjoiU2hyaXNoYWlsIiwibGFzdF9uYW1lIjoiS2FyaWdhciIsInVybCI6Imh0dHA6Ly9xYS1kYXZpbmNpc20udmlydHVlc2VydmUuY29tL2FwaS91c2Vycy82LyIsInVzZXJuYW1lIjoic2thcmlnYXIiLCJyb2xlcyI6W3siaWQiOjEsInRvdGFsX2Z1bmN0aW9ucyI6MTksInRvdGFsX3VzZXJzIjp7ImFjdGl2ZV91c2VyX2NvdW50IjoxMSwiaW5hY3RpdmVfdXNlcl9jb3VudCI6MH0sImNyZWF0ZWRfYXQiOiIyMDI1LTA1LTA4VDA3OjIxOjIyLjE1MzA4MloiLCJtb2RpZmllZF9hdCI6IjIwMjUtMDYtMDRUMDY6NDE6MzQuOTMzODQ5WiIsInJlY29yZF9zdGF0dXMiOnRydWUsInJvbGVfbmFtZSI6IlN1cGVyQWRtaW4iLCJpc19kZWxldGUiOmZhbHNlLCJpc19zdXBlcnVzZXIiOnRydWUsInBsYW50IjoiNlYiLCJjcmVhdGVkX2J5Ijoic3VwZXJ1c2VyIiwibW9kaWZpZWRfYnkiOiJzdXBlcnVzZXIifV0sInBob25lIjoiIiwiZW1haWwiOiJza2FyaWdhckBkYXZpbmNpc20uaW8iLCJyZWNvcmRfc3RhdHVzIjp0cnVlLCJpc19kZWxldGUiOmZhbHNlLCJwZXJtaXNzaW9uX2xpc3QiOnsiU1lTQURNTiI6eyJQTFRfQ0ZHIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIkZVUl9DRkciOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfX0sIlVTUkNUUkwiOnsiVVNFUlMiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiUk9MRVMiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfX0sIk1TVFJEQVRBIjp7IkZVUl9NTlQiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiQUREX01OVCI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJCWV9QUk9EIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIldJUF9NTlQiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOmZhbHNlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIkdSRF9QTEFOIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX19LCJDT1JFUFJPQyI6eyJTSUxfUFJPRCI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fSwiTEFCQU5MWVMiOnsiU1BUX0FOQSI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJSTV9BTkEiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiVEFQX0FOQSI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fSwiTE9HQk9PSyI6eyJGVVJfQkVEIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIlRBUF9MT0ciOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiRFdOX0xPRyI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJEV05fRVZUIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIkRXTl9TUExUIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX19LCJSRVBPUlRTIjp7Ik1BVF9BTkEiOnsidmlldyI6ZmFsc2UsImNyZWF0ZSI6ZmFsc2UsImVkaXQiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJpc0VsaWdpYmxlRm9yTWVudSI6ZmFsc2V9LCJNQVRfU1pFIjp7InZpZXciOmZhbHNlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOmZhbHNlfSwiTUFUX0NPTiI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fX0sImlzX3N1cGVydXNlciI6dHJ1ZSwibG9naW5fdHlwZSI6InNzbyJ9LCJwbGFudF9kYXRhIjp7InBsYW50X25hbWUiOiJBbmdsZWZvcnQiLCJwbGFudF9pZCI6IjZWIiwiYXJlYV9jb2RlIjoiMDBBTjAwIiwicGxhbnRfdGltZV96b25lX2lkIjoiVFpfQ1NUIn19.VK_c6E6oAapjdGO-oo0xKava4ZcNGjRPakRe3O8rgf8
```

### REGULAR USER (Limited Access - No Table Permissions)

| User | Username | Token |
|------|----------|-------|
| No Permission User | nopermission | See below |

**nopermission Token (REGULAR - NO TABLE ACCESS):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMCwidXNlcm5hbWUiOiJub3Blcm1pc3Npb24iLCJpc19zdXBlcnVzZXIiOmZhbHNlfQ.LIMITED_USER_TOKEN
```

> **Note:** Get the actual `nopermission` token from PGAdmin:
> ```sql
> SELECT ut.token FROM users_usertoken ut
> JOIN users_user u ON ut.user_id = u.id
> WHERE u.username = 'nopermission';
> ```

---

## How to Set Token in Browser

### Method 1: Browser Console (Easiest)

1. Open http://localhost:5173
2. Press `F12` to open DevTools
3. Go to **Console** tab
4. Paste this code (replace TOKEN):

```javascript
// Set superuser token (full access)
localStorage.setItem('authToken', 'PASTE_TOKEN_HERE');
location.reload();
```

### Method 2: Application Tab

1. Press `F12` -> **Application** tab
2. Left sidebar -> **Local Storage** -> `http://localhost:5173`
3. Click `authToken` or add new key
4. Paste token in **Value** field
5. Refresh page (`F5`)

---

## Test Scenarios

### Test 1: Superuser Access (Full Access)

```javascript
// In browser console
localStorage.setItem('authToken', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ5NTM3ODQ2LCJpYXQiOjE3NDk0NTE0NDYsImp0aSI6ImZiZWFhN2ZlMTZmYjQxMWQ4N2UwNzJhNjU0ZDEzMmU4IiwidXNlcl9pZCI6NiwidXNlcl9kYXRhIjp7ImlkIjo2LCJmaXJzdF9uYW1lIjoiU2hyaXNoYWlsIiwibGFzdF9uYW1lIjoiS2FyaWdhciIsInVybCI6Imh0dHA6Ly9xYS1kYXZpbmNpc20udmlydHVlc2VydmUuY29tL2FwaS91c2Vycy82LyIsInVzZXJuYW1lIjoic2thcmlnYXIiLCJyb2xlcyI6W3siaWQiOjEsInRvdGFsX2Z1bmN0aW9ucyI6MTksInRvdGFsX3VzZXJzIjp7ImFjdGl2ZV91c2VyX2NvdW50IjoxMSwiaW5hY3RpdmVfdXNlcl9jb3VudCI6MH0sImNyZWF0ZWRfYXQiOiIyMDI1LTA1LTA4VDA3OjIxOjIyLjE1MzA4MloiLCJtb2RpZmllZF9hdCI6IjIwMjUtMDYtMDRUMDY6NDE6MzQuOTMzODQ5WiIsInJlY29yZF9zdGF0dXMiOnRydWUsInJvbGVfbmFtZSI6IlN1cGVyQWRtaW4iLCJpc19kZWxldGUiOmZhbHNlLCJpc19zdXBlcnVzZXIiOnRydWUsInBsYW50IjoiNlYiLCJjcmVhdGVkX2J5Ijoic3VwZXJ1c2VyIiwibW9kaWZpZWRfYnkiOiJzdXBlcnVzZXIifV0sInBob25lIjoiIiwiZW1haWwiOiJza2FyaWdhckBkYXZpbmNpc20uaW8iLCJyZWNvcmRfc3RhdHVzIjp0cnVlLCJpc19kZWxldGUiOmZhbHNlLCJwZXJtaXNzaW9uX2xpc3QiOnsiU1lTQURNTiI6eyJQTFRfQ0ZHIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIkZVUl9DRkciOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfX0sIlVTUkNUUkwiOnsiVVNFUlMiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiUk9MRVMiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfX0sIk1TVFJEQVRBIjp7IkZVUl9NTlQiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiQUREX01OVCI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJCWV9QUk9EIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIldJUF9NTlQiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOmZhbHNlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIkdSRF9QTEFOIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX19LCJDT1JFUFJPQyI6eyJTSUxfUFJPRCI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fSwiTEFCQU5MWVMiOnsiU1BUX0FOQSI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJSTV9BTkEiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiVEFQX0FOQSI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fSwiTE9HQk9PSyI6eyJGVVJfQkVEIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIlRBUF9MT0ciOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjp0cnVlLCJlZGl0Ijp0cnVlLCJkZWxldGUiOnRydWUsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiRFdOX0xPRyI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJEV05fRVZUIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIkRXTl9TUExUIjp7InZpZXciOnRydWUsImNyZWF0ZSI6dHJ1ZSwiZWRpdCI6dHJ1ZSwiZGVsZXRlIjp0cnVlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX19LCJSRVBPUlRTIjp7Ik1BVF9BTkEiOnsidmlldyI6ZmFsc2UsImNyZWF0ZSI6ZmFsc2UsImVkaXQiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJpc0VsaWdpYmxlRm9yTWVudSI6ZmFsc2V9LCJNQVRfU1pFIjp7InZpZXciOmZhbHNlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOmZhbHNlfSwiTUFUX0NPTiI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOnRydWUsImVkaXQiOnRydWUsImRlbGV0ZSI6dHJ1ZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fX0sImlzX3N1cGVydXNlciI6dHJ1ZSwibG9naW5fdHlwZSI6InNzbyJ9LCJwbGFudF9kYXRhIjp7InBsYW50X25hbWUiOiJBbmdsZWZvcnQiLCJwbGFudF9pZCI6IjZWIiwiYXJlYV9jb2RlIjoiMDBBTjAwIiwicGxhbnRfdGltZV96b25lX2lkIjoiVFpfQ1NUIn19.VK_c6E6oAapjdGO-oo0xKava4ZcNGjRPakRe3O8rgf8');
location.reload();
```

**Try these queries:**
- "Show all furnaces" -> Should return data
- "What is the total downtime?" -> Should return data
- Any query -> Should work (full access)

### Test 2: No Authentication (401 Error)

```javascript
// In browser console
localStorage.removeItem('authToken');
location.reload();
```

**Try any query:**
- Expected: `401 "Authentication required"`

### Test 3: Limited User (403 Error)

```javascript
// Set limited user token
localStorage.setItem('authToken', 'LIMITED_USER_TOKEN_HERE');
location.reload();
```

**Try these queries:**
- "Show all furnaces" -> Expected: `403 "No table access permission"`

---

## PGAdmin Queries

### Get All Users with Tokens
```sql
SELECT
    u.id,
    u.username,
    u.first_name,
    u.last_name,
    u.is_superuser,
    ut.token
FROM users_user u
LEFT JOIN users_usertoken ut ON u.id = ut.user_id
WHERE u.record_status = true
  AND ut.token IS NOT NULL
ORDER BY u.is_superuser DESC, u.username;
```

### Get Token for Specific User
```sql
SELECT ut.token
FROM users_usertoken ut
JOIN users_user u ON ut.user_id = u.id
WHERE u.username = 'skarigar';  -- Change username
```

### Check User Roles
```sql
SELECT
    u.username,
    u.is_superuser,
    r.role_name
FROM users_user u
LEFT JOIN users_userrole ur ON u.id = ur.user_id
LEFT JOIN users_role r ON ur.role_id = r.id
WHERE u.record_status = true
ORDER BY u.is_superuser DESC;
```

---

## Expected RBAC Responses

| Scenario | HTTP Code | Message |
|----------|-----------|---------|
| No token | 401 | "Authentication required" |
| Invalid/expired token | 401 | "Invalid or expired token" |
| Valid token, no table access | 403 | "No table access permission" |
| Superuser | 200 | Returns data |
| Regular user with permissions | 200 | Returns filtered data |

---

## Troubleshooting

### Token Not Working?
1. Check token is not expired (decode at jwt.io)
2. Ensure token is correctly copied (no extra spaces)
3. Clear localStorage and try again

### Services Not Running?
```bash
# Check ports
netstat -ano | findstr ":8000 :8003 :5173"

# Restart services
cd backend && ..\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
cd nlp_service && ..\.venv\Scripts\python.exe main.py
cd frontend && npm start
```

### Get Fresh Token
```bash
cd backend
..\.venv\Scripts\python.exe get_test_tokens.py
```
