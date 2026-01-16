# Manual Test Results - Graph Type Inference

**Date**: 2026-01-16
**Tester**: User
**Status**: Testing Complete - Ready for Fixes

---

## Test Results Summary

| # | Query | Rows | Graph Type Returned | Expected | Match? | Issue |
|---|-------|------|---------------------|----------|--------|-------|
| 1 | Show downtime by furnace | 1 | **KPI Card** | Bar/Line | ❌ NO | Single row incorrectly showing KPI |
| 2 | What is the downtime by furnace? | 2 | **Bar Chart** | Bar/Line | ✅ YES | Working correctly |
| 3 | Show total downtime by furnace | 2 | **Bar Chart** | Bar/Line | ✅ YES | Working correctly |
| 4 | Display downtime by shift | 3 | **Bar Chart** | Bar/Line | ✅ YES | Working correctly |
| 5 | Show safety incidents by furnace | 2 | **Bar Chart** | Bar | ✅ YES | Working correctly |
| 6 | Show cycle time by furnace | 50 | **Bar Chart** | Line | ✅ ACCEPT | Bar acceptable for 50 rows |
| 7 | Show taps by furnace | 25 | **Table Only** | Bar | ❌ NO | 25 rows exceeds Rule 7 (max 20) |
| 8 | Display taps by furnace | 25 | **Table Only** | Bar | ❌ NO | 25 rows exceeds Rule 7 (max 20) |

---

## Issues Identified

### Issue 1: Single Row "by furnace" Query → KPI Card (WRONG)

**Query**: "Show downtime by furnace"
**Result**: 1 row (furnace_no=1, total_downtime_hours=1080.27)
**Actual Visualization**: KPI Card showing "1 hrs"
**Expected**: Bar Chart or skip visualization (1 bar is not useful)

**Root Cause**:
- Single-value detection (Rule 1 or 2) triggering KPI card
- "by furnace" pattern (Rule 3) not taking priority over single-value detection

**Fix Needed**:
- "by furnace/shift/etc" patterns should ALWAYS return bar chart, even for 1 row
- OR: For 1 row aggregations, skip visualization entirely (show table only)

---

### Issue 2: 25-Row Tap Queries → Table Only (WRONG)

**Queries**:
- "Show taps by furnace" (25 rows)
- "Display taps by furnace" (25 rows)

**Actual Visualization**: Table only (no chart)
**Expected**: Bar Chart

**Root Cause**:
- Rule 7: "Categorical with values (3-20 rows) → bar chart"
- 25 rows exceeds the max threshold of 20
- Falls through to default table

**Fix Needed**:
- Extend Rule 7 threshold from 20 to 30-50 rows
- Ensure "by furnace/shift" pattern (Rule 3) catches these queries first

---

## Working Correctly (5/8 queries)

✅ **Queries 2-6**: All correctly display bar charts
- 2-3 rows: Bar chart displayed correctly
- 50 rows: Bar chart displayed correctly (Rule 3 or different logic)

**Why Query 6 (50 rows) works but Query 7-8 (25 rows) don't?**
- Query 6: "Show cycle time by furnace" → 50 rows → Bar chart ✓
- Query 7: "Show taps by furnace" → 25 rows → Table ❌

**Hypothesis**:
- Query 6 might be hitting Rule 3 ("by furnace" pattern) successfully
- Query 7-8 might be returning wrong column structure (not categorical + numeric)
- Need to investigate actual SQL results and column types

---

## Root Cause Analysis

### Rule 3: "by X" Pattern Detection (Lines 188-206)

Current logic:
```python
# Rule 3: AGGRESSIVE "by X" detection → bar chart
by_patterns = ['by furnace', 'by shift', 'by machine', ...]
if any(pattern in q_lower for pattern in by_patterns):
    x_col = categorical_cols[0] if categorical_cols else None
    y_col = numeric_cols[0] if numeric_cols else None
    if x_col and y_col and row_count >= 2:  # ← PROBLEM: row_count >= 2
        return {"chart_type": "bar", ...}
```

**Problem 1**: `row_count >= 2` check
- Query 1 has 1 row → Fails this check → Falls through to other rules → Gets KPI card

**Problem 2**: May not be catching tap queries
- Tap queries might return wrong column structure
- Need to check what categorical_cols and numeric_cols are detected

### Rule 7: Row Count Threshold (Lines 242-250)

Current logic:
```python
# Rule 7: Categorical with values (3-20 rows) → bar chart
if categorical_cols and numeric_cols and 3 <= row_count <= 20:
    return {"chart_type": "bar", ...}
```

**Problem**: `row_count <= 20`
- Queries with 21-49 rows miss this rule
- Query 7-8 with 25 rows fall through to default table

---

## Recommended Fixes

### Fix 1: Rule 3 - Remove `row_count >= 2` Check

**Current** (Line 197):
```python
if x_col and y_col and row_count >= 2:
```

**Proposed**:
```python
if x_col and y_col and row_count >= 1:
```

**Rationale**:
- "by furnace/shift" queries should ALWAYS show bar chart, even with 1 row
- User explicitly asked for aggregation visualization
- Alternative: Skip visualization for 1 row (but still counts as success)

### Fix 2: Rule 7 - Extend Row Count Threshold

**Current** (Line 244):
```python
if categorical_cols and numeric_cols and 3 <= row_count <= 20:
```

**Proposed**:
```python
if categorical_cols and numeric_cols and 3 <= row_count <= 50:
```

**Rationale**:
- 25-row tap queries need bar chart
- 50-row query 6 already works (via different rule)
- Bar charts are readable up to ~50 bars

### Fix 3: Investigate Tap Query Column Detection

Need to check:
- What SQL is generated for "Show taps by furnace"?
- What columns are returned?
- Are categorical_cols and numeric_cols detected correctly?

If tap queries return:
- ✅ `furnace_no` (categorical) + `tap_count` (numeric) → Should hit Rule 3
- ❌ Multiple columns without clear categorical/numeric → Falls to table

---

## Testing Plan After Fix

1. **Re-test Query 1**: "Show downtime by furnace" (1 row)
   - Should show bar chart with 1 bar
   - OR: Skip chart, show table only (acceptable)

2. **Re-test Queries 7-8**: "Show taps by furnace" (25 rows)
   - Should show bar chart with 25 bars
   - Verify categorical + numeric columns detected

3. **Regression Test Queries 2-6**: Ensure still working correctly

---

## Next Steps

1. ✅ **Manual testing complete** - Results documented
2. ⚠️ **Fix viz_goal_finder.py** - Apply Fix 1 and Fix 2
3. ⚠️ **Investigate tap query SQL** - Check column structure
4. ⚠️ **Test fixes** - Validate all 8 queries work correctly
5. ⚠️ **Commit and deploy** - Document changes
