# Neurop Block Forge

## Overview
Neurop Block Forge is a production-grade system for converting source code into validated, immutable NeuropBlocks that AI can search and assemble but never modify. This is the first AI-native software memory system.

## System Architecture
```
neurop_forge/
├── core/           # Identity, schema, normalization
├── intake/         # Source fetching, license enforcement
├── parsing/        # AST analysis (Python, JavaScript)
├── conversion/     # Intent classification, block building
├── validation/     # Static analysis, dynamic testing, schema enforcement
├── scoring/        # Trust model
├── library/        # Block storage, indexing, AI fetch engine
├── composition/    # Type/contract matching, graph rules
└── main.py         # Orchestrator
```

## Key Concepts

### NeuropBlock
An immutable, validated unit of functionality with:
- Hash-consistent identity
- Typed interface
- Explicit constraints (purity, determinism, I/O)
- Trust score
- Composition compatibility

### AI Usage Model
AI can:
- Search library by intent
- Reason over metadata
- Assemble block graphs
- Verify compatibility

AI cannot:
- Write code
- Modify blocks
- Bypass trust rules

## Running the Demo
```bash
python -m neurop_forge.main
```

This demonstrates:
1. Converting arithmetic functions to NeuropBlocks
2. Storing them immutably
3. AI query: "build calculator"
4. Returns block graph (not code)

## User Preferences
- Production-grade quality only
- No stubs or TODOs
- No approximations
- Strict schema enforcement

## Recent Changes
- Initial implementation of complete Neurop Block Forge system
- All modules implemented: core, intake, parsing, conversion, validation, scoring, library, composition
- Demonstration with arithmetic functions
