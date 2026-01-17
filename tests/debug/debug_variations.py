#!/usr/bin/env python3
"""Test query variations to find what works."""

import requests
import time
import re

NLP_SERVICE_URL = "http://localhost:8003"

# Test variations of the failed queries
QUERY_VARIATIONS = [
    # Downtime variations
    ("Show downtime by furnace", "Original failed query"),
    ("Show total downtime by furnace", "With 'total' prefix"),
    ("What is the downtime by furnace?", "Question format"),
    ("Show Total downtime by furnace", "Capitalized 'Total'"),

    # Safety variations
    ("What is the average safety incidents percentage?", "Original failed"),
    ("Show average safety incidents", "Simplified"),
    ("What is the average safety incidents?", "Without 'percentage'"),
    ("Show safety incidents by furnace", "By furnace variant"),
]

ALLOWED_TABLES = [
    "kpi_downtime_data", "kpi_safety_incidents_reported_data", "furnace_furnaceconfig"
]

def test_query(question, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{NLP_SERVICE_URL}/api/v1/chat",
                json={"question": question, "allowed_tables": ALLOWED_TABLES},
                timeout=120
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {"success": True, "sql": data.get("sql")}
                else:
                    error = data.get("error", "")
                    if "Token limit" in error:
                        wait_match = re.search(r'wait (\d+) seconds', error)
                        wait_time = int(wait_match.group(1)) + 2 if wait_match else 60
                        print(f" [rate limit, waiting {wait_time}s]", end="", flush=True)
                        time.sleep(wait_time)
                        continue
                    return {"success": False, "error": error}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "Max retries"}

def main():
    print("=" * 70)
    print("TESTING QUERY VARIATIONS")
    print("=" * 70)

    for question, description in QUERY_VARIATIONS:
        print(f"\n[{description}]")
        print(f"Query: {question}")

        result = test_query(question)

        if result.get("success") and result.get("sql"):
            sql = result["sql"][:100].replace('\n', ' ')
            print(f"SUCCESS: {sql}...")
        else:
            print(f"FAILED: {result.get('error', 'No SQL generated')}")

        time.sleep(3)

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
