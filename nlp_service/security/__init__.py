"""
MetalQuery NLP2SQL Security Module
Industrial-grade security implementation for NLP2SQL systems

Provides 4-layer defense against:
- Prompt Injection Attacks (OWASP LLM01:2025)
- Prompt Flipping Jailbreaks (FlipAttack)
- Red Team Attacks (6 vulnerability categories)
- SQL Injection Attacks

Compliance: IEC 62443 SL-2/SL-3
"""

from .flipping_detector import FlippingDetector, PromptSignatureValidator, FlippingMode
from .rbac import RBACMiddleware, DataMaskingEngine, UserRole, RBACPolicy
from .sql_validator import SQLInjectionValidator, SQLQuerySanitizer
from .anomaly_detector import AnomalyDetector, RedTeamDetector, UserBaseline
from .audit_logger import AuditLogger, AuditEvent, EventType, Severity, audit_logger
from .red_team_simulator import RedTeamAttackGenerator, SecurityTestRunner

__all__ = [
    # Flipping Detection
    'FlippingDetector',
    'PromptSignatureValidator',
    'FlippingMode',
    
    # RBAC
    'RBACMiddleware',
    'DataMaskingEngine',
    'UserRole',
    'RBACPolicy',
    
    # SQL Validation
    'SQLInjectionValidator',
    'SQLQuerySanitizer',
    
    # Anomaly Detection
    'AnomalyDetector',
    'RedTeamDetector',
    'UserBaseline',
    
    # Audit Logging
    'AuditLogger',
    'AuditEvent',
    'EventType',
    'Severity',
    'audit_logger',
    
    # Red Team Testing
    'RedTeamAttackGenerator',
    'SecurityTestRunner',
]

__version__ = '1.0.0'
__compliance__ = 'IEC 62443 SL-2/SL-3'
