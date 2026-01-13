# Neurop Forge

## Overview

Neurop Forge is an AI-native execution control layer that provides a library of 4,500+ pre-verified, hash-locked function blocks that AI agents can search, compose, and execute—but never modify. The system transforms AI agents from unpredictable code generators into controlled operators that work within a deterministic, auditable framework.

The core value proposition is controlled AI execution: AI cannot generate arbitrary code, modify logic, or bypass trust rules. Instead, it searches a verified library by intent, composes block workflows, and executes deterministically with full traceability. This makes AI operations auditable, reversible, and suitable for regulated environments (SOC 2, HIPAA, PCI-DSS).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Block Library System
- **Immutable Function Blocks**: Each operation is stored as a JSON file in `.neurop_expanded_library/` with a SHA256 hash identifier
- **Block Categories**: Blocks are classified by type (arithmetic, string, collection, validation, filtering, transformation, comparison, sorting, aggregation)
- **Trust Tiers**: Tier-A blocks are safe for unrestricted AI use; Tier-B blocks require explicit permission
- **Cryptographic Identity**: Every block has a `hash_value` and `semantic_fingerprint` for verification

### Block Metadata Structure
Each block JSON contains:
- **Identity**: Hash algorithm, hash value, semantic fingerprint for immutability verification
- **Composition**: Compatibility rules for chaining blocks (input/output types, conflicts, dependencies)
- **Constraints**: Purity level, determinism, thread safety, I/O operations, side effects
- **Failure Modes**: Exception handling, recovery hints, error conditions

### Execution Model
- **Pure Functions**: Most blocks are deterministic, thread-safe, with no side effects
- **Composability**: Blocks can be chained based on compatible input/output types (arithmetic, string, collection, validation, utility)
- **Audit Trail**: All executions are cryptographically logged in a tamper-proof chain

### Policy Engine
- Whitelist/blacklist system for controlling which blocks AI can access
- Policy enforcement blocks unauthorized actions before execution
- Designed for compliance with regulated industry standards

## External Dependencies

### Core Dependencies
- **Python**: Primary language for the drop-in library
- **SHA256 Hashing**: Used for block identity and integrity verification

### No External Services Required
- The library is self-contained with no external API dependencies
- Block definitions are stored locally as JSON files
- No database required—file-based storage using hash-named JSON files

### Optional Integrations
- Semantic search capabilities for AI to find blocks by intent
- Audit logging system (implementation-specific)
- Policy configuration system for enterprise deployments

## Hosted API (for Render Deployment)

### API Endpoints
The FastAPI server in `api/main.py` provides remote execution:
- `GET /health` - Health check, returns block count
- `POST /execute` - Execute blocks by natural language query (requires X-API-Key header)
- `POST /search` - Search blocks by intent (requires X-API-Key header)
- `GET /stats` - Library and usage statistics
- `GET /audit/chain` - Audit chain verification

### Deployment Files
- `render.yaml` - Render deployment configuration
- `requirements-api.txt` - API-specific dependencies
- `docs/RENDER_DEPLOYMENT.md` - Deployment instructions

### IP Protection Strategy
The `.neurop_expanded_library/` folder contains 4,500+ pre-verified blocks and is:
- Excluded from GitHub via .gitignore
- Excluded from PyPI distribution via MANIFEST.in
- Only accessible via the hosted API

This protects the library as proprietary IP while allowing users to access functionality through the API.