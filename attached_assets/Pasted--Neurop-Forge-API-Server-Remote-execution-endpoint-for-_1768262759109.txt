"""
Neurop Forge API Server
Remote execution endpoint for the 2,700+ block library.
AI agents call this API to execute verified blocks without owning the library.
"""

import os
import json
import hashlib
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from neurop_forge.semantic.composer import SemanticComposer, SemanticIndexEntry
from neurop_forge.semantic.intent_schema import SemanticIntent, SemanticDomain, SemanticOperation, SemanticType
from neurop_forge.runtime.executor import GraphExecutor
from neurop_forge.core.block_schema import NeuropBlock, PurityLevel
from neurop_forge.compliance.audit_chain import AuditChain
from neurop_forge.compliance.policy_engine import PolicyEngine

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

composer: Optional[SemanticComposer] = None
executor: Optional[GraphExecutor] = None
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


def safe_get_operation(op_str: str) -> SemanticOperation:
    """Get SemanticOperation with fallback for unknown values."""
    op_mapping = {
        "process": SemanticOperation.TRANSFORM,
        "execute": SemanticOperation.TRANSFORM,
        "run": SemanticOperation.TRANSFORM,
        "apply": SemanticOperation.TRANSFORM,
        "compute": SemanticOperation.CALCULATE,
        "validate": SemanticOperation.VALIDATE,
        "check": SemanticOperation.CHECK,
    }
    try:
        return SemanticOperation(op_str)
    except ValueError:
        return op_mapping.get(op_str, SemanticOperation.TRANSFORM)


def safe_get_domain(domain_str: str) -> SemanticDomain:
    """Get SemanticDomain with fallback for unknown values."""
    try:
        return SemanticDomain(domain_str)
    except ValueError:
        return SemanticDomain.UTILITY


def safe_get_semantic_type(type_str: str) -> SemanticType:
    """Get SemanticType with fallback for unknown values."""
    try:
        return SemanticType(type_str)
    except ValueError:
        return SemanticType.GENERIC


def load_library():
    """Load the block library from disk."""
    global composer, executor, audit_chain, policy_engine, block_library
    
    if not LIBRARY_PATH.exists():
        print(f"Library path {LIBRARY_PATH} does not exist")
        return False
    
    composer = SemanticComposer()
    executor = GraphExecutor()
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
            executor.register_block(block_id, block)
            
            category = block.metadata.category.lower()
            
            category_to_domain = {
                "validation": "validation",
                "arithmetic": "calculation",
                "string": "string",
                "collection": "collection",
                "filtering": "filtering",
                "transformation": "transformation",
                "sorting": "sorting",
                "aggregation": "aggregation",
                "comparison": "comparison",
                "encoding": "encoding",
                "hashing": "hashing",
                "datetime": "datetime",
                "numeric": "numeric",
                "utility": "utility",
            }
            
            category_to_operation = {
                "validation": "validate",
                "arithmetic": "calculate",
                "string": "transform",
                "collection": "transform",
                "filtering": "filter",
                "transformation": "transform",
                "sorting": "sort",
                "aggregation": "reduce",
                "comparison": "compare",
                "encoding": "encode",
                "hashing": "hash",
            }
            
            domain_str = category_to_domain.get(category, "utility")
            operation_str = category_to_operation.get(category, "transform")
            
            semantic_intent = SemanticIntent(
                domain=safe_get_domain(domain_str),
                operation=safe_get_operation(operation_str),
                input_semantic_types=(SemanticType.GENERIC,),
                output_semantic_types=(SemanticType.GENERIC,),
                preconditions=tuple(block_data.get("validation_rules", {}).get("preconditions", [])),
                postconditions=tuple(block_data.get("validation_rules", {}).get("postconditions", [])),
                can_chain_from=tuple(block_data.get("composition", {}).get("input_compatible_types", [])),
                can_chain_to=tuple(block_data.get("composition", {}).get("output_compatible_types", [])),
            )
            
            entry = SemanticIndexEntry(
                block_identity=block_id,
                name=block.metadata.name,
                description=block.metadata.description,
                category=block.metadata.category,
                semantic_intent=semantic_intent,
                input_data_types=tuple(p.data_type.value for p in block.interface.inputs),
                output_data_types=tuple(p.data_type.value for p in block.interface.outputs),
                trust_score=block_data.get("trust_tier", {}).get("score", 0.8),
                is_pure=block.constraints.purity == PurityLevel.PURE,
                is_deterministic=block.constraints.deterministic,
            )
            
            composer.index_block(entry)
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


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        library_loaded=composer is not None and len(block_library) > 0,
        block_count=len(block_library),
        version="2.0.0",
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        library_loaded=composer is not None and len(block_library) > 0,
        block_count=len(block_library),
        version="2.0.0",
    )


@app.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest, api_key: str = Depends(get_api_key)):
    """
    Execute a block workflow based on natural language intent.
    
    The AI agent describes what it wants to do, we find the right blocks,
    compose them, execute, and return results with full audit trail.
    """
    start_time = time.time()
    
    if composer is None or executor is None:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    try:
        graph = composer.compose(
            query=request.query,
            min_trust=request.options.get("min_trust", 0.2) if request.options else 0.2,
            max_nodes=request.options.get("max_nodes", 10) if request.options else 10,
        )
        
        if not graph.nodes:
            execution_time = (time.time() - start_time) * 1000
            log_usage(api_key, "/execute", request.query, False, execution_time)
            return ExecuteResponse(
                success=False,
                execution_id=hashlib.sha256(f"{time.time()}{request.query}".encode()).hexdigest()[:16],
                result=None,
                audit_hash="no_blocks_found",
                blocks_used=[],
                execution_time_ms=execution_time,
                error="No matching blocks found for query",
            )
        
        result = executor.execute(graph, initial_inputs=request.inputs)
        
        if audit_chain:
            audit_chain.log_execution(
                block_name=graph.nodes[0].block_name if graph.nodes else "unknown",
                inputs=request.inputs,
                outputs=result.final_outputs,
                success=result.is_success,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            audit_hash = audit_chain.last_hash
        else:
            audit_hash = hashlib.sha256(f"{result.execution_id}".encode()).hexdigest()[:32]
        
        execution_time = (time.time() - start_time) * 1000
        log_usage(api_key, "/execute", request.query, result.is_success, execution_time)
        
        return ExecuteResponse(
            success=result.is_success,
            execution_id=result.execution_id,
            result=result.final_outputs if result.is_success else None,
            audit_hash=audit_hash,
            blocks_used=[n.block_name for n in graph.nodes],
            execution_time_ms=execution_time,
            error=result.error if not result.is_success else None,
        )
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        log_usage(api_key, "/execute", request.query, False, execution_time)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, api_key: str = Depends(get_api_key)):
    """
    Search for blocks by natural language query.
    
    Returns matching blocks with their metadata (but not the actual code).
    """
    if composer is None:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    try:
        graph = composer.compose(
            query=request.query,
            min_trust=request.min_trust,
            max_nodes=request.limit,
        )
        
        blocks = []
        for node in graph.nodes:
            blocks.append({
                "name": node.block_name,
                "domain": node.semantic_intent.domain.value,
                "operation": node.semantic_intent.operation.value,
                "why_selected": node.why_selected,
            })
        
        log_usage(api_key, "/search", request.query, True, 0)
        
        return SearchResponse(
            blocks=blocks,
            total_found=len(blocks),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def stats(api_key: str = Depends(get_api_key)):
    """Get library and usage statistics."""
    if composer is None:
        raise HTTPException(status_code=503, detail="Library not loaded")
    
    composer_stats = composer.get_statistics()
    
    return {
        "library": {
            "total_blocks": len(block_library),
            **composer_stats,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
