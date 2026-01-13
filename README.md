# Neurop Forge

**AI-Native Execution Control Layer**

> Others try to control what AI says. We control what AI can do.

---

## Current Status: Alpha

Neurop Forge is in active development. We're building the foundation for controlled AI execution and seeking strategic design partners to shape the enterprise roadmap.

**What's Working:**
- 4,552 verified function blocks
- Policy engine with whitelist enforcement
- Cryptographic audit chain
- Hosted API with stress testing

**What We're Building:**
- Enterprise integrations (SSO, SIEM)
- Compliance documentation (SOC 2, HIPAA alignment)
- Production SLAs and monitoring

**Contact:** wassermanlourens@gmail.com

---

## What Is Neurop Forge?

Neurop Forge is a library of **verified function blocks** that AI agents can search, compose, and execute — but never modify or create.

**The core idea:**
- AI does not generate code
- AI does not modify logic
- AI executes pre-verified operations only

This makes AI execution auditable, reversible, and suitable for regulated environments.

---

## What Is a Block?

A **block** is a single, verified function stored as an immutable JSON file with a cryptographic hash.

Each block contains:
- **Identity** — SHA256 hash that locks the block forever
- **Logic** — The actual Python function
- **Interface** — Inputs, outputs, and data types
- **Constraints** — Purity, determinism, thread safety
- **Trust Score** — Risk level and verification status

### Example Block

```json
{
  "metadata": {
    "name": "calculate_weighted_average",
    "category": "arithmetic",
    "description": "Calculate weighted average rating.",
    "tags": ["arithmetic", "average", "calculate", "ratings"]
  },
  "identity": {
    "algorithm": "sha256",
    "hash_value": "0002097c2ca8f771...",
    "version": "1.0.0"
  },
  "interface": {
    "inputs": [
      {"name": "ratings", "data_type": "list"},
      {"name": "weights", "data_type": "list"}
    ],
    "outputs": [
      {"name": "result", "data_type": "float"}
    ]
  },
  "constraints": {
    "purity": "pure",
    "deterministic": true,
    "thread_safe": true,
    "side_effects": []
  },
  "logic": "def calculate_weighted_average(ratings, weights): ..."
}
```

**Key point:** The hash locks the block. If anyone tries to modify the logic, the hash changes and the block is rejected.

---

## How AI Uses Blocks

```
┌─────────────────────────────────────────────────────────────┐
│                      AI AGENT                               │
│  "I need to validate an email and calculate tax"            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   1. SEARCH                                 │
│  AI searches library by intent                              │
│  Found: is_valid_email, calculate_tax_amount                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   2. POLICY CHECK                           │
│  Policy engine checks whitelist                             │
│  ✓ is_valid_email — ALLOWED                                 │
│  ✓ calculate_tax_amount — ALLOWED                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   3. EXECUTE                                │
│  Blocks run with full audit trace                           │
│  Every input, output, and timestamp logged                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   RESULT                                    │
│  Email: valid                                               │
│  Tax: $42.50                                                │
│  Code written by AI: 0 lines                                │
└─────────────────────────────────────────────────────────────┘
```

---

## The Library

**4,552 verified blocks** across 30+ categories:

| Category | Examples |
|----------|----------|
| Arithmetic | calculate_tax, weighted_average, percentage |
| String | trim, split, join, replace, case_convert |
| Validation | is_valid_email, is_valid_phone, is_valid_url |
| Security | sanitize_html, mask_email, detect_injection |
| Collection | flatten, unique, sort, chunk, filter |
| Date/Time | format_date, calculate_age, time_difference |
| Encoding | base64_encode, sha256_hash, url_encode |
| HTTP | parse_headers, validate_status_code |

Every block is:
- **Verified** — Passes validation before admission
- **Immutable** — Hash-locked, cannot be altered
- **Traced** — Full execution lineage on every run

---

## Policy Engine

The policy engine controls which blocks AI can use:

```python
# Whitelist mode: AI can ONLY use these blocks
policy = PolicyEngine(mode="whitelist")
policy.allow("is_valid_email")
policy.allow("calculate_tax_amount")

# AI tries to use a block
policy.check("is_valid_email")      # ✓ ALLOWED
policy.check("delete_database")     # ✗ BLOCKED (not in whitelist)
```

**Result:** AI cannot execute operations you haven't approved.

---

## Audit Chain

Every execution is cryptographically logged:

```python
{
  "block_id": "a1b2c3d4...",
  "block_name": "calculate_tax_amount",
  "inputs": {"amount": 500, "rate": 0.085},
  "output": 42.5,
  "timestamp": "2026-01-13T10:30:00Z",
  "chain_hash": "f7e8d9c0...",
  "previous_hash": "b4a3c2d1..."
}
```

The chain is tamper-proof. If any record is modified, the chain breaks.

---

## Why This Matters

| Traditional AI | Neurop Forge |
|----------------|--------------|
| AI generates arbitrary code | AI executes verified blocks only |
| Unpredictable output | Deterministic execution |
| Hard to audit | Full cryptographic trace |
| Risky in production | Policy-controlled, reversible |

**The architecture is designed for:**
- SOC 2 compliance requirements
- HIPAA audit trails
- PCI-DSS transaction logging
- Enterprise governance policies

---

## Quick Start

### Python SDK

```bash
pip install neuropforge
```

```python
from neuropforge import NeuropForge

# Initialize with your API key
client = NeuropForge(api_key="your_key")

# Execute a block by exact name
result = client.execute("to_uppercase", text="hello world")
print(result.result)  # "HELLO WORLD"

# Search for blocks (discovery only)
blocks = client.search("validate email")
for block in blocks:
    print(f"{block.name} - {block.domain}/{block.operation}")

# List available blocks
blocks = client.list_blocks(limit=10, category="validation")
```

### CLI Tool

```bash
# Check API health
nf health

# List blocks
nf blocks --limit 10 --category validation

# Search for blocks
nf search "validate email"

# Execute a block
nf exec to_uppercase --input text="hello world"
nf exec string_length -i text="Neurop Forge"
```

### Direct API

```bash
curl -X POST https://neurop-forge.onrender.com/execute-block \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{"block_name": "to_uppercase", "inputs": {"text": "hello"}}'
```

---

## Installation

```bash
pip install neurop-forge
```

Or from source:

```bash
git clone https://github.com/Louw115/neurop-forge.git
cd neurop-forge
pip install -e .
```

---

## Hosted API

Live API for testing: `https://neurop-forge.onrender.com`

```bash
# Health check
curl https://neurop-forge.onrender.com/health

# Execute a block (requires API key)
curl -X POST https://neurop-forge.onrender.com/execute \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "reverse the string hello"}'
```

---

## Stress Test Results

Our policy engine blocks 100% of attack attempts:

| Test | Result |
|------|--------|
| SQL Injection | BLOCKED |
| Ransomware | BLOCKED |
| Data Exfiltration | BLOCKED |
| AI Jailbreaks | BLOCKED |
| Privilege Escalation | BLOCKED |

**112 attack vectors tested. 112 blocked.**

Legitimate operations (payments, registrations, data processing) pass through when using approved blocks.

---

## Who This Is For

**Good fit:**
- Teams deploying AI agents in production
- Enterprises needing auditable AI execution
- Regulated industries (finance, healthcare, insurance)
- Developers building AI-powered automation

**Not a fit:**
- Projects needing AI to generate arbitrary code
- Research on unconstrained AI capabilities
- Applications where auditability doesn't matter

---

## Design Partner Program

We're inviting select partners to shape the enterprise roadmap:

- Early access to new features
- Input on compliance requirements
- Favorable terms for early adopters

**Contact:** wassermanlourens@gmail.com

---

## License

Apache License 2.0

Copyright (c) 2024-2026 Lourens Wasserman
