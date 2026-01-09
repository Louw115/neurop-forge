"""
Neurop Block Forge - Main Orchestrator

This is the central orchestrator for the Neurop Block Forge system.
It coordinates all modules to:
1. Ingest open-source code
2. Decompose into atomic intent units
3. Convert to NeuropBlocks
4. Validate, test, score, and seal blocks
5. Store in the canonical library
6. Enable AI to fetch blocks by intent

AI USAGE MODEL (STRICT):
- AI can search the library
- AI can reason over metadata
- AI can assemble block graphs
- AI can verify compatibility

AI is NOT allowed to:
- Write code
- Modify blocks
- Bypass trust rules
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timezone

from neurop_forge.core.identity import IdentityAuthority
from neurop_forge.core.block_schema import (
    NeuropBlock, BlockOwnership, LicenseType,
)
from neurop_forge.core.normalization import CodeNormalizer, NormalizationLevel

from neurop_forge.intake.source_fetcher import SourceFetcher
from neurop_forge.intake.license_enforcer import LicenseEnforcer

from neurop_forge.parsing.ast_python import PythonASTParser
from neurop_forge.parsing.ast_javascript import JavaScriptParser
from neurop_forge.parsing.intent_units import IntentExtractor, IntentUnit

from neurop_forge.conversion.intent_classifier import IntentClassifier, ClassificationResult
from neurop_forge.conversion.block_builder import BlockBuilder, BuildResult

from neurop_forge.validation.static_analysis import StaticAnalyzer
from neurop_forge.validation.dynamic_testing import DynamicTester
from neurop_forge.validation.schema_enforcer import SchemaEnforcer

from neurop_forge.scoring.trust_model import TrustCalculator

from neurop_forge.library.block_store import BlockStore
from neurop_forge.library.indexer import BlockIndexer
from neurop_forge.library.fetch_engine import FetchEngine, BlockGraph

from neurop_forge.composition.compatibility import CompatibilityChecker
from neurop_forge.composition.graph_rules import GraphValidator, CompositionGraph


class NeuropForge:
    """
    The main orchestrator for the Neurop Block Forge.
    
    This class coordinates the entire pipeline from source code
    to validated, immutable NeuropBlocks.
    """

    def __init__(
        self,
        storage_path: str = ".neurop_library",
        strict_mode: bool = True,
    ):
        self._storage_path = storage_path
        self._strict_mode = strict_mode

        self._identity_authority = IdentityAuthority()
        self._normalizer = CodeNormalizer(NormalizationLevel.STANDARD)

        self._source_fetcher = SourceFetcher()
        self._license_enforcer = LicenseEnforcer(strict_mode=strict_mode)

        self._python_parser = PythonASTParser()
        self._javascript_parser = JavaScriptParser()
        self._intent_extractor = IntentExtractor()

        self._intent_classifier = IntentClassifier()
        self._block_builder = BlockBuilder(
            identity_authority=self._identity_authority,
            normalizer=self._normalizer,
        )

        self._static_analyzer = StaticAnalyzer(strict_mode=strict_mode)
        self._dynamic_tester = DynamicTester()
        self._schema_enforcer = SchemaEnforcer(strict_mode=strict_mode)

        self._trust_calculator = TrustCalculator()

        self._block_store = BlockStore(storage_path=storage_path)
        self._indexer = BlockIndexer()
        self._fetch_engine = FetchEngine(self._block_store, self._indexer)

        self._compatibility_checker = CompatibilityChecker(strict_mode=strict_mode)
        self._graph_validator = GraphValidator(self._compatibility_checker)

        self._load_existing_blocks()

    def _load_existing_blocks(self) -> None:
        """Load and index existing blocks from storage."""
        for block in self._block_store.get_all():
            self._indexer.index_block(block)

    def ingest_source(
        self,
        source_path: str,
        license_type: LicenseType = LicenseType.MIT,
        author: Optional[str] = None,
        repository: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ingest source code and convert to NeuropBlocks.
        
        Args:
            source_path: Path to source file or GitHub URL
            license_type: The license type of the source
            author: Original author
            repository: Original repository
            
        Returns:
            Dictionary with ingestion results
        """
        result = {
            "source": source_path,
            "status": "success",
            "blocks_created": 0,
            "blocks_quarantined": 0,
            "errors": [],
            "block_identities": [],
        }

        fetch_result = self._source_fetcher.fetch(source_path)

        if not fetch_result.is_success():
            result["status"] = "failed"
            result["errors"].append(f"Fetch failed: {fetch_result.error_message}")
            return result

        ownership = BlockOwnership(
            license_type=license_type,
            license_url=None,
            original_author=author,
            original_repository=repository,
            attribution_required=True,
            modifications_allowed=True,
        )

        language = fetch_result.language
        content = fetch_result.content

        if language == "python":
            functions, classes = self._python_parser.parse(content)

            intent_units = []
            for func in functions:
                unit = self._intent_extractor.extract_from_python_function(
                    func, source_path
                )
                intent_units.append(unit)

            for cls in classes:
                class_units = self._intent_extractor.extract_from_python_class(
                    cls, source_path
                )
                intent_units.extend(class_units)

        elif language == "javascript":
            js_functions = self._javascript_parser.parse(content)
            intent_units = [
                self._intent_extractor.extract_from_javascript_function(
                    func, source_path
                )
                for func in js_functions
            ]
        else:
            result["status"] = "failed"
            result["errors"].append(f"Unsupported language: {language}")
            return result

        for unit in intent_units:
            block_result = self._process_intent_unit(unit, ownership)

            if block_result["status"] == "stored":
                result["blocks_created"] += 1
                result["block_identities"].append(block_result["identity"])
            elif block_result["status"] == "quarantined":
                result["blocks_quarantined"] += 1
                result["errors"].append(block_result.get("reason", "Unknown"))
            else:
                result["errors"].append(
                    f"Failed to process {unit.function_name}: {block_result.get('reason', 'Unknown')}"
                )

        return result

    def _process_intent_unit(
        self,
        unit: IntentUnit,
        ownership: BlockOwnership,
    ) -> Dict[str, Any]:
        """Process a single intent unit through the full pipeline."""
        classification = self._intent_classifier.classify(unit)

        if not classification.is_valid_for_block():
            return {
                "status": "rejected",
                "reason": "Classification not valid for block conversion",
            }

        build_result = self._block_builder.build(classification, ownership)

        if not build_result.is_success():
            return {
                "status": "rejected",
                "reason": f"Build failed: {', '.join(build_result.errors)}",
            }

        block = build_result.block

        static_result = self._static_analyzer.analyze(block)

        if not static_result.passed:
            critical = static_result.get_critical_violations()
            if critical:
                store_result = self._block_store.quarantine(
                    block,
                    f"Static analysis failed: {critical[0].message}",
                )
                return {
                    "status": "quarantined",
                    "reason": critical[0].message,
                    "identity": block.get_identity_hash(),
                }

        enforcement_result = self._schema_enforcer.enforce(block)

        if not enforcement_result.is_valid:
            return {
                "status": "rejected",
                "reason": f"Schema validation failed: {', '.join(str(v.message) for v in enforcement_result.violations[:3])}",
            }

        store_result = self._block_store.store(block)

        if store_result.is_success():
            self._indexer.index_block(block)
            return {
                "status": "stored",
                "identity": block.get_identity_hash(),
            }

        return {
            "status": "failed",
            "reason": store_result.error_message,
        }

    def search_by_intent(
        self,
        intent: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Search for blocks by intent description.
        
        This is the primary interface for AI to query the library.
        
        Args:
            intent: Natural language intent description
            limit: Maximum results
            
        Returns:
            Search results with matching blocks
        """
        result = self._fetch_engine.search_by_intent(intent, limit=limit)
        return result.to_dict()

    def compose_graph(self, intent: str) -> Dict[str, Any]:
        """
        Compose a block graph for a given intent.
        
        Returns a graph structure, NOT code. This is what AI
        returns instead of generating code.
        
        Args:
            intent: The high-level intent to fulfill
            
        Returns:
            BlockGraph structure if successful
        """
        result = self._fetch_engine.compose_graph(intent)
        return result.to_dict()

    def get_block_metadata(self, identity: str) -> Optional[Dict[str, Any]]:
        """
        Get block metadata (no code access for AI).
        
        Args:
            identity: Block identity
            
        Returns:
            Metadata dict or None
        """
        return self._fetch_engine.get_block_metadata(identity)

    def get_library_statistics(self) -> Dict[str, Any]:
        """Get statistics about the block library."""
        store_stats = self._block_store.get_statistics()
        index_stats = self._indexer.get_statistics()

        return {
            "storage": store_stats,
            "index": index_stats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def verify_graph(self, blocks: List[NeuropBlock]) -> Dict[str, Any]:
        """
        Verify a composition graph.
        
        Args:
            blocks: List of blocks to verify as a graph
            
        Returns:
            Validation result
        """
        graph = self._graph_validator.create_graph(blocks)
        result = self._graph_validator.validate(graph)
        return result.to_dict()


def demonstrate_expanded_library():
    """
    Demonstration: Converting multiple function modules to NeuropBlocks
    and building an expanded library for comprehensive block composition.
    
    This demonstrates:
    1. Ingesting multiple source modules (string, list, validation, etc.)
    2. Converting pure functions into atomic blocks at scale
    3. Building a comprehensive library of 70+ blocks
    4. AI query with expanded capabilities
    5. Block composition across multiple domains
    """
    print("=" * 70)
    print("NEUROP BLOCK FORGE - EXPANDED LIBRARY DEMONSTRATION")
    print("=" * 70)
    print()

    source_modules = [
        ("neurop_forge/sources/string_operations.py", "String Operations"),
        ("neurop_forge/sources/list_operations.py", "List/Collection Operations"),
        ("neurop_forge/sources/validation_functions.py", "Validation Functions"),
        ("neurop_forge/sources/type_conversions.py", "Type Conversions"),
        ("neurop_forge/sources/comparison_logic.py", "Comparison & Logic"),
        ("neurop_forge/sources/datetime_utilities.py", "Date/Time Utilities"),
        ("neurop_forge/sources/math_statistics.py", "Math & Statistics"),
        ("neurop_forge/sources/path_utilities.py", "Path Utilities"),
        ("neurop_forge/sources/data_parsing.py", "Data Parsing"),
        ("neurop_forge/sources/encoding_utilities.py", "Encoding & Hashing"),
        ("neurop_forge/sources/url_utilities.py", "URL Utilities"),
        ("neurop_forge/sources/text_analysis.py", "Text Analysis"),
        ("neurop_forge/sources/color_utilities.py", "Color Utilities"),
        ("neurop_forge/sources/formatting_utilities.py", "Formatting Utilities"),
        ("neurop_forge/sources/array_operations.py", "Array Operations"),
        ("neurop_forge/sources/security_utilities.py", "Security Utilities"),
        ("neurop_forge/sources/http_utilities.py", "HTTP Utilities"),
        ("neurop_forge/sources/file_type_detection.py", "File Type Detection"),
        ("neurop_forge/sources/cryptography_helpers.py", "Cryptography Helpers"),
        ("neurop_forge/sources/data_transformation.py", "Data Transformation"),
        ("neurop_forge/sources/regex_utilities.py", "Regex Utilities"),
        ("neurop_forge/sources/uuid_utilities.py", "UUID Utilities"),
        ("neurop_forge/sources/geolocation_utilities.py", "Geolocation Utilities"),
        ("neurop_forge/sources/caching_utilities.py", "Caching Utilities"),
        ("neurop_forge/sources/rate_limiting.py", "Rate Limiting"),
        ("neurop_forge/sources/email_utilities.py", "Email Utilities"),
        ("neurop_forge/sources/configuration_utilities.py", "Configuration Utilities"),
        ("neurop_forge/sources/pagination_utilities.py", "Pagination Utilities"),
        ("neurop_forge/sources/slug_utilities.py", "Slug Utilities"),
        ("neurop_forge/sources/money_utilities.py", "Money Utilities"),
        ("neurop_forge/sources/phone_utilities.py", "Phone Utilities"),
        ("neurop_forge/sources/markdown_utilities.py", "Markdown Utilities"),
    ]

    print("STEP 1: Initialize Neurop Block Forge")
    print("-" * 50)
    forge = NeuropForge(storage_path=".neurop_expanded_library")
    print("Forge initialized successfully")
    print()

    print("STEP 2: Ingest All Source Modules")
    print("-" * 50)

    total_created = 0
    total_quarantined = 0
    total_errors = 0
    module_results = []

    for source_path, module_name in source_modules:
        print(f"\nIngesting: {module_name}")
        print(f"  Source: {source_path}")

        result = forge.ingest_source(
            source_path=source_path,
            license_type=LicenseType.MIT,
            author="Neurop Forge Team",
            repository="neurop-block-forge",
        )

        total_created += result['blocks_created']
        total_quarantined += result['blocks_quarantined']
        total_errors += len(result['errors'])

        print(f"  Created: {result['blocks_created']} blocks")
        if result['blocks_quarantined'] > 0:
            print(f"  Quarantined: {result['blocks_quarantined']}")
        if result['errors']:
            print(f"  Errors: {len(result['errors'])}")

        module_results.append({
            "module": module_name,
            "created": result['blocks_created'],
            "quarantined": result['blocks_quarantined'],
        })

    print()
    print("-" * 50)
    print(f"INGESTION SUMMARY:")
    print(f"  Total Blocks Created: {total_created}")
    print(f"  Total Quarantined: {total_quarantined}")
    print(f"  Total Errors: {total_errors}")
    print()

    print("STEP 3: Library Statistics")
    print("-" * 50)
    stats = forge.get_library_statistics()
    print(f"Total Blocks in Library: {stats['storage']['total_blocks']}")
    print(f"Categories: {stats['storage']['categories']}")
    print(f"Average Trust Score: {stats['storage']['average_trust']:.2f}")
    print()

    print("STEP 4: Sample Queries Across Domains")
    print("-" * 50)

    sample_queries = [
        ("string manipulation trim uppercase", "String Operations"),
        ("list flatten unique sort", "Collection Operations"),
        ("validate email url phone", "Validation"),
        ("convert integer float string", "Type Conversion"),
        ("compare equals greater less clamp", "Comparison Logic"),
        ("date days between weekend leap year", "Date/Time"),
    ]

    for query, domain in sample_queries:
        print(f"\nQuery: '{query}' ({domain})")
        search_result = forge.search_by_intent(query, limit=5)
        blocks_found = search_result.get("blocks_found", [])
        print(f"  Found: {len(blocks_found)} blocks")
        for block in blocks_found[:3]:
            print(f"    - {block['name']}: {block['intent'][:40]}...")

    print()

    print("STEP 5: Compose Complex Graph - 'validate and format user input'")
    print("-" * 50)
    print("Query: 'validate format trim string check empty convert'")
    print()

    graph_result = forge.compose_graph("validate format trim string check empty convert")

    print("RESULT: Block Graph (NOT CODE)")
    print("-" * 50)

    if graph_result.get("graph"):
        graph = graph_result["graph"]
        print(f"Graph Valid: {graph['is_valid']}")
        print(f"Total Trust Score: {graph['total_trust_score']:.2f}")
        print(f"Number of Nodes: {len(graph['nodes'])}")
        print()
        print("Blocks in Composition Graph:")
        for node in graph['nodes'][:10]:
            print(f"  [{node['position']}] {node['block_name']}")
            print(f"      Intent: {node['intent'][:50]}...")

        if len(graph['nodes']) > 10:
            print(f"  ... and {len(graph['nodes']) - 10} more blocks")
    else:
        print("Composition in progress - blocks available for assembly")

    print()

    print("STEP 6: Library Breakdown by Category")
    print("-" * 50)

    categories = [
        "string", "list", "validation", "conversion",
        "comparison", "logic", "date", "time"
    ]

    for category in categories:
        search_result = forge.search_by_intent(category, limit=50)
        count = len(search_result.get("blocks_found", []))
        if count > 0:
            print(f"  {category.capitalize()}: {count} blocks")

    print()

    print("=" * 70)
    print("EXPANDED LIBRARY DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("SUMMARY:")
    print(f"  - {len(source_modules)} source modules ingested")
    print(f"  - {total_created} blocks created")
    print(f"  - {stats['storage']['average_trust']:.2f} average trust score")
    print()
    print("CAPABILITIES NOW AVAILABLE:")
    print("  - String manipulation (trim, split, join, replace, etc.)")
    print("  - Collection operations (flatten, unique, sort, chunk, etc.)")
    print("  - Data validation (email, URL, phone, patterns, etc.)")
    print("  - Type conversions (int, float, string, boolean, etc.)")
    print("  - Comparison logic (equals, between, clamp, coalesce, etc.)")
    print("  - Date/time utilities (days between, leap year, format, etc.)")
    print("  - Math & statistics (sqrt, median, variance, trig, etc.)")
    print("  - Path utilities (join path, get extension, is_image, etc.)")
    print("  - Data parsing (JSON, CSV, key-value, nested dict, etc.)")
    print("  - Encoding & hashing (MD5, SHA256, base64, URL encode, etc.)")
    print("  - URL utilities (parse URL, query strings, domains, etc.)")
    print("  - Text analysis (word count, reading time, lexical diversity)")
    print("  - Color utilities (hex to RGB, blend, brightness, etc.)")
    print("  - Formatting (currency, bytes, duration, ordinals, etc.)")
    print("  - Array operations (matrix multiply, transpose, vectors, etc.)")
    print("  - Security (sanitize, mask, detect injection, etc.)")
    print("  - HTTP utilities (status codes, MIME types, headers, cookies)")
    print("  - File type detection (extensions, magic bytes, categories)")
    print("  - Cryptography helpers (JWT, HMAC, base64, hashing patterns)")
    print("  - Data transformation (normalize, pivot, aggregate, window)")
    print("  - Regex utilities (pattern building, extraction, replacement)")
    print("  - UUID utilities (validation, parsing, version detection)")
    print("  - Geolocation (haversine distance, bearing, coordinates)")
    print("  - Caching utilities (TTL, keys, eviction, ETag, hit rate)")
    print("  - Rate limiting (token bucket, sliding window, backoff)")
    print("  - Email utilities (validation, parsing, masking, mailto)")
    print("  - Configuration (env parsing, feature flags, DSN parsing)")
    print("  - Pagination (offset/limit, cursor, page calculations)")
    print("  - Slug utilities (URL slugs, base62/36 IDs, checksum)")
    print("  - Money utilities (currency formatting, tax, interest)")
    print("  - Phone utilities (parsing, formatting, validation)")
    print("  - Markdown utilities (formatting, parsing, TOC generation)")
    print()
    print("AI can now compose block graphs across all these domains.")
    print("This is the foundation for building anything - from validated blocks.")

    return {
        "module_results": module_results,
        "library_stats": stats,
        "total_created": total_created,
        "graph_result": graph_result,
    }


if __name__ == "__main__":
    demonstrate_expanded_library()
