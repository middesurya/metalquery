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

try:
    print("Testing extraction logic with fixed str() conversion...")
    input_text = "Here is valid SQL: SELECT * FROM kpi_table LIMIT 10; Hope this helps."
    output = clean_generated_sql(input_text)
    print(f"Input: {input_text}")
    print(f"Output: {output}")
    
    if output == "SELECT * FROM kpi_table LIMIT 10":
        print("SUCCESS: Extraction working correctly.")
        sys.exit(0)
    else:
        print(f"FAILURE: Expected 'SELECT * FROM kpi_table LIMIT 10', got '{output}'")
        sys.exit(1)
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    sys.exit(1)
