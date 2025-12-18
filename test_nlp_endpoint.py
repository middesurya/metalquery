import requests
import json
import sys

NLP_URL = "http://127.0.0.1:8003/api/v1/generate-sql"

def test_query(question):
    print(f"Testing: {question}")
    try:
        response = requests.post(
            NLP_URL,
            json={"question": question},
            timeout=120
        )
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = sys.argv[1]
        test_query(question)
