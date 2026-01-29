"""
NLP Service - Main FastAPI Application
Enhanced with schema analysis and SQL validation.

✅ VERSION 4.0.0 - WITH DIAGNOSTICS
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config import settings
from sql_guardrails import SQLGuardrails
from schema_loader import schema_loader

# ✅ NEW ENHANCED IMPORTS
from prompts_v2 import build_prompt_with_schema, build_prompt_debug, SchemaAnalyzer
from diagnostic import SQLDiagnostic
from accuracy_scorer import AccuracyScorer

# ✅ BRD RAG IMPORTS
from brd_rag import brd_handler
from query_router import route_query, QueryRouter
from query_guard import QueryGuard, IGNIS_KEYWORDS
from guardrails_layer import CombinedGuard, GuardrailsLayer

# ✅ RATE LIMITING
from rate_limiter import get_rate_limiter, check_rate_limit, record_usage, RateLimitConfig

# ✅ SECURITY MODULE - 4-Layer Defense (IEC 62443 SL-2/SL-3)
from security import (
    FlippingDetector, PromptSignatureValidator,
    SQLInjectionValidator, AnomalyDetector, RedTeamDetector,
    audit_logger
)

# ✅ VISUALIZATION MODULE - LIDA-inspired chart generation
from visualization import VizPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NLP-to-SQL + BRD RAG Service",
    version="5.0.0",
    description="Hybrid service: SQL generation from data + RAG from BRD documents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Mount static files for BRD images
BRD_IMAGES_DIR = Path(__file__).parent / "brd_images"
BRD_IMAGES_DIR.mkdir(exist_ok=True)
app.mount("/api/brd-images", StaticFiles(directory=str(BRD_IMAGES_DIR)), name="brd_images")

guardrails = SQLGuardrails()
diagnostic = None
accuracy_scorer = AccuracyScorer()
brd_initialized = False
guard = QueryGuard(confidence_threshold=0.35)  # ✅ Custom Query Guard
combined_guard = None  # ✅ Combined Guard (initialized on startup)
guardrails_layer = None  # ✅ Guardrails AI layer

# ✅ Security Module Instances (4-Layer Defense)
flipping_detector = None
prompt_validator = None
sql_injection_validator = None
anomaly_detector = None
red_team_detector = None

# ✅ Visualization Pipeline
viz_pipeline = None

# ============================================================
# Models
# ============================================================

class GenerateSQLRequest(BaseModel):
    question: str
    tables: Optional[List[str]] = None
    allowed_tables: Optional[List[str]] = None  # RBAC: table whitelist from Django

class GenerateSQLResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    error: Optional[str] = None
    tables_used: Optional[List[str]] = None
    explanation: Optional[str] = None
    validation_warnings: Optional[List[str]] = None
    confidence_score: Optional[int] = None
    relevance_score: Optional[int] = None

class FormatResponseRequest(BaseModel):
    question: str
    sql: str
    results: Optional[List[Any]] = []

class FormatResponseResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None

class SchemaInfoResponse(BaseModel):
    tables: List[str]
    schema_context: str

# ============================================================
# LLM
# ============================================================

def get_llm(max_tokens: int = None):
    """Get LLM with configurable max tokens."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.model_name,
        temperature=0,
        max_tokens=max_tokens or settings.max_output_tokens,
    )

# ============================================================
# Startup
# ============================================================

@app.on_event("startup")
async def startup_event():
    global diagnostic, brd_initialized
    
    logger.info(f"Starting Hybrid NLP Service (SQL + BRD RAG)...")
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"Backend: {settings.django_api_url}")
    
    # Initialize SQL schema
    try:
        schema_loader.load_schema()
        schema_dict = schema_loader.get_schema_dict()

        # ✅ Initialize diagnostic
        diagnostic = SQLDiagnostic(schema_dict)

        # ✅ Load dynamic keywords from schema into QueryGuard
        guard.load_schema_keywords(schema_dict)

        logger.info(f"✓ Schema loaded: {len(schema_loader.get_table_names())} tables")
        logger.info(f"✓ SQL Diagnostic initialized")
        
    except Exception as e:
        logger.warning(f"Schema load warning: {e}")
    
    # ✅ Initialize BRD RAG system
    try:
        logger.info("Initializing BRD RAG system...")
        brd_initialized = brd_handler.initialize()
        if brd_initialized:
            logger.info("✓ BRD RAG system initialized")
        else:
            logger.warning("⚠ BRD RAG system failed to initialize (PDFs may not be indexed)")
    except Exception as e:
        logger.warning(f"BRD RAG initialization warning: {e}")
    
    # ✅ Initialize Combined Guard (Custom + Guardrails AI)
    global combined_guard, guardrails_layer
    try:
        guardrails_layer = GuardrailsLayer()
        combined_guard = CombinedGuard()
        logger.info("✓ Combined Guard initialized (Custom + Guardrails AI)")
    except Exception as e:
        logger.warning(f"⚠ Combined Guard failed, using custom guard only: {e}")
        combined_guard = None
    
    # ✅ Initialize Security Module (4-Layer Defense)
    global flipping_detector, prompt_validator, sql_injection_validator, anomaly_detector, red_team_detector
    try:
        flipping_detector = FlippingDetector()
        prompt_validator = PromptSignatureValidator()
        sql_injection_validator = SQLInjectionValidator()
        anomaly_detector = AnomalyDetector()
        red_team_detector = RedTeamDetector()
        logger.info("✓ Security module initialized (4-layer defense: Flipping, Injection, Anomaly, Audit)")
    except Exception as e:
        logger.warning(f"⚠ Security module initialization failed: {e}")

    # ✅ Initialize Visualization Pipeline
    global viz_pipeline
    try:
        viz_pipeline = VizPipeline()
        logger.info("✓ Visualization pipeline initialized (LIDA-inspired)")
    except Exception as e:
        logger.warning(f"⚠ Visualization pipeline initialization failed: {e}")
        viz_pipeline = None

    # ✅ Initialize STT Service (Lazy load on first request to speed up boot, or here)
    # We will let it lazy load to not block startup too much, but basic import check is good.
    try:
        from stt_service import stt_service
        # Pre-initialize if you want it ready immediately (optional, might take time)
        # stt_service.initialize() 
        logger.info("✓ STT Service registered")
    except Exception as e:
        logger.warning(f"⚠ STT Service registration failed: {e}")

    logger.info("✓ Query Guard initialized")

# ============================================================
# Endpoints
# ============================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "nlp-to-sql",
        "model": settings.model_name,
        "backend_url": settings.django_api_url,
        "schema_loaded": len(schema_loader.get_table_names() or []) > 0
    }

@app.get("/api/v1/brd-debug")
async def brd_debug():
    """Debug endpoint to check BRD RAG state."""
    from brd_loader import brd_loader

    # Test search
    test_results = brd_loader.search("additives", top_k=2)

    return {
        "brd_initialized_global": brd_initialized,
        "brd_handler_initialized": brd_handler.is_initialized,
        "brd_loader_initialized": brd_loader._initialized,
        "vectorstore_exists": brd_loader.vectorstore is not None,
        "vectorstore_type": str(type(brd_loader.vectorstore)),
        "documents_count": len(brd_loader.documents),
        "images_count": len(brd_loader.images),
        "test_search_results": len(test_results),
        "test_results_preview": test_results[0]['content'][:100] if test_results else "EMPTY"
    }

@app.get("/api/v1/rate-limit-status")
async def rate_limit_status():
    """Get current rate limit status and usage."""
    return get_rate_limiter().get_stats()

@app.get("/api/v1/schema", response_model=SchemaInfoResponse)
async def get_schema():
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

def clean_generated_sql(text: str) -> str:
    import re
    import sqlparse
    
    generated_sql = text.strip()
    
    # Remove markdown code blocks
    if "```" in generated_sql:
        match = re.search(r"```(?:sql)?\s*(.*?)\s*```", generated_sql, re.DOTALL | re.IGNORECASE)
        if match:
            generated_sql = match.group(1)
        else:
            generated_sql = generated_sql.replace("```sql", "").replace("```", "")
    
    # Extract SELECT statement
    sql_start_match = re.search(r"(SELECT\s+.*)", generated_sql, re.DOTALL | re.IGNORECASE)
    if sql_start_match:
        generated_sql = sql_start_match.group(1)
    
    # Parse and clean with sqlparse
    parsed = sqlparse.parse(generated_sql)
    if parsed and len(parsed) > 0:
        # Get the first statement as string
        generated_sql = str(parsed[0]).strip()
    
    # Remove trailing semicolon
    if generated_sql.endswith(";"):
        generated_sql = generated_sql[:-1]
    
    return generated_sql.strip()

@app.post("/api/v1/generate-sql", response_model=GenerateSQLResponse)
async def generate_sql(request: GenerateSQLRequest):
    """
    ✅ ENHANCED FLOW:
    1. Build schema-aware prompt (detects furnace, date, aggregation)
    2. Generate SQL with LLM
    3. Validate with diagnostic
    4. If invalid, regenerate with debug prompt
    """
    logger.info(f"Q: {request.question}")
    
    try:
        if not schema_loader.get_table_names():
            schema_loader.load_schema()
        
        schema_dict = schema_loader.get_schema_dict()
        
        global diagnostic
        if diagnostic is None:
            diagnostic = SQLDiagnostic(schema_dict)
        
        generated_sql = None
        validation_warnings = []
        
        # ════════════════════════════════════════════════════════
        # STEP 1: Schema-Aware Prompt (with RBAC filtering)
        # ════════════════════════════════════════════════════════
        logger.info("📝 Building schema-aware prompt...")
        if request.allowed_tables:
            logger.info(f"🔐 RBAC: Filtering to {len(request.allowed_tables)} allowed tables")
        try:
            prompt = build_prompt_with_schema(
                schema_dict,
                request.question,
                allowed_tables=request.allowed_tables  # Pass RBAC whitelist
            )
            logger.info(f"✓ Prompt: {len(prompt)} chars")
        except Exception as e:
            logger.warning(f"Enhanced prompt failed: {e}, using basic")
            prompt = f"""You are a SQL expert for manufacturing database.

Schema: {schema_loader.get_schema_context(tables=request.tables)}

Generate ONLY valid SQL. No explanation.

Question: {request.question}

SQL:"""
        
        # ════════════════════════════════════════════════════════
        # STEP 2: Rate Limit Check + Generate SQL
        # ════════════════════════════════════════════════════════
        logger.info("🤖 Generating SQL...")
        
        # Estimate tokens and check rate limit
        rate_limiter = get_rate_limiter()
        estimated_input_tokens = rate_limiter.estimate_tokens(prompt)
        can_proceed, rate_msg = rate_limiter.can_make_request(estimated_input_tokens + settings.max_output_tokens)
        
        if not can_proceed:
            logger.warning(f"⚠️ Rate limit hit: {rate_msg}")
            raise HTTPException(status_code=429, detail=rate_msg)
        
        try:
            llm = get_llm()
            response = llm.invoke([HumanMessage(content=prompt)])
            raw_output = response.content.strip()
            logger.info(f"Raw: {raw_output[:80]}...")
            
            # Record token usage
            output_tokens = rate_limiter.estimate_tokens(raw_output)
            record_usage(estimated_input_tokens, output_tokens)
            
            generated_sql = clean_generated_sql(raw_output)
            logger.info(f"Generated: {generated_sql[:80]}...")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")
        
        if not generated_sql or not generated_sql.upper().startswith("SELECT"):
            logger.error("Invalid SQL (no SELECT)")
            raise HTTPException(status_code=500, detail="Invalid SQL generated")
        
        # ════════════════════════════════════════════════════════
        # STEP 3: Validate
        # ════════════════════════════════════════════════════════
        logger.info("✓ Validating SQL...")
        diag = diagnostic.diagnose_query(request.question, generated_sql)
        
        if diag['errors']:
            logger.warning(f"Errors: {diag['errors']}")
            
            # ════════════════════════════════════════════════════════
            # STEP 4: Regenerate with Debug
            # ════════════════════════════════════════════════════════
            logger.info("🔧 Regenerating with debug hints...")
            try:
                debug_prompt = build_prompt_debug(schema_dict, request.question, generated_sql)
                llm = get_llm()
                debug_response = llm.invoke([HumanMessage(content=debug_prompt)])
                debug_sql = clean_generated_sql(debug_response.content.strip())
                
                debug_diag = diagnostic.diagnose_query(request.question, debug_sql)
                
                if not debug_diag['errors']:
                    logger.info("✓ Regenerated SQL valid!")
                    generated_sql = debug_sql
                    validation_warnings = diag['warnings']
                else:
                    logger.warning("Still has errors")
                    validation_warnings = diag['errors'] + diag['warnings']
                    
            except Exception as e:
                logger.warning(f"Debug regen failed: {e}")
                validation_warnings = diag['errors'] + diag['warnings']
        else:
            validation_warnings = diag['warnings']
            logger.info("✓ SQL valid!")
        
        # ════════════════════════════════════════════════════════
        # STEP 5: Security Check
        # ════════════════════════════════════════════════════════
        guardrails.allowed_tables = schema_loader.allowed_tables
        is_valid, error_message = guardrails.validate(generated_sql)
        
        if not is_valid:
            logger.error(f"Security check failed: {error_message}")
            raise HTTPException(status_code=403, detail=f"Security: {error_message}")
        
        tables_used = list(guardrails._extract_tables(generated_sql))
        logger.info(f"✓ Tables: {tables_used}")

        # ════════════════════════════════════════════════════════
        # STEP 6: Accuracy Scoring & Active Self-Correction
        # ════════════════════════════════════════════════════════
        
        # Initial scoring
        relevance_score, relevance_reason = await accuracy_scorer.calculate_relevance(request.question, generated_sql)
        confidence_score = accuracy_scorer.calculate_confidence(diag)
        
        MAX_RELEVANCE_RETRIES = 2
        retry_count = 0
        
        # 🔄 RELEVANCE RETRY LOOP
        while relevance_score < 70 and retry_count < MAX_RELEVANCE_RETRIES:
            retry_count += 1
            logger.warning(f"⚠ Low Relevance ({relevance_score}). Retrying ({retry_count}/{MAX_RELEVANCE_RETRIES}). Reason: {relevance_reason}")
            
            try:
                # Feedback Prompt for the LLM
                feedback_prompt = f"""You are fixing a bad SQL query.
                
User Question: "{request.question}"
Your Previous SQL: "{generated_sql}"
Quality Score: {relevance_score}/100
Feedback: {relevance_reason}

TASK: Generate a CORRECTED SQL query that better answers the user's question.
Schema: {schema_loader.get_schema_context(tables=request.tables)}

Return ONLY the SQL query. No explanation.
"""
                # Invoke LLM for correction
                response = llm.invoke([HumanMessage(content=feedback_prompt)])
                corrected_sql = clean_generated_sql(response.content.strip())
                
                if corrected_sql and corrected_sql.upper().startswith("SELECT"):
                    # Validate correction syntax
                    new_diag = diagnostic.diagnose_query(request.question, corrected_sql)
                    if new_diag['valid']:
                        # Adoption: Update generated_sql and re-score
                        generated_sql = corrected_sql
                        diag = new_diag
                        
                        # Re-calculate scores
                        relevance_score, relevance_reason = await accuracy_scorer.calculate_relevance(request.question, generated_sql)
                        confidence_score = accuracy_scorer.calculate_confidence(diag)
                        
                        logger.info(f"✓ Correction adopted. New Score: {relevance_score}")
                    else:
                        logger.warning("Correction was syntactically invalid. Ignoring.")
            except Exception as e:
                logger.error(f"Relevance retry failed: {e}")
                break

        logger.info(f"📊 Final Scores -> Confidence: {confidence_score}, Relevance: {relevance_score}")

        # ════════════════════════════════════════════════════════════
        # STEP 7: Handle Very Low Relevance - Data doesn't exist
        # ════════════════════════════════════════════════════════════
        if relevance_score < 30:
            logger.warning(f"⚠ Very low relevance ({relevance_score}%). Data likely doesn't exist in schema.")
            return GenerateSQLResponse(
                success=False,
                sql=None,
                tables_used=None,
                error=f"I couldn't find data for '{request.question}'. This information may not exist in the database. Try asking about: OEE, downtime, production, yield, cycle time, energy, defect rate, or other KPIs.",
                confidence_score=confidence_score,
                relevance_score=relevance_score
            )

        # Final decision logic for medium relevance
        if relevance_score < 50:
             logger.warning(f"⚠ Final Relevance too low ({relevance_score}). Flagging.")
             if not validation_warnings:
                 validation_warnings = []
             validation_warnings.append(f"⚠ Low Quality Warning: The AI is only {relevance_score}% confident this answers your specific question.")

        return GenerateSQLResponse(
            success=True,
            sql=generated_sql,
            tables_used=tables_used,
            explanation=f"Generated with {settings.model_name} + active self-correction (Retries: {retry_count})",
            validation_warnings=validation_warnings if validation_warnings else None,
            confidence_score=confidence_score,
            relevance_score=relevance_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return GenerateSQLResponse(
            success=False,
            error=f"Failed: {str(e)}"
        )

@app.post("/api/v1/format-response", response_model=FormatResponseResponse)
async def format_response(request: FormatResponseRequest):
    logger.info(f"Formatting: {request.question}")

    try:
        results = request.results
        row_count = len(results)

        if row_count == 0:
            response_text = f"No data found for: '{request.question}'"
        elif row_count == 1:
            # Clean formatting for single result
            row = results[0]
            if isinstance(row, dict):
                formatted_items = []
                for k, v in row.items():
                    # Format numbers nicely
                    val_str = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
                    # Clean key name (remove underscores, capitalize)
                    key_str = k.replace('_', ' ').title()
                    formatted_items.append(f"**{key_str}**: {val_str}")
                
                response_text = f"Here is the result for '{request.question}':\n\n" + "\n".join(formatted_items)
            else:
                response_text = f"Result: {str(row)}"
        else:
            preview = results[:5]
            response_text = f"Found {row_count} results for '{request.question}'.\n\n**Top {len(preview)}:**\n"
            for i, row in enumerate(preview, 1):
                if isinstance(row, dict):
                    # concise single line per row
                    row_str = ", ".join([f"{v}" for v in row.values()])
                    response_text += f"\n{i}. {row_str}"
                else:
                    response_text += f"\n{i}. {row}"
            
            if row_count > 5:
                response_text += f"\n\n... and {row_count - 5} more rows (see full table below)."

        return FormatResponseResponse(
            success=True,
            response=response_text
        )

    except Exception as e:
        logger.error(f"Format error: {e}")
        return FormatResponseResponse(
            success=False,
            error=f"Format failed: {str(e)}"
        )


# ============================================================
# ✅ SPEECH-TO-TEXT ENDPOINT
# ============================================================

from fastapi import UploadFile, File
import shutil
import tempfile

class TranscribeResponse(BaseModel):
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None

@app.post("/api/v1/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio file using Faster-Whisper (CPU optimized).
    Supports .wav, .mp3, .webm, etc.
    """
    try:
        # Save upload to temporary file
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        logger.info(f"🎤 Received audio file: {file.filename} -> {tmp_path}")

        try:
            from stt_service import stt_service
            text = stt_service.transcribe(tmp_path)
            
            # Cleanup
            os.unlink(tmp_path)
            
            return TranscribeResponse(
                success=True,
                text=text
            )
            
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return TranscribeResponse(
            success=False,
            error=f"Transcription failed: {str(e)}"
        )


# ============================================================
# ✅ CHART CONFIG ENDPOINT - Generates visualization config from results
# ============================================================

class GenerateChartConfigRequest(BaseModel):
    question: str
    results: List[Any]

class GenerateChartConfigResponse(BaseModel):
    success: bool
    chart_config: Optional[Dict] = None
    error: Optional[str] = None

@app.post("/api/v1/generate-chart-config", response_model=GenerateChartConfigResponse)
async def generate_chart_config(request: GenerateChartConfigRequest):
    """
    Generate chart configuration from query results.
    Called by Django after SQL execution with actual data.
    """
    logger.info(f"📊 Generating chart config for: {request.question[:50]}...")

    try:
        if not viz_pipeline:
            return GenerateChartConfigResponse(
                success=False,
                error="Visualization pipeline not initialized"
            )

        if not request.results:
            return GenerateChartConfigResponse(
                success=True,
                chart_config=None  # No chart for empty results
            )

        # Generate chart config using the visualization pipeline
        chart_config = viz_pipeline.generate_config_sync(
            question=request.question,
            results=request.results
        )

        if chart_config:
            logger.info(f"📊 Chart config generated: type={chart_config.get('type')}")
        else:
            logger.info("📊 No chart suitable for this data (table recommended)")

        return GenerateChartConfigResponse(
            success=True,
            chart_config=chart_config
        )

    except Exception as e:
        logger.error(f"Chart config generation error: {e}")
        return GenerateChartConfigResponse(
            success=False,
            error=f"Chart config generation failed: {str(e)}"
        )


# ============================================================
# ✅ HYBRID CHAT ENDPOINT - Answers both SQL and BRD questions
# ============================================================

class HybridChatRequest(BaseModel):
    question: str
    force_type: Optional[str] = None  # "sql" or "brd" to bypass auto-detection
    allowed_tables: Optional[List[str]] = None  # RBAC: table whitelist from Django

class HybridChatResponse(BaseModel):
    success: bool
    query_type: str  # "sql" or "brd"
    response: Optional[str] = None
    sql: Optional[str] = None
    results: Optional[List[Any]] = None
    sources: Optional[List[str]] = None
    images: Optional[List[Dict]] = None  # images from BRD documents
    chart_config: Optional[Dict] = None  # ✅ NEW: Visualization config for Recharts
    error: Optional[str] = None
    routing_confidence: Optional[float] = None
    confidence_score: Optional[int] = None
    relevance_score: Optional[int] = None

@app.post("/api/v1/chat", response_model=HybridChatResponse)
async def hybrid_chat(request: HybridChatRequest):
    """
    ✅ UNIFIED CHAT ENDPOINT
    Automatically routes questions to:
    - SQL generation for data queries
    - BRD RAG for documentation/process queries
    """
    logger.info(f"Hybrid chat: {request.question}")
    
    try:
        # ═══════════════════════════════════════════════════════════
        # ✅ SECURITY LAYER 1A: Flipping Attack Detection
        # ═══════════════════════════════════════════════════════════
        if flipping_detector:
            flip_result = flipping_detector.detect_flipping(request.question)
            if flip_result['is_flipped']:
                logger.warning(f"🚨 FLIPPING ATTACK blocked: {flip_result['detected_modes']}")
                audit_logger.log_flipping_detected(
                    user_id="anonymous", prompt=request.question,
                    detected_modes=flip_result['detected_modes'],
                    confidence=flip_result['confidence'], ip_address="127.0.0.1"
                )
                return HybridChatResponse(
                    success=True, query_type="blocked",
                    response="🔒 Unusual query pattern detected. Please rephrase your question in plain English.",
                    sql=None, results=None, sources=None, error=None, routing_confidence=0.0
                )
        
        # ═══════════════════════════════════════════════════════════
        # ✅ SECURITY LAYER 1B: Prompt Signature Validation
        # ═══════════════════════════════════════════════════════════
        if prompt_validator:
            sig_result = prompt_validator.validate(request.question)
            if not sig_result['is_safe']:
                logger.warning(f"🚨 INJECTION ATTACK blocked: {sig_result['threat_types']}")
                audit_logger.log_blocked_injection(
                    user_id="anonymous", prompt=request.question,
                    attack_type=sig_result['threat_types'][0] if sig_result['threat_types'] else "unknown",
                    confidence=sig_result['threat_score'], ip_address="127.0.0.1"
                )
                return HybridChatResponse(
                    success=True, query_type="blocked",
                    response="🔒 Your query contains patterns that cannot be processed. Please rephrase your question.",
                    sql=None, results=None, sources=None, error=None, routing_confidence=0.0
                )
        
        # ═══════════════════════════════════════════════════════════
        # ✅ SECURITY LAYER 1C: Red Team Attack Detection
        # ═══════════════════════════════════════════════════════════
        if red_team_detector:
            rt_result = red_team_detector.detect(request.question)
            if rt_result['is_attack']:
                logger.warning(f"🚨 RED TEAM ATTACK blocked: {rt_result['categories']}")
                audit_logger.log_red_team_blocked(
                    user_id="anonymous", categories=rt_result['categories'],
                    score=rt_result['score'], ip_address="127.0.0.1"
                )
                return HybridChatResponse(
                    success=True, query_type="blocked",
                    response="🔒 I can only help with manufacturing data queries. Please ask about production metrics, equipment status, or process data.",
                    sql=None, results=None, sources=None, error=None, routing_confidence=0.0
                )
        
        # ═══════════════════════════════════════════════════════════
        # ✅ STEP 0: GUARDRAILS AI CHECK (PII, profanity, sensitive data)
        # ═══════════════════════════════════════════════════════════
        if guardrails_layer:
            gr_result = guardrails_layer.validate(request.question)
            if not gr_result.is_safe:
                logger.warning(f"🛡️ Guardrails AI blocked: {gr_result.reason}")
                return HybridChatResponse(
                    success=True,
                    query_type="blocked",
                    response=guardrails_layer.get_blocked_message(gr_result),
                    sql=None,
                    results=None,
                    sources=None,
                    error=None,
                    routing_confidence=0.0
                )
        
        # ═══════════════════════════════════════════════════════════
        # ✅ STEP 1: ENHANCED QUERY GUARD (7-layer protection)
        # ═══════════════════════════════════════════════════════════
        guard_result = guard.check_query_relevance(request.question)
        
        if not guard_result.is_relevant:
            logger.warning(f"🛡️ Guard blocked: {guard_result.reason}")
            return HybridChatResponse(
                success=True,
                query_type="blocked",
                response=guard_result.suggested_message,
                sql=None,
                results=None,
                sources=None,
                error=None,
                routing_confidence=0.0
            )
        
        # ═══════════════════════════════════════════════════════════
        # ✅ STEP 2: DANGEROUS INTENT CHECK (data modification)
        # ═══════════════════════════════════════════════════════════
        question_lower = request.question.lower()
        dangerous_intents = ["delete", "drop", "truncate", "remove all", "clear all", "erase"]
        safe_contexts = ["how to", "what is", "show", "get", "display", "list"]
        
        # Check if question has dangerous intent without safe context
        has_dangerous_intent = any(d in question_lower for d in dangerous_intents)
        has_safe_context = any(s in question_lower for s in safe_contexts)
        
        if has_dangerous_intent and not has_safe_context:
            logger.warning(f"🛡️ Blocked dangerous request: {request.question[:50]}")
            return HybridChatResponse(
                success=True,
                query_type="blocked",
                response="🔒 I'm a READ-ONLY assistant! I can only help you view and analyze data, not modify or delete it. Try asking something like 'show OEE for furnace 1' instead!",
                sql=None,
                results=None,
                sources=None,
                error=None,
                routing_confidence=1.0
            )
        
        # Determine query type
        if request.force_type:
            query_type = request.force_type
            confidence = 1.0
        else:
            query_type, confidence = route_query(request.question)
        
        logger.info(f"Routed to: {query_type} (confidence: {confidence:.2f})")
        
        # Handle SQL queries
        if query_type == "sql" or query_type == "unknown":
            # Use existing SQL generation logic with RBAC table filtering
            sql_request = GenerateSQLRequest(
                question=request.question,
                allowed_tables=request.allowed_tables  # Pass RBAC whitelist
            )
            sql_response = await generate_sql(sql_request)
            
            # ═══════════════════════════════════════════════════════════
            # ✅ SECURITY LAYER 3: Anomaly Detection (flag, don't block)
            # ═══════════════════════════════════════════════════════════
            if anomaly_detector and sql_response.success and sql_response.sql:
                is_anomalous, reason, score = anomaly_detector.is_anomalous(
                    user_id="anonymous",
                    query_context={'sql': sql_response.sql, 'tables': sql_response.tables_used or []}
                )
                if is_anomalous:
                    logger.warning(f"⚠️ ANOMALY flagged: {reason} (score: {score:.2f})")
                    audit_logger.log_anomaly_detected(
                        user_id="anonymous", reason=reason, score=score, ip_address="127.0.0.1"
                    )
            
            # ✅ AUDIT LOG: Successful query
            if sql_response.success:
                audit_logger.log_query(
                    user_id="anonymous", sql=sql_response.sql or "",
                    result_count=0, execution_time=0, ip_address="127.0.0.1"
                )

            # ✅ VISUALIZATION: Generate chart config (heuristic-based, data-independent)
            # Full chart generation happens in Django after SQL execution with actual results
            chart_config = None
            if sql_response.success and viz_pipeline:
                try:
                    # Generate preliminary config based on question
                    # Django will finalize with actual data
                    chart_config = viz_pipeline.generate_config_sync(
                        question=request.question,
                        results=[]  # Placeholder, Django will inject actual results
                    )
                    if chart_config:
                        logger.info(f"📊 Chart config generated: type={chart_config.get('type')}")
                except Exception as e:
                    logger.warning(f"Visualization config generation failed: {e}")
                    chart_config = None

            return HybridChatResponse(
                success=sql_response.success,
                query_type="sql",
                response=sql_response.explanation if sql_response.success else sql_response.error,
                sql=sql_response.sql,
                results=None,  # Results come from Django after execution
                sources=sql_response.tables_used,
                chart_config=chart_config,  # ✅ NEW: Visualization config
                error=sql_response.error if not sql_response.success else None,
                routing_confidence=confidence,
                confidence_score=sql_response.confidence_score,
                relevance_score=sql_response.relevance_score
            )
        
        # Handle BRD queries
        elif query_type == "brd":
            if not brd_initialized:
                return HybridChatResponse(
                    success=False,
                    query_type="brd",
                    error="BRD document system not initialized. Please wait for indexing to complete.",
                    routing_confidence=confidence
                )
            
            # Query BRD documents (now returns images too)
            logger.info(f">>> BRD QUERY START: '{request.question}'")
            logger.info(f">>> brd_initialized={brd_initialized}, handler._initialized={brd_handler.is_initialized}")
            llm = get_llm()
            brd_result = brd_handler.query(request.question, llm=llm, top_k=5, image_k=3)
            logger.info(f">>> BRD QUERY RESULT: success={brd_result.get('success')}, sources={len(brd_result.get('sources', []))}")
            
            return HybridChatResponse(
                success=brd_result["success"],
                query_type="brd",
                response=brd_result.get("response"),
                sql=None,
                results=None,
                sources=brd_result.get("sources", []),
                images=brd_result.get("images", []),  # NEW: include images
                error=brd_result.get("error"),
                routing_confidence=confidence
            )
        
        else:
            return HybridChatResponse(
                success=False,
                query_type="unknown",
                error="Could not determine query type",
                routing_confidence=confidence
            )
            
    except HTTPException as he:
        # HTTPException has detail attribute, not __str__
        error_msg = he.detail if hasattr(he, 'detail') else str(he)
        logger.error(f"Hybrid chat HTTPException: {error_msg}")
        return HybridChatResponse(
            success=False,
            query_type="error",
            error=error_msg
        )
    except Exception as e:
        logger.error(f"Hybrid chat error: {e}", exc_info=True)
        return HybridChatResponse(
            success=False,
            query_type="unknown",
            error=f"Chat failed: {str(e) if str(e) else type(e).__name__}"
        )


@app.get("/api/v1/routing-test")
async def test_routing(question: str):
    """Test the query router without executing."""
    query_type, confidence = route_query(question)
    explanation = QueryRouter.explain_routing(question)
    return {
        "question": question,
        "query_type": query_type,
        "confidence": confidence,
        "explanation": explanation
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 70)
    print("Hybrid NLP Service - SQL + BRD RAG (Groq API)")
    print("=" * 70)
    print(f"Model: {settings.model_name}")
    print(f"Host: {settings.nlp_service_host}:{settings.nlp_service_port}")
    print(f"Backend: {settings.django_api_url}")
    print("Endpoints:")
    print("  - /api/v1/chat        (Hybrid: auto-routes SQL vs BRD)")
    print("  - /api/v1/generate-sql (SQL only)")
    print("  - /api/v1/routing-test (Test routing)")
    print("=" * 70 + "\n")
    
    uvicorn.run(
        "main:app",
        host=settings.nlp_service_host,
        port=settings.nlp_service_port,
        reload=True  # Enabled for development updates
    )

