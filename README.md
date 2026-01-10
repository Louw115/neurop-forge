# Neurop Forge

Production-grade semantic block composition engine with 2,060+ verified deterministic blocks.

## Installation

```bash
pip install neurop-forge
```

## Quick Start

### Python API

```python
from neurop_forge import NeuropForge

forge = NeuropForge()

# Execute a single block
result = forge.execute_block("reverse_string", {"s": "hello"})
print(result)  # {'result': 'olleh', 'success': True}

# List verified blocks
blocks = forge.list_verified_blocks(category="string", tier="A", limit=10)

# Get library stats
print(forge.stats)
# {'total_blocks': 4550, 'total_verified': 2740, 'tier_a': 2060, 'tier_b': 680}
```

### Convenience Functions

```python
from neurop_forge import execute_block, run_workflow, list_blocks

result = execute_block("to_uppercase", {"s": "hello"})
workflow = run_workflow("text_normalization", {"text": "Hello World"})
blocks = list_blocks(category="validation", tier="A")
```

### CLI

```bash
neurop-forge stats                                    # Show library stats
neurop-forge execute reverse_string -i '{"s":"hi"}'   # Execute block
neurop-forge list --tier A --limit 10                 # List blocks
neurop-forge workflows                                # List workflows
neurop-forge info reverse_string                      # Block details
neurop-forge dedup --detailed                         # Analyze duplicates
neurop-forge standardize --detailed                   # Analyze parameters
```

## What's Included

**2,740 verified blocks** across 175 source modules:

- **2,060 Tier-A blocks** - Deterministic, pure functions
- **680 Tier-B blocks** - Context-dependent (require explicit opt-in)

### Categories

- String manipulation (trim, split, join, replace)
- Collection operations (flatten, unique, sort, chunk)
- Data validation (email, URL, phone, patterns)
- Type conversions (int, float, string, boolean)
- Date/time utilities (days between, leap year, format)
- Math & statistics (sqrt, median, variance, trig)
- Encoding & hashing (MD5, SHA256, base64, URL encode)
- And 40+ more categories...

## Block Tiers

| Tier | Count | Description |
|------|-------|-------------|
| A | 2,060 | Deterministic, pure functions, no external dependencies |
| B | 680 | Context-dependent or complex input requirements |

## V2.0.0 Features

- **Deduplication Engine** - Removes duplicate blocks automatically
- **Parameter Standardization** - Canonical parameter names with alias support
- **Verification Gate** - Only verified blocks in production mode
- **Tier Classification** - Automated safety classification

## License

Dual License:
- **Non-Commercial**: Free with attribution
- **Commercial**: Contact for licensing

Copyright (c) 2024-2026 Lourens Wasserman. All rights reserved.
