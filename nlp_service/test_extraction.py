import sys
import os

# Create dummy settings to allow import
class DummySettings:
    model_name = "test"
    ollama_base_url = "http://localhost:11434"
    django_api_url = "http://localhost:8000"
    nlp_service_host = "localhost"
    nlp_service_port = 8003

sys.modules['config'] = type('config', (), {'settings': DummySettings()})

from main import clean_generated_sql

test_cases = [
    {
        "input": "SELECT * FROM materials;",
        "expected": "SELECT * FROM materials"
    },
    {
        "input": "Here is the SQL: SELECT * FROM materials WHERE id=1",
        "expected": "SELECT * FROM materials WHERE id=1"
    },
    {
        "input": "Sure!\n```sql\nSELECT * FROM materials\n```\nHope this helps.",
        "expected": "SELECT * FROM materials"
    },
    {
        "input": "SELECT * FROM materials; -- some comment",
        "expected": "SELECT * FROM materials"
    }
]

print("Running SQL Extraction Tests...")
for i, test in enumerate(test_cases):
    result = clean_generated_sql(test["input"])
    status = "PASS" if result == test["expected"] else f"FAIL (Got: {result})"
    print(f"Test {i+1}: {status}")

if all(clean_generated_sql(t["input"]) == t["expected"] for t in test_cases):
    print("\nALL TESTS PASSED!")
    sys.exit(0)
else:
    sys.exit(1)
