import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add nlp_service to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'nlp_service')))

def test_nlp_logic():
    print("Testing NLP Service Logic...")
    
    # Mock requests.get to simulate Django API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "schema": {
            "test_table": {
                "description": "A test table",
                "columns": [
                    {"name": "id", "type": "int", "description": "Primary Key"},
                    {"name": "value", "type": "varchar", "description": "Test Value"}
                ]
            }
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch('requests.get', return_value=mock_response):
        
        # Import after patching
        from nlp_service.schema_loader import schema_loader
        from nlp_service.main import generate_sql, GenerateSQLRequest
        
        # Test 1: Schema Loading
        print("\n[1] Testing Schema Loader...")
        schema = schema_loader.load_schema()
        if "test_table" in schema:
            print("SUCCESS: Schema loaded correctly from mock API.")
        else:
            print("FAILED: Schema not loaded.")
            return

        # Test 2: Context Generation
        print("\n[2] Testing Schema Context...")
        context = schema_loader.get_schema_context()
        if "test_table" in context and "id: int" in context:
            print("SUCCESS: Context generated correctly.")
        else:
            print("FAILED: Context generation incorrect.")
            print(f"Context: {context}")
            return
            
        print("\n-----------------------------------------------------------")
        print("Note: Skipping actual LLM call in this script to avoid stalling.")
        print("To fully verify, run 'python nlp_service/main.py' and curl it.")
        print("-----------------------------------------------------------")

if __name__ == "__main__":
    test_nlp_logic()
