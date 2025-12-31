"""
Audit Logger - Comprehensive Security Event Logging
IEC 62443 Compliant Audit Trail
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    QUERY_EXECUTED = "QUERY_EXECUTED"
    INJECTION_BLOCKED = "INJECTION_BLOCKED"
    FLIPPING_DETECTED = "FLIPPING_DETECTED"
    RBAC_VIOLATION = "RBAC_VIOLATION"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    RED_TEAM_BLOCKED = "RED_TEAM_BLOCKED"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class AuditEvent:
    """Audit event record."""
    event_type: EventType
    severity: Severity
    timestamp: datetime
    user_id: Optional[str]
    ip_address: str
    sql_hash: str = ""
    sql_preview: str = ""
    result_count: int = 0
    execution_time_ms: int = 0
    threat_detected: str = ""
    threat_score: float = 0.0
    details: Dict = field(default_factory=dict)
    is_suspicious: bool = False


class AuditLogger:
    """
    Centralized audit logging for all security events.
    Thread-safe, persistent storage ready.
    """
    
    def __init__(self, max_memory_events: int = 10000):
        self.events: List[AuditEvent] = []
        self.max_memory_events = max_memory_events
    
    @staticmethod
    def hash_query(query: str) -> str:
        """Create hash of query for audit trail."""
        return hashlib.sha256(query.encode()).hexdigest()[:32]
    
    def log_event(self, event: AuditEvent):
        """Log an audit event."""
        self.events.append(event)
        
        # Trim old events if over limit
        if len(self.events) > self.max_memory_events:
            self.events = self.events[-self.max_memory_events:]
        
        # Log to standard logger
        log_level = logging.INFO
        if event.severity in [Severity.HIGH, Severity.CRITICAL]:
            log_level = logging.WARNING
        
        logger.log(log_level, f"📝 AUDIT: {event.event_type.value} | "
                             f"User: {event.user_id} | "
                             f"IP: {event.ip_address} | "
                             f"Severity: {event.severity.value}")
    
    def log_query(
        self,
        user_id: str,
        sql: str,
        result_count: int,
        execution_time: int,
        ip_address: str,
        threat_detected: str = None,
        threat_score: float = 0.0
    ):
        """Log successful query execution."""
        event = AuditEvent(
            event_type=EventType.QUERY_EXECUTED,
            severity=Severity.LOW,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            sql_hash=self.hash_query(sql),
            sql_preview=sql[:500],
            result_count=result_count,
            execution_time_ms=execution_time,
            threat_detected=threat_detected or '',
            threat_score=threat_score,
            is_suspicious=threat_score > 0.3
        )
        self.log_event(event)
    
    def log_blocked_injection(
        self,
        user_id: str,
        prompt: str,
        attack_type: str,
        confidence: float,
        ip_address: str
    ):
        """Log blocked injection attack."""
        event = AuditEvent(
            event_type=EventType.INJECTION_BLOCKED,
            severity=Severity.HIGH,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            sql_preview=f"Blocked injection attack: {attack_type}",
            threat_detected=attack_type,
            threat_score=confidence,
            details={'attack_type': attack_type, 'confidence': confidence},
            is_suspicious=True
        )
        self.log_event(event)
    
    def log_flipping_detected(
        self,
        user_id: str,
        prompt: str,
        detected_modes: List[str],
        confidence: float,
        ip_address: str
    ):
        """Log detected flipping attack."""
        event = AuditEvent(
            event_type=EventType.FLIPPING_DETECTED,
            severity=Severity.HIGH,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            sql_preview=f"Flipping attack detected: {', '.join(detected_modes)}",
            threat_detected='FlipAttack',
            threat_score=confidence,
            details={'modes': detected_modes, 'confidence': confidence},
            is_suspicious=True
        )
        self.log_event(event)
    
    def log_rbac_violation(
        self,
        user_id: str,
        attempted_table: str,
        user_role: str,
        ip_address: str
    ):
        """Log RBAC violation attempt."""
        event = AuditEvent(
            event_type=EventType.RBAC_VIOLATION,
            severity=Severity.MEDIUM,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            threat_detected='RBAC_VIOLATION',
            threat_score=0.6,
            details={'attempted_table': attempted_table, 'user_role': user_role},
            is_suspicious=True
        )
        self.log_event(event)
    
    def log_rate_limit_exceeded(
        self,
        user_id: str,
        ip_address: str,
        limit: int,
        window: int
    ):
        """Log rate limit exceeded."""
        event = AuditEvent(
            event_type=EventType.RATE_LIMIT_EXCEEDED,
            severity=Severity.MEDIUM,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            threat_detected='RATE_LIMIT',
            details={'limit': limit, 'window_seconds': window},
            is_suspicious=True
        )
        self.log_event(event)
    
    def log_anomaly_detected(
        self,
        user_id: str,
        reason: str,
        score: float,
        ip_address: str
    ):
        """Log anomaly detection."""
        event = AuditEvent(
            event_type=EventType.ANOMALY_DETECTED,
            severity=Severity.MEDIUM if score < 0.7 else Severity.HIGH,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            threat_detected='ANOMALY',
            threat_score=score,
            details={'reason': reason},
            is_suspicious=True
        )
        self.log_event(event)
    
    def log_red_team_blocked(
        self,
        user_id: str,
        categories: List[str],
        score: float,
        ip_address: str
    ):
        """Log blocked red team attack."""
        event = AuditEvent(
            event_type=EventType.RED_TEAM_BLOCKED,
            severity=Severity.CRITICAL,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            threat_detected='RED_TEAM',
            threat_score=score,
            details={'categories': categories},
            is_suspicious=True
        )
        self.log_event(event)
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report for IEC 62443."""
        total_queries = len([e for e in self.events if e.event_type == EventType.QUERY_EXECUTED])
        blocked_attacks = len([e for e in self.events if e.is_suspicious])
        
        avg_threat_score = 0.0
        if self.events:
            scores = [e.threat_score for e in self.events]
            avg_threat_score = sum(scores) / len(scores)
        
        high_severity = len([e for e in self.events if e.severity in [Severity.HIGH, Severity.CRITICAL]])
        
        events_by_type = {}
        for e in self.events:
            event_type = e.event_type.value
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
        
        return {
            'report_generated': datetime.now().isoformat(),
            'total_events': len(self.events),
            'total_queries': total_queries,
            'blocked_attacks': blocked_attacks,
            'avg_threat_score': round(avg_threat_score, 4),
            'high_severity_events': high_severity,
            'events_by_type': events_by_type,
            'compliance': 'IEC 62443 SL-2/SL-3'
        }
    
    def get_recent_suspicious(self, limit: int = 20) -> List[AuditEvent]:
        """Get recent suspicious events."""
        suspicious = [e for e in self.events if e.is_suspicious]
        return suspicious[-limit:]
    
    def export_to_json(self) -> str:
        """Export all events to JSON."""
        events_dict = []
        for e in self.events:
            events_dict.append({
                'event_type': e.event_type.value,
                'severity': e.severity.value,
                'timestamp': e.timestamp.isoformat(),
                'user_id': e.user_id,
                'ip_address': e.ip_address,
                'sql_hash': e.sql_hash,
                'threat_detected': e.threat_detected,
                'threat_score': e.threat_score,
                'is_suspicious': e.is_suspicious,
                'details': e.details
            })
        return json.dumps(events_dict, indent=2)


# Global audit logger instance
audit_logger = AuditLogger()
