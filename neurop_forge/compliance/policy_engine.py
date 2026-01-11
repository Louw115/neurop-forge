"""
Policy Engine
=============
Define what blocks an AI agent is allowed to call.
Enforce policies and log violations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class PolicyAction(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    AUDIT_ONLY = "AUDIT_ONLY"


@dataclass
class PolicyViolation:
    """Represents a policy violation."""
    block_name: str
    reason: str
    policy_rule: str
    inputs: Dict[str, Any]


class PolicyEngine:
    """
    Policy engine for controlling AI agent block access.
    
    Policies can:
    - Whitelist specific blocks (deny all others)
    - Blacklist specific blocks (allow all others)
    - Require specific tiers (A-only, B-only)
    - Set per-block input constraints
    """
    
    def __init__(
        self,
        mode: str = "whitelist",
        allowed_blocks: Optional[List[str]] = None,
        denied_blocks: Optional[List[str]] = None,
        allowed_tiers: Optional[List[str]] = None,
        max_calls_per_block: Optional[int] = None
    ):
        self.mode = mode
        self.allowed_blocks: Set[str] = set(allowed_blocks or [])
        self.denied_blocks: Set[str] = set(denied_blocks or [])
        self.allowed_tiers: Set[str] = set(allowed_tiers or ["A", "B"])
        self.max_calls_per_block = max_calls_per_block
        self._call_counts: Dict[str, int] = {}
        self._violations: List[PolicyViolation] = []
    
    def check(self, block_name: str, inputs: Dict[str, Any], tier: str = "A") -> tuple[bool, str]:
        """
        Check if a block call is allowed by policy.
        
        Returns:
            (allowed: bool, reason: str)
        """
        if self.mode == "whitelist":
            if block_name not in self.allowed_blocks:
                reason = f"Block '{block_name}' not in allowed whitelist"
                self._record_violation(block_name, reason, "WHITELIST", inputs)
                return False, reason
        
        elif self.mode == "blacklist":
            if block_name in self.denied_blocks:
                reason = f"Block '{block_name}' is explicitly denied"
                self._record_violation(block_name, reason, "BLACKLIST", inputs)
                return False, reason
        
        if tier not in self.allowed_tiers:
            reason = f"Block tier '{tier}' not allowed (allowed: {self.allowed_tiers})"
            self._record_violation(block_name, reason, "TIER_RESTRICTION", inputs)
            return False, reason
        
        if self.max_calls_per_block is not None:
            current_calls = self._call_counts.get(block_name, 0)
            if current_calls >= self.max_calls_per_block:
                reason = f"Block '{block_name}' exceeded max calls ({self.max_calls_per_block})"
                self._record_violation(block_name, reason, "RATE_LIMIT", inputs)
                return False, reason
        
        self._call_counts[block_name] = self._call_counts.get(block_name, 0) + 1
        return True, "ALLOWED"
    
    def _record_violation(self, block_name: str, reason: str, rule: str, inputs: Dict[str, Any]):
        """Record a policy violation."""
        self._violations.append(PolicyViolation(
            block_name=block_name,
            reason=reason,
            policy_rule=rule,
            inputs=inputs
        ))
    
    @property
    def violations(self) -> List[PolicyViolation]:
        return self._violations
    
    def get_stats(self) -> Dict[str, Any]:
        """Get policy enforcement statistics."""
        return {
            "mode": self.mode,
            "allowed_blocks_count": len(self.allowed_blocks),
            "denied_blocks_count": len(self.denied_blocks),
            "allowed_tiers": list(self.allowed_tiers),
            "total_checks": sum(self._call_counts.values()),
            "violations": len(self._violations),
            "call_counts": dict(self._call_counts)
        }
    
    @classmethod
    def financial_policy(cls) -> "PolicyEngine":
        """Pre-built policy for financial operations."""
        return cls(
            mode="whitelist",
            allowed_blocks=[
                "is_valid_email",
                "is_valid_phone", 
                "is_valid_credit_card",
                "mask_credit_card",
                "mask_email",
                "calculate_tax_amount",
                "calculate_interest",
                "verify_account",
                "process_payment",
                "sanitize_html",
                "parse_json",
                "to_json",
                "format_currency",
                "validate_amount"
            ],
            allowed_tiers=["A"],
            max_calls_per_block=100
        )
    
    @classmethod
    def readonly_policy(cls) -> "PolicyEngine":
        """Policy that only allows read/validation blocks."""
        return cls(
            mode="whitelist",
            allowed_blocks=[
                "is_valid_email",
                "is_valid_phone",
                "is_valid_url",
                "is_valid_credit_card",
                "is_palindrome",
                "is_numeric",
                "is_alpha",
                "word_count",
                "string_length",
                "count_vowels",
                "parse_json"
            ],
            allowed_tiers=["A", "B"]
        )
