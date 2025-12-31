"""
RBAC - Role-Based Access Control for MetalQuery
4-tier access control with data masking
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class UserRole(Enum):
    ADMIN = "admin"         # Full access
    ENGINEER = "engineer"   # Design specs visible
    OPERATOR = "operator"   # Limited specs, no composition
    VIEWER = "viewer"       # Read-only, high-level data only


@dataclass
class RBACPolicy:
    """RBAC policy definition for a role."""
    role: UserRole
    accessible_tables: Optional[List[str]]  # None = all tables
    readable_columns: Optional[List[str]]   # None = all columns
    max_result_rows: int
    allow_delete: bool
    allow_update: bool
    masked_columns: List[str]


class RBACMiddleware:
    """
    Enforces role-based access control at the query level.
    Dynamically modifies queries to include role-based restrictions.
    """
    
    def __init__(self):
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[str, RBACPolicy]:
        """Load RBAC policies."""
        return {
            'admin': RBACPolicy(
                role=UserRole.ADMIN,
                accessible_tables=None,  # All tables
                readable_columns=None,   # All columns
                max_result_rows=10000,
                allow_delete=True,
                allow_update=True,
                masked_columns=[]
            ),
            'engineer': RBACPolicy(
                role=UserRole.ENGINEER,
                accessible_tables=[
                    'kpi_overall_equipment_efficiency_data',
                    'kpi_downtime_data',
                    'kpi_yield_data',
                    'kpi_energy_used_data',
                    'kpi_defect_rate_data',
                    'core_process_tap_production',
                    'core_process_tap_process',
                    'furnace_furnaceconfig',
                    'furnace_config_parameters',
                    'log_book_furnace_down_time_event',
                ],
                readable_columns=None,  # All except masked
                max_result_rows=5000,
                allow_delete=False,
                allow_update=False,
                masked_columns=['cost', 'supplier_id', 'internal_notes']
            ),
            'operator': RBACPolicy(
                role=UserRole.OPERATOR,
                accessible_tables=[
                    'kpi_overall_equipment_efficiency_data',
                    'kpi_downtime_data',
                    'kpi_yield_data',
                    'core_process_tap_production',
                    'furnace_furnaceconfig',
                ],
                readable_columns=[
                    'furnace_no', 'date', 'shift_id', 'oee_percentage',
                    'downtime_hours', 'yield_percentage', 'cast_weight'
                ],
                max_result_rows=1000,
                allow_delete=False,
                allow_update=False,
                masked_columns=['composition', 'cost', 'heat_treatment_process', 'supplier_id']
            ),
            'viewer': RBACPolicy(
                role=UserRole.VIEWER,
                accessible_tables=[
                    'kpi_overall_equipment_efficiency_data',
                    'kpi_downtime_data',
                    'furnace_furnaceconfig',
                ],
                readable_columns=['furnace_no', 'date', 'oee_percentage', 'downtime_hours'],
                max_result_rows=500,
                allow_delete=False,
                allow_update=False,
                masked_columns=['*']  # Mask most details
            )
        }
    
    def get_policy(self, user_role: str) -> RBACPolicy:
        """Get policy for a role."""
        return self.policies.get(user_role, self.policies['viewer'])
    
    def check_table_access(self, user_role: str, tables: List[str]) -> tuple[bool, str]:
        """
        Check if user can access the specified tables.
        Returns: (allowed, reason)
        """
        policy = self.get_policy(user_role)
        
        if policy.accessible_tables is None:
            return True, "Full access"
        
        for table in tables:
            if table not in policy.accessible_tables:
                logger.warning(f"🚫 RBAC VIOLATION: {user_role} cannot access {table}")
                return False, f"Role {user_role} cannot access table {table}"
        
        return True, "Access granted"
    
    def check_operation(self, user_role: str, operation: str) -> tuple[bool, str]:
        """
        Check if user can perform the specified operation.
        """
        policy = self.get_policy(user_role)
        
        if operation.upper() == 'DELETE' and not policy.allow_delete:
            return False, f"Role {user_role} cannot delete"
        
        if operation.upper() == 'UPDATE' and not policy.allow_update:
            return False, f"Role {user_role} cannot update"
        
        return True, "Operation allowed"
    
    def apply_row_limit(self, user_role: str, requested_limit: int) -> int:
        """
        Apply row limit based on role.
        """
        policy = self.get_policy(user_role)
        return min(requested_limit, policy.max_result_rows)
    
    def get_masked_columns(self, user_role: str) -> List[str]:
        """Get list of columns that should be masked for this role."""
        policy = self.get_policy(user_role)
        return policy.masked_columns


class DataMaskingEngine:
    """
    Masks sensitive data in query results before returning to user.
    """
    
    def __init__(self, rbac: RBACMiddleware = None):
        self.rbac = rbac or RBACMiddleware()
    
    def mask_result(self, data: List[Dict], user_role: str) -> List[Dict]:
        """
        Apply masking to result set based on user role.
        """
        masked_columns = self.rbac.get_masked_columns(user_role)
        
        if not masked_columns:
            return data
        
        if '*' in masked_columns:
            # Mask all sensitive columns
            sensitive_patterns = ['cost', 'price', 'supplier', 'composition', 'internal', 'secret']
            masked_columns = sensitive_patterns
        
        masked_data = []
        for row in data:
            masked_row = {}
            for key, value in row.items():
                should_mask = any(pattern in key.lower() for pattern in masked_columns)
                if should_mask:
                    masked_row[key] = '***MASKED***'
                else:
                    masked_row[key] = value
            masked_data.append(masked_row)
        
        return masked_data
