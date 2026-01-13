# Neurop Forge
## For Platform Teams & AI Developers

---

### What It Is

An immutable function library for AI agents. 4,500+ verified blocks that AI can search, compose, and execute — but never modify.

```python
from neurop_forge import NeuropForge

forge = NeuropForge()
result = forge.execute_block("reverse_string", {"s": "hello"})
# {'result': 'olleh', 'success': True}
```

The AI used a block. It wrote zero code.

---

### Why It Matters

When AI generates code, you get:
- Non-deterministic outputs
- No execution trace
- Hard-to-audit behavior
- Rollback nightmares

When AI executes verified blocks:
- Deterministic results
- Full trace on every run
- Auditable by design
- Hash-locked immutability

---

### Trust Tiers

| Tier | Count | Description | AI Access |
|------|-------|-------------|-----------|
| A | 4,400+ | Pure, deterministic, no side effects | Unrestricted |
| B | ~60 | Context-dependent, complex inputs | Opt-in only |

```python
# Tier-A only (default, safe)
result = forge.execute_block("to_uppercase", {"s": "hi"})

# Tier-B allowed (explicit)
result = forge.execute_block("parse_config", {"path": "/app/config.yaml"}, tier_a_only=False)
```

---

### Installation

```bash
pip install neurop-forge
```

---

### API

```python
from neurop_forge import NeuropForge, execute_block, run_workflow, list_verified_blocks

# Initialize
forge = NeuropForge()

# Execute a block
forge.execute_block("block_id", {"param": "value"})

# Run a composed workflow
forge.run_workflow("workflow_id", {"input": "data"})

# List blocks by category/tier
forge.list_verified_blocks(category="string", tier="A", limit=10)

# Library stats
forge.stats
# {'total_verified': 4552, 'tier_a': 4489, 'tier_b': 63}
```

---

### CLI

```bash
neurop-forge stats                                    # Library overview
neurop-forge execute reverse_string -i '{"s":"hi"}'   # Execute block
neurop-forge list --tier A --category string          # Filter blocks
neurop-forge info reverse_string                      # Block metadata
neurop-forge workflows                                # List workflows
```

---

### Categories (30+)

- String manipulation
- Collection operations
- Data validation
- Type conversions
- Date/time utilities
- Math & statistics
- Encoding & hashing
- Security utilities
- HTTP/API helpers
- Database patterns
- And more...

---

### Integration Pattern

```python
# Your AI agent
def handle_user_request(intent: str, data: dict):
    forge = NeuropForge()
    
    # AI searches for matching blocks
    candidates = forge.list_verified_blocks(category=intent, tier="A")
    
    # AI selects and executes (doesn't write code)
    for block in candidates:
        result = forge.execute_block(block["id"], data)
        if result["success"]:
            return result
    
    return {"error": "No matching block found"}
```

---

### What You Get

- **4,500+ verified blocks** ready to use
- **Full execution trace** on every call
- **Trust tier enforcement** by default
- **Immutability guarantee** — blocks are hash-locked

---

**License:** Dual (Non-Commercial with Attribution / Commercial)  
**Author:** Lourens Wasserman
