#!/usr/bin/env python3
"""Verify query routing to understand why queries fail."""

import sys
sys.path.insert(0, 'nlp_service')

from query_router import QueryRouter

test_queries = [
    # Failed queries
    "Show downtime by furnace",
    "What is the average safety incidents percentage?",
    "Show taps by furnace",

    # Successful similar queries
    "What is the total downtime?",
    "Show OEE by furnace",
    "What is the average yield?",

    # Variations
    "What is the downtime by furnace?",
    "Show safety incidents by furnace",
]

print("=" * 70)
print("QUERY ROUTING ANALYSIS")
print("=" * 70)

for query in test_queries:
    route_type, confidence = QueryRouter.route(query)
    print(f"\nQuery: {query}")
    print(f"  Route: {route_type.upper()} (confidence: {confidence:.0%})")
