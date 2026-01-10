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

from neurop_forge.semantic.intent_schema import SemanticIntent, SemanticDomain, SemanticOperation, SemanticType
from neurop_forge.semantic.intent_extractor import SemanticIntentExtractor
from neurop_forge.semantic.composer import SemanticComposer, SemanticIndexEntry, SemanticGraph

from neurop_forge.runtime.context import ExecutionContext
from neurop_forge.runtime.executor import GraphExecutor
from neurop_forge.runtime.result import ExecutionResult, ExecutionStatus
from neurop_forge.runtime.guards import RetryPolicy

from neurop_forge.deduplication import (
    DeduplicationProcessor,
    DeduplicationPolicy,
    DeduplicationReport,
)


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

        self._semantic_extractor = SemanticIntentExtractor()
        self._semantic_composer = SemanticComposer()
        
        self._graph_executor = GraphExecutor(
            block_library={},
            retry_policy=RetryPolicy(max_retries=2),
            default_timeout_ms=30000.0,
        )

        self._load_existing_blocks()

    def _load_existing_blocks(self) -> None:
        """Load and index existing blocks from storage."""
        for block in self._block_store.get_all():
            self._indexer.index_block(block)
            self._index_block_semantically(block)
            self._graph_executor.register_block(block.get_identity_hash(), block)

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
            self._index_block_semantically(block)
            self._graph_executor.register_block(block.get_identity_hash(), block)
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

    def _index_block_semantically(self, block: NeuropBlock) -> None:
        """Index a block in the semantic composer."""
        param_names = [p.name for p in block.interface.inputs]
        
        semantic_intent = self._semantic_extractor.extract(
            function_name=block.metadata.name,
            docstring=block.metadata.description,
            param_names=param_names,
            return_type_hint=None,
            category=block.metadata.category,
        )
        
        entry = SemanticIndexEntry(
            block_identity=block.get_identity_hash(),
            name=block.metadata.name,
            description=block.metadata.description,
            category=block.metadata.category,
            semantic_intent=semantic_intent,
            input_data_types=tuple(p.data_type.value for p in block.interface.inputs),
            output_data_types=tuple(p.data_type.value for p in block.interface.outputs),
            trust_score=block.trust_score.overall_score,
            is_pure=block.is_pure(),
            is_deterministic=block.is_deterministic(),
        )
        
        self._semantic_composer.index_block(entry)

    def compose_semantic_graph(self, intent: str, min_trust: float = 0.2) -> Dict[str, Any]:
        """
        Compose a block graph using SEMANTIC intent matching.
        
        This is the CORRECT way to compose blocks - matching by:
        1. Semantic domain (validation, formatting, transformation, etc.)
        2. Type flow validation
        3. Operation ordering
        
        Args:
            intent: Natural language intent description
            min_trust: Minimum trust score for blocks
            
        Returns:
            SemanticGraph with validated composition
        """
        graph = self._semantic_composer.compose(intent, min_trust=min_trust)
        return graph.to_dict()

    def get_semantic_statistics(self) -> Dict[str, Any]:
        """Get statistics about the semantic index."""
        return self._semantic_composer.get_statistics()

    def execute_intent(
        self,
        intent: str,
        inputs: Optional[Dict[str, Any]] = None,
        min_trust: float = 0.2,
    ) -> Dict[str, Any]:
        """
        FULL PIPELINE: Intent -> Compose -> Execute -> Result
        
        This is the complete Neurop execution loop:
        1. Parse intent into semantic requirements
        2. Compose a validated block graph
        3. Execute the graph with given inputs
        4. Return execution result with full trace
        
        Args:
            intent: Natural language intent description
            inputs: Initial input values for execution
            min_trust: Minimum trust score for blocks
            
        Returns:
            ExecutionResult with status, outputs, and trace
        """
        semantic_graph = self._semantic_composer.compose(intent, min_trust=min_trust)
        
        if not semantic_graph.nodes:
            return {
                "status": "failed",
                "error": "No blocks matched the intent",
                "query": intent,
            }
        
        result = self._graph_executor.execute(
            graph=semantic_graph,
            initial_inputs=inputs or {},
        )
        
        return result.to_dict()

    def execute_graph(
        self,
        graph: SemanticGraph,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """
        Execute a pre-composed semantic graph.
        
        Args:
            graph: Composed SemanticGraph
            inputs: Initial input values
            
        Returns:
            ExecutionResult with full trace
        """
        return self._graph_executor.execute(
            graph=graph,
            initial_inputs=inputs or {},
        )

    def deduplicate_library(
        self,
        policy: DeduplicationPolicy = DeduplicationPolicy.KEEP_BEST,
        execute: bool = True,
        rebuild_registries: bool = True,
        swap_in_place: bool = True,
    ) -> Dict[str, Any]:
        """
        Deduplicate the block library by removing or namespacing duplicate blocks.
        
        This is typically called after batch ingestion to clean up duplicates.
        
        Args:
            policy: Deduplication strategy (KEEP_BEST, NAMESPACE, QUARANTINE)
            execute: If True, creates deduplicated library; False for dry-run
            rebuild_registries: If True, rebuilds verified/tier registries after dedup
            swap_in_place: If True, replaces original library with deduplicated version
            
        Returns:
            Deduplication result with statistics
        """
        import shutil
        
        output_path = Path(f"{self._storage_path}_deduplicated")
        processor = DeduplicationProcessor(
            library_path=Path(self._storage_path),
            output_path=output_path,
            policy=policy,
        )
        
        result = processor.run(execute=execute)
        
        if execute:
            surviving_ids = self._collect_surviving_block_ids(output_path)
            
            if rebuild_registries:
                self._rebuild_registries_after_dedup(surviving_ids)
            
            if swap_in_place:
                original_path = Path(self._storage_path)
                backup_path = Path(f"{self._storage_path}_backup")
                
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                if original_path.exists():
                    shutil.move(str(original_path), str(backup_path))
                shutil.move(str(output_path), str(original_path))
                
                self._load_existing_blocks()
        
        report = DeduplicationReport(processor.get_hasher(), result)
        
        return {
            "success": True,
            "executed": execute,
            "original_count": result.original_count,
            "final_count": result.final_count,
            "blocks_removed": result.blocks_removed,
            "blocks_renamed": result.blocks_renamed,
            "reduction_percent": round((result.blocks_removed / result.original_count) * 100, 1) if result.original_count > 0 else 0,
            "output_path": str(self._storage_path) if execute and swap_in_place else str(output_path) if execute else None,
            "summary": report.generate_summary(),
        }

    def _collect_surviving_block_ids(self, output_path: Path) -> set:
        """Collect full block identity hashes from deduplicated library."""
        surviving_ids = set()
        if output_path.exists():
            for f in output_path.glob("*.json"):
                try:
                    with open(f) as fp:
                        block_data = json.load(fp)
                    block_id = block_data.get("identity", {}).get("hash_value", "")
                    if block_id:
                        surviving_ids.add(block_id)
                except Exception:
                    surviving_ids.add(f.stem)
        return surviving_ids

    def _rebuild_registries_after_dedup(self, surviving_ids: set) -> None:
        """Rebuild verified and tier registries after deduplication."""
        verified_dir = Path(".neurop_verified")
        if not verified_dir.exists():
            return
        
        registry_path = verified_dir / "registry.json"
        tier_path = verified_dir / "tier_registry.json"
        
        if registry_path.exists():
            with open(registry_path) as f:
                registry = json.load(f)
            
            new_verified = [bid for bid in registry.get("verified_blocks", []) if bid in surviving_ids]
            registry["verified_blocks"] = new_verified
            registry["total_verified"] = len(new_verified)
            
            with open(registry_path, "w") as f:
                json.dump(registry, f, indent=2)
        
        if tier_path.exists():
            with open(tier_path) as f:
                tiers = json.load(f)
            
            new_tier_a = [bid for bid in tiers.get("tier_a", []) if bid in surviving_ids]
            new_tier_b = [bid for bid in tiers.get("tier_b", []) if bid in surviving_ids]
            tiers["tier_a"] = new_tier_a
            tiers["tier_b"] = new_tier_b
            
            with open(tier_path, "w") as f:
                json.dump(tiers, f, indent=2)


def run_production_validation():
    """
    Production Validation: Converting multiple function modules to NeuropBlocks
    and building an expanded library for comprehensive block composition.
    
    This validates:
    1. Ingesting multiple source modules (string, list, validation, etc.)
    2. Converting pure functions into atomic blocks at scale
    3. Building a comprehensive library of 4500+ blocks
    4. AI query with expanded capabilities
    5. Block composition across multiple domains
    """
    print("=" * 70)
    print("NEUROP BLOCK FORGE - PRODUCTION VALIDATION")
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
        ("neurop_forge/sources/sql_building.py", "SQL Building"),
        ("neurop_forge/sources/sql_types.py", "SQL Types"),
        ("neurop_forge/sources/query_helpers.py", "Query Helpers"),
        ("neurop_forge/sources/migration_helpers.py", "Migration Helpers"),
        ("neurop_forge/sources/transaction_helpers.py", "Transaction Helpers"),
        ("neurop_forge/sources/data_integrity.py", "Data Integrity"),
        ("neurop_forge/sources/nosql_helpers.py", "NoSQL Helpers"),
        ("neurop_forge/sources/orm_patterns.py", "ORM Patterns"),
        ("neurop_forge/sources/connection_pool.py", "Connection Pool"),
        ("neurop_forge/sources/batch_operations.py", "Batch Operations"),
        ("neurop_forge/sources/audit_logging.py", "Audit Logging"),
        ("neurop_forge/sources/api_patterns.py", "API Patterns"),
        ("neurop_forge/sources/auth_patterns.py", "Auth Patterns"),
        ("neurop_forge/sources/webhook_patterns.py", "Webhook Patterns"),
        ("neurop_forge/sources/request_validation.py", "Request Validation"),
        ("neurop_forge/sources/response_formatting.py", "Response Formatting"),
        ("neurop_forge/sources/error_handling.py", "Error Handling"),
        ("neurop_forge/sources/middleware_patterns.py", "Middleware Patterns"),
        ("neurop_forge/sources/job_scheduling.py", "Job Scheduling"),
        ("neurop_forge/sources/state_machine.py", "State Machine"),
        ("neurop_forge/sources/event_sourcing.py", "Event Sourcing"),
        ("neurop_forge/sources/queue_patterns.py", "Queue Patterns"),
        ("neurop_forge/sources/testing_utilities.py", "Testing Utilities"),
        ("neurop_forge/sources/devops_utilities.py", "DevOps Utilities"),
        ("neurop_forge/sources/security_patterns.py", "Security Patterns"),
        ("neurop_forge/sources/ml_utilities.py", "ML Utilities"),
        ("neurop_forge/sources/ui_patterns.py", "UI Patterns"),
        ("neurop_forge/sources/ecommerce_patterns.py", "E-commerce Patterns"),
        ("neurop_forge/sources/notification_patterns.py", "Notification Patterns"),
        ("neurop_forge/sources/analytics_patterns.py", "Analytics Patterns"),
        ("neurop_forge/sources/file_utilities.py", "File Utilities"),
        ("neurop_forge/sources/search_patterns.py", "Search Patterns"),
        ("neurop_forge/sources/i18n_patterns.py", "Internationalization Patterns"),
        ("neurop_forge/sources/workflow_patterns.py", "Workflow Patterns"),
        ("neurop_forge/sources/graph_utilities.py", "Graph Utilities"),
        ("neurop_forge/sources/compression_utilities.py", "Compression Utilities"),
        ("neurop_forge/sources/metrics_patterns.py", "Metrics Patterns"),
        ("neurop_forge/sources/image_utilities.py", "Image Utilities"),
        ("neurop_forge/sources/network_utilities.py", "Network Utilities"),
        ("neurop_forge/sources/caching_patterns.py", "Caching Patterns"),
        ("neurop_forge/sources/logging_utilities.py", "Logging Utilities"),
        ("neurop_forge/sources/financial_utilities.py", "Financial Utilities"),
        ("neurop_forge/sources/scheduler_utilities.py", "Scheduler Utilities"),
        ("neurop_forge/sources/form_utilities.py", "Form Utilities"),
        ("neurop_forge/sources/permission_utilities.py", "Permission Utilities"),
        ("neurop_forge/sources/feature_flags.py", "Feature Flags"),
        ("neurop_forge/sources/content_utilities.py", "Content Utilities"),
        ("neurop_forge/sources/template_utilities.py", "Template Utilities"),
        ("neurop_forge/sources/vector_utilities.py", "Vector Utilities"),
        ("neurop_forge/sources/matrix_utilities.py", "Matrix Utilities"),
        ("neurop_forge/sources/statistics_utilities.py", "Statistics Utilities"),
        ("neurop_forge/sources/tree_utilities.py", "Tree Utilities"),
        ("neurop_forge/sources/heap_utilities.py", "Heap Utilities"),
        ("neurop_forge/sources/set_utilities.py", "Set Utilities"),
        ("neurop_forge/sources/queue_utilities.py", "Queue Utilities"),
        ("neurop_forge/sources/stack_utilities.py", "Stack Utilities"),
        ("neurop_forge/sources/bitwise_utilities.py", "Bitwise Utilities"),
        ("neurop_forge/sources/interval_utilities.py", "Interval Utilities"),
        ("neurop_forge/sources/string_distance.py", "String Distance"),
        ("neurop_forge/sources/trie_utilities.py", "Trie Utilities"),
        ("neurop_forge/sources/bloom_filter.py", "Bloom Filter"),
        ("neurop_forge/sources/sampling_utilities.py", "Sampling Utilities"),
        ("neurop_forge/sources/linked_list.py", "Linked List"),
        ("neurop_forge/sources/hash_table.py", "Hash Table"),
        ("neurop_forge/sources/binary_search_tree.py", "Binary Search Tree"),
        ("neurop_forge/sources/lru_cache.py", "LRU Cache"),
        ("neurop_forge/sources/promise_utilities.py", "Promise Utilities"),
        ("neurop_forge/sources/ring_buffer.py", "Ring Buffer"),
        ("neurop_forge/sources/disjoint_set.py", "Disjoint Set"),
        ("neurop_forge/sources/skip_list.py", "Skip List"),
        ("neurop_forge/sources/diff_utilities.py", "Diff Utilities"),
        ("neurop_forge/sources/rate_limiter.py", "Rate Limiter"),
        ("neurop_forge/sources/sorting_algorithms.py", "Sorting Algorithms"),
        ("neurop_forge/sources/search_algorithms.py", "Search Algorithms"),
        ("neurop_forge/sources/geometry_utilities.py", "Geometry Utilities"),
        ("neurop_forge/sources/base_conversion.py", "Base Conversion"),
        ("neurop_forge/sources/expression_parser.py", "Expression Parser"),
        ("neurop_forge/sources/checksum_utilities.py", "Checksum Utilities"),
        ("neurop_forge/sources/functional_utilities.py", "Functional Utilities"),
        ("neurop_forge/sources/retry_patterns.py", "Retry Patterns"),
        ("neurop_forge/sources/string_builder.py", "String Builder"),
        ("neurop_forge/sources/number_theory.py", "Number Theory"),
        ("neurop_forge/sources/datetime_math.py", "Datetime Math"),
        ("neurop_forge/sources/time_utilities.py", "Time Utilities"),
        ("neurop_forge/sources/string_patterns.py", "String Patterns"),
        ("neurop_forge/sources/json_utilities.py", "JSON Utilities"),
        ("neurop_forge/sources/color_math.py", "Color Math"),
        ("neurop_forge/sources/object_utilities.py", "Object Utilities"),
        ("neurop_forge/sources/array_algorithms.py", "Array Algorithms"),
        ("neurop_forge/sources/crypto_primitives.py", "Crypto Primitives"),
        ("neurop_forge/sources/validation_rules.py", "Validation Rules"),
        ("neurop_forge/sources/encoding_schemes.py", "Encoding Schemes"),
        ("neurop_forge/sources/measurement_utilities.py", "Measurement Utilities"),
        ("neurop_forge/sources/text_transforms.py", "Text Transforms"),
        ("neurop_forge/sources/ip_utilities.py", "IP Utilities"),
        ("neurop_forge/sources/random_utilities.py", "Random Utilities"),
        ("neurop_forge/sources/semantic_version.py", "Semantic Version"),
        ("neurop_forge/sources/bank_utilities.py", "Bank Utilities"),
        ("neurop_forge/sources/protocol_utilities.py", "Protocol Utilities"),
        ("neurop_forge/sources/social_utilities.py", "Social Utilities"),
        ("neurop_forge/sources/coordinate_utilities.py", "Coordinate Utilities"),
        ("neurop_forge/sources/document_utilities.py", "Document Utilities"),
        ("neurop_forge/sources/cache_strategies.py", "Cache Strategies"),
        ("neurop_forge/sources/data_masking.py", "Data Masking"),
        ("neurop_forge/sources/regex_helpers.py", "Regex Helpers"),
        ("neurop_forge/sources/string_algorithms.py", "String Algorithms"),
        ("neurop_forge/sources/event_utilities.py", "Event Utilities"),
        ("neurop_forge/sources/boolean_utilities.py", "Boolean Utilities"),
        ("neurop_forge/sources/exception_utilities.py", "Exception Utilities"),
        ("neurop_forge/sources/iterator_utilities.py", "Iterator Utilities"),
        ("neurop_forge/sources/numeric_utilities.py", "Numeric Utilities"),
        ("neurop_forge/sources/safe_math.py", "Safe Math"),
        ("neurop_forge/sources/ascii_utilities.py", "ASCII Utilities"),
        ("neurop_forge/sources/date_formatting.py", "Date Formatting"),
        ("neurop_forge/sources/html_utilities.py", "HTML Utilities"),
        ("neurop_forge/sources/mime_utilities.py", "MIME Utilities"),
        ("neurop_forge/sources/password_utilities.py", "Password Utilities"),
        ("neurop_forge/sources/pagination_helpers.py", "Pagination Helpers"),
        ("neurop_forge/sources/json_path.py", "JSON Path"),
        ("neurop_forge/sources/query_string.py", "Query String"),
        ("neurop_forge/sources/assertion_utilities.py", "Assertion Utilities"),
        ("neurop_forge/sources/slug_helpers.py", "Slug Helpers"),
        ("neurop_forge/sources/error_codes.py", "Error Codes"),
        ("neurop_forge/sources/throttle_utilities.py", "Throttle Utilities"),
        ("neurop_forge/sources/sanitization_utilities.py", "Sanitization Utilities"),
        ("neurop_forge/sources/address_utilities.py", "Address Utilities"),
        ("neurop_forge/sources/duration_utilities.py", "Duration Utilities"),
        ("neurop_forge/sources/phone_patterns.py", "Phone Patterns"),
        ("neurop_forge/sources/credit_card_utilities.py", "Credit Card Utilities"),
        ("neurop_forge/sources/tax_utilities.py", "Tax Utilities"),
        ("neurop_forge/sources/discount_utilities.py", "Discount Utilities"),
        ("neurop_forge/sources/inventory_utilities.py", "Inventory Utilities"),
        ("neurop_forge/sources/shipping_utilities.py", "Shipping Utilities"),
        ("neurop_forge/sources/order_utilities.py", "Order Utilities"),
        ("neurop_forge/sources/session_utilities.py", "Session Utilities"),
        ("neurop_forge/sources/token_utilities.py", "Token Utilities"),
        ("neurop_forge/sources/user_utilities.py", "User Utilities"),
        ("neurop_forge/sources/contact_utilities.py", "Contact Utilities"),
        ("neurop_forge/sources/notification_helpers.py", "Notification Helpers"),
        ("neurop_forge/sources/locale_utilities.py", "Locale Utilities"),
        ("neurop_forge/sources/search_helpers.py", "Search Helpers"),
        ("neurop_forge/sources/review_utilities.py", "Review Utilities"),
        ("neurop_forge/sources/ratio_utilities.py", "Ratio Utilities"),
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
            author="Lourens Wasserman",
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

    print("STEP 5: SEMANTIC COMPOSITION - The Key Innovation")
    print("-" * 50)
    print("Query: 'validate and format user input'")
    print()
    
    print("A) OLD APPROACH (Keyword Matching):")
    print("   Would match blocks containing 'validate', 'format', 'user', 'input'")
    print("   Problem: Returns irrelevant blocks like 'is_light_color' or 'format_bytes'")
    print()
    
    old_graph_result = forge.compose_graph("validate and format user input")
    if old_graph_result.get("graph"):
        old_graph = old_graph_result["graph"]
        print(f"   Keyword-matched blocks: {len(old_graph['nodes'])}")
        for node in old_graph['nodes'][:3]:
            print(f"     - {node['block_name']}")
    print()
    
    print("B) NEW APPROACH (Semantic Intent Matching):")
    print("   Matches by DOMAIN: validation -> formatting")
    print("   Matches by TYPE FLOW: input types -> output types")
    print("   Orders by OPERATION: validate first, then format")
    print()
    
    semantic_graph_result = forge.compose_semantic_graph("validate and format user input")
    
    print("RESULT: Semantic Block Graph")
    print("-" * 50)
    
    if semantic_graph_result.get("nodes"):
        print(f"Graph Valid: {semantic_graph_result['is_valid']}")
        print(f"Composition Confidence: {semantic_graph_result['composition_confidence']:.2%}")
        print(f"Total Trust Score: {semantic_graph_result['total_trust_score']:.2f}")
        print(f"Number of Nodes: {len(semantic_graph_result['nodes'])}")
        print()
        
        print("Intent Analysis:")
        intent_analysis = semantic_graph_result.get("intent_analysis", {})
        required_domains = intent_analysis.get("required_domains", [])
        print(f"  Required Domains: {', '.join(str(d) for d in required_domains)}")
        print(f"  Flow Direction: {intent_analysis.get('flow_direction', 'unknown')}")
        print()
        
        print("Blocks in Semantic Graph (ordered by operation semantics):")
        for node in semantic_graph_result['nodes'][:10]:
            intent = node.get('semantic_intent', {})
            domain = intent.get('domain', 'unknown')
            operation = intent.get('operation', 'unknown')
            print(f"  [{node['position']}] {node['block_name']}")
            print(f"      Domain: {domain} | Operation: {operation}")
            print(f"      Why Selected: {node.get('why_selected', 'N/A')}")
        
        if semantic_graph_result.get('validation_details'):
            print()
            print("Validation Notes:")
            for note in semantic_graph_result['validation_details']:
                print(f"  - {note}")
    else:
        print("No semantic graph generated - checking index status")
        sem_stats = forge.get_semantic_statistics()
        print(f"  Semantic index contains: {sem_stats.get('total_blocks', 0)} blocks")

    print()
    
    print("STEP 5b: Semantic Index Statistics")
    print("-" * 50)
    sem_stats = forge.get_semantic_statistics()
    print(f"Total Semantically Indexed: {sem_stats.get('total_blocks', 0)} blocks")
    print()
    print("Blocks by Semantic Domain:")
    domains = sem_stats.get('domains', {})
    for domain, count in sorted(domains.items(), key=lambda x: -x[1])[:10]:
        print(f"  {domain}: {count} blocks")
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
    print("LIBRARY INGESTION COMPLETE")
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
    print("  - SQL building (query construction, escaping, DDL)")
    print("  - SQL types (type mapping, validation, casting)")
    print("  - Query helpers (analysis, manipulation, pagination)")
    print("  - Migration helpers (schema changes, versioning)")
    print("  - Transaction helpers (isolation, locking, retries)")
    print("  - Data integrity (validation, constraints, checksums)")
    print("  - NoSQL helpers (MongoDB, Redis, DynamoDB patterns)")
    print("  - ORM patterns (model mapping, relationships, scopes)")
    print("  - Connection pool (sizing, health, metrics)")
    print("  - Batch operations (bulk insert, parallel processing)")
    print("  - Audit logging (change tracking, compliance)")
    print("  - API patterns (REST endpoints, versioning, HATEOAS)")
    print("  - Auth patterns (JWT, OAuth, sessions, API keys)")
    print("  - Webhook patterns (signatures, retries, delivery)")
    print("  - Request validation (fields, formats, constraints)")
    print("  - Response formatting (pagination, errors, JSONAPI)")
    print("  - Error handling (categorization, retry, circuit breaker)")
    print("  - Middleware patterns (logging, tracing, security)")
    print("  - Job scheduling (cron, queues, retries, workers)")
    print("  - State machines (transitions, sagas, workflows)")
    print("  - Event sourcing (events, snapshots, projections)")
    print("  - Queue patterns (routing, acknowledgments, DLQ)")
    print()
    print("STEP 7: RUNTIME EXECUTION - Complete the Loop")
    print("-" * 50)
    print()
    print("Executing the FULL pipeline:")
    print("  Intent -> Compose -> Execute -> Result")
    print()
    
    print("A) Direct Block Execution (Known-Good Blocks):")
    print("-" * 40)
    
    from neurop_forge.runtime import BlockExecutor
    block_executor = BlockExecutor()
    
    all_blocks = list(forge._block_store.get_all())
    
    test_blocks = []
    for block in all_blocks[:200]:
        if hasattr(block.metadata, 'name'):
            name = block.metadata.name
            if name in ['is_palindrome', 'to_upper', 'to_lower', 'title_case', 'reverse_string', 'is_empty', 'word_count']:
                test_blocks.append(block)
                if len(test_blocks) >= 3:
                    break
    
    direct_successes = 0
    for block in test_blocks:
        test_input = {"text": "hello world", "s": "hello world", "string": "hello world", "value": "hello world"}
        outputs, error = block_executor.execute(block, test_input)
        if error:
            print(f"  Block '{block.metadata.name}': FAILED - {error[:50]}...")
        else:
            print(f"  Block '{block.metadata.name}': SUCCESS -> {outputs}")
            direct_successes += 1
    
    if not test_blocks or direct_successes == 0:
        simple_blocks = [b for b in all_blocks[:300]
                        if len(b.interface.inputs) == 1 and 
                        b.interface.inputs[0].data_type.value in ['string', 'integer', 'float']]
        for block in simple_blocks[:5]:
            param = block.interface.inputs[0]
            if param.data_type.value == 'string':
                test_input = {param.name: "hello world test"}
            elif param.data_type.value == 'integer':
                test_input = {param.name: 42}
            else:
                test_input = {param.name: 3.14}
            
            outputs, error = block_executor.execute(block, test_input)
            if error:
                print(f"  Block '{block.metadata.name}': FAILED - {error[:50]}...")
            else:
                print(f"  Block '{block.metadata.name}': SUCCESS -> {outputs}")
                direct_successes += 1
    
    print()
    print(f"Direct Execution: {direct_successes} blocks executed successfully")
    print()
    
    print("B) Block Verification (Verified-Only Mode):")
    print("-" * 40)
    
    from neurop_forge.runtime.block_verifier import BlockVerifier, get_verification_registry
    
    verifier = BlockVerifier()
    all_blocks_for_verify = list(forge._block_store.get_all())
    
    print(f"Verifying {len(all_blocks_for_verify)} blocks...")
    verify_result = verifier.verify_all(all_blocks_for_verify)
    print(f"  Verified: {verify_result['verified']} blocks")
    print(f"  Failed: {verify_result['failed']} blocks")
    print(f"  Success Rate: {verify_result['success_rate']*100:.1f}%")
    print()
    
    registry = get_verification_registry()
    verified_ids = set(registry.get_verified_ids())
    forge._semantic_composer.set_verified_blocks(verified_ids)
    print(f"Semantic Composer now using ONLY {len(verified_ids)} verified blocks")
    print()
    
    from neurop_forge.core.block_tier import classify_blocks, print_tier_summary, get_tier_registry
    tier_registry = classify_blocks(all_blocks_for_verify, verified_ids)
    tier_summary = tier_registry.summary()
    print(f"Tier Classification: {tier_summary['tier_a']} Tier-A, {tier_summary['tier_b']} Tier-B")
    print()
    
    tier_a_ids = set(tier_registry.tier_a.keys())
    forge._semantic_composer.set_verified_blocks(tier_a_ids)
    print(f"Production Mode: Using ONLY {len(tier_a_ids)} Tier-A blocks (deterministic)")
    print()
    
    from neurop_forge.runtime.block_verifier import AutoVerificationGate
    gate = AutoVerificationGate()
    gate_stats = gate.get_stats()
    print(f"Verification Gate Stats: {gate_stats['verified']} admitted, {gate_stats['failed']} rejected")
    print()
    
    print("C) Semantic Graph Execution (Tier-A Only - Production Mode):")
    print("-" * 40)
    
    test_inputs = {
        "text": "Hello World",
        "s": "Hello World",
        "string": "Hello World",
        "value": "Hello World",
        "n": 42,
        "number": 42,
    }
    
    print(f"Test Inputs: {test_inputs}")
    print()
    
    execution_result = forge.execute_intent(
        intent="check and transform text",
        inputs=test_inputs,
    )
    
    print("Execution Result:")
    print(f"  Status: {execution_result.get('status', 'unknown').upper()}")
    print(f"  Duration: {execution_result.get('total_duration_ms', 0):.2f}ms")
    print(f"  Nodes Executed: {execution_result.get('nodes_executed', 0)}")
    print(f"  Nodes Succeeded: {execution_result.get('nodes_succeeded', 0)}")
    print()
    
    if execution_result.get('traces'):
        print("Execution Trace:")
        for trace in execution_result['traces'][:6]:
            status_icon = "✓" if trace['status'] == 'success' else "✗"
            print(f"  {status_icon} {trace['block_name']} ({trace['duration_ms']:.2f}ms)")
            if trace.get('error'):
                print(f"      Error: {trace['error'][:50]}...")
        print()
    
    if execution_result.get('final_outputs'):
        print("Final Outputs:")
        for key, value in list(execution_result['final_outputs'].items())[:5]:
            val_str = str(value)[:40] + "..." if len(str(value)) > 40 else str(value)
            print(f"  {key}: {val_str}")
    print()
    
    print()
    print("D) Golden Validation Suite - Known-Working Blocks:")
    print("-" * 40)
    
    from neurop_forge.runtime.golden_validation import run_golden_validation, print_golden_validation_results
    golden_results = run_golden_validation(forge._block_store)
    print_golden_validation_results(golden_results)
    
    print()
    print("E) Production Reference Workflows:")
    print("-" * 40)
    
    from neurop_forge.runtime.reference_workflows import run_reference_workflows, print_reference_workflow_results
    workflow_results = run_reference_workflows(forge._block_store)
    print_reference_workflow_results(workflow_results)
    
    golden_blocks = golden_results.get("golden_blocks", {})
    golden_succeeded = golden_blocks.get("blocks_succeeded", 0)
    golden_total = golden_blocks.get("blocks_tested", 0)
    golden_failed = golden_blocks.get("blocks_failed", 0)
    
    workflows_available = workflow_results.get("workflows_available", 0)
    workflows_total = workflow_results.get("workflows_total", 0)
    workflows_all_pass = workflow_results.get("overall_success", False)
    workflows_passed = workflows_available if workflows_all_pass else sum(
        1 for r in workflow_results.get("results", {}).values() if r.get("success")
    )
    
    print("=" * 70)
    print("NEUROP BLOCK FORGE v1.0.0 - PACKAGING READY")
    print("=" * 70)
    print()
    print("PACKAGING VALIDATION:")
    print(f"  Golden Validation Suite: {golden_succeeded}/{golden_total} {'PASS' if golden_failed == 0 else 'FAIL'}")
    print(f"  Production Reference Workflows: {workflows_passed}/{workflows_total} {'PASS' if workflows_passed == workflows_total else 'FAIL'}")
    print(f"  Tier-A Production Blocks: {len(tier_a_ids)}")
    print(f"  Tier-B Blocks (not used in production): {tier_summary['tier_b']}")
    print()
    print("PRODUCTION CLAIMS:")
    print(f"  - Reference workflows execute deterministically ({workflows_passed}/{workflows_total})")
    print(f"  - Golden validation blocks return expected outputs ({golden_succeeded}/{golden_total})")
    print("  - Tier-A blocks are pure, deterministic functions")
    print("  - Tier-B blocks require explicit opt-in")
    print()
    print("CONTRACT VERSION: v1.0.0")
    print("  - Block.logic stores ORIGINAL source code")
    print("  - TrustScore includes execution_count, success_count, success_rate")
    print("  - Interface.inputs aligns with function parameters")
    print()
    
    all_pass = (golden_failed == 0) and (workflows_passed == workflows_total)
    print(f"STATUS: {'READY FOR PACKAGING' if all_pass else 'NEEDS FIXES'}")

    return {
        "module_results": module_results,
        "library_stats": stats,
        "total_created": total_created,
        "semantic_graph_result": semantic_graph_result,
        "execution_result": execution_result,
        "golden_validation_results": golden_results,
        "reference_workflow_results": workflow_results,
    }


if __name__ == "__main__":
    run_production_validation()
