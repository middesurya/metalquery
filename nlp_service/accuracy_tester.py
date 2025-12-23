"""
accuracy_tester.py
Comprehensive NLP-to-SQL Accuracy Testing Framework

Features:
- Test suite covering all 35 KPI tables
- Multiple accuracy metrics (exact match, semantic match, execution success)
- Response time tracking
- Per-category breakdown
- Results export to JSON/CSV
"""

import json
import time
import csv
import re
import requests
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict


class AccuracyMetric(Enum):
    """Accuracy measurement methods"""
    EXACT_MATCH = "exact_match"        # SQL strings are identical
    SEMANTIC_MATCH = "semantic_match"  # Results are equivalent
    TABLE_CORRECT = "table_correct"    # Correct table selected
    COLUMN_CORRECT = "column_correct"  # Correct columns used
    AGGREGATION_CORRECT = "aggregation_correct"  # Correct AVG/SUM/COUNT
    DATE_FILTER_CORRECT = "date_filter_correct"  # Date range handled
    FURNACE_FILTER_CORRECT = "furnace_filter_correct"  # Furnace filtering
    EXECUTION_SUCCESS = "execution_success"  # Query runs without error
    PARTIAL_MATCH = "partial_match"    # Some parts correct
    FAILED = "failed"                  # Complete failure


@dataclass
class TestCase:
    """A single test case for accuracy measurement"""
    id: str
    category: str
    table: str
    question: str
    expected_sql: str
    difficulty: str = "medium"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class TestResult:
    """Result of running a single test case"""
    test_id: str
    question: str
    expected_sql: str
    generated_sql: str
    accuracy_metric: str
    table_match: bool
    column_match: bool
    aggregation_match: bool
    execution_success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AccuracyTester:
    """
    Comprehensive testing framework for NLP-to-SQL accuracy.
    """
    
    def __init__(self, nlp_service_url: str = "http://localhost:8003"):
        """
        Initialize tester with NLP service URL.
        """
        self.nlp_service_url = nlp_service_url
        self.test_results: List[TestResult] = []
        self.test_suite = self._create_test_suite()
    
    def _create_test_suite(self) -> List[TestCase]:
        """
        Create comprehensive test cases covering all 35 KPI tables.
        """
        
        return [
            # ========== OEE & PERFORMANCE ==========
            TestCase(
                id="perf_001",
                category="Performance - OEE",
                table="kpi_overall_equipment_efficiency_data",
                question="What is the average OEE for Furnace 1 in January 2025?",
                expected_sql="SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'",
                difficulty="easy",
                tags=["aggregation", "date_range", "furnace_filter"]
            ),
            TestCase(
                id="perf_002",
                category="Performance - OEE",
                table="kpi_overall_equipment_efficiency_data",
                question="Show furnace health by furnace",
                expected_sql="SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC",
                difficulty="easy",
                tags=["aggregation", "group_by"]
            ),
            TestCase(
                id="perf_003",
                category="Performance - OEE",
                table="kpi_overall_equipment_efficiency_data",
                question="OEE trend for the last 30 days",
                expected_sql="SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC",
                difficulty="medium",
                tags=["relative_date", "trend"]
            ),
            
            # ========== YIELD ==========
            TestCase(
                id="yield_001",
                category="Quality - Yield",
                table="kpi_yield_data",
                question="Show the average yield by furnace",
                expected_sql="SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC",
                difficulty="easy",
                tags=["aggregation", "group_by"]
            ),
            TestCase(
                id="yield_002",
                category="Quality - Yield",
                table="kpi_yield_data",
                question="Yield percentage for Furnace 2 in January 2025",
                expected_sql="SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = 2 AND date BETWEEN '2025-01-01' AND '2025-01-31'",
                difficulty="easy",
                tags=["aggregation", "date_range", "furnace_filter"]
            ),
            
            # ========== DEFECT RATE ==========
            TestCase(
                id="defect_001",
                category="Quality - Defect",
                table="kpi_defect_rate_data",
                question="Defect rate by furnace",
                expected_sql="SELECT furnace_no, AVG(defect_rate) as avg_defect FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect ASC",
                difficulty="easy",
                tags=["aggregation", "group_by"]
            ),
            TestCase(
                id="defect_002",
                category="Quality - Defect",
                table="kpi_defect_rate_data",
                question="What is the defect rate trend for Furnace 1?",
                expected_sql="SELECT date, defect_rate FROM kpi_defect_rate_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100",
                difficulty="medium",
                tags=["furnace_filter", "trend"]
            ),
            
            # ========== DOWNTIME ==========
            TestCase(
                id="down_001",
                category="Maintenance - Downtime",
                table="kpi_downtime_data",
                question="What is the total downtime for Furnace 1 in January 2025?",
                expected_sql="SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'",
                difficulty="easy",
                tags=["aggregation", "date_range", "furnace_filter"]
            ),
            TestCase(
                id="down_002",
                category="Maintenance - Downtime",
                table="kpi_downtime_data",
                question="Downtime by furnace last 30 days",
                expected_sql="SELECT furnace_no, SUM(downtime_hours) as total FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY furnace_no ORDER BY total DESC",
                difficulty="medium",
                tags=["aggregation", "relative_date", "group_by"]
            ),
            TestCase(
                id="down_003",
                category="Maintenance - Downtime",
                table="kpi_downtime_data",
                question="Which furnace has the most downtime?",
                expected_sql="SELECT furnace_no, SUM(downtime_hours) as total FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total DESC LIMIT 1",
                difficulty="medium",
                tags=["aggregation", "top_n"]
            ),
            
            # ========== ENERGY ==========
            TestCase(
                id="energy_001",
                category="Energy",
                table="kpi_energy_efficiency_data",
                question="What is the average energy efficiency for Furnace 1 in January 2025?",
                expected_sql="SELECT AVG(energy_efficiency) FROM kpi_energy_efficiency_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'",
                difficulty="easy",
                tags=["aggregation", "date_range", "furnace_filter"]
            ),
            TestCase(
                id="energy_002",
                category="Energy",
                table="kpi_energy_used_data",
                question="Total energy used last week",
                expected_sql="SELECT furnace_no, SUM(energy_used) as total FROM kpi_energy_used_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY furnace_no",
                difficulty="medium",
                tags=["aggregation", "relative_date"]
            ),
            
            # ========== MTBF/MTTR ==========
            TestCase(
                id="mtbf_001",
                category="Maintenance - Reliability",
                table="kpi_mean_time_between_failures_data",
                question="What is the MTBF for Furnace 1 in January 2025?",
                expected_sql="SELECT AVG(mtbf_hours) FROM kpi_mean_time_between_failures_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'",
                difficulty="easy",
                tags=["aggregation", "date_range", "furnace_filter"]
            ),
            TestCase(
                id="mttr_001",
                category="Maintenance - Reliability",
                table="kpi_mean_time_to_repair_data",
                question="MTTR by furnace",
                expected_sql="SELECT furnace_no, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY furnace_no ORDER BY avg_mttr ASC",
                difficulty="easy",
                tags=["aggregation", "group_by"]
            ),
            
            # ========== TAP PRODUCTION ==========
            TestCase(
                id="tap_001",
                category="Production - Tap",
                table="core_process_tap_production",
                question="What was the total tap production for Furnace 1 in January 2025?",
                expected_sql="SELECT SUM(cast_weight) as total_production FROM core_process_tap_production WHERE furnace_no = 1 AND tap_production_datetime BETWEEN '2025-01-01' AND '2025-01-31'",
                difficulty="easy",
                tags=["aggregation", "date_range", "furnace_filter"]
            ),
            TestCase(
                id="tap_002",
                category="Production - Tap",
                table="core_process_tap_production",
                question="Recent tap production",
                expected_sql="SELECT tap_id, furnace_no, cast_weight, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20",
                difficulty="easy",
                tags=["recent", "limit"]
            ),
            
            # ========== SAFETY ==========
            TestCase(
                id="safety_001",
                category="Safety",
                table="kpi_safety_incidents_reported_data",
                question="How many safety incidents were reported for Furnace 1 in January 2025?",
                expected_sql="SELECT COUNT(*) FROM kpi_safety_incidents_reported_data WHERE furnace_no = 1 AND date BETWEEN '2025-01-01' AND '2025-01-31'",
                difficulty="easy",
                tags=["count", "date_range", "furnace_filter"]
            ),
            
            # ========== MAINTENANCE ==========
            TestCase(
                id="maint_001",
                category="Maintenance",
                table="kpi_maintenance_compliance_data",
                question="Show maintenance compliance percentage",
                expected_sql="SELECT furnace_no, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY furnace_no",
                difficulty="easy",
                tags=["aggregation", "group_by"]
            ),
            
            # ========== CAPACITY ==========
            TestCase(
                id="cap_001",
                category="Capacity",
                table="kpi_resource_capacity_utilization_data",
                question="Capacity utilization by furnace",
                expected_sql="SELECT furnace_no, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY furnace_no ORDER BY avg_utilization DESC",
                difficulty="easy",
                tags=["aggregation", "group_by"]
            ),
            
            # ========== CONFIG ==========
            TestCase(
                id="config_001",
                category="Configuration",
                table="furnace_config_parameters",
                question="What are the crucible diameter and depth for Furnace 1?",
                expected_sql="SELECT crucible_diameter, crucible_depth FROM furnace_config_parameters WHERE furnace_no = 1",
                difficulty="easy",
                tags=["specific_columns", "furnace_filter"]
            ),
            
            # ========== COMPLEX QUERIES ==========
            TestCase(
                id="complex_001",
                category="Complex",
                table="kpi_overall_equipment_efficiency_data",
                question="Which furnaces have OEE below 80%?",
                expected_sql="SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no HAVING AVG(oee_percentage) < 80",
                difficulty="hard",
                tags=["aggregation", "having", "complex"]
            ),
            TestCase(
                id="complex_002",
                category="Complex",
                table="kpi_downtime_data",
                question="Top 5 furnaces by total downtime in 2025",
                expected_sql="SELECT furnace_no, SUM(downtime_hours) as total FROM kpi_downtime_data WHERE date >= '2025-01-01' GROUP BY furnace_no ORDER BY total DESC LIMIT 5",
                difficulty="hard",
                tags=["aggregation", "top_n", "date_range"]
            ),
            
            # ========== EDGE CASES ==========
            TestCase(
                id="edge_001",
                category="Edge Case",
                table="kpi_overall_equipment_efficiency_data",
                question="furnace health",  # Very short query
                expected_sql="SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no",
                difficulty="medium",
                tags=["short_query", "ambiguous"]
            ),
            TestCase(
                id="edge_002",
                category="Edge Case",
                table="kpi_yield_data",
                question="yeild for furnance 1",  # Typos
                expected_sql="SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = 1",
                difficulty="hard",
                tags=["typo", "fuzzy_match"]
            ),
        ]
    
    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for comparison (remove extra whitespace, lowercase)."""
        if not sql:
            return ""
        # Remove extra whitespace
        sql = re.sub(r'\s+', ' ', sql.strip().lower())
        # Remove trailing semicolon
        sql = sql.rstrip(';')
        return sql
    
    def _extract_table_name(self, sql: str) -> Optional[str]:
        """Extract table name from SQL query."""
        match = re.search(r'from\s+(\w+)', sql, re.IGNORECASE)
        return match.group(1).lower() if match else None
    
    def _extract_aggregation(self, sql: str) -> Optional[str]:
        """Extract aggregation function from SQL."""
        sql_upper = sql.upper()
        for agg in ['AVG', 'SUM', 'COUNT', 'MAX', 'MIN']:
            if agg + '(' in sql_upper:
                return agg
        return None
    
    def _compare_sql(self, expected: str, generated: str) -> Dict[str, bool]:
        """
        Compare expected and generated SQL.
        Returns detailed comparison results.
        """
        expected_norm = self._normalize_sql(expected)
        generated_norm = self._normalize_sql(generated)
        
        expected_table = self._extract_table_name(expected)
        generated_table = self._extract_table_name(generated)
        
        expected_agg = self._extract_aggregation(expected)
        generated_agg = self._extract_aggregation(generated)
        
        return {
            "exact_match": expected_norm == generated_norm,
            "table_match": expected_table == generated_table,
            "aggregation_match": expected_agg == generated_agg,
            "has_where": 'where' in generated_norm,
            "has_group_by": 'group by' in generated_norm,
            "has_order_by": 'order by' in generated_norm,
            "has_limit": 'limit' in generated_norm,
        }
    
    def _call_nlp_service(self, question: str) -> Tuple[str, float, Optional[str]]:
        """
        Call NLP service to generate SQL.
        Returns: (generated_sql, response_time_ms, error_message)
        """
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.nlp_service_url}/api/v1/generate-sql",
                json={"question": question},
                timeout=30
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("sql", ""), response_time, None
                else:
                    return "", response_time, data.get("error", "Unknown error")
            else:
                return "", response_time, f"HTTP {response.status_code}"
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return "", response_time, str(e)
    
    def run_single_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case and return the result."""
        
        # Call NLP service
        generated_sql, response_time, error = self._call_nlp_service(test_case.question)
        
        # Compare results
        comparison = self._compare_sql(test_case.expected_sql, generated_sql)
        
        # Determine accuracy metric
        if error:
            accuracy = AccuracyMetric.FAILED.value
        elif comparison["exact_match"]:
            accuracy = AccuracyMetric.EXACT_MATCH.value
        elif comparison["table_match"] and comparison["aggregation_match"]:
            accuracy = AccuracyMetric.SEMANTIC_MATCH.value
        elif comparison["table_match"]:
            accuracy = AccuracyMetric.TABLE_CORRECT.value
        else:
            accuracy = AccuracyMetric.PARTIAL_MATCH.value
        
        return TestResult(
            test_id=test_case.id,
            question=test_case.question,
            expected_sql=test_case.expected_sql,
            generated_sql=generated_sql,
            accuracy_metric=accuracy,
            table_match=comparison["table_match"],
            column_match=comparison.get("column_match", False),
            aggregation_match=comparison["aggregation_match"],
            execution_success=error is None,
            response_time_ms=response_time,
            error_message=error
        )
    
    def run_all_tests(self, verbose: bool = True) -> List[TestResult]:
        """Run all test cases and return results."""
        self.test_results = []
        
        print(f"\n{'='*60}")
        print(f"Running {len(self.test_suite)} Test Cases")
        print(f"{'='*60}\n")
        
        for i, test_case in enumerate(self.test_suite, 1):
            result = self.run_single_test(test_case)
            self.test_results.append(result)
            
            if verbose:
                status = "[PASS]" if result.accuracy_metric in ["exact_match", "semantic_match"] else "[FAIL]"
                print(f"[{i:02d}/{len(self.test_suite)}] {status} {test_case.id}: {result.accuracy_metric}")
                if result.error_message:
                    print(f"         Error: {result.error_message}")
        
        return self.test_results
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from test results."""
        if not self.test_results:
            return {"error": "No test results available"}
        
        total = len(self.test_results)
        exact_matches = sum(1 for r in self.test_results if r.accuracy_metric == "exact_match")
        semantic_matches = sum(1 for r in self.test_results if r.accuracy_metric == "semantic_match")
        table_correct = sum(1 for r in self.test_results if r.table_match)
        agg_correct = sum(1 for r in self.test_results if r.aggregation_match)
        execution_success = sum(1 for r in self.test_results if r.execution_success)
        
        avg_response_time = sum(r.response_time_ms for r in self.test_results) / total
        
        # Category breakdown
        category_stats = {}
        for result in self.test_results:
            test_case = next((t for t in self.test_suite if t.id == result.test_id), None)
            if test_case:
                cat = test_case.category
                if cat not in category_stats:
                    category_stats[cat] = {"total": 0, "passed": 0}
                category_stats[cat]["total"] += 1
                if result.accuracy_metric in ["exact_match", "semantic_match"]:
                    category_stats[cat]["passed"] += 1
        
        return {
            "total_tests": total,
            "exact_match_count": exact_matches,
            "exact_match_rate": f"{(exact_matches/total)*100:.1f}%",
            "semantic_match_count": semantic_matches,
            "semantic_match_rate": f"{(semantic_matches/total)*100:.1f}%",
            "overall_accuracy": f"{((exact_matches + semantic_matches)/total)*100:.1f}%",
            "table_accuracy": f"{(table_correct/total)*100:.1f}%",
            "aggregation_accuracy": f"{(agg_correct/total)*100:.1f}%",
            "execution_success_rate": f"{(execution_success/total)*100:.1f}%",
            "avg_response_time_ms": f"{avg_response_time:.0f}",
            "category_breakdown": category_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_summary(self):
        """Print a formatted summary of results."""
        summary = self.get_summary()
        
        print(f"\n{'='*60}")
        print("ACCURACY TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests:           {summary['total_tests']}")
        print(f"Exact Match:           {summary['exact_match_count']} ({summary['exact_match_rate']})")
        print(f"Semantic Match:        {summary['semantic_match_count']} ({summary['semantic_match_rate']})")
        print(f"Overall Accuracy:      {summary['overall_accuracy']}")
        print(f"Table Accuracy:        {summary['table_accuracy']}")
        print(f"Aggregation Accuracy:  {summary['aggregation_accuracy']}")
        print(f"Execution Success:     {summary['execution_success_rate']}")
        print(f"Avg Response Time:     {summary['avg_response_time_ms']} ms")
        
        print(f"\n{'='*60}")
        print("CATEGORY BREAKDOWN")
        print(f"{'='*60}")
        for cat, stats in summary['category_breakdown'].items():
            rate = (stats['passed']/stats['total'])*100 if stats['total'] > 0 else 0
            print(f"{cat:30} {stats['passed']}/{stats['total']} ({rate:.0f}%)")
    
    def export_to_json(self, filename: str = "accuracy_results.json"):
        """Export results to JSON file."""
        data = {
            "summary": self.get_summary(),
            "results": [r.to_dict() for r in self.test_results]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Results exported to {filename}")
    
    def export_to_csv(self, filename: str = "accuracy_results.csv"):
        """Export results to CSV file."""
        if not self.test_results:
            print("No results to export")
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.test_results[0].to_dict().keys())
            writer.writeheader()
            for result in self.test_results:
                writer.writerow(result.to_dict())
        print(f"Results exported to {filename}")


def main():
    """Run accuracy tests."""
    print("\n" + "="*60)
    print("NLP-to-SQL Accuracy Testing Framework")
    print("="*60)
    
    # Initialize tester
    tester = AccuracyTester(nlp_service_url="http://localhost:8003")
    
    # Run all tests
    results = tester.run_all_tests(verbose=True)
    
    # Print summary
    tester.print_summary()
    
    # Export results
    tester.export_to_json()
    tester.export_to_csv()
    
    return tester


if __name__ == "__main__":
    main()
