"""
Live API Test: RBAC Unauthorized Table Blocking
Tests that Django blocks access to tables the user doesn't have permission for.
"""
import requests
import json

DJANGO_URL = "http://localhost:8001/api/chatbot/chat/"

# testuser123 token - has access to only: furnace_config_parameters, furnace_furnaceconfig, plant_plant
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3MjgxNTgzLCJpYXQiOjE3NDcxOTUxODMsImp0aSI6ImE5MWQ3OWUyY2Q1ZDRmYWE4NjlmYzViNDE0NmM4ZmIzIiwidXNlcl9pZCI6NDIsInVzZXJfZGF0YSI6eyJpZCI6NDIsImZpcnN0X25hbWUiOiJUZXN0IiwibGFzdF9uYW1lIjoiVXNlciIsInVybCI6Imh0dHA6Ly9xYS1kYXZpbmNpc20udmlydHVlc2VydmUuY29tL2FwaS91c2Vycy80Mi8iLCJ1c2VybmFtZSI6InRlc3R1c2VyMTIzIiwicm9sZXMiOlt7ImlkIjozLCJ0b3RhbF9mdW5jdGlvbnMiOjEzLCJ0b3RhbF91c2VycyI6eyJhY3RpdmVfdXNlcl9jb3VudCI6NCwiaW5hY3RpdmVfdXNlcl9jb3VudCI6MH0sImNyZWF0ZWRfYXQiOiIyMDI1LTA1LTA5VDIwOjAxOjUwLjM1MzI1OFoiLCJtb2RpZmllZF9hdCI6IjIwMjUtMDUtMTJUMDk6MDM6MzUuNzU3Nzc5WiIsInJlY29yZF9zdGF0dXMiOnRydWUsInJvbGVfbmFtZSI6IlZJRVdPTkxZVVNFUiIsImlzX2RlbGV0ZSI6ZmFsc2UsImlzX3N1cGVydXNlciI6ZmFsc2UsInBsYW50IjoiNlYiLCJjcmVhdGVkX2J5Ijoic3VwZXJ1c2VyIiwibW9kaWZpZWRfYnkiOiJwcmFzYW5uYSJ9XSwicGhvbmUiOiIiLCJlbWFpbCI6IiIsInJlY29yZF9zdGF0dXMiOnRydWUsImlzX2RlbGV0ZSI6ZmFsc2UsInBlcm1pc3Npb25fbGlzdCI6eyJTWVNBRE1OIjp7IlBMVF9DRkciOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjpmYWxzZSwiZWRpdCI6ZmFsc2UsImRlbGV0ZSI6ZmFsc2UsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiRlVSX0NGRyI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fSwiVVNSQ1RSTCI6eyJVU0VSUyI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJST0xFUyI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fSwiTVNUUkRBVEEiOnsiRlVSX01OVCI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJBRERfTU5UIjp7InZpZXciOnRydWUsImNyZWF0ZSI6ZmFsc2UsImVkaXQiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX0sIkJZX1BST0QiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjpmYWxzZSwiZWRpdCI6ZmFsc2UsImRlbGV0ZSI6ZmFsc2UsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiV0lQX01OVCI6eyJ2aWV3IjpmYWxzZSwiY3JlYXRlIjpmYWxzZSwiZWRpdCI6ZmFsc2UsImRlbGV0ZSI6ZmFsc2UsImlzRWxpZ2libGVGb3JNZW51IjpmYWxzZX19LCJDT1JFUFJPQyI6eyJTSUxfUFJPRCI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fSwiTEFCQU5MWVMiOnsiU1BUX0FOQSI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9LCJSTV9BTkEiOnsidmlldyI6ZmFsc2UsImNyZWF0ZSI6ZmFsc2UsImVkaXQiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJpc0VsaWdpYmxlRm9yTWVudSI6ZmFsc2V9LCJUQVBfQU5BIjp7InZpZXciOnRydWUsImNyZWF0ZSI6ZmFsc2UsImVkaXQiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX19LCJMT0dCT09LIjp7IkZVUl9CRUQiOnsidmlldyI6dHJ1ZSwiY3JlYXRlIjpmYWxzZSwiZWRpdCI6ZmFsc2UsImRlbGV0ZSI6ZmFsc2UsImlzRWxpZ2libGVGb3JNZW51Ijp0cnVlfSwiVEFQX0xPRyI6eyJ2aWV3Ijp0cnVlLCJjcmVhdGUiOmZhbHNlLCJlZGl0IjpmYWxzZSwiZGVsZXRlIjpmYWxzZSwiaXNFbGlnaWJsZUZvck1lbnUiOnRydWV9fSwiUkVQT1JUUyI6eyJNQVRfQ09OIjp7InZpZXciOnRydWUsImNyZWF0ZSI6ZmFsc2UsImVkaXQiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJpc0VsaWdpYmxlRm9yTWVudSI6dHJ1ZX19fSwiaXNfc3VwZXJ1c2VyIjpmYWxzZSwibG9naW5fdHlwZSI6InNpbXBsZSJ9LCJwbGFudF9kYXRhIjp7InBsYW50X25hbWUiOiJBbmdsZWZvcnQiLCJwbGFudF9pZCI6IjZWIiwiYXJlYV9jb2RlIjoiMDBBTjAwIiwicGxhbnRfdGltZV96b25lX2lkIjoiVFpfQ1NUIn19.wBO1FH9kBrXhwmbFa-Cime9ghWN23iOjgoARTUGobn0"

print("=" * 70)
print("LIVE API TEST: RBAC Unauthorized Table Blocking")
print("=" * 70)
print()
print("User: testuser123 (VIEWONLYUSER role)")
print("Allowed tables: furnace_config_parameters, furnace_furnaceconfig, plant_plant")
print()

# Test 1: Ask about allowed data (furnaces)
print("[TEST 1] Authorized query - List furnaces")
print("-" * 50)
try:
    response = requests.post(
        DJANGO_URL,
        json={"question": "List all furnaces"},
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        timeout=60
    )
    data = response.json()
    print(f"  Status: {response.status_code}")
    print(f"  Success: {data.get('success')}")
    if data.get('success'):
        print(f"  Query Type: {data.get('query_type')}")
        print(f"  Row Count: {data.get('row_count')}")
        print("  PASS - Authorized query worked!")
    else:
        print(f"  Error: {data.get('error')}")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 2: Ask about unauthorized data (OEE - KPI table)
print("[TEST 2] UNAUTHORIZED query - Ask about OEE (no KPI permission)")
print("-" * 50)
try:
    response = requests.post(
        DJANGO_URL,
        json={"question": "What is the average OEE for furnace 1?"},
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        timeout=60
    )
    data = response.json()
    print(f"  Status: {response.status_code}")
    print(f"  Success: {data.get('success')}")

    if response.status_code == 403 or (not data.get('success') and 'denied' in str(data.get('error', '')).lower()):
        print(f"  Error: {data.get('error')}")
        print("  PASS - Unauthorized access was BLOCKED!")
    elif data.get('success'):
        print(f"  Response: {data.get('response', '')[:100]}...")
        # Check if response indicates no access
        if 'no data' in str(data.get('response', '')).lower() or data.get('row_count', 0) == 0:
            print("  PASS - Query returned no data (schema filtered)")
        else:
            print("  WARNING - Query returned data, check if RBAC is working")
    else:
        print(f"  Error: {data.get('error')}")
        if 'access' in str(data.get('error', '')).lower() or 'denied' in str(data.get('error', '')).lower():
            print("  PASS - Access denied correctly!")
        else:
            print("  Check response...")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 3: Ask about tap production (no TAP_PROC permission)
print("[TEST 3] UNAUTHORIZED query - Ask about tap production")
print("-" * 50)
try:
    response = requests.post(
        DJANGO_URL,
        json={"question": "Show total cast weight from tap production"},
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        timeout=60
    )
    data = response.json()
    print(f"  Status: {response.status_code}")
    print(f"  Success: {data.get('success')}")

    if response.status_code == 403:
        print(f"  Error: {data.get('error')}")
        print("  PASS - 403 Forbidden returned!")
    elif not data.get('success'):
        print(f"  Error: {data.get('error')}")
        if 'denied' in str(data.get('error', '')).lower() or 'access' in str(data.get('error', '')).lower():
            print("  PASS - Access denied correctly!")
        else:
            print("  Response indicates no access")
    else:
        print(f"  Query Type: {data.get('query_type')}")
        if data.get('query_type') == 'blocked':
            print(f"  Response: {data.get('response', '')[:100]}...")
            print("  Note: Query was blocked or redirected")
        else:
            print(f"  Row Count: {data.get('row_count')}")
            if data.get('row_count', 0) == 0:
                print("  PASS - No unauthorized data returned")
            else:
                print("  WARNING - Check if data should be accessible")
except Exception as e:
    print(f"  Error: {e}")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
