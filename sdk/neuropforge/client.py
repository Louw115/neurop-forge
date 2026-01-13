"""
Neurop Forge API Client.

A thin wrapper around the Neurop Forge hosted API for deterministic
block execution with full audit trail.
"""
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import httpx


class NeuropForgeError(Exception):
    """Base exception for Neurop Forge errors."""
    pass


class BlockNotFoundError(NeuropForgeError):
    """Raised when a block doesn't exist."""
    pass


class ExecutionError(NeuropForgeError):
    """Raised when block execution fails."""
    pass


class AuthenticationError(NeuropForgeError):
    """Raised when API key is invalid."""
    pass


@dataclass
class BlockInfo:
    """Information about a block."""
    name: str
    category: str
    description: str
    inputs: List[str]


@dataclass
class ExecutionResult:
    """Result of block execution."""
    success: bool
    block_name: str
    result: Any
    execution_time_ms: float
    block_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class SearchResult:
    """Result of block search."""
    name: str
    domain: str
    operation: str
    why_selected: str


class NeuropForge:
    """
    Neurop Forge API Client.
    
    Provides deterministic execution of pre-verified, hash-locked function blocks.
    AI agents can search, compose, and execute blocks - but never modify them.
    
    Args:
        api_key: Your Neurop Forge API key. Defaults to NEUROP_API_KEY env var.
        base_url: API base URL. Defaults to production API.
        timeout: Request timeout in seconds. Default 30.
    
    Example:
        >>> client = NeuropForge(api_key="demo_my_key")
        >>> result = client.execute("to_uppercase", text="hello")
        >>> print(result.result)  # "HELLO"
    """
    
    DEFAULT_URL = "https://neurop-forge.onrender.com"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0
    ):
        self.api_key = api_key or os.environ.get("NEUROP_API_KEY")
        if not self.api_key:
            raise NeuropForgeError(
                "API key required. Pass api_key or set NEUROP_API_KEY env var."
            )
        
        self.base_url = (base_url or os.environ.get("NEUROP_API_URL") or self.DEFAULT_URL).rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key},
            timeout=timeout
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def health(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Dict with status, library_loaded, block_count, version.
        """
        response = self._client.get("/health")
        return response.json()
    
    def execute(self, block_name: str, **inputs) -> ExecutionResult:
        """
        Execute a block by exact name.
        
        This is the primary method. AI agents call blocks by exact name
        for deterministic, auditable execution.
        
        Args:
            block_name: Exact name of the block to execute.
            **inputs: Keyword arguments for block inputs.
        
        Returns:
            ExecutionResult with success status and result.
        
        Raises:
            BlockNotFoundError: If block doesn't exist.
            ExecutionError: If execution fails.
            AuthenticationError: If API key is invalid.
        
        Example:
            >>> result = client.execute("to_uppercase", text="hello")
            >>> result.result  # "HELLO"
        """
        response = self._client.post(
            "/execute-block",
            json={"block_name": block_name, "inputs": inputs}
        )
        
        if response.status_code == 401:
            raise AuthenticationError("Missing API key")
        if response.status_code == 403:
            raise AuthenticationError("Invalid API key")
        
        data = response.json()
        
        if not data.get("success"):
            error = data.get("error", "Unknown error")
            if "not found" in error.lower():
                raise BlockNotFoundError(f"Block '{block_name}' not found")
            raise ExecutionError(error)
        
        return ExecutionResult(
            success=True,
            block_name=block_name,
            result=data["result"].get("result"),
            execution_time_ms=data.get("execution_time_ms", 0),
            block_id=data.get("debug_info", {}).get("block_id")
        )
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search for blocks by natural language query.
        
        Use this for discovery only. For production, call blocks by exact name.
        
        Args:
            query: Natural language description of what you need.
            limit: Maximum results to return.
        
        Returns:
            List of SearchResult with matching blocks.
        """
        response = self._client.post(
            "/search",
            json={"query": query, "limit": limit}
        )
        
        if response.status_code == 401:
            raise AuthenticationError("Missing API key")
        if response.status_code == 403:
            raise AuthenticationError("Invalid API key")
        
        data = response.json()
        return [
            SearchResult(
                name=b["name"],
                domain=b.get("domain", ""),
                operation=b.get("operation", ""),
                why_selected=b.get("why_selected", "")
            )
            for b in data.get("blocks", [])
        ]
    
    def list_blocks(self, limit: int = 50, category: Optional[str] = None) -> List[BlockInfo]:
        """
        List available blocks.
        
        Args:
            limit: Maximum blocks to return.
            category: Filter by category (e.g., "validation", "string").
        
        Returns:
            List of BlockInfo objects.
        """
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        response = self._client.get("/blocks", params=params)
        
        if response.status_code == 401:
            raise AuthenticationError("Missing API key")
        if response.status_code == 403:
            raise AuthenticationError("Invalid API key")
        
        data = response.json()
        return [
            BlockInfo(
                name=b["name"],
                category=b["category"],
                description=b["description"],
                inputs=b["inputs"]
            )
            for b in data.get("blocks", [])
        ]
    
    def stats(self) -> Dict[str, Any]:
        """
        Get library and usage statistics.
        
        Returns:
            Dict with library stats, usage metrics, and version.
        """
        response = self._client.get("/stats")
        
        if response.status_code == 401:
            raise AuthenticationError("Missing API key")
        if response.status_code == 403:
            raise AuthenticationError("Invalid API key")
        
        return response.json()
    
    def audit_chain(self) -> Dict[str, Any]:
        """
        Get audit chain for verification.
        
        Returns:
            Dict with chain_hash, event_count, integrity_valid.
        """
        response = self._client.get("/audit/chain")
        
        if response.status_code == 401:
            raise AuthenticationError("Missing API key")
        if response.status_code == 403:
            raise AuthenticationError("Invalid API key")
        
        return response.json()
