"""
Neurop Forge SDK - Thin Python client for the Neurop Forge API.

Usage:
    from neuropforge import NeuropForge
    
    client = NeuropForge(api_key="your_key")
    result = client.execute("to_uppercase", text="hello world")
    print(result)  # "HELLO WORLD"
"""
from .client import NeuropForge, NeuropForgeError, BlockNotFoundError, ExecutionError

__version__ = "1.0.0"
__all__ = ["NeuropForge", "NeuropForgeError", "BlockNotFoundError", "ExecutionError"]
