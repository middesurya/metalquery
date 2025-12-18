
"""
NLP Service - Main FastAPI Application
Provides endpoints for Natural Language to SQL conversion.

SECURITY NOTE: This service ONLY generates SQL and formats responses.
It does NOT connect to or execute queries against the database.
Database access is handled by the Django backend (security boundary).
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage

from config import settings
from guardrails import SQLGuardrails
from schema_loader import SchemaLoader
from prompts import get_sql_generation_prompt, RESPONSE_FORMAT_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NLP-to-SQL Service",
    description="""
    Converts natural language queries to safe SQL statements.
    
    **Security Architecture:**
    - This service ONLY generates SQL - it does NOT execute queries
    - Database access is handled by the Django backend (security boundary)
    - AI is isolated from the database
    """,
    version="2.0.0"
)

# Add CORS middleware - in production, restrict to Django backend only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],  # Django + React
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Initialize components
schema_loader = SchemaLoader()
guardrails = SQLGuardrails()


# ============================================================
# Request/Response Models
# ============================================================

class GenerateSQLRequest(BaseModel):
    """Request model for SQL generation."""
    question: str
    tables: Optional[List[str]] = None  # Optional: limit to specific tables


class GenerateSQLResponse(BaseModel):
    """Response model for SQL generation."""
    success: bool
    sql: Optional[str] = None
    error: Optional[str] = None
    tables_used: Optional[List[str]] = None
    explanation: Optional[str] = None  # Brief explanation of the query


class FormatResponseRequest(BaseModel):
    """Request model for response formatting."""
    question: str
    sql: str
    results: List[Dict[str, Any]]


class FormatResponseResponse(BaseModel):
    """Response model for formatted answer."""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None


class SchemaInfoResponse(BaseModel):
    """Response model for schema information."""
    tables: List[str]
    schema_context: str


# ============================================================
# LLM Configuration
# ============================================================

def get_llm():
    """Get configured LLM instance."""
    if settings.llm_provider == "ollama":
        logger.info(f"Using Local LLM: {settings.ollama_model}")
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0
        )
    
    return ChatOpenAI(
        model="gpt-4o-mini",  # Cost-effective and capable
        temperature=0,  # Deterministic output for SQL
        api_key=settings.openai_api_key
    )


# ============================================================
# Startup Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Load schema on startup."""
    logger.info("Starting NLP-to-SQL Service (SQL Generation Only)...")
    logger.info("NOTE: This service does NOT connect to the database for queries.")
    logger.info("Database access is handled by the Django backend.")
    try:
        schema_loader.load_schema()
        logger.info(f"Loaded schema for tables: {schema_loader.get_table_names()}")
    except Exception as e:
        logger.warning(f"Could not load schema on startup: {e}")
        logger.info("Schema will be loaded on first request")


# ============================================================
# Health & Schema Endpoints
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "nlp-to-sql",
        "version": "2.0.0",
        "mode": "sql-generation-only",
        "note": "This service generates SQL but does NOT execute queries"
    }


@app.get("/api/v1/schema", response_model=SchemaInfoResponse)
async def get_schema():
    """Get available database schema information."""
    try:
        if not schema_loader.get_table_names():
            schema_loader.load_schema()
        
        return SchemaInfoResponse(
            tables=schema_loader.get_table_names(),
            schema_context=schema_loader.get_schema_context()
        )
    except Exception as e:
        logger.error(f"Error loading schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/reload-schema")
async def reload_schema(tables: Optional[List[str]] = None):
    """Reload database schema (useful after schema changes)."""
    try:
        schema_loader._schema_cache.clear()
        schema_loader._allowed_tables.clear()
        schema_loader.load_schema(tables=tables)
        return {
            "success": True,
            "tables": schema_loader.get_table_names()
        }
    except Exception as e:
        logger.error(f"Error reloading schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# SQL Generation Endpoint (Core Functionality)
# ============================================================

@app.post("/api/v1/generate-sql", response_model=GenerateSQLResponse)
async def generate_sql(request: GenerateSQLRequest):
    """
    Generate SQL from natural language question.
    
    This is the main endpoint that converts user questions to SQL.
    The generated SQL is validated by guardrails before returning.
    
    NOTE: This endpoint does NOT execute the SQL.
    SQL execution is handled by the Django backend.
    """
    logger.info(f"Generating SQL for question: {request.question}")
    
    try:
        # Load schema if not already loaded
        if not schema_loader.get_table_names():
            schema_loader.load_schema(tables=request.tables)
        
        # Get schema context for the prompt
        requested_tables = request.tables if request.tables and len(request.tables) > 0 else None
        schema_context = schema_loader.get_schema_context(tables=requested_tables)
        
        # Build system prompt with schema
        system_prompt = get_sql_generation_prompt(schema_context)
        
        # Initialize LLM
        llm = get_llm()
        
        # Generate SQL using LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {request.question}\nOutput ONLY the SQL block or the direct answer.")
        ]
        
        logger.info(f"System Prompt Length: {len(system_prompt)} chars")
        logger.info(f"Number of tables in context: {len(schema_loader.get_table_names())}")
        
        # Retry loop for self-correction
        MAX_RETRIES = 3
        current_try = 0
        last_error = None
        
        while current_try < MAX_RETRIES:
            current_try += 1
            if current_try > 1:
                logger.info(f"Self-correction attempt {current_try}...")
            
            response = llm.invoke(messages)
            generated_content = response.content.strip()
            
            # Detect if it's SQL or a direct answer
            is_sql = False
            sql_query = None
            direct_answer = None
            
            import re
            sql_match = re.search(r'```(?:sql)?\s*(.*?)```', generated_content, re.DOTALL | re.IGNORECASE)
            
            if sql_match:
                is_sql = True
                sql_query = sql_match.group(1).strip().rstrip(';').strip()
                logger.info(f"Detected SQL: {sql_query}")
            else:
                # If no SQL block, check if it's just raw SQL without blocks (e.g. starts with SELECT)
                if re.match(r'^\s*SELECT\s', generated_content, re.IGNORECASE):
                    is_sql = True
                    sql_query = generated_content.rstrip(';').strip()
                    logger.info("Detected raw SQL (no markdown block)")
                else:
                    is_sql = False
                    direct_answer = generated_content
                    logger.info("Detected direct text answer")
            
            # If it's SQL, run guardrails
            if is_sql:
                # Update guardrails with allowed tables
                guardrails = SQLGuardrails(allowed_tables=set(schema_loader.get_table_names()))
                is_valid, error_msg = guardrails.validate(sql_query)
                
                if is_valid:
                    # Success! Return the valid SQL
                    tables_used = list(guardrails._extract_tables(sql_query))
                    return GenerateSQLResponse(
                        success=True,
                        sql=sql_query,
                        tables_used=tables_used,
                        explanation=f"Query to answer: {request.question}"
                    )
                else:
                    # Validation failed - Feed back into LLM for correction
                    logger.warning(f"SQL failed validation (Attempt {current_try}): {error_msg}")
                    last_error = error_msg
                    
                    # Add error context to messages for next iteration
                    messages.append(HumanMessage(content=f"The SQL you generated was invalid. Error: {error_msg}\nPlease correct the query and ensure you use ONLY tables from the provided schema."))
                    continue
            else:
                # If it's a direct answer, return it immediately (no SQL validation needed)
                return GenerateSQLResponse(
                    success=True,
                    sql=None,
                    tables_used=[],
                    explanation=direct_answer
                )
        
        # If we exit the loop, we failed to generate valid SQL after retries
        return GenerateSQLResponse(
            success=False,
            error=f"Failed to generate valid SQL after {MAX_RETRIES} attempts. Last error: {last_error}",
            sql=None
        )
        
    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        return GenerateSQLResponse(
            success=False,
            error=f"Failed to generate SQL: {str(e)}"
        )


# ============================================================
# Response Formatting Endpoint
# ============================================================

@app.post("/api/v1/format-response", response_model=FormatResponseResponse)
async def format_response(request: FormatResponseRequest):
    """
    Format SQL query results into natural language.
    
    Takes the original question, executed SQL, and results,
    then generates a human-friendly response.
    
    NOTE: This receives results from Django backend - 
    this service does NOT query the database.
    """
    logger.info(f"Formatting response for question: {request.question}")
    
    try:
        llm = get_llm()
        
        # Format results for prompt
        results_str = str(request.results[:20])  # Limit to first 20 rows
        if len(request.results) > 20:
            results_str += f"\n... and {len(request.results) - 20} more rows"
        
        prompt = RESPONSE_FORMAT_PROMPT.format(
            question=request.question,
            sql=request.sql,
            results=results_str
        )
        
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        
        return FormatResponseResponse(
            success=True,
            response=response.content.strip()
        )
        
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return FormatResponseResponse(
            success=False,
            error=f"Failed to format response: {str(e)}"
        )


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("NLP-to-SQL Service v2.0.0")
    print("=" * 60)
    print("Mode: SQL Generation Only")
    print("This service generates SQL but does NOT execute queries.")
    print("Database access is handled by the Django backend.")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "main:app",
        host=settings.nlp_service_host,
        port=settings.nlp_service_port,
        reload=True
    )
