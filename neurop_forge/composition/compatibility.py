"""
Type and contract matching for block composition.

This module verifies that blocks can be composed together by checking:
- Type compatibility between outputs and inputs
- Contract compatibility (constraints must align)
- Trust level requirements
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from neurop_forge.core.block_schema import (
    NeuropBlock, BlockInterface, DataType, PurityLevel,
)


class CompatibilityStatus(Enum):
    """Status of compatibility check."""
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass
class TypeMatch:
    """Result of type matching."""
    source_type: DataType
    target_type: DataType
    is_match: bool
    requires_conversion: bool
    conversion_risk: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type.value,
            "target_type": self.target_type.value,
            "is_match": self.is_match,
            "requires_conversion": self.requires_conversion,
            "conversion_risk": self.conversion_risk,
        }


@dataclass
class CompatibilityResult:
    """Result of compatibility check."""
    status: CompatibilityStatus
    source_identity: str
    target_identity: str
    type_matches: Tuple[TypeMatch, ...]
    constraint_issues: Tuple[str, ...]
    trust_compatible: bool
    overall_score: float
    recommendations: Tuple[str, ...]

    def is_compatible(self) -> bool:
        return self.status == CompatibilityStatus.COMPATIBLE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "source_identity": self.source_identity,
            "target_identity": self.target_identity,
            "type_matches": [m.to_dict() for m in self.type_matches],
            "constraint_issues": list(self.constraint_issues),
            "trust_compatible": self.trust_compatible,
            "overall_score": self.overall_score,
            "recommendations": list(self.recommendations),
        }


class CompatibilityChecker:
    """
    Checker for block composition compatibility.
    
    Verifies:
    - Output types of source match input types of target
    - Constraint requirements are compatible
    - Trust levels are sufficient
    """

    TYPE_COMPATIBILITY: Dict[DataType, Set[DataType]] = {
        DataType.INTEGER: {DataType.INTEGER, DataType.FLOAT, DataType.ANY},
        DataType.FLOAT: {DataType.FLOAT, DataType.ANY},
        DataType.STRING: {DataType.STRING, DataType.ANY},
        DataType.BOOLEAN: {DataType.BOOLEAN, DataType.ANY},
        DataType.LIST: {DataType.LIST, DataType.ANY},
        DataType.DICT: {DataType.DICT, DataType.ANY},
        DataType.BYTES: {DataType.BYTES, DataType.ANY},
        DataType.NONE: {DataType.NONE, DataType.ANY},
        DataType.ANY: {
            DataType.INTEGER, DataType.FLOAT, DataType.STRING,
            DataType.BOOLEAN, DataType.LIST, DataType.DICT,
            DataType.BYTES, DataType.NONE, DataType.ANY,
        },
    }

    CONVERSION_RISKS: Dict[Tuple[DataType, DataType], float] = {
        (DataType.INTEGER, DataType.FLOAT): 0.0,
        (DataType.FLOAT, DataType.INTEGER): 0.3,
        (DataType.STRING, DataType.INTEGER): 0.5,
        (DataType.STRING, DataType.FLOAT): 0.5,
        (DataType.ANY, DataType.ANY): 0.1,
    }

    def __init__(self, strict_mode: bool = True):
        self._strict_mode = strict_mode

    def check_compatibility(
        self,
        source: NeuropBlock,
        target: NeuropBlock,
    ) -> CompatibilityResult:
        """
        Check if source block output is compatible with target block input.
        
        Args:
            source: The source block (provides output)
            target: The target block (receives input)
            
        Returns:
            CompatibilityResult with detailed analysis
        """
        source_id = source.get_identity_hash()
        target_id = target.get_identity_hash()

        type_matches = self._check_type_compatibility(
            source.interface, target.interface
        )

        constraint_issues = self._check_constraint_compatibility(source, target)

        trust_compatible = self._check_trust_compatibility(source, target)

        overall_score = self._calculate_compatibility_score(
            type_matches, constraint_issues, trust_compatible
        )

        if overall_score >= 0.8 and not constraint_issues:
            status = CompatibilityStatus.COMPATIBLE
        elif overall_score >= 0.5:
            status = CompatibilityStatus.PARTIAL
        elif overall_score > 0:
            status = CompatibilityStatus.INCOMPATIBLE
        else:
            status = CompatibilityStatus.UNKNOWN

        recommendations = self._generate_recommendations(
            type_matches, constraint_issues, trust_compatible
        )

        return CompatibilityResult(
            status=status,
            source_identity=source_id,
            target_identity=target_id,
            type_matches=tuple(type_matches),
            constraint_issues=tuple(constraint_issues),
            trust_compatible=trust_compatible,
            overall_score=overall_score,
            recommendations=tuple(recommendations),
        )

    def _check_type_compatibility(
        self,
        source_interface: BlockInterface,
        target_interface: BlockInterface,
    ) -> List[TypeMatch]:
        """Check type compatibility between interfaces."""
        matches: List[TypeMatch] = []

        for output in source_interface.outputs:
            for input_param in target_interface.inputs:
                is_match = self._types_match(output.data_type, input_param.data_type)
                requires_conversion = (
                    output.data_type != input_param.data_type and
                    input_param.data_type != DataType.ANY
                )
                risk = self.CONVERSION_RISKS.get(
                    (output.data_type, input_param.data_type), 0.0
                )

                matches.append(TypeMatch(
                    source_type=output.data_type,
                    target_type=input_param.data_type,
                    is_match=is_match,
                    requires_conversion=requires_conversion,
                    conversion_risk=risk,
                ))

        return matches

    def _types_match(self, source: DataType, target: DataType) -> bool:
        """Check if source type can be used as target type."""
        if source == target:
            return True
        if target == DataType.ANY:
            return True
        compatible = self.TYPE_COMPATIBILITY.get(source, set())
        return target in compatible

    def _check_constraint_compatibility(
        self,
        source: NeuropBlock,
        target: NeuropBlock,
    ) -> List[str]:
        """Check constraint compatibility between blocks."""
        issues: List[str] = []

        if target.constraints.purity == PurityLevel.PURE:
            if source.constraints.purity != PurityLevel.PURE:
                issues.append(
                    "Target requires pure input but source is impure"
                )

        if target.constraints.deterministic:
            if not source.constraints.deterministic:
                issues.append(
                    "Target requires deterministic input but source is non-deterministic"
                )

        if source.failure_modes.can_fail:
            if not target.failure_modes.can_fail:
                issues.append(
                    "Source can fail but target doesn't handle failures"
                )

        return issues

    def _check_trust_compatibility(
        self,
        source: NeuropBlock,
        target: NeuropBlock,
    ) -> bool:
        """Check if trust levels are compatible."""
        source_trust = source.trust_score.overall_score
        target_trust = target.trust_score.overall_score

        if source_trust < 0.2 or target_trust < 0.2:
            return False

        if abs(source_trust - target_trust) > 0.5:
            return False

        return True

    def _calculate_compatibility_score(
        self,
        type_matches: List[TypeMatch],
        constraint_issues: List[str],
        trust_compatible: bool,
    ) -> float:
        """Calculate overall compatibility score."""
        if not type_matches:
            return 0.5

        type_score = sum(
            1.0 if m.is_match else (0.5 if m.requires_conversion else 0.0)
            for m in type_matches
        ) / len(type_matches)

        constraint_penalty = len(constraint_issues) * 0.2
        constraint_score = max(0, 1.0 - constraint_penalty)

        trust_score = 1.0 if trust_compatible else 0.5

        return (type_score * 0.4 + constraint_score * 0.4 + trust_score * 0.2)

    def _generate_recommendations(
        self,
        type_matches: List[TypeMatch],
        constraint_issues: List[str],
        trust_compatible: bool,
    ) -> List[str]:
        """Generate recommendations for improving compatibility."""
        recommendations: List[str] = []

        for match in type_matches:
            if match.requires_conversion:
                recommendations.append(
                    f"Consider adding type conversion from {match.source_type.value} "
                    f"to {match.target_type.value}"
                )

        for issue in constraint_issues:
            recommendations.append(f"Address constraint issue: {issue}")

        if not trust_compatible:
            recommendations.append(
                "Improve trust scores of blocks to ensure compatibility"
            )

        return recommendations

    def find_compatible_blocks(
        self,
        source: NeuropBlock,
        candidates: List[NeuropBlock],
        min_score: float = 0.5,
    ) -> List[Tuple[NeuropBlock, CompatibilityResult]]:
        """
        Find compatible blocks from a list of candidates.
        
        Args:
            source: The source block
            candidates: List of candidate blocks
            min_score: Minimum compatibility score
            
        Returns:
            List of (block, result) tuples for compatible blocks
        """
        compatible: List[Tuple[NeuropBlock, CompatibilityResult]] = []

        for candidate in candidates:
            result = self.check_compatibility(source, candidate)
            if result.overall_score >= min_score:
                compatible.append((candidate, result))

        compatible.sort(key=lambda x: x[1].overall_score, reverse=True)
        return compatible
