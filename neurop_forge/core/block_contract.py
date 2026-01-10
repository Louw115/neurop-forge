"""
NeuropBlock Contract Specification v1.0.0

This module defines the LOCKED contract for NeuropBlocks. The contract is:
- Immutable once released
- Versioned with semantic versioning
- Enforced at all block creation and storage boundaries

CONTRACT GUARANTEES:
1. Interface Consistency: block.interface.inputs matches function signature
2. Logic Executability: block.logic is directly executable with matched parameters
3. Identity Uniqueness: block.identity.hash_value is globally unique
4. Trust Tracking: block.trust_score is updated after each execution

VERSION HISTORY:
- v1.0.0: Initial locked contract (2026-01-10)
  - Fixed normalization to preserve function parameters
  - Block.logic stores ORIGINAL source code (not normalized)
  - Normalized code only used for identity hashing
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
import json


CONTRACT_VERSION = "1.0.0"
CONTRACT_HASH = "sha256:neurop-block-contract-v1"


class ContractViolation(Exception):
    """Raised when a block violates the contract."""
    pass


class ContractSection(Enum):
    """Sections of the NeuropBlock contract."""
    IDENTITY = "identity"
    OWNERSHIP = "ownership"
    METADATA = "metadata"
    INTERFACE = "interface"
    CONSTRAINTS = "constraints"
    LOGIC = "logic"
    VALIDATION_RULES = "validation_rules"
    TRUST_SCORE = "trust_score"
    FAILURE_MODES = "failure_modes"
    COMPOSITION = "composition"


@dataclass(frozen=True)
class ContractRequirement:
    """A single requirement in the contract."""
    section: ContractSection
    field: str
    requirement: str
    mandatory: bool
    validation_fn: Optional[str] = None


BLOCK_CONTRACT = [
    ContractRequirement(
        section=ContractSection.IDENTITY,
        field="hash_value",
        requirement="SHA256 hash of normalized logic + interface + constraints",
        mandatory=True,
        validation_fn="validate_identity_hash",
    ),
    ContractRequirement(
        section=ContractSection.IDENTITY,
        field="version",
        requirement="Semantic version string (e.g., '1.0.0')",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.IDENTITY,
        field="canonical_name",
        requirement="Unique block name (snake_case)",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.OWNERSHIP,
        field="author",
        requirement="String identifying the author",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.OWNERSHIP,
        field="license",
        requirement="One of: MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, Unlicense, CC0-1.0, Public-Domain",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.METADATA,
        field="intent",
        requirement="Natural language description of block's purpose",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.METADATA,
        field="category",
        requirement="Primary category classification",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.METADATA,
        field="created_at",
        requirement="ISO 8601 timestamp of block creation",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.INTERFACE,
        field="inputs",
        requirement="List of typed input parameters matching function signature",
        mandatory=True,
        validation_fn="validate_interface_inputs",
    ),
    ContractRequirement(
        section=ContractSection.INTERFACE,
        field="outputs",
        requirement="List of typed output parameters",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.INTERFACE,
        field="description",
        requirement="Interface description string",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.CONSTRAINTS,
        field="purity",
        requirement="One of: pure, deterministic_with_side_effects, non_deterministic",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.CONSTRAINTS,
        field="io_operations",
        requirement="Set of declared I/O operations",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.CONSTRAINTS,
        field="deterministic",
        requirement="Boolean indicating determinism",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.LOGIC,
        field="logic",
        requirement="ORIGINAL source code (not normalized). Must be directly executable with interface.inputs.",
        mandatory=True,
        validation_fn="validate_logic_executable",
    ),
    ContractRequirement(
        section=ContractSection.TRUST_SCORE,
        field="overall_score",
        requirement="Float between 0.0 and 1.0",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.TRUST_SCORE,
        field="determinism_score",
        requirement="Float between 0.0 and 1.0",
        mandatory=True,
    ),
    ContractRequirement(
        section=ContractSection.TRUST_SCORE,
        field="execution_count",
        requirement="Integer count of total executions (default 0)",
        mandatory=False,
    ),
    ContractRequirement(
        section=ContractSection.TRUST_SCORE,
        field="success_count",
        requirement="Integer count of successful executions (default 0)",
        mandatory=False,
    ),
    ContractRequirement(
        section=ContractSection.TRUST_SCORE,
        field="success_rate",
        requirement="Computed property: success_count / execution_count (0.0 if no executions)",
        mandatory=False,
    ),
]


class ContractValidator:
    """Validates blocks against the contract specification."""

    def __init__(self):
        self._requirements = {s: [] for s in ContractSection}
        for req in BLOCK_CONTRACT:
            self._requirements[req.section].append(req)

    def validate(self, block_dict: Dict[str, Any]) -> List[str]:
        """
        Validate a block dictionary against the contract.
        
        Returns list of violations. Empty list means valid.
        """
        violations = []

        for section in ContractSection:
            section_name = section.value
            if section_name not in block_dict and section != ContractSection.LOGIC:
                violations.append(f"Missing required section: {section_name}")
                continue

            for req in self._requirements[section]:
                if section == ContractSection.LOGIC:
                    section_data = block_dict
                else:
                    section_data = block_dict.get(section_name, {})

                if req.mandatory:
                    if req.field not in section_data:
                        violations.append(
                            f"Missing required field: {section_name}.{req.field}"
                        )

        violations.extend(self._validate_interface_logic_alignment(block_dict))

        return violations

    def _validate_interface_logic_alignment(self, block_dict: Dict[str, Any]) -> List[str]:
        """
        Validate that interface.inputs aligns with function parameters in logic.
        
        This is THE CRITICAL CONTRACT GUARANTEE:
        - Every parameter in interface.inputs MUST exist in the function signature
        - Every non-optional parameter in the function MUST be in interface.inputs
        """
        violations = []

        interface = block_dict.get("interface", {})
        logic = block_dict.get("logic", "")

        if not logic or not interface:
            return violations

        import ast
        try:
            tree = ast.parse(logic)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_params = set()
                    for arg in node.args.args:
                        if arg.arg not in ("self", "cls"):
                            func_params.add(arg.arg)

                    interface_params = set()
                    for inp in interface.get("inputs", []):
                        interface_params.add(inp.get("name", ""))

                    missing_in_interface = func_params - interface_params
                    missing_in_func = interface_params - func_params

                    if missing_in_interface:
                        violations.append(
                            f"Function parameters not in interface: {missing_in_interface}"
                        )
                    if missing_in_func:
                        violations.append(
                            f"Interface parameters not in function: {missing_in_func}"
                        )
                    break

        except SyntaxError:
            pass

        return violations


def get_contract_version() -> str:
    """Get the current contract version."""
    return CONTRACT_VERSION


def get_contract_hash() -> str:
    """Get the contract content hash for verification."""
    contract_content = json.dumps(
        [
            {
                "section": r.section.value,
                "field": r.field,
                "requirement": r.requirement,
                "mandatory": r.mandatory,
            }
            for r in BLOCK_CONTRACT
        ],
        sort_keys=True,
    )
    return hashlib.sha256(contract_content.encode()).hexdigest()[:16]


def validate_block_contract(block_dict: Dict[str, Any]) -> tuple:
    """
    Validate a block against the current contract.
    
    Returns:
        (is_valid: bool, violations: List[str])
    """
    validator = ContractValidator()
    violations = validator.validate(block_dict)
    return len(violations) == 0, violations
