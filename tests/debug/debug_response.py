#!/usr/bin/env python3
"""Debug API response to see chart_config structure."""
import requests
import json

response = requests.post(
    "http://localhost:8003/api/v1/chat",
    json={
        "question": "What is the average oee for all furnaces",
        "allowed_tables": ["kpi_overall_equipment_efficiency_data"]
    },
    timeout=120
)

data = response.json()

print("=" * 60)
print("API Response Debug")
print("=" * 60)
print(f"success: {data.get('success')}")
print(f"sql: {data.get('sql', '')[:100] if data.get('sql') else 'None'}...")
print(f"chart_config type: {type(data.get('chart_config'))}")
print(f"chart_config: {json.dumps(data.get('chart_config'), indent=2, default=str)}")
print("=" * 60)

# List all keys in the response
print("\nAll response keys:")
for key, value in data.items():
    val_str = str(value)[:50] if value else "None"
    print(f"  {key}: {val_str}")
