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
**948 blocks** across 32 source modules (97% pass rate, 28 quarantined)

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
27. Configuration utilities
28. Pagination utilities
29. Slug utilities
30. Money utilities
31. Phone utilities
32. Markdown utilities

## Target
- Goal: 4,500+ blocks for world-changing coverage
- Current: Phase 3 complete (948 blocks, 21%)
- Remaining: ~3,552 blocks across business logic, database patterns, web/API, data science, specialized domains

## Recent Changes
- Phase 3 complete: 948 blocks from 32 source modules
- Added configuration utilities (31 blocks): env parsing, feature flags, DSN parsing
- Added pagination utilities (27 blocks): offset/limit, cursor, page calculations
- Added slug utilities (34 blocks): URL slugs, base62/36 IDs, checksum
- Added money utilities (43 blocks): currency formatting, tax, interest
- Added phone utilities (26 blocks): parsing, formatting, validation
- Added markdown utilities (34 blocks): formatting, parsing, TOC generation
- Fixed determinism bug in is_feature_enabled_for_user (switched from hash() to hashlib.sha256)
- All 32 modules verified as pure, deterministic, atomic
