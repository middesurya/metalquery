"""
NLP Service - Main FastAPI Application
Provides endpoints for Natural Language to SQL conversion.
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
from langchain.schema import HumanMessage, SystemMessage

from config import settings
from guardrails import SQLGuardrails, validate_sql
from schema_loader import SchemaLoader
from prompts import get_sql_generation_prompt, RESPONSE_FORMAT_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NLP-to-SQL Service",
    description="Converts natural language queries to safe SQL statements",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
schema_loader = SchemaLoader()
guardrails = SQLGuardrails()


# Request/Response Models
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


# Initialize LLM
def get_llm():
    """Get configured LLM instance."""
    return ChatOpenAI(
        model="gpt-4o-mini",  # Cost-effective and capable
        temperature=0,  # Deterministic output for SQL
        api_key=settings.openai_api_key
    )


@app.on_event("startup")
async def startup_event():
    """Load schema on startup."""
    logger.info("Starting NLP-to-SQL Service...")
    try:
        schema_loader.load_schema()
        logger.info(f"Loaded schema for tables: {schema_loader.get_table_names()}")
    except Exception as e:
        logger.warning(f"Could not load schema on startup: {e}")
        logger.info("Schema will be loaded on first request")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "nlp-to-sql"}


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


@app.post("/api/v1/generate-sql", response_model=GenerateSQLResponse)
async def generate_sql(request: GenerateSQLRequest):
    """
    Generate SQL from natural language question.
    
    This is the main endpoint that converts user questions to SQL.
    The generated SQL is validated by guardrails before returning.
    """
    logger.info(f"Generating SQL for question: {request.question}")
    
    try:
        # Load schema if not already loaded
        if not schema_loader.get_table_names():
            schema_loader.load_schema(tables=request.tables)
        
        # Get schema context for the prompt
        schema_context = schema_loader.get_schema_context(tables=request.tables)
        
        # Build system prompt with schema
        system_prompt = get_sql_generation_prompt(schema_context)
        
        # Initialize LLM
        llm = get_llm()
        
        # Generate SQL using LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.question)
        ]
        
        response = llm.invoke(messages)
        generated_sql = response.content.strip()
        
        # Clean up SQL (remove markdown code blocks if present)
        if generated_sql.startswith("```"):
            lines = generated_sql.split("\n")
            generated_sql = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        generated_sql = generated_sql.strip()
        
        logger.info(f"Generated SQL: {generated_sql}")
        
        # Update guardrails with allowed tables
        guardrails.allowed_tables = schema_loader.allowed_tables
        
        # Validate SQL against guardrails
        is_valid, error_message = guardrails.validate(generated_sql)
        
        if not is_valid:
            logger.warning(f"SQL validation failed: {error_message}")
            return GenerateSQLResponse(
                success=False,
                error=f"Generated SQL failed security validation: {error_message}"
            )
        
        # Extract tables used in query
        tables_used = list(guardrails._extract_tables(generated_sql))
        
        return GenerateSQLResponse(
            success=True,
            sql=generated_sql,
            tables_used=tables_used
        )
        
    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        return GenerateSQLResponse(
            success=False,
            error=f"Failed to generate SQL: {str(e)}"
        )


@app.post("/api/v1/format-response", response_model=FormatResponseResponse)
async def format_response(request: FormatResponseRequest):
    """
    Format SQL query results into natural language.
    
    Takes the original question, executed SQL, and results,
    then generates a human-friendly response.
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


class ChatRequest(BaseModel):
    """Request model for complete chat flow."""
    question: str


class ChatResponse(BaseModel):
    """Response model for complete chat flow."""
    success: bool
    response: Optional[str] = None
    sql: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None
    error: Optional[str] = None


def execute_sql_query(sql: str) -> List[Dict[str, Any]]:
    """Execute SQL query and return results as list of dicts."""
    import psycopg2
    import psycopg2.extras
    
    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            results = cur.fetchall()
            # Convert RealDictRow to regular dict
            return [dict(row) for row in results]
    finally:
        conn.close()


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Complete chat endpoint that:
    1. Generates SQL from natural language
    2. Executes the query
    3. Returns formatted natural language response
    """
    logger.info(f"Chat request: {request.question}")
    
    try:
        # Step 1: Load schema if not already loaded
        if not schema_loader.get_table_names():
            schema_loader.load_schema()
        
        # Step 2: Get schema context for the prompt
        schema_context = schema_loader.get_schema_context()
        
        # Step 3: Build system prompt with schema
        system_prompt = get_sql_generation_prompt(schema_context)
        
        # Step 4: Initialize LLM and generate SQL
        llm = get_llm()
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.question)
        ]
        
        response = llm.invoke(messages)
        generated_sql = response.content.strip()
        
        # Clean up SQL (remove markdown code blocks if present)
        if generated_sql.startswith("```"):
            lines = generated_sql.split("\n")
            generated_sql = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        generated_sql = generated_sql.strip()
        
        logger.info(f"Generated SQL: {generated_sql}")
        
        # Step 5: Validate SQL against guardrails
        guardrails.allowed_tables = schema_loader.allowed_tables
        is_valid, error_message = guardrails.validate(generated_sql)
        
        if not is_valid:
            logger.warning(f"SQL validation failed: {error_message}")
            return ChatResponse(
                success=False,
                error=f"Query validation failed: {error_message}",
                sql=generated_sql
            )
        
        # Step 6: Execute the SQL query
        try:
            results = execute_sql_query(generated_sql)
            row_count = len(results)
            logger.info(f"Query returned {row_count} rows")
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            return ChatResponse(
                success=False,
                error=f"Database query error: {str(db_error)}",
                sql=generated_sql
            )
        
        # Step 7: Format the response using LLM
        results_str = str(results[:20])  # Limit to first 20 rows for formatting
        if len(results) > 20:
            results_str += f"\n... and {len(results) - 20} more rows"
        
        format_prompt = RESPONSE_FORMAT_PROMPT.format(
            question=request.question,
            sql=generated_sql,
            results=results_str
        )
        
        format_messages = [HumanMessage(content=format_prompt)]
        format_response = llm.invoke(format_messages)
        formatted_answer = format_response.content.strip()
        
        return ChatResponse(
            success=True,
            response=formatted_answer,
            sql=generated_sql,
            results=results[:50],  # Limit results to 50 rows
            row_count=row_count
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            success=False,
            error=f"Failed to process question: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.nlp_service_host,
        port=settings.nlp_service_port,
        reload=True
    )
