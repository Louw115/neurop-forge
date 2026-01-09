"""
Trust model for NeuropBlock scoring.

This module calculates trust scores based on:
- Determinism verification
- Test coverage
- License compliance
- Risk assessment
- Static analysis results

Trust scores determine whether a block can be exposed to AI assembly.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from neurop_forge.core.block_schema import (
    NeuropBlock, TrustScore, RiskLevel, PurityLevel, IOType,
)
from neurop_forge.validation.static_analysis import AnalysisResult, Severity
from neurop_forge.validation.dynamic_testing import TestResult


class TrustTier(Enum):
    """Trust tier classification."""
    VERIFIED = "verified"  # >= 0.8
    TRUSTED = "trusted"  # >= 0.6
    PROVISIONAL = "provisional"  # >= 0.4
    UNTRUSTED = "untrusted"  # >= 0.2
    QUARANTINED = "quarantined"  # < 0.2


@dataclass
class TrustAssessment:
    """Complete trust assessment for a block."""
    block_identity: str
    overall_score: float
    tier: TrustTier
    component_scores: Dict[str, float]
    risk_factors: Tuple[str, ...]
    risk_level: RiskLevel
    eligible_for_assembly: bool
    assessment_timestamp: str
    recommendations: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_identity": self.block_identity,
            "overall_score": self.overall_score,
            "tier": self.tier.value,
            "component_scores": self.component_scores,
            "risk_factors": list(self.risk_factors),
            "risk_level": self.risk_level.value,
            "eligible_for_assembly": self.eligible_for_assembly,
            "assessment_timestamp": self.assessment_timestamp,
            "recommendations": list(self.recommendations),
        }

    def to_trust_score(self) -> TrustScore:
        """Convert assessment to TrustScore for block storage."""
        return TrustScore(
            overall_score=self.overall_score,
            determinism_score=self.component_scores.get("determinism", 0.0),
            test_coverage_score=self.component_scores.get("test_coverage", 0.0),
            license_score=self.component_scores.get("license", 0.0),
            static_analysis_score=self.component_scores.get("static_analysis", 0.0),
            risk_level=self.risk_level,
            risk_factors=self.risk_factors,
            last_verified=self.assessment_timestamp,
        )


class TrustCalculator:
    """
    Calculator for NeuropBlock trust scores.
    
    Trust is calculated as a weighted combination of:
    - Determinism (25%): Same inputs always produce same outputs
    - Test Coverage (25%): Percentage of tests passing
    - License Compliance (20%): Valid, permissive license
    - Static Analysis (30%): No violations, low complexity
    
    Blocks with trust score < 0.2 are quarantined and never exposed to AI.
    """

    WEIGHTS = {
        "determinism": 0.25,
        "test_coverage": 0.25,
        "license": 0.20,
        "static_analysis": 0.30,
    }

    MINIMUM_TRUST_FOR_ASSEMBLY = 0.2

    RISK_MULTIPLIERS = {
        RiskLevel.NONE: 1.0,
        RiskLevel.LOW: 0.95,
        RiskLevel.MEDIUM: 0.8,
        RiskLevel.HIGH: 0.5,
        RiskLevel.CRITICAL: 0.0,
    }

    def __init__(self):
        pass

    def calculate(
        self,
        block: NeuropBlock,
        static_result: Optional[AnalysisResult] = None,
        test_result: Optional[TestResult] = None,
    ) -> TrustAssessment:
        """
        Calculate trust score for a block.
        
        Args:
            block: The block to assess
            static_result: Optional static analysis result
            test_result: Optional dynamic test result
            
        Returns:
            TrustAssessment with complete scoring
        """
        component_scores: Dict[str, float] = {}
        risk_factors: List[str] = []

        determinism_score = self._calculate_determinism_score(block, test_result)
        component_scores["determinism"] = determinism_score

        test_score = self._calculate_test_score(test_result)
        component_scores["test_coverage"] = test_score

        license_score = self._calculate_license_score(block)
        component_scores["license"] = license_score

        static_score = self._calculate_static_score(block, static_result)
        component_scores["static_analysis"] = static_score

        risk_factors.extend(self._identify_risk_factors(block, static_result, test_result))
        risk_level = self._determine_risk_level(risk_factors, component_scores)

        raw_score = sum(
            score * self.WEIGHTS[component]
            for component, score in component_scores.items()
        )

        risk_multiplier = self.RISK_MULTIPLIERS.get(risk_level, 1.0)
        overall_score = raw_score * risk_multiplier

        overall_score = max(0.0, min(1.0, overall_score))

        tier = self._determine_tier(overall_score)

        eligible = overall_score >= self.MINIMUM_TRUST_FOR_ASSEMBLY

        recommendations = self._generate_recommendations(
            component_scores, risk_factors, overall_score
        )

        return TrustAssessment(
            block_identity=block.get_identity_hash(),
            overall_score=overall_score,
            tier=tier,
            component_scores=component_scores,
            risk_factors=tuple(risk_factors),
            risk_level=risk_level,
            eligible_for_assembly=eligible,
            assessment_timestamp=datetime.now(timezone.utc).isoformat(),
            recommendations=tuple(recommendations),
        )

    def _calculate_determinism_score(
        self,
        block: NeuropBlock,
        test_result: Optional[TestResult],
    ) -> float:
        """Calculate determinism component score."""
        if block.constraints.deterministic:
            base_score = 0.8

            if test_result and test_result.determinism_verified:
                return 1.0

            if block.constraints.purity == PurityLevel.PURE:
                return 0.9

            return base_score
        else:
            return 0.3

    def _calculate_test_score(self, test_result: Optional[TestResult]) -> float:
        """Calculate test coverage component score."""
        if test_result is None:
            return 0.0

        if test_result.total_tests == 0:
            return 0.0

        pass_rate = test_result.passed / test_result.total_tests

        if test_result.errors > 0:
            pass_rate *= 0.8

        return pass_rate

    def _calculate_license_score(self, block: NeuropBlock) -> float:
        """Calculate license compliance component score."""
        from neurop_forge.core.block_schema import LicenseType

        license_scores = {
            LicenseType.MIT: 1.0,
            LicenseType.BSD_2_CLAUSE: 1.0,
            LicenseType.BSD_3_CLAUSE: 1.0,
            LicenseType.APACHE_2_0: 1.0,
            LicenseType.UNLICENSE: 1.0,
            LicenseType.CC0: 1.0,
            LicenseType.PUBLIC_DOMAIN: 1.0,
        }

        license_type = block.ownership.license_type
        return license_scores.get(license_type, 0.5)

    def _calculate_static_score(
        self,
        block: NeuropBlock,
        static_result: Optional[AnalysisResult],
    ) -> float:
        """Calculate static analysis component score."""
        if static_result is None:
            return 0.5

        if not static_result.passed:
            critical_count = len(static_result.get_critical_violations())
            if critical_count > 0:
                return 0.0
            return 0.3

        violation_count = len(static_result.violations)
        if violation_count == 0:
            return 1.0
        elif violation_count <= 2:
            return 0.8
        elif violation_count <= 5:
            return 0.6
        else:
            return 0.4

    def _identify_risk_factors(
        self,
        block: NeuropBlock,
        static_result: Optional[AnalysisResult],
        test_result: Optional[TestResult],
    ) -> List[str]:
        """Identify risk factors for the block."""
        factors: List[str] = []

        if not block.constraints.deterministic:
            factors.append("non_deterministic")

        if block.constraints.purity != PurityLevel.PURE:
            factors.append("impure_function")

        io_ops = block.constraints.io_operations
        risky_io = {IOType.FILE_WRITE, IOType.NETWORK_WRITE, IOType.DATABASE_WRITE}
        if io_ops & risky_io:
            factors.append("write_operations")

        if IOType.RANDOM in io_ops:
            factors.append("uses_randomness")

        if IOType.TIME in io_ops:
            factors.append("time_dependent")

        if static_result:
            for violation in static_result.violations:
                if violation.severity in (Severity.CRITICAL, Severity.HIGH):
                    factors.append(f"violation: {violation.violation_type.value}")

        if test_result:
            if test_result.failed > 0:
                factors.append(f"failing_tests: {test_result.failed}")
            if test_result.errors > 0:
                factors.append(f"test_errors: {test_result.errors}")

        if block.failure_modes.can_fail:
            factors.append("can_fail")

        return factors

    def _determine_risk_level(
        self,
        risk_factors: List[str],
        component_scores: Dict[str, float],
    ) -> RiskLevel:
        """Determine overall risk level."""
        if not risk_factors:
            return RiskLevel.NONE

        critical_indicators = ["violation: forbidden_operation", "violation: hidden_io"]
        if any(ind in risk_factors for ind in critical_indicators):
            return RiskLevel.CRITICAL

        high_indicators = ["write_operations", "violation: purity_violation"]
        if any(ind in risk_factors for ind in high_indicators):
            return RiskLevel.HIGH

        avg_score = sum(component_scores.values()) / len(component_scores)
        if avg_score < 0.5:
            return RiskLevel.HIGH
        elif avg_score < 0.7:
            return RiskLevel.MEDIUM

        medium_indicators = ["non_deterministic", "impure_function", "uses_randomness"]
        if any(ind in risk_factors for ind in medium_indicators):
            return RiskLevel.MEDIUM

        if len(risk_factors) > 0:
            return RiskLevel.LOW

        return RiskLevel.NONE

    def _determine_tier(self, score: float) -> TrustTier:
        """Determine trust tier from score."""
        if score >= 0.8:
            return TrustTier.VERIFIED
        elif score >= 0.6:
            return TrustTier.TRUSTED
        elif score >= 0.4:
            return TrustTier.PROVISIONAL
        elif score >= 0.2:
            return TrustTier.UNTRUSTED
        else:
            return TrustTier.QUARANTINED

    def _generate_recommendations(
        self,
        component_scores: Dict[str, float],
        risk_factors: List[str],
        overall_score: float,
    ) -> List[str]:
        """Generate recommendations for improving trust score."""
        recommendations: List[str] = []

        if component_scores.get("test_coverage", 0) < 0.5:
            recommendations.append("Add more test cases to improve test coverage")

        if component_scores.get("determinism", 0) < 0.8:
            recommendations.append("Verify determinism through repeated execution tests")

        if component_scores.get("static_analysis", 0) < 0.8:
            recommendations.append("Address static analysis violations")

        if "non_deterministic" in risk_factors:
            recommendations.append("Consider making function deterministic if possible")

        if "impure_function" in risk_factors:
            recommendations.append("Consider refactoring to pure function")

        if overall_score < 0.2:
            recommendations.append("Block is quarantined - significant improvements needed")

        return recommendations

    def recalculate_trust(
        self,
        block: NeuropBlock,
        new_test_result: TestResult,
    ) -> TrustAssessment:
        """
        Recalculate trust after new test results.
        
        Args:
            block: The block to reassess
            new_test_result: New test results
            
        Returns:
            Updated TrustAssessment
        """
        return self.calculate(block, None, new_test_result)

    def is_eligible_for_assembly(self, block: NeuropBlock) -> bool:
        """Quick check if block is eligible for AI assembly."""
        return block.trust_score.overall_score >= self.MINIMUM_TRUST_FOR_ASSEMBLY
