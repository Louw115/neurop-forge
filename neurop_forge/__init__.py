"""
Neurop Block Forge - Production-grade semantic block composition engine.

Provides 2,060+ verified Tier-A deterministic blocks for reliable execution.

Quick Start:
    from neurop_forge import NeuropForge
    
    forge = NeuropForge()
    result = forge.execute_block("reverse_string", {"s": "hello"})
    print(result)  # {'result': 'olleh', 'success': True}

Or use convenience functions:
    from neurop_forge import execute_block, run_workflow, list_blocks
    
    result = execute_block("to_uppercase", {"s": "hello"})
    workflow = run_workflow("text_normalization", {"text": "Hello World"})
    blocks = list_blocks(category="string", tier="A")
"""

__version__ = "1.0.0"
__author__ = "Neurop Project"

from neurop_forge.api import (
    NeuropForge,
    execute_block,
    run_workflow,
    list_blocks
)

__all__ = [
    "NeuropForge",
    "execute_block",
    "run_workflow", 
    "list_blocks",
    "__version__"
]
