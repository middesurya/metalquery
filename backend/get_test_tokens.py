"""Get test tokens for RBAC testing"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

print("Available test tokens:")
print("-" * 60)

with connection.cursor() as c:
    c.execute("""
        SELECT ut.token, u.username, u.is_superuser
        FROM users_usertoken ut
        JOIN users_user u ON ut.user_id = u.id
        WHERE u.record_status = true
        LIMIT 10
    """)
    rows = c.fetchall()

    if not rows:
        print("No tokens found in database!")
    else:
        for token, username, is_super in rows:
            if token:
                user_type = "SUPERUSER" if is_super else "Regular"
                print(f"User: {username:20} | Type: {user_type:10} | Token: {token[:30]}...")
            else:
                print(f"User: {username:20} | Token: NULL (skipped)")
