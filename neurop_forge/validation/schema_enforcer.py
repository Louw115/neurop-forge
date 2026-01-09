"""
Schema enforcer for NeuropBlock validation.

This module enforces the strict NeuropBlock schema requirements.
Any block missing required fields or with invalid values is REJECTED.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from neurop_forge.core.block_schema import (
    NeuropBlock, BlockInterface, BlockConstraints, BlockMetadata,
    BlockOwnership, ValidationRules, TrustScore, FailureModes,
    CompositionCompatibility, PurityLevel, DataType, LicenseType,
    RiskLevel, FailureMode,
)


class EnforcementStatus(Enum):
    """Status of schema enforcement."""
    VALID = "valid"
    INVALID = "invalid"
    MISSING_FIELDS = "missing_fields"
    TYPE_MISMATCH = "type_mismatch"


@dataclass
class FieldViolation:
    """A violation of schema requirements."""
    field_path: str
    expected: str
    actual: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_path": self.field_path,
            "expected": self.expected,
            "actual": self.actual,
            "message": self.message,
        }


@dataclass
class EnforcementResult:
    """Result of schema enforcement."""
    status: EnforcementStatus
    is_valid: bool
    violations: Tuple[FieldViolation, ...]
    missing_fields: Tuple[str, ...]
    warnings: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "is_valid": self.is_valid,
            "violations": [v.to_dict() for v in self.violations],
            "missing_fields": list(self.missing_fields),
            "warnings": list(self.warnings),
        }


class SchemaEnforcer:
    """
    Enforces strict schema requirements for NeuropBlocks.
    
    Required sections (ALL mandatory):
    - identity (hash-derived, reproducible)
    - ownership & license provenance
    - metadata (human + AI readable)
    - interface (typed inputs/outputs)
    - constraints (runtime, purity, I/O)
    - logic (embedded, normalized)
    - validation rules
    - trust & risk scores
    - failure modes
    - composition compatibility
    
    Any block missing one field is INVALID and must be rejected.
    """

    REQUIRED_IDENTITY_FIELDS: Set[str] = {
        "hash_value", "algorithm", "version", "semantic_fingerprint"
    }

    REQUIRED_OWNERSHIP_FIELDS: Set[str] = {
        "license_type", "attribution_required", "modifications_allowed"
    }

    REQUIRED_METADATA_FIELDS: Set[str] = {
        "name", "intent", "description", "category", "tags", "version",
        "created_at", "language"
    }

    REQUIRED_INTERFACE_FIELDS: Set[str] = {
        "inputs", "outputs", "description"
    }

    REQUIRED_CONSTRAINTS_FIELDS: Set[str] = {
        "purity", "io_operations", "side_effects", "deterministic", "thread_safe"
    }

    REQUIRED_VALIDATION_FIELDS: Set[str] = {
        "input_validators", "output_validators", "invariants",
        "preconditions", "postconditions"
    }

    REQUIRED_TRUST_FIELDS: Set[str] = {
        "overall_score", "determinism_score", "test_coverage_score",
        "license_score", "static_analysis_score", "risk_level",
        "risk_factors", "last_verified"
    }

    REQUIRED_FAILURE_FIELDS: Set[str] = {
        "can_fail", "failure_mode", "possible_exceptions",
        "error_conditions", "recovery_hints"
    }

    REQUIRED_COMPOSITION_FIELDS: Set[str] = {
        "composable", "input_compatible_types", "output_compatible_types",
        "requires_blocks", "conflicts_with", "composition_notes"
    }

    def __init__(self, strict_mode: bool = True):
        self._strict_mode = strict_mode

    def enforce(self, block: NeuropBlock) -> EnforcementResult:
        """
        Enforce schema requirements on a NeuropBlock.
        
        Args:
            block: The block to validate
            
        Returns:
            EnforcementResult with validation status
        """
        violations: List[FieldViolation] = []
        missing_fields: List[str] = []
        warnings: List[str] = []

        violations.extend(self._check_identity(block.identity))
        violations.extend(self._check_ownership(block.ownership))
        violations.extend(self._check_metadata(block.metadata))
        violations.extend(self._check_interface(block.interface))
        violations.extend(self._check_constraints(block.constraints))

        if not block.logic or not block.logic.strip():
            violations.append(FieldViolation(
                field_path="logic",
                expected="non-empty string",
                actual="empty",
                message="Logic must be present and non-empty",
            ))

        violations.extend(self._check_validation_rules(block.validation_rules))
        violations.extend(self._check_trust_score(block.trust_score))
        violations.extend(self._check_failure_modes(block.failure_modes))
        violations.extend(self._check_composition(block.composition))

        if not block.sealed:
            warnings.append("Block is not sealed")

        violations.extend(self._cross_validate(block))

        is_valid = len(violations) == 0 and len(missing_fields) == 0

        if not is_valid:
            status = EnforcementStatus.INVALID
            if missing_fields:
                status = EnforcementStatus.MISSING_FIELDS
        else:
            status = EnforcementStatus.VALID

        return EnforcementResult(
            status=status,
            is_valid=is_valid,
            violations=tuple(violations),
            missing_fields=tuple(missing_fields),
            warnings=tuple(warnings),
        )

    def _check_identity(self, identity: Dict[str, Any]) -> List[FieldViolation]:
        """Check identity section requirements."""
        violations: List[FieldViolation] = []

        for field in self.REQUIRED_IDENTITY_FIELDS:
            if field not in identity:
                violations.append(FieldViolation(
                    field_path=f"identity.{field}",
                    expected="present",
                    actual="missing",
                    message=f"Required field identity.{field} is missing",
                ))
            elif not identity[field]:
                violations.append(FieldViolation(
                    field_path=f"identity.{field}",
                    expected="non-empty value",
                    actual="empty",
                    message=f"Field identity.{field} cannot be empty",
                ))

        if "hash_value" in identity:
            hash_val = identity["hash_value"]
            if len(hash_val) < 32:
                violations.append(FieldViolation(
                    field_path="identity.hash_value",
                    expected="hash length >= 32",
                    actual=f"length {len(hash_val)}",
                    message="Hash value is too short",
                ))

        return violations

    def _check_ownership(self, ownership: BlockOwnership) -> List[FieldViolation]:
        """Check ownership section requirements."""
        violations: List[FieldViolation] = []

        if ownership.license_type is None:
            violations.append(FieldViolation(
                field_path="ownership.license_type",
                expected="valid LicenseType",
                actual="None",
                message="License type is required",
            ))

        return violations

    def _check_metadata(self, metadata: BlockMetadata) -> List[FieldViolation]:
        """Check metadata section requirements."""
        violations: List[FieldViolation] = []

        if not metadata.name or not metadata.name.strip():
            violations.append(FieldViolation(
                field_path="metadata.name",
                expected="non-empty string",
                actual="empty",
                message="Metadata name is required",
            ))

        if not metadata.intent or not metadata.intent.strip():
            violations.append(FieldViolation(
                field_path="metadata.intent",
                expected="non-empty string",
                actual="empty",
                message="Intent description is required",
            ))

        if not metadata.language or not metadata.language.strip():
            violations.append(FieldViolation(
                field_path="metadata.language",
                expected="non-empty string",
                actual="empty",
                message="Language is required",
            ))

        if not metadata.version or not metadata.version.strip():
            violations.append(FieldViolation(
                field_path="metadata.version",
                expected="version string",
                actual="empty",
                message="Version is required",
            ))

        return violations

    def _check_interface(self, interface: BlockInterface) -> List[FieldViolation]:
        """Check interface section requirements."""
        violations: List[FieldViolation] = []

        if interface.inputs is None:
            violations.append(FieldViolation(
                field_path="interface.inputs",
                expected="tuple of TypedParameter",
                actual="None",
                message="Interface inputs are required",
            ))

        if interface.outputs is None:
            violations.append(FieldViolation(
                field_path="interface.outputs",
                expected="tuple of TypedParameter",
                actual="None",
                message="Interface outputs are required",
            ))
        elif len(interface.outputs) == 0:
            violations.append(FieldViolation(
                field_path="interface.outputs",
                expected="at least one output",
                actual="empty",
                message="At least one output is required",
            ))

        for i, param in enumerate(interface.inputs or ()):
            if not param.name:
                violations.append(FieldViolation(
                    field_path=f"interface.inputs[{i}].name",
                    expected="non-empty string",
                    actual="empty",
                    message=f"Input parameter {i} name is required",
                ))
            if param.data_type is None:
                violations.append(FieldViolation(
                    field_path=f"interface.inputs[{i}].data_type",
                    expected="DataType",
                    actual="None",
                    message=f"Input parameter {i} type is required",
                ))

        return violations

    def _check_constraints(self, constraints: BlockConstraints) -> List[FieldViolation]:
        """Check constraints section requirements."""
        violations: List[FieldViolation] = []

        if constraints.purity is None:
            violations.append(FieldViolation(
                field_path="constraints.purity",
                expected="PurityLevel",
                actual="None",
                message="Purity level is required",
            ))

        if constraints.io_operations is None:
            violations.append(FieldViolation(
                field_path="constraints.io_operations",
                expected="frozenset of IOType",
                actual="None",
                message="I/O operations declaration is required",
            ))

        return violations

    def _check_validation_rules(self, rules: ValidationRules) -> List[FieldViolation]:
        """Check validation rules section requirements."""
        violations: List[FieldViolation] = []

        if rules.input_validators is None:
            violations.append(FieldViolation(
                field_path="validation_rules.input_validators",
                expected="tuple",
                actual="None",
                message="Input validators are required",
            ))

        if rules.output_validators is None:
            violations.append(FieldViolation(
                field_path="validation_rules.output_validators",
                expected="tuple",
                actual="None",
                message="Output validators are required",
            ))

        return violations

    def _check_trust_score(self, trust: TrustScore) -> List[FieldViolation]:
        """Check trust score section requirements."""
        violations: List[FieldViolation] = []

        if trust.overall_score <= 0:
            violations.append(FieldViolation(
                field_path="trust_score.overall_score",
                expected="score > 0",
                actual=str(trust.overall_score),
                message="Trust score must be greater than zero",
            ))

        if trust.overall_score > 1.0:
            violations.append(FieldViolation(
                field_path="trust_score.overall_score",
                expected="score <= 1.0",
                actual=str(trust.overall_score),
                message="Trust score cannot exceed 1.0",
            ))

        if trust.risk_level is None:
            violations.append(FieldViolation(
                field_path="trust_score.risk_level",
                expected="RiskLevel",
                actual="None",
                message="Risk level is required",
            ))

        return violations

    def _check_failure_modes(self, failure: FailureModes) -> List[FieldViolation]:
        """Check failure modes section requirements."""
        violations: List[FieldViolation] = []

        if failure.failure_mode is None:
            violations.append(FieldViolation(
                field_path="failure_modes.failure_mode",
                expected="FailureMode",
                actual="None",
                message="Failure mode is required",
            ))

        return violations

    def _check_composition(self, composition: CompositionCompatibility) -> List[FieldViolation]:
        """Check composition compatibility section requirements."""
        violations: List[FieldViolation] = []

        if composition.composable is None:
            violations.append(FieldViolation(
                field_path="composition.composable",
                expected="boolean",
                actual="None",
                message="Composable flag is required",
            ))

        return violations

    def _cross_validate(self, block: NeuropBlock) -> List[FieldViolation]:
        """Cross-validate fields for consistency."""
        violations: List[FieldViolation] = []

        if block.constraints.purity == PurityLevel.PURE:
            if block.constraints.side_effects and len(block.constraints.side_effects) > 0:
                has_real_effects = any(
                    e != "none" for e in block.constraints.side_effects
                )
                if has_real_effects:
                    violations.append(FieldViolation(
                        field_path="constraints",
                        expected="no side effects for pure function",
                        actual=str(block.constraints.side_effects),
                        message="Pure blocks cannot have side effects",
                    ))

        if block.constraints.deterministic:
            from neurop_forge.core.block_schema import IOType
            non_deterministic_io = {IOType.RANDOM, IOType.TIME}
            if block.constraints.io_operations & non_deterministic_io:
                violations.append(FieldViolation(
                    field_path="constraints",
                    expected="no non-deterministic I/O",
                    actual=str(block.constraints.io_operations),
                    message="Deterministic blocks cannot use random or time I/O",
                ))

        return violations

    def quick_check(self, block: NeuropBlock) -> bool:
        """Quick check if block has all required sections."""
        try:
            if not block.identity:
                return False
            if not block.ownership:
                return False
            if not block.metadata:
                return False
            if not block.interface:
                return False
            if not block.constraints:
                return False
            if not block.logic:
                return False
            if not block.validation_rules:
                return False
            if not block.trust_score:
                return False
            if not block.failure_modes:
                return False
            if not block.composition:
                return False
            if block.trust_score.overall_score <= 0:
                return False
            return True
        except Exception:
            return False
