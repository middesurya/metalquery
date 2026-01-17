#!/usr/bin/env python3
"""Quick test of tap process query routing fixes."""
import sys
sys.path.append('nlp_service')

from query_router import QueryRouter

# Test queries
TEST_QUERIES = [
    "Show taps by furnace",
    "Display taps by furnace",
    "How many taps today?",
    "Show tap production by furnace",
    "What is the tap count for furnace 1",
    "Show recent tap production data",
    # Control - should route to BRD
    "What is the tap hole log?",
    "Explain the tap analysis report",
    "What is the tapping process?",
]

print("=" * 70)
print("TAP PROCESS QUERY ROUTING TEST")
print("=" * 70)

for query in TEST_QUERIES:
    route_type, confidence = QueryRouter.route(query)

    expected = "BRD" if any(x in query.lower() for x in ["what is the tap hole", "explain", "process?"]) else "SQL"
    status = "PASS" if route_type.upper() == expected else "FAIL"

    print(f"\n[{status}] {query}")
    print(f"  Route: {route_type.upper()} (confidence: {confidence:.0%})")
    print(f"  Expected: {expected}")

print("\n" + "=" * 70)
