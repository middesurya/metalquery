#!/usr/bin/env python3
"""Check actual API response structure."""
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
print("Full Response Structure:")
print(json.dumps(data, indent=2, default=str))

print("\n\nKey Fields:")
print(f"success: {data.get('success')}")
print(f"sql: {data.get('sql', '')[:100]}")
print(f"visualization_config: {data.get('visualization_config')}")
print(f"show_kpi_card: {data.get('show_kpi_card')}")
print(f"show_table: {data.get('show_table')}")
print(f"chart_type in root: {data.get('chart_type')}")

# Check for nested chart info
viz = data.get('visualization_config') or {}
print(f"\nviz_config keys: {viz.keys() if viz else 'None'}")
print(f"chart_config: {viz.get('chart_config')}")
print(f"graph_type: {data.get('graph_type')}")
print(f"recommended_visualization: {data.get('recommended_visualization')}")
