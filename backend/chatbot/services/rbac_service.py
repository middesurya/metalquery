"""
RBAC Service - Single Source of Truth for Table Access Control
Queries existing auth tables to determine user's allowed tables.
"""
import logging
from typing import Set, Optional, Dict, Tuple
from django.db import connection
from django.core.cache import cache

from ignis.schema.exposed_tables import (
    FUNCTION_TABLE_MAPPING,
    KPI_METRIC_TABLE_MAPPING,
    EXPOSED_TABLES,
)

logger = logging.getLogger(__name__)

CACHE_TTL = 300  # 5 minutes


class RBACService:
    """
    Centralized RBAC service that determines allowed tables for a user.
    Integrates with existing users_usertoken, users_rolepermission, users_role_kpis.
    """

    @staticmethod
    def get_user_from_token(token: str) -> Optional[Dict]:
        """
        Look up user from token in users_usertoken table.
        Returns: {user_id, plant_id, username, is_superuser} or None
        """
        if not token:
            return None

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ut.user_id, ut.plant_id, u.username, u.is_superuser
                    FROM users_usertoken ut
                    JOIN users_user u ON ut.user_id = u.id
                    WHERE ut.token = %s AND u.record_status = true
                """, [token])
                row = cursor.fetchone()

                if row:
                    return {
                        'user_id': row[0],
                        'plant_id': row[1],
                        'username': row[2],
                        'is_superuser': row[3],
                    }
        except Exception as e:
            logger.error(f"Token lookup failed: {e}")

        return None

    @staticmethod
    def get_user_role_id(user_id: int) -> Optional[int]:
        """Get role_id for a user from users_userrole."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT role_id FROM users_userrole
                    WHERE user_id = %s
                    ORDER BY date_assigned DESC
                    LIMIT 1
                """, [user_id])
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Role lookup failed: {e}")
            return None

    @staticmethod
    def get_function_permissions(role_id: int, plant_id: str) -> Set[str]:
        """
        Get function codes where user has 'view' permission.
        Note: function_master_id stores function_code directly (VARCHAR).
        """
        function_codes = set()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT function_master_id
                    FROM users_rolepermission
                    WHERE role_id = %s
                      AND plant_id = %s
                      AND view = true
                      AND record_status = true
                """, [role_id, plant_id])

                function_codes = {row[0] for row in cursor.fetchall() if row[0]}

        except Exception as e:
            logger.error(f"Function permissions lookup failed: {e}")

        return function_codes

    @staticmethod
    def get_kpi_permissions(role_id: int) -> Set[str]:
        """
        Get KPI metric codes for a role.
        Note: kpi_metric_code is stored directly in users_role_kpis (VARCHAR).
        """
        kpi_codes = set()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT kpi_metric_code
                    FROM users_role_kpis
                    WHERE role_id = %s AND record_status = true
                """, [role_id])

                kpi_codes = {row[0] for row in cursor.fetchall() if row[0]}

        except Exception as e:
            logger.error(f"KPI permissions lookup failed: {e}")

        return kpi_codes

    @classmethod
    def get_allowed_tables(cls, token: str) -> Tuple[Set[str], Optional[Dict]]:
        """
        Main entry point: Get allowed tables for a token.

        Returns:
            (allowed_tables, user_info) or (empty_set, None) if unauthorized
        """
        # Check cache first
        cache_key = f"rbac_tables_{hash(token)}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Step 1: Validate token -> get user
        user_info = cls.get_user_from_token(token)
        if not user_info:
            logger.warning("Invalid or missing token")
            return set(), None

        # Step 2: Superuser gets all tables
        if user_info.get('is_superuser'):
            logger.info(f"Superuser {user_info['username']} - full access")
            result = (set(EXPOSED_TABLES), user_info)
            cache.set(cache_key, result, CACHE_TTL)
            return result

        # Step 3: Get role
        role_id = cls.get_user_role_id(user_info['user_id'])
        if not role_id:
            logger.warning(f"No role found for user {user_info['user_id']}")
            return set(), user_info

        # Step 4: Get function permissions -> map to tables
        function_codes = cls.get_function_permissions(role_id, user_info['plant_id'])
        allowed_tables = set()

        for func_code in function_codes:
            tables = FUNCTION_TABLE_MAPPING.get(func_code, [])
            allowed_tables.update(tables)

        # Step 5: Get KPI permissions -> map to tables
        kpi_codes = cls.get_kpi_permissions(role_id)
        for kpi_code in kpi_codes:
            table = KPI_METRIC_TABLE_MAPPING.get(kpi_code)
            if table:
                allowed_tables.add(table)

        # Intersect with EXPOSED_TABLES (defense in depth)
        allowed_tables = allowed_tables.intersection(EXPOSED_TABLES)

        logger.info(f"User {user_info['username']} allowed {len(allowed_tables)} tables")

        # Cache result
        result = (allowed_tables, user_info)
        cache.set(cache_key, result, CACHE_TTL)

        return result
