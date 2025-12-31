"""
Anomaly Detector - Behavioral Analysis for Red Team Attack Detection
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserBaseline:
    """User's historical behavior baseline."""
    avg_queries_per_hour: float = 5.0
    avg_result_rows: int = 50
    frequently_accessed_tables: List[str] = field(default_factory=list)
    max_query_time: float = 5.0
    typical_query_patterns: List[str] = field(default_factory=list)


class AnomalyDetector:
    """
    Detects unusual query patterns that might indicate red team attacks.
    Tracks: query frequency, result size, table access patterns, user behavior.
    """
    
    def __init__(self):
        self.user_baselines: Dict[str, UserBaseline] = {}
        self.user_query_history: Dict[str, List[datetime]] = defaultdict(list)
        self.restricted_tables = {
            'audit_logs', 'user_credentials', 'system_config',
            'security_logs', 'api_keys', 'passwords'
        }
        self.anomaly_threshold = 0.7
    
    def get_baseline(self, user_id: str) -> UserBaseline:
        """Get or create user baseline."""
        if user_id not in self.user_baselines:
            self.user_baselines[user_id] = UserBaseline()
        return self.user_baselines[user_id]
    
    def is_anomalous(self, user_id: str, query_context: Dict) -> Tuple[bool, str, float]:
        """
        Check if current query deviates significantly from baseline.
        Returns: (is_anomalous, reason, score)
        """
        reasons = []
        anomaly_score = 0.0
        baseline = self.get_baseline(user_id)
        
        # Check 1: Query frequency spike
        hourly_count = self._get_hourly_query_count(user_id)
        if hourly_count > baseline.avg_queries_per_hour * 3:
            reasons.append(f"Query frequency spike: {hourly_count} queries/hour")
            anomaly_score += 0.3
        
        # Check 2: Unusual result set size
        estimated_rows = query_context.get('estimated_rows', 0)
        if estimated_rows > baseline.avg_result_rows * 5:
            reasons.append(f"Abnormal result size: {estimated_rows} rows")
            anomaly_score += 0.2
        
        # Check 3: Accessing restricted tables
        accessed_tables = query_context.get('tables', [])
        for table in accessed_tables:
            if table.lower() in self.restricted_tables:
                reasons.append(f"Restricted table access: {table}")
                anomaly_score += 0.4
        
        # Check 4: UNION clause (potential data exfiltration)
        sql = query_context.get('sql', '')
        if 'UNION' in sql.upper():
            reasons.append("UNION clause detected (potential data exfiltration)")
            anomaly_score += 0.3
        
        # Check 5: Multiple table access in single query
        if len(accessed_tables) > 4:
            reasons.append(f"Too many tables in query: {len(accessed_tables)}")
            anomaly_score += 0.2
        
        # Check 6: Unusual query time
        query_time = query_context.get('execution_time', 0)
        if query_time > baseline.max_query_time * 3:
            reasons.append(f"Unusual query time: {query_time}s")
            anomaly_score += 0.15
        
        # Track query for baseline updates
        self._record_query(user_id)
        
        is_anomalous = anomaly_score >= self.anomaly_threshold
        reason = " | ".join(reasons) if reasons else "No anomalies detected"
        
        if is_anomalous:
            logger.warning(f"🚨 ANOMALY DETECTED for user {user_id}: {reason} (score: {anomaly_score:.2f})")
        
        return is_anomalous, reason, min(anomaly_score, 1.0)
    
    def _get_hourly_query_count(self, user_id: str) -> int:
        """Get query count for past hour."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        history = self.user_query_history.get(user_id, [])
        recent_queries = [q for q in history if q > hour_ago]
        
        return len(recent_queries)
    
    def _record_query(self, user_id: str):
        """Record query timestamp for baseline tracking."""
        self.user_query_history[user_id].append(datetime.now())
        
        # Clean up old entries (keep last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        self.user_query_history[user_id] = [
            q for q in self.user_query_history[user_id] if q > cutoff
        ]
    
    def update_baseline(self, user_id: str, query_stats: Dict):
        """Update user baseline with new query statistics."""
        baseline = self.get_baseline(user_id)
        
        # Rolling average updates
        if 'result_rows' in query_stats:
            baseline.avg_result_rows = (baseline.avg_result_rows * 0.9 + 
                                        query_stats['result_rows'] * 0.1)
        
        if 'tables' in query_stats:
            for table in query_stats['tables']:
                if table not in baseline.frequently_accessed_tables:
                    baseline.frequently_accessed_tables.append(table)
                    # Keep only top 20 tables
                    baseline.frequently_accessed_tables = baseline.frequently_accessed_tables[-20:]
        
        if 'execution_time' in query_stats:
            baseline.max_query_time = max(baseline.max_query_time, query_stats['execution_time'])


class RedTeamDetector:
    """
    Specific detection for red team attack patterns.
    Based on 6 vulnerability categories.
    """
    
    def __init__(self):
        self.attack_patterns = {
            'reward_hacking': [
                r'fake\s+result',
                r'pretend\s+completed',
                r'looks\s+good\s+but',
            ],
            'deceptive_alignment': [
                r'hidden\s+goal',
                r'true\s+objective',
                r'real\s+purpose',
            ],
            'data_exfiltration': [
                r'extract\s+all',
                r'dump\s+database',
                r'export\s+everything',
                r'show\s+all\s+records',
            ],
            'privilege_escalation': [
                r'admin\s+access',
                r'bypass\s+permission',
                r'override\s+role',
            ],
            'prompt_leaking': [
                r'show\s+system\s+prompt',
                r'reveal\s+instructions',
                r'what\s+are\s+your\s+rules',
            ],
            'model_manipulation': [
                r'ignore\s+training',
                r'forget\s+constraints',
                r'new\s+persona',
            ]
        }
    
    def detect(self, prompt: str) -> Dict[str, any]:
        """
        Detect red team attack patterns in prompt.
        """
        import re
        
        detected = []
        total_score = 0.0
        
        for category, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    detected.append(category)
                    total_score += 0.25
                    break
        
        detected = list(set(detected))
        
        result = {
            'is_attack': len(detected) > 0,
            'categories': detected,
            'score': min(total_score, 1.0),
            'severity': 'HIGH' if total_score > 0.5 else 'MEDIUM' if total_score > 0.25 else 'LOW'
        }
        
        if result['is_attack']:
            logger.warning(f"🚨 RED TEAM ATTACK DETECTED: {detected} (score: {total_score:.2f})")
        
        return result
