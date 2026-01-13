"""
Regression tests for Neurop Forge API endpoints.
These tests ensure core functionality remains stable.
"""
import pytest
import httpx
import os

BASE_URL = os.environ.get("NEUROP_API_URL", "http://localhost:5000")
API_KEY = os.environ.get("NEUROP_API_KEY", "demo_test_key")


class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    def test_root_health(self):
        """Root endpoint returns healthy status."""
        response = httpx.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["library_loaded"] is True
        assert data["block_count"] > 4000
    
    def test_health_endpoint(self):
        """Health endpoint returns healthy status."""
        response = httpx.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["library_loaded"] is True


class TestBlocksEndpoint:
    """Test /blocks endpoint."""
    
    def test_list_blocks_requires_auth(self):
        """Blocks endpoint requires API key."""
        response = httpx.get(f"{BASE_URL}/blocks")
        assert response.status_code == 401
    
    def test_list_blocks_with_auth(self):
        """Blocks endpoint returns blocks with valid key."""
        response = httpx.get(
            f"{BASE_URL}/blocks",
            headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "blocks" in data
        assert len(data["blocks"]) > 0
        assert "name" in data["blocks"][0]
        assert "category" in data["blocks"][0]
    
    def test_list_blocks_with_limit(self):
        """Blocks endpoint respects limit parameter."""
        response = httpx.get(
            f"{BASE_URL}/blocks?limit=5",
            headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["blocks"]) == 5


class TestSearchEndpoint:
    """Test /search endpoint."""
    
    def test_search_requires_auth(self):
        """Search endpoint requires API key."""
        response = httpx.post(
            f"{BASE_URL}/search",
            json={"query": "validate email"}
        )
        assert response.status_code == 401
    
    def test_search_finds_blocks(self):
        """Search returns relevant blocks."""
        response = httpx.post(
            f"{BASE_URL}/search",
            headers={"X-API-Key": API_KEY},
            json={"query": "validate email", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "blocks" in data
        assert len(data["blocks"]) > 0
        names = [b["name"] for b in data["blocks"]]
        assert any("email" in name.lower() for name in names)


class TestExecuteBlockEndpoint:
    """Test /execute-block endpoint - the primary endpoint."""
    
    def test_execute_requires_auth(self):
        """Execute endpoint requires API key."""
        response = httpx.post(
            f"{BASE_URL}/execute-block",
            json={"block_name": "to_uppercase", "inputs": {"text": "hello"}}
        )
        assert response.status_code == 401
    
    def test_execute_to_uppercase(self):
        """Execute to_uppercase block."""
        response = httpx.post(
            f"{BASE_URL}/execute-block",
            headers={"X-API-Key": API_KEY},
            json={"block_name": "to_uppercase", "inputs": {"text": "hello world"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["result"] == "HELLO WORLD"
    
    def test_execute_to_lowercase(self):
        """Execute to_lowercase block."""
        response = httpx.post(
            f"{BASE_URL}/execute-block",
            headers={"X-API-Key": API_KEY},
            json={"block_name": "to_lowercase", "inputs": {"text": "HELLO WORLD"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["result"] == "hello world"
    
    def test_execute_string_length(self):
        """Execute string_length block."""
        response = httpx.post(
            f"{BASE_URL}/execute-block",
            headers={"X-API-Key": API_KEY},
            json={"block_name": "string_length", "inputs": {"text": "Neurop Forge"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["result"] == 12
    
    def test_execute_nonexistent_block(self):
        """Nonexistent block returns error with helpful info."""
        response = httpx.post(
            f"{BASE_URL}/execute-block",
            headers={"X-API-Key": API_KEY},
            json={"block_name": "fake_block_xyz", "inputs": {}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"].lower()
        assert "debug_info" in data
    
    def test_execute_deterministic(self):
        """Same inputs always produce same outputs."""
        for _ in range(3):
            response = httpx.post(
                f"{BASE_URL}/execute-block",
                headers={"X-API-Key": API_KEY},
                json={"block_name": "to_uppercase", "inputs": {"text": "test123"}}
            )
            data = response.json()
            assert data["success"] is True
            assert data["result"]["result"] == "TEST123"


class TestAuditEndpoint:
    """Test /audit/chain endpoint."""
    
    def test_audit_chain_requires_auth(self):
        """Audit endpoint requires API key."""
        response = httpx.get(f"{BASE_URL}/audit/chain")
        assert response.status_code == 401
    
    def test_audit_chain_returns_info(self):
        """Audit chain returns verification info."""
        response = httpx.get(
            f"{BASE_URL}/audit/chain",
            headers={"X-API-Key": API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "chain_hash" in data
        assert "event_count" in data
        assert "integrity_valid" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
