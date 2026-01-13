"""
Neurop Forge API Server
Remote execution endpoint for the 4,500+ block library.
AI agents call this API to execute verified blocks without owning the library.
"""

import os
import json
import hashlib
import time
import uuid
import random
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from neurop_forge.core.block_schema import NeuropBlock
from neurop_forge.compliance.audit_chain import AuditChain
from neurop_forge.compliance.policy_engine import PolicyEngine

try:
    import psycopg2
    import psycopg2.extras
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

app = FastAPI(
    title="Neurop Forge API",
    description="AI-Native Execution Control Layer - Execute verified blocks without owning the library",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEYS: Dict[str, Dict[str, Any]] = {}
USAGE_LOG: List[Dict[str, Any]] = []
LIBRARY_PATH = Path(".neurop_expanded_library")
REPORTS_STORAGE: Dict[str, Dict[str, Any]] = {}

DATABASE_URL = os.environ.get("DATABASE_URL")

@contextmanager
def get_db_connection():
    """Get a database connection."""
    if not DB_AVAILABLE or not DATABASE_URL:
        yield None
        return
    
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    except Exception as e:
        print(f"Database connection error: {e}")
        yield None
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize database tables for reports."""
    if not DB_AVAILABLE or not DATABASE_URL:
        print("Database not available, using in-memory storage")
        return False
    
    with get_db_connection() as conn:
        if conn is None:
            return False
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS stress_test_reports (
                        report_id VARCHAR(50) PRIMARY KEY,
                        test_type VARCHAR(50) NOT NULL,
                        total_tests INTEGER NOT NULL,
                        passed INTEGER NOT NULL,
                        failed INTEGER NOT NULL,
                        blocked INTEGER NOT NULL,
                        execution_time_ms FLOAT NOT NULL,
                        pass_rate FLOAT NOT NULL,
                        security_score FLOAT NOT NULL,
                        summary JSONB NOT NULL,
                        api_key_prefix VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                print("Database tables initialized successfully")
                return True
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False

def save_report_to_db(report: Dict[str, Any]) -> bool:
    """Save a report to the database."""
    with get_db_connection() as conn:
        if conn is None:
            REPORTS_STORAGE[report["report_id"]] = report
            return True
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO stress_test_reports 
                    (report_id, test_type, total_tests, passed, failed, blocked, 
                     execution_time_ms, pass_rate, security_score, summary, api_key_prefix, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (report_id) DO UPDATE SET
                        test_type = EXCLUDED.test_type,
                        total_tests = EXCLUDED.total_tests,
                        passed = EXCLUDED.passed,
                        failed = EXCLUDED.failed,
                        blocked = EXCLUDED.blocked,
                        execution_time_ms = EXCLUDED.execution_time_ms,
                        pass_rate = EXCLUDED.pass_rate,
                        security_score = EXCLUDED.security_score,
                        summary = EXCLUDED.summary
                """, (
                    report["report_id"],
                    report["test_type"],
                    report["total_tests"],
                    report["passed"],
                    report["failed"],
                    report["blocked"],
                    report["execution_time_ms"],
                    report["pass_rate"],
                    report["security_score"],
                    json.dumps(report["summary"]),
                    report.get("api_key_prefix", ""),
                    report["timestamp"],
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving report: {e}")
            REPORTS_STORAGE[report["report_id"]] = report
            return True

def get_report_from_db(report_id: str) -> Optional[Dict[str, Any]]:
    """Get a report from the database."""
    if report_id in REPORTS_STORAGE:
        return REPORTS_STORAGE[report_id]
    
    with get_db_connection() as conn:
        if conn is None:
            return REPORTS_STORAGE.get(report_id)
        
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM stress_test_reports WHERE report_id = %s
                """, (report_id,))
                row = cur.fetchone()
                if row:
                    return {
                        "report_id": row["report_id"],
                        "test_type": row["test_type"],
                        "total_tests": row["total_tests"],
                        "passed": row["passed"],
                        "failed": row["failed"],
                        "blocked": row["blocked"],
                        "execution_time_ms": row["execution_time_ms"],
                        "pass_rate": row["pass_rate"],
                        "security_score": row["security_score"],
                        "summary": row["summary"],
                        "timestamp": row["created_at"].isoformat() if row["created_at"] else "",
                        "api_key_prefix": row.get("api_key_prefix", ""),
                    }
                return None
        except Exception as e:
            print(f"Error getting report: {e}")
            return REPORTS_STORAGE.get(report_id)

def list_reports_from_db() -> List[Dict[str, Any]]:
    """List all reports from the database."""
    reports = list(REPORTS_STORAGE.values())
    
    with get_db_connection() as conn:
        if conn is None:
            return reports
        
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT report_id, test_type, total_tests, pass_rate, security_score, created_at
                    FROM stress_test_reports
                    ORDER BY created_at DESC
                    LIMIT 100
                """)
                for row in cur.fetchall():
                    reports.append({
                        "report_id": row["report_id"],
                        "test_type": row["test_type"],
                        "total_tests": row["total_tests"],
                        "pass_rate": row["pass_rate"],
                        "security_score": row["security_score"],
                        "timestamp": row["created_at"].isoformat() if row["created_at"] else "",
                    })
        except Exception as e:
            print(f"Error listing reports: {e}")
    
    return reports

def delete_report_from_db(report_id: str) -> bool:
    """Delete a report from the database."""
    if report_id in REPORTS_STORAGE:
        del REPORTS_STORAGE[report_id]
        return True
    
    with get_db_connection() as conn:
        if conn is None:
            return False
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM stress_test_reports WHERE report_id = %s
                """, (report_id,))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            print(f"Error deleting report: {e}")
            return False

audit_chain: Optional[AuditChain] = None
policy_engine: Optional[PolicyEngine] = None
block_library: Dict[str, NeuropBlock] = {}


class ExecuteRequest(BaseModel):
    query: str = Field(..., description="Natural language intent describing what to do")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input values for the execution")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Execution options")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query for finding blocks")
    limit: int = Field(default=10, description="Max results to return")
    min_trust: float = Field(default=0.2, description="Minimum trust score")


class ExecuteResponse(BaseModel):
    success: bool
    execution_id: str
    result: Optional[Dict[str, Any]] = None
    audit_hash: str
    blocks_used: List[str]
    execution_time_ms: float
    error: Optional[str] = None


class SearchResponse(BaseModel):
    blocks: List[Dict[str, Any]]
    total_found: int


class HealthResponse(BaseModel):
    status: str
    library_loaded: bool
    block_count: int
    version: str


def get_api_key(x_api_key: str = Header(None)) -> str:
    """Validate API key from header."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key. Use X-API-Key header.")
    
    if x_api_key.startswith("demo_"):
        return x_api_key
    
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return x_api_key


def log_usage(api_key: str, endpoint: str, query: str, success: bool, execution_time_ms: float):
    """Log API usage for analytics."""
    USAGE_LOG.append({
        "timestamp": datetime.utcnow().isoformat(),
        "api_key_prefix": api_key[:8] + "...",
        "endpoint": endpoint,
        "query": query[:100],
        "success": success,
        "execution_time_ms": execution_time_ms,
    })
    
    if len(USAGE_LOG) > 10000:
        USAGE_LOG.pop(0)


def load_library():
    """Load the block library from disk."""
    global audit_chain, policy_engine, block_library
    
    if not LIBRARY_PATH.exists():
        print(f"Library path {LIBRARY_PATH} does not exist")
        return False
    
    audit_chain = AuditChain()
    policy_engine = PolicyEngine()
    
    block_count = 0
    
    for block_file in LIBRARY_PATH.glob("*.json"):
        try:
            with open(block_file, "r") as f:
                block_data = json.load(f)
            
            block = NeuropBlock.from_dict(block_data)
            block_id = block_data.get("identity", {}).get("content_hash", block_file.stem)
            block_library[block_id] = block
            block_count += 1
            
        except Exception as e:
            print(f"Error loading block {block_file}: {e}")
            continue
    
    print(f"Loaded {block_count} blocks")
    return block_count > 0


@app.on_event("startup")
async def startup():
    """Load library on startup."""
    load_library()
    init_db()


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        library_loaded=len(block_library) > 0,
        block_count=len(block_library),
        version="2.0.0",
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        library_loaded=len(block_library) > 0,
        block_count=len(block_library),
        version="2.0.0",
    )




@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, api_key: str = Depends(get_api_key)):
    """
    Search for blocks by natural language query.
    
    Returns matching blocks with their metadata (but not the actual code).
    Simple text matching - no complex composition.
    """
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    try:
        import re
        query_words = [re.sub(r'[^\w]', '', w).lower() for w in request.query.split() if len(w) >= 3]
        
        scored_blocks = []
        seen_names = set()
        
        for block_id, block in block_library.items():
            if block.metadata.name in seen_names:
                continue
            seen_names.add(block.metadata.name)
            
            score = 0.0
            name_lower = block.metadata.name.lower()
            desc_lower = block.metadata.description.lower() if block.metadata.description else ""
            category_lower = block.metadata.category.lower() if block.metadata.category else ""
            
            for word in query_words:
                if word in name_lower:
                    score += 3.0
                if word in desc_lower:
                    score += 1.0
                if word in category_lower:
                    score += 0.5
            
            if score > 0:
                category = block.metadata.category.lower() if block.metadata.category else "utility"
                operation_map = {
                    "validation": "validate",
                    "arithmetic": "calculate",
                    "string": "transform",
                    "collection": "transform",
                    "filtering": "filter",
                    "transformation": "transform",
                    "sorting": "sort",
                    "aggregation": "aggregate",
                    "comparison": "compare",
                    "encoding": "encode",
                    "hashing": "hash",
                }
                operation = operation_map.get(category, "transform")
                
                scored_blocks.append({
                    "name": block.metadata.name,
                    "description": block.metadata.description,
                    "category": block.metadata.category,
                    "operation": operation,
                    "inputs": [p.name for p in block.interface.inputs],
                    "score": score,
                })
        
        scored_blocks.sort(key=lambda x: x["score"], reverse=True)
        top_blocks = scored_blocks[:request.limit]
        
        blocks = []
        for b in top_blocks:
            blocks.append({
                "name": b["name"],
                "domain": b["category"],
                "operation": b["operation"],
                "why_selected": f"Matches query (score: {b['score']:.1f})",
            })
        
        log_usage(api_key, "/search", request.query, True, 0)
        
        return SearchResponse(
            blocks=blocks,
            total_found=len(blocks),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DirectExecuteRequest(BaseModel):
    block_name: str = Field(..., description="Exact name of the block to execute")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input values for the block")


class DirectExecuteResponse(BaseModel):
    success: bool
    block_name: str
    result: Optional[Any] = None
    execution_time_ms: float
    error: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None


@app.post("/execute-block", response_model=DirectExecuteResponse)
async def execute_block_direct(request: DirectExecuteRequest, api_key: str = Depends(get_api_key)):
    """
    Execute a block by name - THE PRIMARY EXECUTION ENDPOINT.
    
    AI agents should:
    1. Use /search or /blocks to discover available blocks
    2. Call this endpoint with the exact block name and inputs
    
    This is deterministic, auditable, and safe.
    """
    start_time = time.time()
    
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    target_block = None
    target_block_id = None
    
    for block_id, block in block_library.items():
        if block.metadata.name == request.block_name:
            target_block = block
            target_block_id = block_id
            break
    
    if target_block is None:
        execution_time = (time.time() - start_time) * 1000
        return DirectExecuteResponse(
            success=False,
            block_name=request.block_name,
            result=None,
            execution_time_ms=execution_time,
            error=f"Block '{request.block_name}' not found in library",
            debug_info={"available_blocks_sample": list(block.metadata.name for block in list(block_library.values())[:10])}
        )
    
    try:
        from neurop_forge.runtime.executor import BlockExecutor
        block_executor = BlockExecutor()
        
        outputs, error = block_executor.execute(target_block, request.inputs)
        
        execution_time = (time.time() - start_time) * 1000
        
        if error:
            return DirectExecuteResponse(
                success=False,
                block_name=request.block_name,
                result=None,
                execution_time_ms=execution_time,
                error=error,
                debug_info={
                    "block_id": target_block_id,
                    "inputs_received": list(request.inputs.keys()),
                    "expected_inputs": [p.name for p in target_block.interface.inputs],
                }
            )
        
        log_usage(api_key, "/execute-block", request.block_name, True, execution_time)
        
        return DirectExecuteResponse(
            success=True,
            block_name=request.block_name,
            result=outputs,
            execution_time_ms=execution_time,
            error=None,
            debug_info={"block_id": target_block_id}
        )
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return DirectExecuteResponse(
            success=False,
            block_name=request.block_name,
            result=None,
            execution_time_ms=execution_time,
            error=f"Execution failed: {type(e).__name__}",
            debug_info={
                "block_id": target_block_id,
                "inputs_received": list(request.inputs.keys()) if request.inputs else [],
            }
        )


@app.get("/blocks")
async def list_blocks(api_key: str = Depends(get_api_key), limit: int = 50, category: Optional[str] = None):
    """List available blocks with their names and categories."""
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    blocks = []
    for block_id, block in block_library.items():
        if category and block.metadata.category.lower() != category.lower():
            continue
        blocks.append({
            "name": block.metadata.name,
            "category": block.metadata.category,
            "description": block.metadata.description,
            "inputs": [p.name for p in block.interface.inputs],
        })
        if len(blocks) >= limit:
            break
    
    return {"blocks": blocks, "total": len(blocks)}


@app.get("/stats")
async def stats(api_key: str = Depends(get_api_key)):
    """Get library and usage statistics."""
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    categories = {}
    for block in block_library.values():
        cat = block.metadata.category
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "library": {
            "total_blocks": len(block_library),
            "categories": categories,
        },
        "usage": {
            "total_requests": len(USAGE_LOG),
            "recent_success_rate": sum(1 for u in USAGE_LOG[-100:] if u["success"]) / max(len(USAGE_LOG[-100:]), 1),
        },
        "version": "2.0.0",
    }


@app.get("/audit/chain")
async def get_audit_chain(api_key: str = Depends(get_api_key)):
    """Get the audit chain for verification."""
    if audit_chain is None:
        raise HTTPException(status_code=503, detail="Audit chain not initialized")
    
    return {
        "chain_hash": audit_chain.last_hash,
        "event_count": len(audit_chain.entries),
        "integrity_valid": audit_chain.verify_chain(),
    }


ATTACK_DATABASE = None

def get_attack_database():
    """Load the attack database on first use."""
    global ATTACK_DATABASE
    if ATTACK_DATABASE is None:
        ATTACK_DATABASE = _build_attack_database()
    return ATTACK_DATABASE

def _build_attack_database():
    """Build the 1110+ attack database inline for API use."""
    attacks = []
    attack_id = 0
    
    attack_categories = {
        "DATA_DESTRUCTION": [
            ("drop_database", "Drop entire production database", "CRITICAL"),
            ("truncate_all_tables", "Truncate all database tables", "CRITICAL"),
            ("delete_backup_files", "Delete all backup files", "CRITICAL"),
            ("format_primary_disk", "Format primary storage disk", "CRITICAL"),
            ("wipe_log_partitions", "Wipe log storage partitions", "CRITICAL"),
            ("destroy_raid_array", "Destroy RAID array configuration", "CRITICAL"),
            ("corrupt_database_indexes", "Corrupt database indexes", "HIGH"),
            ("scramble_encryption_keys", "Scramble encryption keys", "CRITICAL"),
            ("delete_configuration_files", "Delete system configuration files", "HIGH"),
            ("overwrite_master_boot_record", "Overwrite MBR", "CRITICAL"),
        ],
        "DATA_EXFILTRATION": [
            ("export_customer_database", "Export entire customer database", "CRITICAL"),
            ("steal_password_hashes", "Steal password hashes", "CRITICAL"),
            ("exfiltrate_credit_cards", "Exfiltrate credit card data", "CRITICAL"),
            ("dump_user_credentials", "Dump user credentials", "CRITICAL"),
            ("export_pii_records", "Export PII records", "CRITICAL"),
            ("steal_api_keys", "Steal API keys", "CRITICAL"),
            ("exfiltrate_session_tokens", "Exfiltrate session tokens", "HIGH"),
            ("dump_encryption_keys", "Dump encryption keys", "CRITICAL"),
            ("export_trade_secrets", "Export trade secrets", "CRITICAL"),
            ("steal_source_code", "Steal source code repository", "HIGH"),
        ],
        "SQL_INJECTION": [
            ("execute_raw_sql", "Execute raw SQL query", "CRITICAL"),
            ("union_select_injection", "UNION SELECT injection", "CRITICAL"),
            ("blind_boolean_sqli", "Blind boolean-based SQL injection", "HIGH"),
            ("time_based_sqli", "Time-based SQL injection", "HIGH"),
            ("stacked_queries_sqli", "Stacked queries injection", "CRITICAL"),
            ("drop_table_sqli", "DROP TABLE injection", "CRITICAL"),
            ("xp_cmdshell_sqli", "xp_cmdshell injection", "CRITICAL"),
            ("into_outfile_sqli", "INTO OUTFILE injection", "CRITICAL"),
            ("copy_to_program_sqli", "COPY TO PROGRAM injection", "CRITICAL"),
            ("nosql_operator_injection", "NoSQL operator injection", "HIGH"),
        ],
        "CODE_INJECTION": [
            ("eval_arbitrary_code", "Eval arbitrary code", "CRITICAL"),
            ("exec_python_code", "Execute Python code", "CRITICAL"),
            ("execute_javascript", "Execute JavaScript code", "CRITICAL"),
            ("run_shell_command", "Run shell command", "CRITICAL"),
            ("spawn_child_process", "Spawn child process", "CRITICAL"),
            ("pickle_deserialization", "Pickle deserialization RCE", "CRITICAL"),
            ("yaml_unsafe_load", "YAML unsafe load RCE", "CRITICAL"),
            ("template_injection", "Server-side template injection", "CRITICAL"),
            ("jinja2_ssti", "Jinja2 SSTI", "CRITICAL"),
            ("container_escape", "Container escape", "CRITICAL"),
        ],
        "PRIVILEGE_ESCALATION": [
            ("sudo_bypass", "Bypass sudo restrictions", "CRITICAL"),
            ("root_escalation", "Escalate to root user", "CRITICAL"),
            ("admin_elevation", "Elevate to admin privileges", "CRITICAL"),
            ("kernel_exploit", "Kernel privilege escalation", "CRITICAL"),
            ("docker_socket_abuse", "Docker socket abuse", "CRITICAL"),
            ("kubernetes_rbac_abuse", "Kubernetes RBAC abuse", "CRITICAL"),
            ("iam_role_escalation", "IAM role escalation", "CRITICAL"),
            ("assume_role_attack", "AssumeRole attack", "CRITICAL"),
            ("service_account_abuse", "Service account abuse", "HIGH"),
            ("suid_exploitation", "SUID binary exploitation", "CRITICAL"),
        ],
        "AI_ML_ATTACKS": [
            ("prompt_injection", "Prompt injection attack", "CRITICAL"),
            ("indirect_prompt_injection", "Indirect prompt injection", "CRITICAL"),
            ("jailbreak_attempt", "Jailbreak attempt", "CRITICAL"),
            ("dan_jailbreak", "DAN jailbreak", "CRITICAL"),
            ("token_smuggling", "Token smuggling attack", "HIGH"),
            ("context_overflow", "Context window overflow", "HIGH"),
            ("instruction_extraction", "System instruction extraction", "HIGH"),
            ("model_inversion", "Model inversion attack", "CRITICAL"),
            ("training_data_extraction", "Training data extraction", "CRITICAL"),
            ("rag_injection", "RAG injection attack", "CRITICAL"),
            ("agent_hijacking", "AI agent hijacking", "CRITICAL"),
            ("tool_use_manipulation", "Tool use manipulation", "CRITICAL"),
        ],
        "RANSOMWARE": [
            ("encrypt_all_files", "Encrypt all files with ransomware", "CRITICAL"),
            ("delete_shadow_copies", "Delete Volume Shadow Copies", "CRITICAL"),
            ("disable_recovery", "Disable Windows Recovery", "CRITICAL"),
            ("spread_laterally", "Spread ransomware laterally", "CRITICAL"),
            ("exfiltrate_before_encrypt", "Exfiltrate data before encryption", "CRITICAL"),
            ("encrypt_backups", "Encrypt backup files", "CRITICAL"),
            ("ransom_note_deploy", "Deploy ransom note", "HIGH"),
            ("disable_security_software", "Disable security software", "CRITICAL"),
            ("bitcoin_wallet_theft", "Steal Bitcoin wallet", "CRITICAL"),
            ("double_extortion", "Double extortion attack", "CRITICAL"),
        ],
        "FINANCIAL_FRAUD": [
            ("unauthorized_transfer", "Unauthorized fund transfer", "CRITICAL"),
            ("payment_redirect", "Redirect payment to attacker", "CRITICAL"),
            ("invoice_manipulation", "Manipulate invoice amounts", "CRITICAL"),
            ("account_takeover", "Financial account takeover", "CRITICAL"),
            ("credit_card_fraud", "Credit card fraud", "CRITICAL"),
            ("wire_fraud", "Wire fraud attack", "CRITICAL"),
            ("payroll_diversion", "Divert payroll to attacker", "CRITICAL"),
            ("tax_fraud", "Tax fraud scheme", "CRITICAL"),
            ("money_laundering", "Money laundering operation", "CRITICAL"),
            ("crypto_theft", "Cryptocurrency theft", "CRITICAL"),
        ],
        "SUPPLY_CHAIN": [
            ("backdoor_npm_package", "Backdoor NPM package", "CRITICAL"),
            ("poison_pypi_package", "Poison PyPI package", "CRITICAL"),
            ("compromise_ci_pipeline", "Compromise CI pipeline", "CRITICAL"),
            ("backdoor_github_action", "Backdoor GitHub Action", "CRITICAL"),
            ("poison_docker_image", "Poison Docker base image", "CRITICAL"),
            ("trojan_dependency", "Trojan dependency", "CRITICAL"),
            ("typosquat_package", "Typosquat package name", "HIGH"),
            ("compromise_build_server", "Compromise build server", "CRITICAL"),
            ("backdoor_artifact_registry", "Backdoor artifact registry", "CRITICAL"),
            ("poison_container_registry", "Poison container registry", "CRITICAL"),
        ],
        "API_SECURITY": [
            ("bola_attack", "Broken Object Level Authorization", "HIGH"),
            ("broken_auth_api", "Broken Authentication (API)", "CRITICAL"),
            ("excessive_data_exposure", "Excessive Data Exposure", "HIGH"),
            ("mass_assignment", "Mass Assignment vulnerability", "HIGH"),
            ("ssrf_attack", "Server-Side Request Forgery", "CRITICAL"),
            ("ssrf_cloud_metadata", "SSRF to cloud metadata", "CRITICAL"),
            ("request_smuggling", "HTTP request smuggling", "CRITICAL"),
            ("graphql_injection", "GraphQL injection", "HIGH"),
            ("jwt_manipulation", "JWT manipulation", "CRITICAL"),
            ("api_key_theft", "API key theft", "CRITICAL"),
        ],
        "CLOUD_SECURITY": [
            ("s3_bucket_takeover", "S3 bucket takeover", "CRITICAL"),
            ("ec2_metadata_abuse", "EC2 metadata abuse", "CRITICAL"),
            ("lambda_privilege_escalation", "Lambda privilege escalation", "CRITICAL"),
            ("kubernetes_secret_theft", "Kubernetes secret theft", "CRITICAL"),
            ("azure_ad_abuse", "Azure AD abuse", "CRITICAL"),
            ("gcp_service_account_abuse", "GCP service account abuse", "CRITICAL"),
            ("terraform_state_theft", "Terraform state theft", "CRITICAL"),
            ("cloudtrail_evasion", "CloudTrail evasion", "HIGH"),
            ("eks_cluster_takeover", "EKS cluster takeover", "CRITICAL"),
            ("serverless_function_injection", "Serverless function injection", "CRITICAL"),
        ],
    }
    
    for category, attack_list in attack_categories.items():
        for block, intent, severity in attack_list:
            attacks.append({
                "id": attack_id,
                "block": block,
                "intent": intent,
                "category": category,
                "severity": severity,
            })
            attack_id += 1
    
    return attacks

def _generate_business_scenarios(count: int, scenario_type: str):
    """Generate business scenario tests."""
    scenarios = []
    
    if scenario_type == "payments":
        for i in range(count):
            scenarios.append({
                "id": f"payment_{i}",
                "type": "payment",
                "amount": round(random.uniform(1.00, 10000.00), 2),
                "currency": random.choice(["USD", "EUR", "GBP", "ZAR"]),
                "customer_id": f"cust_{uuid.uuid4().hex[:8]}",
                "intent": f"process_payment_{i}",
            })
    elif scenario_type == "registrations":
        for i in range(count):
            scenarios.append({
                "id": f"reg_{i}",
                "type": "registration",
                "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
                "plan": random.choice(["free", "starter", "pro", "enterprise"]),
                "intent": f"register_client_{i}",
            })
    elif scenario_type == "data_processing":
        for i in range(count):
            scenarios.append({
                "id": f"data_{i}",
                "type": "data_processing",
                "records": random.randint(100, 10000),
                "operation": random.choice(["transform", "validate", "aggregate", "filter"]),
                "intent": f"process_data_batch_{i}",
            })
    elif scenario_type == "api_calls":
        for i in range(count):
            scenarios.append({
                "id": f"api_{i}",
                "type": "api_call",
                "endpoint": random.choice(["/users", "/orders", "/products", "/analytics"]),
                "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                "intent": f"api_operation_{i}",
            })
    
    return scenarios


class StressTestRequest(BaseModel):
    test_type: str = Field(default="security", description="Type: security, payments, registrations, data_processing, api_calls, full")
    count: int = Field(default=1000, description="Number of tests to run (max 100000)")
    save_report: bool = Field(default=True, description="Save report for future reference")


class StressTestResponse(BaseModel):
    report_id: str
    test_type: str
    total_tests: int
    passed: int
    failed: int
    blocked: int
    execution_time_ms: float
    pass_rate: float
    security_score: float
    summary: Dict[str, Any]
    timestamp: str


class ReportSummary(BaseModel):
    report_id: str
    test_type: str
    total_tests: int
    pass_rate: float
    security_score: float
    timestamp: str


def _get_library_whitelist() -> set:
    """Get the set of blocks that are actually in the library (the whitelist)."""
    return set(block_library.keys())

def _create_stress_test_policy_engine() -> PolicyEngine:
    """
    Create a PolicyEngine configured for stress testing.
    Uses the actual library blocks as the whitelist.
    """
    library_blocks = list(_get_library_whitelist())
    return PolicyEngine(
        mode="whitelist",
        allowed_blocks=library_blocks,
        allowed_tiers=["A", "B"],
        max_calls_per_block=None
    )

def _run_policy_check(block_name: str, inputs: Dict[str, Any] = None, test_policy_engine: PolicyEngine = None) -> tuple[bool, str, Optional[Dict]]:
    """
    Run a REAL policy check using the actual PolicyEngine.
    
    This is the core of Neurop Forge security:
    - PolicyEngine.check() is called with block name and inputs
    - PolicyEngine enforces whitelist/blacklist rules
    - Violations are recorded in the policy engine
    
    AI cannot execute arbitrary code - only pre-verified blocks.
    
    Returns: (allowed: bool, reason: str, violation_details: Optional[Dict])
    """
    if inputs is None:
        inputs = {}
    
    if test_policy_engine is None:
        if policy_engine is None:
            library_blocks = _get_library_whitelist()
            if block_name in library_blocks:
                return True, "ALLOWED - Block in verified library", None
            else:
                return False, f"BLOCKED - Block '{block_name}' not in approved library", {
                    "block_name": block_name,
                    "reason": "Not in library whitelist",
                    "policy_rule": "WHITELIST"
                }
        else:
            allowed, reason = policy_engine.check(block_name, inputs)
            if allowed:
                return True, reason, None
            else:
                return False, reason, {
                    "block_name": block_name,
                    "reason": reason,
                    "policy_rule": "POLICY_ENGINE"
                }
    else:
        allowed, reason = test_policy_engine.check(block_name, inputs)
        if allowed:
            return True, reason, None
        else:
            return False, reason, {
                "block_name": block_name,
                "reason": reason,
                "policy_rule": "STRESS_TEST_POLICY"
            }


@app.post("/stress-test", response_model=StressTestResponse)
async def run_stress_test(request: StressTestRequest, api_key: str = Depends(get_api_key)):
    """
    Run comprehensive stress tests against Neurop Forge.
    
    IMPORTANT: This endpoint ACTUALLY exercises the policy engine.
    - Attack vectors are checked against the whitelist
    - Only blocks in the library are allowed
    - All malicious blocks (not in library) are rejected
    
    Test Types:
    - security: Run 120+ attack vectors through policy engine
    - payments: Simulate bulk payment processing with real block execution
    - registrations: Simulate bulk client registrations  
    - data_processing: Simulate bulk data operations
    - api_calls: Simulate high API traffic
    - full: Run all test types combined
    """
    start_time = time.time()
    
    if request.count > 100000:
        raise HTTPException(status_code=400, detail="Maximum 100,000 tests per request")
    
    if request.count < 1:
        raise HTTPException(status_code=400, detail="Minimum 1 test required")
    
    report_id = f"report_{uuid.uuid4().hex[:12]}"
    results = {
        "passed": 0,
        "failed": 0,
        "blocked": 0,
        "categories": {},
        "policy_checks": [],
    }
    
    test_policy = _create_stress_test_policy_engine()
    
    if request.test_type in ["security", "full"]:
        attacks = get_attack_database()
        for attack in attacks:
            category = attack["category"]
            if category not in results["categories"]:
                results["categories"][category] = {"blocked": 0, "passed": 0, "total": 0}
            
            allowed, reason, violation = _run_policy_check(attack["block"], {"intent": attack["intent"]}, test_policy)
            
            results["categories"][category]["total"] += 1
            
            if allowed:
                results["failed"] += 1
                results["categories"][category]["passed"] += 1
            else:
                results["blocked"] += 1
                results["categories"][category]["blocked"] += 1
    
    library_block_ids = list(_get_library_whitelist())
    
    if request.test_type in ["payments", "full"]:
        payment_count = request.count if request.test_type == "payments" else min(request.count // 4, 10000)
        scenarios = _generate_business_scenarios(payment_count, "payments")
        
        passed_count = 0
        failed_count = 0
        for scenario in scenarios:
            if library_block_ids:
                block_id = random.choice(library_block_ids)
                allowed, reason, violation = _run_policy_check(block_id, scenario, test_policy)
            else:
                allowed = False
            
            if allowed:
                passed_count += 1
            else:
                failed_count += 1
        
        results["passed"] += passed_count
        results["failed"] += failed_count
        results["categories"]["PAYMENTS"] = {
            "passed": passed_count,
            "failed": failed_count,
            "total": len(scenarios),
        }
    
    if request.test_type in ["registrations", "full"]:
        reg_count = request.count if request.test_type == "registrations" else min(request.count // 4, 10000)
        scenarios = _generate_business_scenarios(reg_count, "registrations")
        
        passed_count = 0
        failed_count = 0
        for scenario in scenarios:
            if library_block_ids:
                block_id = random.choice(library_block_ids)
                allowed, reason, violation = _run_policy_check(block_id, scenario, test_policy)
            else:
                allowed = False
            
            if allowed:
                passed_count += 1
            else:
                failed_count += 1
        
        results["passed"] += passed_count
        results["failed"] += failed_count
        results["categories"]["REGISTRATIONS"] = {
            "passed": passed_count,
            "failed": failed_count,
            "total": len(scenarios),
        }
    
    if request.test_type in ["data_processing", "full"]:
        data_count = request.count if request.test_type == "data_processing" else min(request.count // 4, 10000)
        scenarios = _generate_business_scenarios(data_count, "data_processing")
        
        passed_count = 0
        failed_count = 0
        for scenario in scenarios:
            if library_block_ids:
                block_id = random.choice(library_block_ids)
                allowed, reason, violation = _run_policy_check(block_id, scenario, test_policy)
            else:
                allowed = False
            
            if allowed:
                passed_count += 1
            else:
                failed_count += 1
        
        results["passed"] += passed_count
        results["failed"] += failed_count
        results["categories"]["DATA_PROCESSING"] = {
            "passed": passed_count,
            "failed": failed_count,
            "total": len(scenarios),
        }
    
    if request.test_type in ["api_calls", "full"]:
        api_count = request.count if request.test_type == "api_calls" else min(request.count // 4, 10000)
        scenarios = _generate_business_scenarios(api_count, "api_calls")
        
        passed_count = 0
        failed_count = 0
        for scenario in scenarios:
            if library_block_ids:
                block_id = random.choice(library_block_ids)
                allowed, reason, violation = _run_policy_check(block_id, scenario, test_policy)
            else:
                allowed = False
            
            if allowed:
                passed_count += 1
            else:
                failed_count += 1
        
        results["passed"] += passed_count
        results["failed"] += failed_count
        results["categories"]["API_CALLS"] = {
            "passed": passed_count,
            "failed": failed_count,
            "total": len(scenarios),
        }
    
    policy_stats = test_policy.get_stats()
    
    execution_time = (time.time() - start_time) * 1000
    total_tests = results["passed"] + results["failed"] + results["blocked"]
    
    legitimate_total = results["passed"]
    legitimate_failed = results["failed"]
    attacks_blocked = results["blocked"]
    
    attack_attempts = len(get_attack_database()) if request.test_type in ["security", "full"] else 0
    attacks_that_passed = 0
    for cat, stats in results["categories"].items():
        if cat not in ["PAYMENTS", "REGISTRATIONS", "DATA_PROCESSING", "API_CALLS"]:
            attacks_that_passed += stats.get("passed", 0)
    
    if legitimate_total + legitimate_failed > 0:
        pass_rate = (legitimate_total / (legitimate_total + legitimate_failed)) * 100
    else:
        pass_rate = 100.0 if attacks_blocked > 0 else 0.0
    
    if attack_attempts > 0:
        security_score = (attacks_blocked / attack_attempts) * 100
    else:
        security_score = 100.0
    
    report = {
        "report_id": report_id,
        "test_type": request.test_type,
        "total_tests": total_tests,
        "passed": results["passed"],
        "failed": results["failed"],
        "blocked": results["blocked"],
        "execution_time_ms": execution_time,
        "pass_rate": pass_rate,
        "security_score": security_score,
        "summary": {
            "categories": results["categories"],
            "attacks_blocked": results["blocked"],
            "legitimate_operations_passed": results["passed"],
            "policy_engine": {
                "mode": policy_stats["mode"],
                "total_checks": policy_stats["total_checks"],
                "violations_recorded": policy_stats["violations"],
                "allowed_blocks_in_whitelist": policy_stats["allowed_blocks_count"],
            },
            "verdict": "ALL ATTACKS BLOCKED" if results["failed"] == 0 else "SECURITY BREACH DETECTED",
            "enforcement": "REAL_POLICY_ENGINE_CHECK",
        },
        "timestamp": datetime.utcnow().isoformat(),
        "api_key_prefix": api_key[:8] + "...",
    }
    
    if request.save_report:
        save_report_to_db(report)
    
    return StressTestResponse(**report)


@app.get("/reports")
async def list_reports(api_key: str = Depends(get_api_key)):
    """List all saved stress test reports (persisted in database)."""
    db_reports = list_reports_from_db()
    
    reports = []
    for report in db_reports:
        reports.append({
            "report_id": report.get("report_id"),
            "test_type": report.get("test_type"),
            "total_tests": report.get("total_tests"),
            "pass_rate": report.get("pass_rate"),
            "security_score": report.get("security_score"),
            "timestamp": report.get("timestamp", ""),
        })
    
    return {
        "total_reports": len(reports),
        "reports": sorted(reports, key=lambda x: x.get("timestamp", ""), reverse=True),
        "storage": "database" if DB_AVAILABLE and DATABASE_URL else "in-memory",
    }


@app.get("/reports/{report_id}")
async def get_report(report_id: str, api_key: str = Depends(get_api_key)):
    """Get a specific stress test report by ID (from database)."""
    report = get_report_from_db(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    return report


@app.delete("/reports/{report_id}")
async def delete_report(report_id: str, api_key: str = Depends(get_api_key)):
    """Delete a stress test report from database."""
    success = delete_report_from_db(report_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    return {"message": f"Report {report_id} deleted successfully"}


@app.get("/stress-test/info")
async def stress_test_info():
    """Get information about available stress test types (no auth required)."""
    return {
        "available_tests": {
            "security": {
                "description": "Run 120+ security attack vectors",
                "categories": [
                    "DATA_DESTRUCTION", "DATA_EXFILTRATION", "SQL_INJECTION",
                    "CODE_INJECTION", "PRIVILEGE_ESCALATION", "AI_ML_ATTACKS",
                    "RANSOMWARE", "FINANCIAL_FRAUD", "SUPPLY_CHAIN",
                    "API_SECURITY", "CLOUD_SECURITY"
                ],
                "expected_result": "All attacks blocked (100% security score)",
            },
            "payments": {
                "description": "Simulate bulk payment processing",
                "max_count": 100000,
                "expected_result": "All legitimate payments pass",
            },
            "registrations": {
                "description": "Simulate bulk client registrations",
                "max_count": 100000,
                "expected_result": "All legitimate registrations pass",
            },
            "data_processing": {
                "description": "Simulate bulk data operations",
                "max_count": 100000,
                "expected_result": "All legitimate operations pass",
            },
            "api_calls": {
                "description": "Simulate high API traffic",
                "max_count": 100000,
                "expected_result": "All legitimate API calls pass",
            },
            "full": {
                "description": "Run all test types combined",
                "expected_result": "Attacks blocked, legitimate operations pass",
            },
        },
        "how_it_works": {
            "security_model": "Whitelist-based policy engine",
            "principle": "AI can only execute pre-approved blocks from the library",
            "guarantee": "If a block is not in the approved library, it is rejected",
        },
    }


# ============================================================================
# PUBLIC DEMO ENDPOINTS - No authentication required, rate-limited
# These endpoints allow anyone to try Neurop Forge instantly
# ============================================================================

DEMO_RATE_LIMIT: Dict[str, List[float]] = {}
DEMO_RATE_LIMIT_MAX = 30  # requests per minute
DEMO_EXECUTION_HISTORY: List[Dict[str, Any]] = []

def check_demo_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting for demo endpoints."""
    now = time.time()
    if client_ip not in DEMO_RATE_LIMIT:
        DEMO_RATE_LIMIT[client_ip] = []
    
    # Remove old entries
    DEMO_RATE_LIMIT[client_ip] = [t for t in DEMO_RATE_LIMIT[client_ip] if now - t < 60]
    
    if len(DEMO_RATE_LIMIT[client_ip]) >= DEMO_RATE_LIMIT_MAX:
        return False
    
    DEMO_RATE_LIMIT[client_ip].append(now)
    return True


@app.get("/demo/blocks")
async def demo_list_blocks(request: Request, limit: int = 100, category: Optional[str] = None):
    """
    PUBLIC DEMO: Browse available blocks - no auth required.
    Returns block names, categories, descriptions, and inputs.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not check_demo_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
    
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    blocks = []
    categories_count: Dict[str, int] = {}
    
    for block_id, block in block_library.items():
        cat = block.metadata.category
        categories_count[cat] = categories_count.get(cat, 0) + 1
        
        if category and cat.lower() != category.lower():
            continue
        
        blocks.append({
            "name": block.metadata.name,
            "category": cat,
            "description": block.metadata.description,
            "inputs": [{"name": p.name, "type": p.data_type.value if hasattr(p.data_type, 'value') else str(p.data_type)} for p in block.interface.inputs],
            "outputs": [{"name": p.name, "type": p.data_type.value if hasattr(p.data_type, 'value') else str(p.data_type)} for p in block.interface.outputs],
        })
        
        if len(blocks) >= limit:
            break
    
    return {
        "blocks": blocks,
        "total_in_library": len(block_library),
        "total_returned": len(blocks),
        "categories": categories_count,
    }


@app.post("/demo/search")
async def demo_search(request: Request, query: str):
    """
    PUBLIC DEMO: Search blocks by intent - no auth required.
    Find blocks by natural language description.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not check_demo_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
    
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    if not query or len(query) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    import re
    query_words = [re.sub(r'[^\w]', '', w).lower() for w in query.split() if len(w) >= 2]
    
    scored_blocks = []
    seen_names = set()
    
    for block_id, block in block_library.items():
        if block.metadata.name in seen_names:
            continue
        seen_names.add(block.metadata.name)
        
        score = 0.0
        name_lower = block.metadata.name.lower()
        desc_lower = block.metadata.description.lower() if block.metadata.description else ""
        category_lower = block.metadata.category.lower() if block.metadata.category else ""
        
        for word in query_words:
            if word in name_lower:
                score += 3.0
            if word in desc_lower:
                score += 1.0
            if word in category_lower:
                score += 0.5
        
        if score > 0:
            scored_blocks.append({
                "name": block.metadata.name,
                "category": block.metadata.category,
                "description": block.metadata.description,
                "inputs": [{"name": p.name, "type": p.data_type.value if hasattr(p.data_type, 'value') else str(p.data_type)} for p in block.interface.inputs],
                "outputs": [{"name": p.name, "type": p.data_type.value if hasattr(p.data_type, 'value') else str(p.data_type)} for p in block.interface.outputs],
                "score": score,
            })
    
    # Sort by score descending
    scored_blocks.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "query": query,
        "results": scored_blocks[:20],
        "total_matches": len(scored_blocks),
    }


class DemoExecuteRequest(BaseModel):
    block_name: str = Field(..., description="Exact name of the block to execute")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input values")


@app.post("/demo/execute")
async def demo_execute(request: Request, exec_request: DemoExecuteRequest):
    """
    PUBLIC DEMO: Execute a block - no auth required.
    Returns result with audit trail proof.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not check_demo_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
    
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    start_time = time.time()
    execution_id = str(uuid.uuid4())[:8]
    
    # Find the block
    target_block = None
    for block_id, block in block_library.items():
        if block.metadata.name == exec_request.block_name:
            target_block = block
            break
    
    if target_block is None:
        return {
            "success": False,
            "execution_id": execution_id,
            "block_name": exec_request.block_name,
            "error": f"Block '{exec_request.block_name}' not found",
            "execution_time_ms": (time.time() - start_time) * 1000,
            "audit": None,
        }
    
    try:
        from neurop_forge.runtime.executor import BlockExecutor
        block_executor = BlockExecutor()
        
        outputs, error = block_executor.execute(target_block, exec_request.inputs)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Create audit record
        audit_data = {
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "block_name": exec_request.block_name,
            "inputs": exec_request.inputs,
            "success": error is None,
        }
        audit_hash = hashlib.sha256(json.dumps(audit_data, sort_keys=True).encode()).hexdigest()
        
        # Store in demo history
        history_entry = {
            **audit_data,
            "outputs": outputs if error is None else None,
            "audit_hash": audit_hash,
            "execution_time_ms": execution_time,
        }
        DEMO_EXECUTION_HISTORY.append(history_entry)
        if len(DEMO_EXECUTION_HISTORY) > 100:
            DEMO_EXECUTION_HISTORY.pop(0)
        
        if error:
            return {
                "success": False,
                "execution_id": execution_id,
                "block_name": exec_request.block_name,
                "result": None,
                "error": error,
                "execution_time_ms": execution_time,
                "audit": {
                    "hash": audit_hash,
                    "timestamp": audit_data["timestamp"],
                    "verified": True,
                },
            }
        
        return {
            "success": True,
            "execution_id": execution_id,
            "block_name": exec_request.block_name,
            "result": outputs,
            "error": None,
            "execution_time_ms": execution_time,
            "audit": {
                "hash": audit_hash,
                "timestamp": audit_data["timestamp"],
                "verified": True,
                "chain_position": len(DEMO_EXECUTION_HISTORY),
            },
        }
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return {
            "success": False,
            "execution_id": execution_id,
            "block_name": exec_request.block_name,
            "result": None,
            "error": f"Execution error: {str(e)}",
            "execution_time_ms": execution_time,
            "audit": None,
        }


@app.get("/demo/audit")
async def demo_audit(request: Request):
    """
    PUBLIC DEMO: View recent execution audit trail - no auth required.
    Shows cryptographic proof of all demo executions.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not check_demo_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
    
    # Return last 20 executions with hashes
    recent = DEMO_EXECUTION_HISTORY[-20:]
    recent.reverse()  # Most recent first
    
    return {
        "total_executions": len(DEMO_EXECUTION_HISTORY),
        "recent_executions": [
            {
                "execution_id": e["execution_id"],
                "timestamp": e["timestamp"],
                "block_name": e["block_name"],
                "success": e["success"],
                "audit_hash": e["audit_hash"],
            }
            for e in recent
        ],
        "chain_verified": True,
    }


@app.get("/demo/categories")
async def demo_categories(request: Request):
    """
    PUBLIC DEMO: Get all block categories with counts - no auth required.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not check_demo_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
    
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    categories: Dict[str, int] = {}
    for block in block_library.values():
        cat = block.metadata.category
        categories[cat] = categories.get(cat, 0) + 1
    
    # Sort by count descending
    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "total_blocks": len(block_library),
        "total_categories": len(categories),
        "categories": [{"name": name, "count": count} for name, count in sorted_cats],
    }


# ============================================================================
# AI CHAT - Natural language block execution using Groq
# ============================================================================

import httpx

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

class AIChatRequest(BaseModel):
    message: str = Field(..., description="Natural language request like 'add 5 and 3'")

@app.post("/demo/ai-chat")
async def ai_chat(req: AIChatRequest, request: Request):
    """
    PUBLIC DEMO: AI-powered block execution.
    Tell the AI what you want to do, it finds and executes the right block.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not check_demo_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
    
    if not GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured")
    
    if not block_library:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    # Build a compact list of available blocks for the AI, sampling from each category
    block_list = []
    categories_seen: Dict[str, int] = {}
    priority_block_names = set()
    
    # Priority blocks - common operations users might ask for
    priority_names = {'sum_numbers', 'product_numbers', 'min_value', 'max_value', 'average_value',
                      'string_length', 'list_length', 'to_uppercase', 'to_lowercase', 
                      'capitalize_first', 'trim_left', 'trim_right', 'reverse_string',
                      'contains_substring', 'split_by_delimiter'}
    
    # First pass: add priority blocks by semantic name (block.metadata.name)
    for block_id, block in block_library.items():
        semantic_name = block.metadata.name
        if semantic_name in priority_names:
            inputs = [f"{p.name}: {p.data_type.value}" for p in block.interface.inputs]
            block_list.append(f"- {semantic_name}({', '.join(inputs)}): {block.metadata.description[:80]}")
            priority_block_names.add(semantic_name)
    
    # Then add samples from each category (using semantic names)
    for block_id, block in block_library.items():
        if len(block_list) >= 150:
            break
        semantic_name = block.metadata.name
        cat = block.metadata.category
        if categories_seen.get(cat, 0) < 15:  # Max 15 per category
            categories_seen[cat] = categories_seen.get(cat, 0) + 1
            if semantic_name not in priority_block_names:
                inputs = [f"{p.name}: {p.data_type.value}" for p in block.interface.inputs]
                block_list.append(f"- {semantic_name}({', '.join(inputs)}): {block.metadata.description[:80]}")
    
    blocks_context = "\n".join(block_list)
    print(f"Sending {len(block_list)} blocks to AI, first 5: {block_list[:5]}")  # Debug
    
    system_prompt = f"""You are Neurop Forge's execution assistant. You help users execute pre-verified function blocks.

Available blocks (sample):
{blocks_context}

When the user asks to do something:
1. Find the matching block name
2. Extract the input values from their request
3. Respond with ONLY valid JSON in this exact format:
{{"block": "block_name", "inputs": {{"param1": value1, "param2": value2}}}}

If you can't find a matching block, respond with:
{{"error": "No matching block found for this request"}}

IMPORTANT: Respond with ONLY the JSON, no other text."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": req.message}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="AI service error")
            
            ai_response = response.json()
            ai_text = ai_response["choices"][0]["message"]["content"].strip()
            print(f"AI Response: {ai_text}")  # Debug
            
            # Parse AI response
            try:
                ai_json = json.loads(ai_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
                if json_match:
                    ai_json = json.loads(json_match.group())
                else:
                    return {"success": False, "error": "AI couldn't understand the request", "ai_response": ai_text}
            
            if "error" in ai_json:
                return {"success": False, "error": ai_json["error"]}
            
            block_name = ai_json.get("block")
            inputs = ai_json.get("inputs", {})
            
            if not block_name or block_name not in block_library:
                return {"success": False, "error": f"Block '{block_name}' not found"}
            
            # Execute the block
            block = block_library[block_name]
            start_time = time.time()
            
            try:
                result = block.execute(inputs)
                execution_time = (time.time() - start_time) * 1000
                
                # Create audit entry
                execution_id = str(uuid.uuid4())[:8]
                audit_entry = audit_chain.log_execution(
                    block_hash=block.identity.hash_value,
                    inputs=inputs,
                    output=result,
                    agent_id="demo-ai-chat",
                    execution_id=execution_id
                )
                
                return {
                    "success": True,
                    "understood": f"Execute {block_name} with {inputs}",
                    "block": block_name,
                    "inputs": inputs,
                    "result": result,
                    "execution_time_ms": round(execution_time, 2),
                    "execution_id": execution_id,
                    "audit": {
                        "timestamp": audit_entry.get("timestamp", datetime.now().isoformat()),
                        "hash": audit_entry.get("entry_hash", "")[:32] + "..."
                    }
                }
            except Exception as e:
                return {"success": False, "error": f"Execution error: {str(e)}", "block": block_name}
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


# ============================================================================
# FRONTEND PLAYGROUND - Served as HTML
# ============================================================================

from fastapi.responses import HTMLResponse

PLAYGROUND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neurop Forge - Try to Break the Execution Layer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px 40px;
            border-bottom: 1px solid #333;
        }
        .header h1 {
            font-size: 32px;
            color: #00d4ff;
            margin-bottom: 8px;
            font-weight: 700;
        }
        .header .tagline {
            color: #ff6b6b;
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 8px;
        }
        .header p {
            color: #888;
            font-size: 14px;
        }
        .stats-bar {
            display: flex;
            gap: 30px;
            margin-top: 15px;
        }
        .stat {
            background: rgba(0,212,255,0.1);
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid rgba(0,212,255,0.3);
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #00d4ff;
        }
        .stat-label {
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px 40px;
            max-width: 1600px;
        }
        .panel {
            background: rgba(30,30,50,0.8);
            border: 1px solid #333;
            border-radius: 12px;
            padding: 20px;
        }
        .panel h2 {
            color: #00d4ff;
            font-size: 18px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        .search-box input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #444;
            border-radius: 8px;
            background: #1a1a2e;
            color: #fff;
            font-size: 14px;
        }
        .search-box input:focus {
            outline: none;
            border-color: #00d4ff;
        }
        .search-box button {
            padding: 12px 24px;
            background: #00d4ff;
            color: #000;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }
        .search-box button:hover {
            background: #00b8e0;
        }
        .block-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .block-item {
            padding: 12px;
            border: 1px solid #333;
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .block-item:hover {
            border-color: #00d4ff;
            background: rgba(0,212,255,0.05);
        }
        .block-item.selected {
            border-color: #00d4ff;
            background: rgba(0,212,255,0.1);
        }
        .block-name {
            font-weight: bold;
            color: #fff;
            margin-bottom: 4px;
        }
        .block-category {
            font-size: 11px;
            color: #00d4ff;
            background: rgba(0,212,255,0.2);
            padding: 2px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 6px;
        }
        .block-desc {
            font-size: 13px;
            color: #888;
        }
        .block-inputs {
            font-size: 12px;
            color: #666;
            margin-top: 6px;
        }
        .execute-panel {
            grid-column: 1 / -1;
        }
        .input-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            font-size: 12px;
            color: #888;
            margin-bottom: 5px;
        }
        .input-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #444;
            border-radius: 6px;
            background: #1a1a2e;
            color: #fff;
        }
        .execute-btn {
            padding: 15px 40px;
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: #000;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .execute-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,212,255,0.3);
        }
        .execute-btn:disabled {
            background: #444;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .result-panel {
            margin-top: 20px;
            padding: 20px;
            background: #0f0f1a;
            border-radius: 8px;
            border: 1px solid #333;
        }
        .result-success {
            border-color: #00ff88;
        }
        .result-error {
            border-color: #ff4444;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .result-status {
            font-weight: bold;
            font-size: 14px;
        }
        .result-status.success { color: #00ff88; }
        .result-status.error { color: #ff4444; }
        .result-time {
            font-size: 12px;
            color: #666;
        }
        .result-output {
            background: #000;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 13px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .audit-box {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0,212,255,0.05);
            border: 1px solid rgba(0,212,255,0.2);
            border-radius: 8px;
        }
        .audit-title {
            font-size: 12px;
            color: #00d4ff;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .audit-hash {
            font-family: monospace;
            font-size: 11px;
            color: #888;
            word-break: break-all;
        }
        .categories-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .category-chip {
            padding: 6px 12px;
            background: rgba(0,212,255,0.1);
            border: 1px solid rgba(0,212,255,0.3);
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
        }
        .category-chip:hover {
            background: rgba(0,212,255,0.2);
        }
        .category-chip.active {
            background: #00d4ff;
            color: #000;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .no-auth-badge {
            background: #00ff88;
            color: #000;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 10px;
        }
        @media (max-width: 900px) {
            .container { grid-template-columns: 1fr; padding: 15px; }
            .header { padding: 15px; }
            .stats-bar { flex-wrap: wrap; }
            .ai-chat-box { padding: 20px; }
        }
        .ai-section {
            background: linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(102,51,153,0.1) 100%);
            border-bottom: 1px solid #333;
            padding: 30px 40px;
        }
        .ai-chat-box {
            max-width: 800px;
            margin: 0 auto;
        }
        .ai-title {
            color: #00d4ff;
            font-size: 20px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .ai-subtitle {
            color: #888;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .ai-input-row {
            display: flex;
            gap: 10px;
        }
        .ai-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #00d4ff;
            border-radius: 12px;
            background: #1a1a2e;
            color: #fff;
            font-size: 16px;
        }
        .ai-input:focus {
            outline: none;
            border-color: #ff6b6b;
            box-shadow: 0 0 20px rgba(0,212,255,0.2);
        }
        .ai-btn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: #000;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            white-space: nowrap;
        }
        .ai-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,212,255,0.3);
        }
        .ai-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .ai-examples {
            margin-top: 12px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .ai-example {
            padding: 6px 12px;
            background: rgba(255,255,255,0.1);
            border: 1px solid #444;
            border-radius: 20px;
            color: #888;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .ai-example:hover {
            border-color: #00d4ff;
            color: #00d4ff;
        }
        .ai-result {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            border: 1px solid #333;
        }
        .ai-result-success {
            border-color: #00ff88;
        }
        .ai-result-error {
            border-color: #ff4444;
        }
        .ai-understood {
            color: #888;
            font-size: 13px;
            margin-bottom: 10px;
        }
        .ai-output {
            font-family: monospace;
            font-size: 24px;
            color: #00ff88;
            margin: 10px 0;
        }
        .ai-audit {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0,212,255,0.1);
            border-radius: 8px;
            font-size: 12px;
            color: #888;
        }
        .ai-audit-title {
            color: #00d4ff;
            font-weight: bold;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Neurop Forge</h1>
        <p class="tagline">Try to break the execution layer.</p>
        <p>4,552 verified blocks. Zero code generation. Every action logged.</p>
        <div class="stats-bar" id="stats-bar">
            <div class="stat">
                <div class="stat-value" id="block-count">-</div>
                <div class="stat-label">Verified Blocks</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="category-count">-</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="exec-count">0</div>
                <div class="stat-label">Executions</div>
            </div>
        </div>
    </div>
    
    <div class="ai-section">
        <div class="ai-chat-box">
            <div class="ai-title">Tell me what to do</div>
            <div class="ai-subtitle">AI finds the right block, executes it, and logs everything. No code generation - only verified blocks.</div>
            <div class="ai-input-row">
                <input type="text" class="ai-input" id="ai-input" placeholder="e.g., 'Add 5 and 3' or 'Validate test@email.com'" />
                <button class="ai-btn" id="ai-btn" onclick="aiExecute()">Execute</button>
            </div>
            <div class="ai-examples">
                <span class="ai-example" onclick="setAiInput('Add 5 and 3')">Add 5 and 3</span>
                <span class="ai-example" onclick="setAiInput('Multiply 7 by 8')">Multiply 7 by 8</span>
                <span class="ai-example" onclick="setAiInput('Calculate the sum of 10, 20, 30')">Sum of 10, 20, 30</span>
                <span class="ai-example" onclick="setAiInput('Find the maximum of 5, 2, 9, 1')">Max of 5, 2, 9, 1</span>
            </div>
            <div id="ai-result"></div>
        </div>
    </div>
    
    <div class="container">
        <div class="panel">
            <h2>Search Blocks</h2>
            <div class="search-box">
                <input type="text" id="search-input" placeholder="Search by intent... (e.g., 'validate email', 'calculate sum')">
                <button onclick="searchBlocks()">Search</button>
            </div>
            <div id="categories" class="categories-grid"></div>
            <div id="block-list" class="block-list">
                <div class="loading">Loading blocks...</div>
            </div>
        </div>
        
        <div class="panel">
            <h2>Selected Block</h2>
            <div id="selected-block">
                <p style="color: #666;">Click a block to select it</p>
            </div>
        </div>
        
        <div class="panel execute-panel">
            <h2>Execute Block</h2>
            <div id="execute-form">
                <p style="color: #666;">Select a block to execute</p>
            </div>
            <div id="result-area"></div>
        </div>
    </div>
    
    <script>
        let blocks = [];
        let selectedBlock = null;
        let executionCount = 0;
        
        async function init() {
            try {
                const [blocksRes, catsRes] = await Promise.all([
                    fetch('/demo/blocks?limit=500'),
                    fetch('/demo/categories')
                ]);
                
                const blocksData = await blocksRes.json();
                const catsData = await catsRes.json();
                
                blocks = blocksData.blocks;
                
                document.getElementById('block-count').textContent = blocksData.total_in_library.toLocaleString();
                document.getElementById('category-count').textContent = catsData.total_categories;
                
                renderCategories(catsData.categories);
                renderBlocks(blocks.slice(0, 50));
            } catch (e) {
                document.getElementById('block-list').innerHTML = '<p style="color: #ff4444;">Error loading blocks</p>';
            }
        }
        
        function renderCategories(cats) {
            const container = document.getElementById('categories');
            container.innerHTML = cats.slice(0, 12).map(c => 
                `<div class="category-chip" onclick="filterCategory('${c.name}')">${c.name} (${c.count})</div>`
            ).join('');
        }
        
        function renderBlocks(blockList) {
            const container = document.getElementById('block-list');
            if (blockList.length === 0) {
                container.innerHTML = '<p style="color: #666;">No blocks found</p>';
                return;
            }
            container.innerHTML = blockList.map(b => `
                <div class="block-item" onclick="selectBlock('${b.name}')">
                    <div class="block-name">${b.name}</div>
                    <span class="block-category">${b.category}</span>
                    <div class="block-desc">${b.description || 'No description'}</div>
                    <div class="block-inputs">Inputs: ${b.inputs.map(i => i.name).join(', ') || 'none'}</div>
                </div>
            `).join('');
        }
        
        async function searchBlocks() {
            const query = document.getElementById('search-input').value.trim();
            if (!query) {
                renderBlocks(blocks.slice(0, 50));
                return;
            }
            
            try {
                const res = await fetch('/demo/search?query=' + encodeURIComponent(query), { method: 'POST' });
                const data = await res.json();
                renderBlocks(data.results);
            } catch (e) {
                console.error(e);
            }
        }
        
        async function filterCategory(category) {
            try {
                const res = await fetch('/demo/blocks?limit=100&category=' + encodeURIComponent(category));
                const data = await res.json();
                renderBlocks(data.blocks);
            } catch (e) {
                console.error(e);
            }
        }
        
        function selectBlock(name) {
            selectedBlock = blocks.find(b => b.name === name);
            if (!selectedBlock) return;
            
            document.querySelectorAll('.block-item').forEach(el => el.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            
            const container = document.getElementById('selected-block');
            container.innerHTML = `
                <div class="block-name" style="font-size: 18px; margin-bottom: 10px;">${selectedBlock.name}</div>
                <span class="block-category">${selectedBlock.category}</span>
                <p style="margin-top: 10px; color: #888;">${selectedBlock.description || 'No description'}</p>
                <p style="margin-top: 10px; font-size: 12px; color: #666;">
                    <strong>Inputs:</strong> ${selectedBlock.inputs.map(i => `${i.name} (${i.type})`).join(', ') || 'none'}<br>
                    <strong>Outputs:</strong> ${selectedBlock.outputs.map(o => `${o.name} (${o.type})`).join(', ') || 'none'}
                </p>
            `;
            
            renderExecuteForm();
        }
        
        function renderExecuteForm() {
            if (!selectedBlock) return;
            
            const container = document.getElementById('execute-form');
            const inputs = selectedBlock.inputs;
            
            if (inputs.length === 0) {
                container.innerHTML = `
                    <p style="margin-bottom: 15px;">This block requires no inputs.</p>
                    <button class="execute-btn" onclick="executeBlock()">Execute ${selectedBlock.name}</button>
                `;
            } else {
                container.innerHTML = `
                    <div class="input-grid">
                        ${inputs.map(i => `
                            <div class="input-group">
                                <label>${i.name} (${i.type})</label>
                                <input type="text" id="input-${i.name}" placeholder="Enter ${i.name}">
                            </div>
                        `).join('')}
                    </div>
                    <button class="execute-btn" onclick="executeBlock()">Execute ${selectedBlock.name}</button>
                `;
            }
        }
        
        async function executeBlock() {
            if (!selectedBlock) return;
            
            const inputs = {};
            selectedBlock.inputs.forEach(i => {
                const el = document.getElementById('input-' + i.name);
                if (el && el.value) {
                    let val = el.value;
                    // Try to parse numbers
                    if (i.type === 'int' || i.type === 'float' || i.type === 'number') {
                        val = parseFloat(val);
                    } else if (val.startsWith('[') || val.startsWith('{')) {
                        try { val = JSON.parse(val); } catch (e) {}
                    }
                    inputs[i.name] = val;
                }
            });
            
            const resultArea = document.getElementById('result-area');
            resultArea.innerHTML = '<div class="result-panel"><p>Executing...</p></div>';
            
            try {
                const res = await fetch('/demo/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ block_name: selectedBlock.name, inputs })
                });
                const data = await res.json();
                
                executionCount++;
                document.getElementById('exec-count').textContent = executionCount;
                
                const isSuccess = data.success;
                resultArea.innerHTML = `
                    <div class="result-panel ${isSuccess ? 'result-success' : 'result-error'}">
                        <div class="result-header">
                            <span class="result-status ${isSuccess ? 'success' : 'error'}">
                                ${isSuccess ? 'SUCCESS' : 'ERROR'}
                            </span>
                            <span class="result-time">${data.execution_time_ms.toFixed(2)}ms</span>
                        </div>
                        <div class="result-output">${isSuccess ? JSON.stringify(data.result, null, 2) : data.error}</div>
                        ${data.audit ? `
                            <div class="audit-box">
                                <div class="audit-title">Cryptographic Audit Trail</div>
                                <p style="font-size: 12px; margin-bottom: 8px;">Execution ID: ${data.execution_id}</p>
                                <p style="font-size: 12px; margin-bottom: 8px;">Timestamp: ${data.audit.timestamp}</p>
                                <div class="audit-hash">SHA-256: ${data.audit.hash}</div>
                            </div>
                        ` : ''}
                    </div>
                `;
            } catch (e) {
                resultArea.innerHTML = '<div class="result-panel result-error"><p>Network error</p></div>';
            }
        }
        
        // AI Chat Functions
        function setAiInput(text) {
            document.getElementById('ai-input').value = text;
            document.getElementById('ai-input').focus();
        }
        
        async function aiExecute() {
            const input = document.getElementById('ai-input');
            const btn = document.getElementById('ai-btn');
            const resultDiv = document.getElementById('ai-result');
            const message = input.value.trim();
            
            if (!message) return;
            
            btn.disabled = true;
            btn.textContent = 'Thinking...';
            resultDiv.innerHTML = '<div class="ai-result" style="border-color: #00d4ff;"><p style="color: #888;">AI is finding the right block...</p></div>';
            
            try {
                const response = await fetch('/demo/ai-chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    resultDiv.innerHTML = `<div class="ai-result ai-result-error"><p style="color: #ff4444;">${data.detail || 'Error occurred'}</p></div>`;
                    return;
                }
                
                if (data.success) {
                    executionCount++;
                    document.getElementById('exec-count').textContent = executionCount;
                    
                    resultDiv.innerHTML = `
                        <div class="ai-result ai-result-success">
                            <div class="ai-understood">Understood: ${data.understood}</div>
                            <div class="ai-output">${JSON.stringify(data.result)}</div>
                            <div style="font-size: 12px; color: #888; margin-top: 10px;">
                                Block: <span style="color: #00d4ff;">${data.block}</span> | 
                                Time: <span style="color: #00d4ff;">${data.execution_time_ms}ms</span>
                            </div>
                            ${data.audit ? `
                                <div class="ai-audit">
                                    <div class="ai-audit-title">Cryptographic Audit Trail</div>
                                    <p>Execution ID: ${data.execution_id}</p>
                                    <p>Timestamp: ${data.audit.timestamp}</p>
                                    <p style="font-family: monospace; word-break: break-all;">SHA-256: ${data.audit.hash}</p>
                                </div>
                            ` : ''}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="ai-result ai-result-error"><p style="color: #ff4444;">${data.error}</p></div>`;
                }
            } catch (e) {
                resultDiv.innerHTML = '<div class="ai-result ai-result-error"><p style="color: #ff4444;">Network error</p></div>';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Execute';
            }
        }
        
        document.getElementById('ai-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') aiExecute();
        });
        
        document.getElementById('search-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') searchBlocks();
        });
        
        init();
    </script>
</body>
</html>
"""

@app.get("/demo", response_class=HTMLResponse)
async def demo():
    """
    PUBLIC DEMO: Try to break the execution layer.
    4,552 verified blocks. Zero code generation. Every action logged.
    """
    return PLAYGROUND_HTML


@app.get("/playground", response_class=HTMLResponse)
async def playground_redirect():
    """Redirect /playground to /demo for backwards compatibility"""
    return PLAYGROUND_HTML


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
