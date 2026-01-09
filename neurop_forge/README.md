# Neurop Block Forge

**The First AI-Native Software Memory System**

## Overview

Neurop Block Forge is a production-grade system that:

1. **Ingests open-source code** from GitHub or local files
2. **Decomposes it into atomic intent units** using AST analysis
3. **Converts each unit into a PERFECT NeuropBlock**
4. **Validates, tests, scores, and seals each block**
5. **Stores blocks in a canonical Neurop Library**
6. **Allows AI to fetch blocks by intent and guarantees**
7. **Never generates application code**
8. **Only assembles from verified blocks**

## Philosophy

> Code is raw material.
> NeuropBlocks are knowledge.
> AI assembles knowledge, not text.

## What is a NeuropBlock?

A NeuropBlock is PERFECT only if ALL conditions are met:

### Structural Invariants
- One block = one intent
- Immutable after creation
- Deterministic unless explicitly declared otherwise
- Explicit side-effect declaration
- No hidden I/O
- No implicit state
- Hash-consistent identity

### Required Sections (ALL Mandatory)
- `identity` - Hash-derived, reproducible
- `ownership` - License provenance
- `metadata` - Human + AI readable
- `interface` - Typed inputs/outputs
- `constraints` - Runtime, purity, I/O
- `logic` - Embedded, normalized
- `validation_rules` - Input/output validators
- `trust_score` - Determinism × tests × license × risk
- `failure_modes` - How block may fail
- `composition` - Compatibility rules

**Any block missing one field is INVALID and must be rejected.**

## AI Usage Model (Strict)

### AI IS ALLOWED TO:
- Search the library
- Reason over metadata
- Assemble block graphs
- Verify compatibility

### AI IS NOT ALLOWED TO:
- Write code
- Modify blocks
- Bypass trust rules

## System Architecture

```
neurop_forge/
├── core/
│   ├── identity.py          # Canonical hash & identity authority
│   ├── block_schema.py      # Strict Neurop schema (no flexibility)
│   └── normalization.py     # Code → intent normalization
│
├── intake/
│   ├── source_fetcher.py    # GitHub / local file fetching
│   └── license_enforcer.py  # MIT/BSD/Apache only
│
├── parsing/
│   ├── ast_python.py        # Python AST analysis
│   ├── ast_javascript.py    # JavaScript parsing
│   └── intent_units.py      # Extract atomic intent units
│
├── conversion/
│   ├── intent_classifier.py # Classify intents
│   └── block_builder.py     # Produces ONLY valid NeuropBlocks
│
├── validation/
│   ├── static_analysis.py   # Forbidden ops, purity, determinism
│   ├── dynamic_testing.py   # Repeatability + edge tests
│   └── schema_enforcer.py   # Rejects invalid blocks
│
├── scoring/
│   └── trust_model.py       # Determinism × tests × license × risk
│
├── library/
│   ├── block_store.py       # Immutable storage
│   ├── indexer.py           # Intent + constraint index
│   └── fetch_engine.py      # AI query resolution
│
├── composition/
│   ├── compatibility.py     # Type & contract matching
│   └── graph_rules.py       # How blocks connect
│
└── main.py                  # Orchestrator
```

## Usage

### Basic Usage

```python
from neurop_forge.main import NeuropForge
from neurop_forge.core.block_schema import LicenseType

# Initialize the forge
forge = NeuropForge()

# Ingest source code
result = forge.ingest_source(
    source_path="path/to/source.py",
    license_type=LicenseType.MIT,
    author="Author Name",
    repository="https://github.com/owner/repo"
)

print(f"Blocks created: {result['blocks_created']}")
```

### AI Query Interface

```python
# Search by intent (returns metadata, not code)
results = forge.search_by_intent("add two numbers")

# Compose a block graph (returns graph, not code)
graph = forge.compose_graph("build calculator")

# Get block metadata (no code access for AI)
metadata = forge.get_block_metadata(block_identity)
```

### Running the Demonstration

```bash
python -m neurop_forge.main
```

This demonstrates:
1. Converting arithmetic functions into atomic blocks
2. Storing them immutably
3. AI query: "build calculator"
4. Returned block graph (not code)
5. Proof that assembly uses only validated blocks

## Hard Rules (System Enforced)

- ❌ No monolithic blocks
- ❌ No "application-level" blocks
- ❌ No guessing intent without AST evidence
- ❌ No dynamic code generation
- ❌ No weak typing
- ❌ No mutable blocks
- ❌ No silent failure

**If a block cannot be verified → it is rejected.**

## Validation Requirements

Every NeuropBlock must:
1. Pass schema validation
2. Pass static analysis
3. Pass deterministic replay
4. Have reproducible hash
5. Have explainable intent
6. Have a non-zero trust score

Blocks failing any step:
- Are quarantined
- Never exposed to AI assembly

## Trust Model

Trust score is calculated as:
- 25% Determinism verification
- 25% Test coverage
- 20% License compliance
- 30% Static analysis score

Minimum trust score for AI assembly: 0.2

## License Requirements

Only the following licenses are accepted:
- MIT
- BSD-2-Clause
- BSD-3-Clause
- Apache-2.0
- Unlicense
- CC0-1.0
- Public Domain

All other licenses are rejected.

## Guarantees

1. **Immutability**: Blocks cannot be modified after creation
2. **Determinism**: Same inputs always produce same outputs (for deterministic blocks)
3. **Traceability**: Every block has verified provenance
4. **Trust**: Every block has a calculated, verifiable trust score
5. **Composition Safety**: Block graphs are validated for type and contract compatibility

## This is NOT:

- A code generator
- A framework
- A library wrapper
- A prototype

## This IS:

**The first AI-native software memory system**

Where code is raw material, NeuropBlocks are knowledge, and AI assembles knowledge, not text.
