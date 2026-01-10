"""Check user permissions and get full tokens"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection
from chatbot.services.rbac_service import RBACService

# Get tokens
print("=" * 60)
print("TOKENS FOR TESTING")
print("=" * 60)

with connection.cursor() as c:
    c.execute("""
        SELECT ut.token, u.username, u.is_superuser
        FROM users_usertoken ut
        JOIN users_user u ON ut.user_id = u.id
        WHERE u.record_status = true AND ut.token IS NOT NULL
    """)
    rows = c.fetchall()

    for token, username, is_super in rows:
        print(f"\nUser: {username}")
        print(f"Superuser: {is_super}")
        print(f"Token: {token}")

        # Get allowed tables using RBACService
        allowed_tables, user_info = RBACService.get_allowed_tables(token)
        print(f"Allowed Tables ({len(allowed_tables)}): {sorted(allowed_tables)[:5]}...")
