import os
import django
import sys
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot.relevant_models import RELEVANT_MODELS

def check_connectivity():
    print(f"Checking connectivity for {len(RELEVANT_MODELS)} tables...\n")
    print(f"{'TABLE NAME':<50} | {'STATUS':<10} | {'ROWS':<10}")
    print("-" * 80)

    success_count = 0
    
    for model in RELEVANT_MODELS:
        table_name = model._meta.db_table
        try:
            # Try to count rows - this forces a DB query
            count = model.objects.count()
            print(f"{table_name:<50} | {'OK':<10} | {count:<10}")
            success_count += 1
        except Exception as e:
            # If counting fails, there's a connectivity or schema mismatch issue
            error_msg = str(e).split('\n')[0][:30] + "..." # Truncate error
            print(f"{table_name:<50} | {'FAILED':<10} | {error_msg}")

    print("-" * 80)
    print(f"\nSuccessfully connected to {success_count}/{len(RELEVANT_MODELS)} tables.")

if __name__ == "__main__":
    check_connectivity()
