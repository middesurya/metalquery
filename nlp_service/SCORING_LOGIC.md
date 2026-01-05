# Confidence & Relevance Score Calculation - Deep Dive

This document explains exactly how the MetalQuery NLP service calculates Confidence and Relevance scores for every SQL query.

---

## Overview

| Score | Type | Calculation Method | Purpose |
|-------|------|-------------------|---------|
| **Confidence** | Technical | Rule-based (code logic) | "Is the SQL syntactically correct?" |
| **Relevance** | Semantic | AI-based (LLM judge) | "Does the SQL answer the question?" |

---

## 1. CONFIDENCE SCORE (0-100)

### Source File
`d:\metalquery\nlp_service\accuracy_scorer.py` → `calculate_confidence()` method

### Step-by-Step Calculation

```
┌────────────────────────────────────────────────────────────────────┐
│                        CONFIDENCE ALGORITHM                         │
└────────────────────────────────────────────────────────────────────┘

  STEP 1: Start with BASE SCORE = 100
  
  STEP 2: Check if SQL is syntactically valid
          ├── If NOT valid → RETURN 0 (immediate failure)
          └── If valid → continue
  
  STEP 3: Check if table exists in schema
          ├── If table NOT found → RETURN 0 (immediate failure)
          └── If table exists → continue
  
  STEP 4: Count ERRORS from diagnostic
          └── Each error: SUBTRACT 20 points
              Examples of errors:
              - Column not found
              - Invalid JOIN
              - Missing required field
  
  STEP 5: Count WARNINGS from diagnostic
          └── Each warning: SUBTRACT 5 points
              Examples of warnings:
              - Type mismatch (string vs number)
              - Risky SQL pattern
              - Missing LIMIT clause
  
  STEP 6: FINAL SCORE = max(0, min(100, calculated_score))
          └── Clamp between 0 and 100
```

### Python Code

```python
def calculate_confidence(self, diagnostic_result: Dict[str, Any]) -> int:
    score = 100  # Step 1: Base score
    
    errors = diagnostic_result.get('errors', [])
    warnings = diagnostic_result.get('warnings', [])

    # Step 2: Critical - Invalid SQL
    if not diagnostic_result.get('valid', False):
        return 0
    
    # Step 3: Critical - Table not found
    if any("table" in e.lower() and "not found" in e.lower() for e in errors):
        return 0
        
    # Step 4: Major Errors
    score -= (len(errors) * 20)
    
    # Step 5: Warnings
    score -= (len(warnings) * 5)
    
    # Step 6: Clamp
    return max(0, min(100, score))
```

### Examples

| Scenario | Calculation | Final Score |
|----------|-------------|-------------|
| Valid SQL, no issues | 100 - 0 - 0 | **100%** |
| Valid SQL, 1 error | 100 - 20 | **80%** |
| Valid SQL, 2 errors | 100 - 40 | **60%** |
| Valid SQL, 1 error + 2 warnings | 100 - 20 - 10 | **70%** |
| Invalid SQL syntax | Immediate | **0%** |
| Table doesn't exist | Immediate | **0%** |

---

## 2. RELEVANCE SCORE (0-100)

### Source File
`d:\metalquery\nlp_service\accuracy_scorer.py` → `calculate_relevance()` method

### Step-by-Step Calculation

```
┌────────────────────────────────────────────────────────────────────┐
│                        RELEVANCE ALGORITHM                          │
└────────────────────────────────────────────────────────────────────┘

  STEP 1: Build evaluation prompt with:
          ├── User's original question
          └── Generated SQL query
  
  STEP 2: Send to LLM (Groq API) with this prompt:
  
          "You are a SQL Quality Judge. Rate the relevance 
           of the SQL to the User Question on a scale of 0-100.
           
           User Question: "{question}"
           Generated SQL: "{sql}"
           
           Scoring Criteria:
           - 100: Perfect match
           - 80-99: Good match (minor issues)
           - 50-79: Acceptable
           - < 50: Poor/Wrong
           
           Return ONLY: {"score": <0-100>, "reason": "..."}"
  
  STEP 3: Parse LLM response as JSON
          └── Extract "score" and "reason"
  
  STEP 4: Return score (0-100) and reason string
```

### Python Code

```python
async def calculate_relevance(self, question: str, sql: str) -> int:
    prompt = f"""You are a SQL Quality Judge. Rate the relevance...
    
User Question: "{question}"
Generated SQL: "{sql}"

Scoring Criteria:
- 100: Perfect match (Correct structure, efficient, captures intent)
- 80-99: Good match (Minor issues, extra columns, slightly inefficient)
- 50-79: Acceptable (Technically correct but might miss nuance)
- < 50: Poor/Wrong (Wrong table, missing filters, different question)

Return ONLY a JSON: {{"score": <integer>, "reason": "<explanation>"}}
"""
    
    response = self.llm.invoke([HumanMessage(content=prompt)])
    data = json.loads(response.content)
    
    score = int(data.get("score", 0))
    reason = data.get("reason", "No reason")
    
    return score, reason
```

### Real Examples

#### Example 1: Perfect Match ✅
```
Question: "What is the average OEE for furnace 1?"
SQL: "SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1"

LLM Response: {"score": 95, "reason": "Correct table, correct column, correct filter"}
```

#### Example 2: Good Match with Minor Issue ⚠️
```
Question: "Show production efficiency for July"  
SQL: "SELECT date, AVG(production_efficiency_percentage) FROM ... 
      WHERE EXTRACT(MONTH FROM date) = 7 GROUP BY date ORDER BY date LIMIT 100"

LLM Response: {"score": 80, "reason": "Correct but includes extra columns and unnecessary LIMIT"}
```

#### Example 3: Wrong Answer ❌
```
Question: "What is the furnace age?"
SQL: "SELECT COUNT(furnace_no) as furnace_age FROM furnace_furnaceconfig 
      WHERE created_at <= CURRENT_DATE - INTERVAL '1 year'"

LLM Response: {"score": 20, "reason": "Query counts old furnaces but doesn't answer 'furnace age'. 
              There is no furnace_age column in the schema."}
```

---

## 3. HOW THEY'RE USED TOGETHER

### Flow in main.py

```
User asks: "What is the OEE for furnace 1?"
                    │
                    ▼
┌─────────────────────────────────────┐
│   STEP 1: Generate SQL with LLM     │
│   Output: "SELECT AVG(oee_...)..."  │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│   STEP 2: Run SQL Diagnostic        │
│   - Validate syntax                 │
│   - Check tables exist              │
│   - Check columns exist             │
│   Output: {valid: true, errors: []} │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│   STEP 3: Calculate CONFIDENCE      │
│   confidence = 100 - (errors × 20)  │
│              - (warnings × 5)       │
│   Output: 100                       │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│   STEP 4: Calculate RELEVANCE       │
│   (Send to LLM for judgment)        │
│   Output: 95, "Perfect match"       │
└─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│   STEP 5: Decision Logic            │
│                                     │
│   if relevance < 30:                │
│       → ERROR: "Data doesn't exist" │
│                                     │
│   elif relevance < 50:              │
│       → WARNING: "Low quality"      │
│                                     │
│   else:                             │
│       → SUCCESS: Return SQL         │
└─────────────────────────────────────┘
```

---

## 4. DECISION THRESHOLDS

| Relevance Score | System Behavior |
|-----------------|-----------------|
| **< 30%** | ❌ Returns ERROR: "Data doesn't exist in database" |
| **30-49%** | ⚠️ Returns SQL with LOW QUALITY WARNING |
| **50-79%** | ✅ Returns SQL normally |
| **80-100%** | ✅ Returns SQL with high confidence |

---

## 5. KEY DIFFERENCES

| Aspect | Confidence | Relevance |
|--------|------------|-----------|
| **Type** | Deterministic | AI-judged |
| **Speed** | Instant (code) | Requires API call |
| **What it checks** | Syntax, schema | Semantic meaning |
| **Can be fooled?** | No | Possibly (LLM dependent) |
| **Example issue it catches** | `SELECT * FORM table` (typo) | Correct SQL but wrong answer |

---

## Summary

**Confidence** = "Is the SQL technically valid?" (Rule-based)  
**Relevance** = "Does it answer the question?" (AI-judged)

Both scores together give a complete picture of SQL quality!
