"""
Strict NeuropBlock schema definition.

This module defines the EXACT structure of a NeuropBlock with NO flexibility.
Every block MUST conform to this schema or be rejected. The schema enforces:

- One block = one intent
- Immutability after creation
- Explicit side-effect declaration
- No hidden I/O
- No implicit state
- Hash-consistent identity

A NeuropBlock is PERFECT only if ALL required sections are present and valid.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, FrozenSet
from enum import Enum
from datetime import datetime
import json


class PurityLevel(Enum):
    """Declares the purity level of a block's logic."""
    PURE = "pure"
    DETERMINISTIC_WITH_SIDE_EFFECTS = "deterministic_with_side_effects"
    NON_DETERMINISTIC = "non_deterministic"


class IOType(Enum):
    """Types of I/O operations a block may perform."""
    NONE = "none"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    NETWORK_READ = "network_read"
    NETWORK_WRITE = "network_write"
    DATABASE_READ = "database_read"
    DATABASE_WRITE = "database_write"
    CONSOLE_OUTPUT = "console_output"
    RANDOM = "random"
    TIME = "time"


class DataType(Enum):
    """Supported data types for block interfaces."""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    NONE = "none"
    ANY = "any"
    BYTES = "bytes"


class LicenseType(Enum):
    """Allowed license types for source code."""
    MIT = "MIT"
    BSD_2_CLAUSE = "BSD-2-Clause"
    BSD_3_CLAUSE = "BSD-3-Clause"
    APACHE_2_0 = "Apache-2.0"
    UNLICENSE = "Unlicense"
    CC0 = "CC0-1.0"
    PUBLIC_DOMAIN = "Public-Domain"


class FailureMode(Enum):
    """How a block may fail."""
    NEVER = "never"
    RAISES_EXCEPTION = "raises_exception"
    RETURNS_ERROR = "returns_error"
    RETURNS_NONE = "returns_none"


class RiskLevel(Enum):
    """Risk assessment for a block."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TypedParameter:
    """A typed parameter for block interfaces."""
    name: str
    data_type: DataType
    description: str
    optional: bool = False
    default_value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "data_type": self.data_type.value,
            "description": self.description,
            "optional": self.optional,
            "default_value": self.default_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TypedParameter":
        return cls(
            name=data["name"],
            data_type=DataType(data["data_type"]),
            description=data["description"],
            optional=data.get("optional", False),
            default_value=data.get("default_value"),
        )


@dataclass(frozen=True)
class BlockInterface:
    """
    Typed interface specification for a NeuropBlock.
    
    Defines exactly what inputs the block accepts and what outputs it produces.
    All types are explicitly declared - no weak typing allowed.
    """
    inputs: tuple  # Tuple of TypedParameter
    outputs: tuple  # Tuple of TypedParameter
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inputs": [p.to_dict() for p in self.inputs],
            "outputs": [p.to_dict() for p in self.outputs],
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockInterface":
        return cls(
            inputs=tuple(TypedParameter.from_dict(p) for p in data["inputs"]),
            outputs=tuple(TypedParameter.from_dict(p) for p in data["outputs"]),
            description=data["description"],
        )


@dataclass(frozen=True)
class BlockConstraints:
    """
    Runtime, purity, and I/O constraints for a NeuropBlock.
    
    These constraints are declared explicitly and enforced at validation time.
    """
    purity: PurityLevel
    io_operations: FrozenSet[IOType]
    side_effects: tuple  # Tuple of strings describing side effects
    deterministic: bool
    thread_safe: bool
    max_execution_time_ms: Optional[int] = None
    max_memory_bytes: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "purity": self.purity.value,
            "io_operations": [io.value for io in self.io_operations],
            "side_effects": list(self.side_effects),
            "deterministic": self.deterministic,
            "thread_safe": self.thread_safe,
            "max_execution_time_ms": self.max_execution_time_ms,
            "max_memory_bytes": self.max_memory_bytes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockConstraints":
        return cls(
            purity=PurityLevel(data["purity"]),
            io_operations=frozenset(IOType(io) for io in data["io_operations"]),
            side_effects=tuple(data["side_effects"]),
            deterministic=data["deterministic"],
            thread_safe=data["thread_safe"],
            max_execution_time_ms=data.get("max_execution_time_ms"),
            max_memory_bytes=data.get("max_memory_bytes"),
        )


@dataclass(frozen=True)
class BlockMetadata:
    """
    Human and AI readable metadata for a NeuropBlock.
    """
    name: str
    intent: str
    description: str
    category: str
    tags: tuple  # Tuple of strings
    version: str
    created_at: str
    language: str
    source_file: Optional[str] = None
    source_line_start: Optional[int] = None
    source_line_end: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "intent": self.intent,
            "description": self.description,
            "category": self.category,
            "tags": list(self.tags),
            "version": self.version,
            "created_at": self.created_at,
            "language": self.language,
            "source_file": self.source_file,
            "source_line_start": self.source_line_start,
            "source_line_end": self.source_line_end,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockMetadata":
        return cls(
            name=data["name"],
            intent=data["intent"],
            description=data["description"],
            category=data["category"],
            tags=tuple(data["tags"]),
            version=data["version"],
            created_at=data["created_at"],
            language=data["language"],
            source_file=data.get("source_file"),
            source_line_start=data.get("source_line_start"),
            source_line_end=data.get("source_line_end"),
        )


@dataclass(frozen=True)
class BlockOwnership:
    """Ownership and license provenance for a NeuropBlock."""
    license_type: LicenseType
    license_url: Optional[str]
    original_author: Optional[str]
    original_repository: Optional[str]
    attribution_required: bool
    modifications_allowed: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "license_type": self.license_type.value,
            "license_url": self.license_url,
            "original_author": self.original_author,
            "original_repository": self.original_repository,
            "attribution_required": self.attribution_required,
            "modifications_allowed": self.modifications_allowed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockOwnership":
        return cls(
            license_type=LicenseType(data["license_type"]),
            license_url=data.get("license_url"),
            original_author=data.get("original_author"),
            original_repository=data.get("original_repository"),
            attribution_required=data["attribution_required"],
            modifications_allowed=data["modifications_allowed"],
        )


@dataclass(frozen=True)
class ValidationRules:
    """Validation rules that must pass for the block to be valid."""
    input_validators: tuple  # Tuple of validation rule strings
    output_validators: tuple  # Tuple of validation rule strings
    invariants: tuple  # Tuple of invariant condition strings
    preconditions: tuple
    postconditions: tuple

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_validators": list(self.input_validators),
            "output_validators": list(self.output_validators),
            "invariants": list(self.invariants),
            "preconditions": list(self.preconditions),
            "postconditions": list(self.postconditions),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationRules":
        return cls(
            input_validators=tuple(data["input_validators"]),
            output_validators=tuple(data["output_validators"]),
            invariants=tuple(data["invariants"]),
            preconditions=tuple(data["preconditions"]),
            postconditions=tuple(data["postconditions"]),
        )


@dataclass(frozen=True)
class TrustScore:
    """Trust and risk assessment for a NeuropBlock."""
    overall_score: float  # 0.0 to 1.0
    determinism_score: float
    test_coverage_score: float
    license_score: float
    static_analysis_score: float
    risk_level: RiskLevel
    risk_factors: tuple  # Tuple of risk factor strings
    last_verified: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "determinism_score": self.determinism_score,
            "test_coverage_score": self.test_coverage_score,
            "license_score": self.license_score,
            "static_analysis_score": self.static_analysis_score,
            "risk_level": self.risk_level.value,
            "risk_factors": list(self.risk_factors),
            "last_verified": self.last_verified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrustScore":
        return cls(
            overall_score=data["overall_score"],
            determinism_score=data["determinism_score"],
            test_coverage_score=data["test_coverage_score"],
            license_score=data["license_score"],
            static_analysis_score=data["static_analysis_score"],
            risk_level=RiskLevel(data["risk_level"]),
            risk_factors=tuple(data["risk_factors"]),
            last_verified=data["last_verified"],
        )


@dataclass(frozen=True)
class FailureModes:
    """Explicit declaration of how a block may fail."""
    can_fail: bool
    failure_mode: FailureMode
    possible_exceptions: tuple  # Tuple of exception type names
    error_conditions: tuple  # Tuple of error condition descriptions
    recovery_hints: tuple  # Tuple of recovery suggestions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "can_fail": self.can_fail,
            "failure_mode": self.failure_mode.value,
            "possible_exceptions": list(self.possible_exceptions),
            "error_conditions": list(self.error_conditions),
            "recovery_hints": list(self.recovery_hints),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailureModes":
        return cls(
            can_fail=data["can_fail"],
            failure_mode=FailureMode(data["failure_mode"]),
            possible_exceptions=tuple(data["possible_exceptions"]),
            error_conditions=tuple(data["error_conditions"]),
            recovery_hints=tuple(data["recovery_hints"]),
        )


@dataclass(frozen=True)
class CompositionCompatibility:
    """Declares how this block can be composed with others."""
    composable: bool
    input_compatible_types: tuple  # Tuple of block category strings
    output_compatible_types: tuple  # Tuple of block category strings
    requires_blocks: tuple  # Tuple of required block identities
    conflicts_with: tuple  # Tuple of conflicting block categories
    composition_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "composable": self.composable,
            "input_compatible_types": list(self.input_compatible_types),
            "output_compatible_types": list(self.output_compatible_types),
            "requires_blocks": list(self.requires_blocks),
            "conflicts_with": list(self.conflicts_with),
            "composition_notes": self.composition_notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompositionCompatibility":
        return cls(
            composable=data["composable"],
            input_compatible_types=tuple(data["input_compatible_types"]),
            output_compatible_types=tuple(data["output_compatible_types"]),
            requires_blocks=tuple(data["requires_blocks"]),
            conflicts_with=tuple(data["conflicts_with"]),
            composition_notes=data["composition_notes"],
        )


@dataclass(frozen=True)
class NeuropBlock:
    """
    The canonical NeuropBlock structure.
    
    This is an IMMUTABLE, SEALED unit of verified functionality.
    ALL fields are MANDATORY. Any block missing a field is INVALID.
    
    A NeuropBlock represents:
    - One atomic intent
    - Deterministic behavior (unless explicitly declared otherwise)
    - Explicit side-effect declaration
    - No hidden I/O
    - No implicit state
    - Hash-consistent identity
    """
    identity: Dict[str, Any]  # BlockIdentity serialized
    ownership: BlockOwnership
    metadata: BlockMetadata
    interface: BlockInterface
    constraints: BlockConstraints
    logic: str  # Normalized, embedded logic
    validation_rules: ValidationRules
    trust_score: TrustScore
    failure_modes: FailureModes
    composition: CompositionCompatibility
    sealed: bool = True

    def __post_init__(self) -> None:
        """Validate that all required fields are present and valid."""
        if not self.identity:
            raise ValueError("Identity is required")
        if not self.ownership:
            raise ValueError("Ownership is required")
        if not self.metadata:
            raise ValueError("Metadata is required")
        if not self.interface:
            raise ValueError("Interface is required")
        if not self.constraints:
            raise ValueError("Constraints are required")
        if not self.logic or not self.logic.strip():
            raise ValueError("Logic is required and cannot be empty")
        if not self.validation_rules:
            raise ValueError("Validation rules are required")
        if not self.trust_score:
            raise ValueError("Trust score is required")
        if not self.failure_modes:
            raise ValueError("Failure modes are required")
        if not self.composition:
            raise ValueError("Composition compatibility is required")
        if self.trust_score.overall_score <= 0:
            raise ValueError("Trust score must be greater than zero")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize block to dictionary representation."""
        return {
            "identity": self.identity,
            "ownership": self.ownership.to_dict(),
            "metadata": self.metadata.to_dict(),
            "interface": self.interface.to_dict(),
            "constraints": self.constraints.to_dict(),
            "logic": self.logic,
            "validation_rules": self.validation_rules.to_dict(),
            "trust_score": self.trust_score.to_dict(),
            "failure_modes": self.failure_modes.to_dict(),
            "composition": self.composition.to_dict(),
            "sealed": self.sealed,
        }

    def to_json(self) -> str:
        """Serialize block to canonical JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NeuropBlock":
        """Deserialize block from dictionary representation."""
        return cls(
            identity=data["identity"],
            ownership=BlockOwnership.from_dict(data["ownership"]),
            metadata=BlockMetadata.from_dict(data["metadata"]),
            interface=BlockInterface.from_dict(data["interface"]),
            constraints=BlockConstraints.from_dict(data["constraints"]),
            logic=data["logic"],
            validation_rules=ValidationRules.from_dict(data["validation_rules"]),
            trust_score=TrustScore.from_dict(data["trust_score"]),
            failure_modes=FailureModes.from_dict(data["failure_modes"]),
            composition=CompositionCompatibility.from_dict(data["composition"]),
            sealed=data.get("sealed", True),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "NeuropBlock":
        """Deserialize block from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def get_identity_hash(self) -> str:
        """Get the canonical hash identifier for this block."""
        return self.identity.get("hash_value", "")

    def get_intent(self) -> str:
        """Get the declared intent of this block."""
        return self.metadata.intent

    def is_pure(self) -> bool:
        """Check if this block is pure (no side effects)."""
        return self.constraints.purity == PurityLevel.PURE

    def is_deterministic(self) -> bool:
        """Check if this block is deterministic."""
        return self.constraints.deterministic

    def get_trust_level(self) -> float:
        """Get the overall trust score."""
        return self.trust_score.overall_score
