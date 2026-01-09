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

## Library Status
**753 blocks** across 26 source modules (97.6% pass rate, 18 quarantined)

### Domains Covered
1. String manipulation
2. Collection operations
3. Data validation
4. Type conversions
5. Comparison logic
6. Date/time utilities
7. Math & statistics
8. Path utilities
9. Data parsing
10. Encoding & hashing
11. URL utilities
12. Text analysis
13. Color utilities
14. Formatting
15. Array operations
16. Security utilities
17. HTTP utilities
18. File type detection
19. Cryptography helpers
20. Data transformation
21. Regex utilities
22. UUID utilities
23. Geolocation utilities
24. Caching utilities
25. Rate limiting
26. Email utilities

## Target
- Goal: 4,500+ blocks for world-changing coverage
- Current: Phase 2 complete (750+ blocks)
- Remaining: ~3,750 blocks across business logic, database patterns, web/API, data science, specialized domains

## Recent Changes
- Phase 2 complete: 753 blocks from 26 source modules
- Added regex utilities (55 blocks): pattern building, matching, extraction
- Added UUID utilities (36 blocks): validation, parsing, version detection
- Added geolocation (37 blocks): haversine distance, bearing, coordinates
- Added caching utilities (41 blocks): TTL, keys, eviction, ETag
- Added rate limiting (47 blocks): token bucket, sliding window, backoff
- Added email utilities (32 blocks): validation, parsing, masking
- All functions verified as pure, deterministic, atomic
