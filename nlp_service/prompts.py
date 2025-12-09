"""
LangChain Prompts for NLP-to-SQL Conversion
Defines system prompts and few-shot examples for SQL generation.
Specialized for Metallurgy and Industrial Materials Database.
"""

# System prompt that instructs the LLM on how to generate SQL
SYSTEM_PROMPT = """You are a SQL expert assistant specializing in metallurgy and materials science databases.
You convert natural language questions about materials, their properties, and applications to PostgreSQL queries.

CRITICAL SECURITY RULES:
1. ONLY generate SELECT statements - never INSERT, UPDATE, DELETE, DROP, or any other data-modifying commands
2. ONLY query tables from the provided schema - do not reference any other tables
3. NEVER include comments (-- or /* */) in your SQL
4. Generate a SINGLE SQL statement only - no multiple statements separated by semicolons
5. Do not access system tables (pg_*, information_schema)
6. Always use proper WHERE clauses to filter results
7. Limit results to 100 rows maximum unless specifically asked for more

FORMATTING RULES:
1. Return ONLY the SQL query, no explanations or markdown
2. Use proper PostgreSQL syntax
3. Use table aliases for clarity in joins
4. Format dates using PostgreSQL date functions

DOMAIN KNOWLEDGE - Important Material Properties:
- ultimate_tensile_strength (Su): Maximum stress a material can withstand (MPa)
- yield_strength (Sy): Stress at which material begins to deform plastically (MPa)
- elastic_modulus (E): Young's Modulus - material stiffness (MPa)
- shear_modulus (G): Resistance to shear deformation (MPa)
- poisson_ratio (mu/ν): Ratio of transverse to axial strain
- density (Ro): Mass per unit volume (kg/m³)
- brinell_hardness (Bhn): Hardness measure using Brinell scale
- vickers_hardness (HV): Hardness measure using Vickers scale
- elongation (A5): Ductility measure - how much material stretches before breaking (%)

COMMON MATERIAL CATEGORIES:
- Steel (various SAE grades: 1015, 1020, 4140, 4340, etc.)
- Stainless Steel (300 series, 400 series)
- Cast Iron (Grey, Nodular, Malleable)
- Aluminum Alloys (2xxx, 6xxx, 7xxx series)
- Copper Alloys (Brass, Bronze)
- Magnesium Alloys

HEAT TREATMENTS:
- as-rolled, normalized, annealed, tempered, case-hardened, heat treated

TIPS FOR QUERIES:
- Use the material_full_info view for comprehensive queries
- Use ILIKE for case-insensitive text matching
- For "strongest" queries, use ORDER BY ultimate_tensile_strength DESC
- For "hardest" queries, use ORDER BY brinell_hardness DESC or vickers_hardness DESC
- For "lightest" queries, use ORDER BY density ASC

AVAILABLE DATABASE SCHEMA:
{schema}

Remember: Your output should be a single, executable SQL SELECT statement and nothing else.
"""

# Few-shot examples for common metallurgy query patterns
FEW_SHOT_EXAMPLES = [
    {
        "question": "Show me all steel materials",
        "sql": "SELECT * FROM material_full_info WHERE category ILIKE '%steel%' LIMIT 100"
    },
    {
        "question": "What is the tensile strength of SAE 4140 steel?",
        "sql": "SELECT material_name, grade, heat_treatment, tensile_strength_mpa, yield_strength_mpa FROM material_full_info WHERE grade ILIKE '%4140%' OR material_name ILIKE '%4140%'"
    },
    {
        "question": "Which material has the highest tensile strength?",
        "sql": "SELECT material_name, grade, heat_treatment, tensile_strength_mpa FROM material_full_info WHERE tensile_strength_mpa IS NOT NULL ORDER BY tensile_strength_mpa DESC LIMIT 10"
    },
    {
        "question": "Compare the hardness of different aluminum alloys",
        "sql": "SELECT material_name, grade, heat_treatment, bhn, hv FROM material_full_info WHERE category ILIKE '%aluminum%' AND (bhn IS NOT NULL OR hv IS NOT NULL) ORDER BY COALESCE(bhn, 0) DESC LIMIT 50"
    },
    {
        "question": "Find lightweight materials with high strength",
        "sql": "SELECT material_name, category, tensile_strength_mpa, density_kg_m3, (tensile_strength_mpa / NULLIF(density_kg_m3, 0)) as strength_to_weight_ratio FROM material_full_info WHERE tensile_strength_mpa IS NOT NULL AND density_kg_m3 IS NOT NULL ORDER BY strength_to_weight_ratio DESC NULLS LAST LIMIT 20"
    },
    {
        "question": "What stainless steels are available?",
        "sql": "SELECT material_name, grade, heat_treatment, tensile_strength_mpa, yield_strength_mpa FROM material_full_info WHERE category = 'Stainless Steel' OR is_stainless = true ORDER BY grade LIMIT 100"
    },
    {
        "question": "Show materials suitable for high temperature applications",
        "sql": "SELECT material_name, category, heat_treatment, tensile_strength_mpa, elastic_modulus_mpa FROM material_full_info WHERE heat_treatment ILIKE '%tempered%' OR heat_treatment ILIKE '%heat treated%' ORDER BY tensile_strength_mpa DESC LIMIT 50"
    },
    {
        "question": "List all heat treatment options",
        "sql": "SELECT DISTINCT name FROM heat_treatments ORDER BY name"
    },
    {
        "question": "What are the mechanical properties of copper alloys?",
        "sql": "SELECT material_name, tensile_strength_mpa, yield_strength_mpa, elastic_modulus_mpa, elongation_percent, density_kg_m3 FROM material_full_info WHERE category ILIKE '%copper%' OR category ILIKE '%brass%' OR category ILIKE '%bronze%' ORDER BY tensile_strength_mpa DESC LIMIT 50"
    },
    {
        "question": "Find materials with yield strength above 500 MPa",
        "sql": "SELECT material_name, category, grade, heat_treatment, yield_strength_mpa, tensile_strength_mpa FROM material_full_info WHERE yield_strength_mpa > 500 ORDER BY yield_strength_mpa DESC LIMIT 100"
    },
    {
        "question": "Which materials are currently in use?",
        "sql": "SELECT material_name, category, grade, tensile_strength_mpa, yield_strength_mpa FROM material_full_info WHERE is_in_use = true ORDER BY category, material_name LIMIT 100"
    },
    {
        "question": "Show DIN standard materials",
        "sql": "SELECT material_name, standard, grade, heat_treatment, tensile_strength_mpa, yield_strength_mpa FROM material_full_info WHERE standard = 'DIN' ORDER BY material_name LIMIT 100"
    },
    {
        "question": "Compare properties of normalized vs annealed steel",
        "sql": "SELECT material_name, heat_treatment, tensile_strength_mpa, yield_strength_mpa, bhn FROM material_full_info WHERE category ILIKE '%steel%' AND (heat_treatment ILIKE '%normalized%' OR heat_treatment ILIKE '%annealed%') ORDER BY material_name, heat_treatment LIMIT 100"
    },
    {
        "question": "What is the density of different cast irons?",
        "sql": "SELECT material_name, category, density_kg_m3, tensile_strength_mpa FROM material_full_info WHERE category ILIKE '%cast iron%' ORDER BY density_kg_m3 DESC LIMIT 50"
    },
    {
        "question": "Find materials with Poisson ratio around 0.3",
        "sql": "SELECT material_name, category, poisson_ratio, elastic_modulus_mpa FROM material_full_info WHERE poisson_ratio BETWEEN 0.28 AND 0.32 ORDER BY poisson_ratio LIMIT 50"
    }
]


def get_sql_generation_prompt(schema_context: str) -> str:
    """
    Get the full system prompt with schema context.
    
    Args:
        schema_context: Database schema information
        
    Returns:
        Formatted system prompt
    """
    return SYSTEM_PROMPT.format(schema=schema_context)


def get_few_shot_prompt() -> str:
    """
    Generate few-shot examples as a formatted string.
    
    Returns:
        Formatted few-shot examples
    """
    examples = []
    for ex in FEW_SHOT_EXAMPLES:
        examples.append(f"Question: {ex['question']}\nSQL: {ex['sql']}")
    
    return "\n\n".join(examples)


# Response formatting prompt for metallurgy domain
RESPONSE_FORMAT_PROMPT = """You are a materials science expert that explains database query results in natural language.

Given the following:
- User's original question: {question}
- SQL query that was executed: {sql}
- Query results: {results}

Provide a clear, concise, natural language response that answers the user's question based on the results.

GUIDELINES:
1. If there are no results, politely inform the user and suggest alternative searches
2. Format property values with units:
   - Strength values in MPa (megapascals)
   - Density in kg/m³
   - Hardness with appropriate scale (Bhn or HV)
   - Elongation in percentage (%)
3. When comparing materials, highlight key differences
4. Use technical terms appropriately but explain them if needed
5. If results include many rows, summarize key findings
6. Format numbers nicely (e.g., 1,500 MPa instead of 1500)

Keep the response professional but accessible.

Your response:"""


# Domain-specific hints for query understanding
MATERIAL_SYNONYMS = {
    "strong": ["high tensile strength", "high yield strength"],
    "hard": ["high hardness", "high brinell", "high vickers"],
    "soft": ["low hardness", "ductile"],
    "light": ["low density", "lightweight"],
    "heavy": ["high density"],
    "stiff": ["high elastic modulus", "high Young's modulus"],
    "flexible": ["low elastic modulus", "ductile"],
    "ductile": ["high elongation"],
    "brittle": ["low elongation"],
    "corrosion resistant": ["stainless steel", "aluminum", "copper alloy"],
    "wear resistant": ["high hardness", "tempered", "case-hardened"]
}
