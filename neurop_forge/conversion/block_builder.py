"""
Block builder for creating NeuropBlocks from classified intent units.

This module is responsible for producing ONLY valid NeuropBlocks.
Invalid blocks are rejected, not approximated.
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from neurop_forge.core.identity import IdentityAuthority, BlockIdentity
from neurop_forge.core.block_schema import (
    NeuropBlock, BlockInterface, BlockConstraints, BlockMetadata,
    BlockOwnership, ValidationRules, TrustScore, FailureModes,
    CompositionCompatibility, TypedParameter, DataType, PurityLevel,
    IOType, LicenseType, FailureMode, RiskLevel,
)
from neurop_forge.core.normalization import CodeNormalizer, NormalizationLevel
from neurop_forge.conversion.intent_classifier import ClassificationResult
from neurop_forge.parsing.intent_units import IntentUnit, IntentCategory


class BuildStatus(Enum):
    """Status of block building."""
    SUCCESS = "success"
    VALIDATION_FAILED = "validation_failed"
    INCOMPLETE_DATA = "incomplete_data"
    NON_ATOMIC = "non_atomic"
    REJECTED = "rejected"


@dataclass
class BuildResult:
    """Result of block building operation."""
    status: BuildStatus
    block: Optional[NeuropBlock]
    errors: Tuple[str, ...]
    warnings: Tuple[str, ...]
    build_duration_ms: float

    def is_success(self) -> bool:
        return self.status == BuildStatus.SUCCESS and self.block is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "block_identity": self.block.get_identity_hash() if self.block else None,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "build_duration_ms": self.build_duration_ms,
        }


class BlockBuilder:
    """
    Builder for creating valid NeuropBlocks from classified intent units.
    
    This builder enforces all schema requirements:
    - All required sections must be present
    - All types must be explicit
    - All constraints must be declared
    - Trust score must be non-zero
    
    Invalid blocks are REJECTED, never approximated.
    """

    TYPE_MAPPING: Dict[str, DataType] = {
        "int": DataType.INTEGER,
        "integer": DataType.INTEGER,
        "float": DataType.FLOAT,
        "double": DataType.FLOAT,
        "number": DataType.FLOAT,
        "str": DataType.STRING,
        "string": DataType.STRING,
        "text": DataType.STRING,
        "bool": DataType.BOOLEAN,
        "boolean": DataType.BOOLEAN,
        "list": DataType.LIST,
        "array": DataType.LIST,
        "dict": DataType.DICT,
        "object": DataType.DICT,
        "map": DataType.DICT,
        "none": DataType.NONE,
        "null": DataType.NONE,
        "void": DataType.NONE,
        "any": DataType.ANY,
        "bytes": DataType.BYTES,
    }

    CATEGORY_TO_BLOCK_CATEGORY: Dict[IntentCategory, str] = {
        IntentCategory.ARITHMETIC: "arithmetic",
        IntentCategory.STRING_MANIPULATION: "string",
        IntentCategory.LIST_OPERATION: "collection",
        IntentCategory.DICT_OPERATION: "collection",
        IntentCategory.COMPARISON: "comparison",
        IntentCategory.CONVERSION: "conversion",
        IntentCategory.VALIDATION: "validation",
        IntentCategory.TRANSFORMATION: "transformation",
        IntentCategory.AGGREGATION: "aggregation",
        IntentCategory.FILTERING: "filtering",
        IntentCategory.SORTING: "sorting",
        IntentCategory.SEARCHING: "searching",
        IntentCategory.IO_OPERATION: "io",
        IntentCategory.UTILITY: "utility",
        IntentCategory.UNKNOWN: "unknown",
    }

    def __init__(
        self,
        identity_authority: Optional[IdentityAuthority] = None,
        normalizer: Optional[CodeNormalizer] = None,
    ):
        self._identity_authority = identity_authority or IdentityAuthority()
        self._normalizer = normalizer or CodeNormalizer(NormalizationLevel.STANDARD)

    def build(
        self,
        classification: ClassificationResult,
        ownership: BlockOwnership,
        base_trust_score: float = 0.5,
    ) -> BuildResult:
        """
        Build a NeuropBlock from a classified intent unit.
        
        Args:
            classification: The classification result
            ownership: License and ownership information
            base_trust_score: Base trust score (0.0 to 1.0)
            
        Returns:
            BuildResult with the built block or errors
        """
        import time
        start_time = time.time()

        errors: List[str] = []
        warnings: List[str] = []

        intent_unit = classification.intent_unit

        if not classification.is_valid_for_block():
            return BuildResult(
                status=BuildStatus.VALIDATION_FAILED,
                block=None,
                errors=(
                    f"Classification not valid for block: "
                    f"confidence={classification.confidence:.2f}, "
                    f"atomic={classification.is_atomic}, "
                    f"requires_decomposition={classification.requires_decomposition}",
                ),
                warnings=(),
                build_duration_ms=(time.time() - start_time) * 1000,
            )

        if classification.requires_decomposition:
            return BuildResult(
                status=BuildStatus.NON_ATOMIC,
                block=None,
                errors=("Intent unit requires decomposition into atomic units",),
                warnings=(),
                build_duration_ms=(time.time() - start_time) * 1000,
            )

        try:
            interface = self._build_interface(intent_unit, classification)
        except ValueError as e:
            errors.append(f"Interface build failed: {e}")
            return BuildResult(
                status=BuildStatus.INCOMPLETE_DATA,
                block=None,
                errors=tuple(errors),
                warnings=tuple(warnings),
                build_duration_ms=(time.time() - start_time) * 1000,
            )

        constraints = self._build_constraints(intent_unit)

        if intent_unit.language == "python":
            normalized = self._normalizer.normalize_python(intent_unit.source)
        else:
            normalized = self._normalizer.normalize_javascript(intent_unit.source)

        try:
            identity = self._identity_authority.generate_identity(
                normalized_logic=normalized.normalized,
                interface=interface.to_dict(),
                constraints=constraints.to_dict(),
            )
        except ValueError as e:
            errors.append(f"Identity generation failed: {e}")
            return BuildResult(
                status=BuildStatus.VALIDATION_FAILED,
                block=None,
                errors=tuple(errors),
                warnings=tuple(warnings),
                build_duration_ms=(time.time() - start_time) * 1000,
            )

        metadata = self._build_metadata(intent_unit, classification)

        validation_rules = self._build_validation_rules(intent_unit, interface)

        trust_score = self._build_trust_score(
            intent_unit, classification, base_trust_score
        )

        failure_modes = self._build_failure_modes(intent_unit)

        composition = self._build_composition(classification)

        try:
            block = NeuropBlock(
                identity=identity.to_dict(),
                ownership=ownership,
                metadata=metadata,
                interface=interface,
                constraints=constraints,
                logic=normalized.normalized,
                validation_rules=validation_rules,
                trust_score=trust_score,
                failure_modes=failure_modes,
                composition=composition,
                sealed=True,
            )
        except ValueError as e:
            errors.append(f"Block creation failed: {e}")
            return BuildResult(
                status=BuildStatus.VALIDATION_FAILED,
                block=None,
                errors=tuple(errors),
                warnings=tuple(warnings),
                build_duration_ms=(time.time() - start_time) * 1000,
            )

        return BuildResult(
            status=BuildStatus.SUCCESS,
            block=block,
            errors=tuple(errors),
            warnings=tuple(warnings),
            build_duration_ms=(time.time() - start_time) * 1000,
        )

    def _build_interface(
        self,
        intent_unit: IntentUnit,
        classification: ClassificationResult,
    ) -> BlockInterface:
        """Build the interface specification."""
        inputs: List[TypedParameter] = []

        for param in intent_unit.parameters:
            name = param.get("name", "")
            if name in ("self", "cls"):
                continue

            type_str = param.get("type") or "any"
            data_type = self._map_type(type_str)

            typed_param = TypedParameter(
                name=name,
                data_type=data_type,
                description=f"Parameter {name}",
                optional=param.get("optional", False),
                default_value=param.get("default"),
            )
            inputs.append(typed_param)

        return_type_str = intent_unit.return_type or "any"
        return_data_type = self._map_type(return_type_str)

        outputs = [
            TypedParameter(
                name="result",
                data_type=return_data_type,
                description=f"Return value of {intent_unit.function_name}",
                optional=False,
            )
        ]

        return BlockInterface(
            inputs=tuple(inputs),
            outputs=tuple(outputs),
            description=intent_unit.intent.description,
        )

    def _map_type(self, type_str: str) -> DataType:
        """Map a type string to a DataType enum."""
        if not type_str:
            return DataType.ANY

        type_lower = type_str.lower().strip()

        for key, data_type in self.TYPE_MAPPING.items():
            if key in type_lower:
                return data_type

        if "[" in type_lower or "list" in type_lower:
            return DataType.LIST
        if "dict" in type_lower or "map" in type_lower:
            return DataType.DICT
        if "optional" in type_lower:
            return DataType.ANY

        return DataType.ANY

    def _build_constraints(self, intent_unit: IntentUnit) -> BlockConstraints:
        """Build the constraints specification."""
        if intent_unit.is_pure:
            purity = PurityLevel.PURE
        elif intent_unit.is_deterministic:
            purity = PurityLevel.DETERMINISTIC_WITH_SIDE_EFFECTS
        else:
            purity = PurityLevel.NON_DETERMINISTIC

        io_ops: Set[IOType] = set()
        for side_effect in intent_unit.side_effects:
            if "file" in side_effect.lower():
                io_ops.add(IOType.FILE_READ)
            elif "network" in side_effect.lower() or "fetch" in side_effect.lower():
                io_ops.add(IOType.NETWORK_READ)
            elif "console" in side_effect.lower() or "print" in side_effect.lower():
                io_ops.add(IOType.CONSOLE_OUTPUT)
            elif "random" in side_effect.lower():
                io_ops.add(IOType.RANDOM)
            elif "time" in side_effect.lower() or "date" in side_effect.lower():
                io_ops.add(IOType.TIME)

        if not io_ops:
            io_ops.add(IOType.NONE)

        return BlockConstraints(
            purity=purity,
            io_operations=frozenset(io_ops),
            side_effects=tuple(intent_unit.side_effects),
            deterministic=intent_unit.is_deterministic,
            thread_safe=intent_unit.is_pure,
            max_execution_time_ms=None,
            max_memory_bytes=None,
        )

    def _build_metadata(
        self,
        intent_unit: IntentUnit,
        classification: ClassificationResult,
    ) -> BlockMetadata:
        """Build the metadata section."""
        category = self.CATEGORY_TO_BLOCK_CATEGORY.get(
            classification.primary_category,
            "unknown"
        )

        return BlockMetadata(
            name=intent_unit.function_name,
            intent=intent_unit.intent.description,
            description=intent_unit.intent.description,
            category=category,
            tags=classification.semantic_tags,
            version="1.0.0",
            created_at=datetime.now(timezone.utc).isoformat(),
            language=intent_unit.language,
            source_file=intent_unit.source_location.get("file") if intent_unit.source_location else None,
            source_line_start=intent_unit.source_location.get("line_start") if intent_unit.source_location else None,
            source_line_end=intent_unit.source_location.get("line_end") if intent_unit.source_location else None,
        )

    def _build_validation_rules(
        self,
        intent_unit: IntentUnit,
        interface: BlockInterface,
    ) -> ValidationRules:
        """Build the validation rules section."""
        input_validators: List[str] = []
        for param in interface.inputs:
            if param.data_type != DataType.ANY:
                input_validators.append(
                    f"type({param.name}) == {param.data_type.value}"
                )
            if not param.optional:
                input_validators.append(f"{param.name} is not None")

        output_validators: List[str] = []
        for output in interface.outputs:
            if output.data_type != DataType.ANY:
                output_validators.append(
                    f"type(result) == {output.data_type.value}"
                )

        return ValidationRules(
            input_validators=tuple(input_validators),
            output_validators=tuple(output_validators),
            invariants=(),
            preconditions=tuple(input_validators),
            postconditions=tuple(output_validators),
        )

    def _build_trust_score(
        self,
        intent_unit: IntentUnit,
        classification: ClassificationResult,
        base_score: float,
    ) -> TrustScore:
        """Build the trust score section."""
        determinism_score = 1.0 if intent_unit.is_deterministic else 0.5
        test_coverage = 0.0  # Will be updated by dynamic testing
        license_score = 1.0  # Assuming valid license from intake
        static_analysis_score = classification.confidence

        overall_score = (
            0.3 * determinism_score +
            0.2 * test_coverage +
            0.2 * license_score +
            0.3 * static_analysis_score
        ) * base_score

        overall_score = max(0.01, min(1.0, overall_score))

        risk_factors: List[str] = []
        risk_level = RiskLevel.LOW

        if not intent_unit.is_pure:
            risk_factors.append("impure_function")
            risk_level = RiskLevel.MEDIUM

        if not intent_unit.is_deterministic:
            risk_factors.append("non_deterministic")
            risk_level = RiskLevel.MEDIUM

        if intent_unit.side_effects:
            risk_factors.append(f"side_effects: {', '.join(intent_unit.side_effects)}")
            risk_level = RiskLevel.MEDIUM

        return TrustScore(
            overall_score=overall_score,
            determinism_score=determinism_score,
            test_coverage_score=test_coverage,
            license_score=license_score,
            static_analysis_score=static_analysis_score,
            risk_level=risk_level,
            risk_factors=tuple(risk_factors),
            last_verified=datetime.now(timezone.utc).isoformat(),
        )

    def _build_failure_modes(self, intent_unit: IntentUnit) -> FailureModes:
        """Build the failure modes section."""
        can_fail = len(intent_unit.side_effects) > 0 or not intent_unit.is_pure

        possible_exceptions: List[str] = ["Exception"]
        if "division" in intent_unit.function_name.lower():
            possible_exceptions.append("ZeroDivisionError")
        if "index" in intent_unit.function_name.lower():
            possible_exceptions.append("IndexError")
        if "key" in intent_unit.function_name.lower():
            possible_exceptions.append("KeyError")

        error_conditions: List[str] = []
        if intent_unit.parameters:
            error_conditions.append("Invalid input types")
            error_conditions.append("None values when not allowed")

        return FailureModes(
            can_fail=can_fail,
            failure_mode=FailureMode.RAISES_EXCEPTION if can_fail else FailureMode.NEVER,
            possible_exceptions=tuple(possible_exceptions),
            error_conditions=tuple(error_conditions),
            recovery_hints=("Validate inputs before calling", "Handle exceptions appropriately"),
        )

    def _build_composition(
        self,
        classification: ClassificationResult,
    ) -> CompositionCompatibility:
        """Build the composition compatibility section."""
        category = self.CATEGORY_TO_BLOCK_CATEGORY.get(
            classification.primary_category,
            "unknown"
        )

        compatible_inputs = ["arithmetic", "string", "collection", "utility"]
        compatible_outputs = ["arithmetic", "string", "collection", "validation", "utility"]

        return CompositionCompatibility(
            composable=True,
            input_compatible_types=tuple(compatible_inputs),
            output_compatible_types=tuple(compatible_outputs),
            requires_blocks=(),
            conflicts_with=(),
            composition_notes=f"Atomic {category} block, composable with standard types",
        )

    def batch_build(
        self,
        classifications: List[ClassificationResult],
        ownership: BlockOwnership,
        base_trust_score: float = 0.5,
    ) -> List[BuildResult]:
        """Build multiple blocks from classifications."""
        return [
            self.build(c, ownership, base_trust_score)
            for c in classifications
        ]
