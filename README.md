# Neurop Forge

**2,700+ verified function blocks AI can execute but never modify.**

Neurop Forge is an immutable function library for AI systems. AI agents can search, compose, and execute blocks — but they cannot write code, alter logic, or bypass trust rules.

This turns AI from unpredictable authors into controlled operators.

## The Problem

AI systems that generate or modify code are:
- Unpredictable
- Impossible to audit
- Difficult to roll back
- Risky in production

## The Solution

Neurop Forge enforces immutability at the architecture level:

| What AI Can Do | What AI Cannot Do |
|----------------|-------------------|
| Search blocks by intent | Write new code |
| Compose block graphs | Modify existing blocks |
| Execute with full trace | Bypass verification |
| Reason over metadata | Skip trust tiers |

Every block is:
- **Verified** — passes automated validation before admission
- **Immutable** — hash-locked, cannot be altered
- **Traced** — full execution lineage on every run
- **Scored** — trust tier classification (A or B)

## Trust Tiers

Blocks are classified into safety tiers for controlled AI composition:

| Tier | Count | What It Means |
|------|-------|---------------|
| **A** | 2,060 | Deterministic, pure functions, no side effects, no external dependencies |
| **B** | 680 | Context-dependent, may require specific inputs, explicit opt-in required |

Tier-A blocks are safe for unrestricted AI use.  
Tier-B blocks require explicit permission — AI cannot silently use them.

## Quick Example

AI executes blocks. AI does not write code.

```python
from neurop_forge import NeuropForge

forge = NeuropForge()

# AI executes a verified block
result = forge.execute_block("reverse_string", {"s": "hello"})
print(result)  # {'result': 'olleh', 'success': True}

# AI composes a workflow from verified blocks
workflow = forge.run_workflow("text_normalization", {"text": "Hello World"})

# AI queries the library
blocks = forge.list_verified_blocks(category="string", tier="A", limit=10)
```

The AI used three blocks. It modified zero lines of code.

## Installation

```bash
pip install neurop-forge
```

Neurop Forge is designed to sit under AI agents, not replace them.

## CLI

```bash
neurop-forge stats                                    # Library overview
neurop-forge execute reverse_string -i '{"s":"hi"}'   # Execute a block
neurop-forge list --tier A --limit 10                 # List Tier-A blocks
neurop-forge info reverse_string                      # Block details
neurop-forge workflows                                # Available workflows
```

## AI Agent Demo

See GPT-4 call verified blocks with zero code generation:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-key-here

# Run the demo
python demos/ai_agent_demo.py
```

### Example Output

```
======================================================================
  NEUROP FORGE - AI AGENT DEMO
  GPT as a Controlled Operator (Not a Code Writer)
======================================================================

  USER REQUEST:
  "I need to validate some customer data. Check if the email john.doe@company.com
   is valid, verify the phone number +1-555-867-5309, and also sanitize this
   HTML input: <script>alert('xss')</script>"
----------------------------------------------------------------------

  AI AGENT REASONING...

  EXECUTING VERIFIED BLOCKS:
  ----------------------------------------
  | Block: is_valid_email
  | Input: {"email": "john.doe@company.com"}
  | Output: True
  ----------------------------------------
  | Block: is_valid_phone
  | Input: {"phone": "+1-555-867-5309"}
  | Output: True
  ----------------------------------------
  | Block: sanitize_html
  | Input: {"text": "<script>alert('xss')</script>"}
  | Output: &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;
  ----------------------------------------

======================================================================
  AI AGENT RESPONSE:
======================================================================

  1. Email Validation: john.doe@company.com is valid: True
  2. Phone Validation: +1-555-867-5309 is valid: True
  3. HTML Sanitization: XSS attack neutralized

======================================================================
  EXECUTION SUMMARY
======================================================================
  Verified Blocks Called: 3
  Lines of Code Written by AI: 0
  All blocks are: VERIFIED, IMMUTABLE, DETERMINISTIC
======================================================================
```

The AI selected 3 blocks from 23 available. It executed them with real inputs. It wrote zero code.

## What's Included

**2,740 verified blocks** across 175 source modules and 30+ categories:

- String manipulation (trim, split, join, replace, case conversion)
- Collection operations (flatten, unique, sort, chunk, filter)
- Data validation (email, URL, phone, patterns, schemas)
- Type conversions (int, float, string, boolean, parsing)
- Date/time utilities (formatting, calculation, comparison)
- Math & statistics (sqrt, median, variance, trigonometry)
- Encoding & hashing (MD5, SHA256, base64, URL encode)
- Security utilities (sanitize, mask, injection detection)
- HTTP/API helpers (status codes, headers, cookies, MIME types)
- Database patterns (SQL building, migrations, transactions)
- And more...

## Who This Is For

**Good fit:**
- Teams deploying AI agents in production
- Enterprises needing auditable AI execution
- Platforms requiring deterministic AI behavior
- Developers building AI-powered automation

**Not a fit:**
- Projects needing AI to generate arbitrary code
- Research on unconstrained AI capabilities
- Applications where auditability doesn't matter

## V2.0.0 Features

- **Verification Gate** — blocks must pass validation to enter the library
- **Tier Classification** — automated A/B safety classification
- **Deduplication Engine** — removes duplicate blocks automatically
- **Parameter Standardization** — canonical names with alias support
- **Full Execution Trace** — every run is logged and auditable

v2.0.0 establishes the execution and trust layer. Policy engines and orchestration remain external by design.

## License

Dual License:
- **Non-Commercial**: Free with attribution
- **Commercial**: Contact for licensing

Copyright (c) 2024-2026 Lourens Wasserman. All rights reserved.
