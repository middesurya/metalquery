import os
import django
import sys
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot.models import AuditLog
from chatbot.views import execute_safe_query

def verify():
    print("Verifying Database Connection and AuditLog...")

    # 1. Test AuditLog creation
    try:
        log = AuditLog.objects.create(
            question="Test verification",
            sql="SELECT 1",
            success=True,
            row_count=1
        )
        print(f"[SUCCESS] Created AuditLog: {log}")
    except Exception as e:
        print(f"[FAILED] Could not create AuditLog: {e}")
        return

    # 2. Test execute_safe_query
    try:
        results = execute_safe_query("SELECT 1 as val")
        print(f"[SUCCESS] Query Result: {results}")
        if results == [{'val': 1}]:
             print("[SUCCESS] Query returned expected result.")
        else:
             print("[FAILED] Query returned unexpected result.")

    except Exception as e:
        print(f"[FAILED] Query execution failed: {e}")

if __name__ == "__main__":
    verify()
