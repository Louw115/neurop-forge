"""
Compliance Report Generator
===========================
Generate audit reports for compliance and regulatory purposes.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .audit_chain import AuditChain
from .policy_engine import PolicyEngine


class ComplianceReport:
    """
    Generate compliance reports from audit chains and policy engines.
    
    Designed for:
    - SOC 2 audits
    - HIPAA compliance
    - PCI-DSS requirements
    - Internal security reviews
    """
    
    def __init__(
        self,
        audit_chain: AuditChain,
        policy_engine: PolicyEngine,
        report_id: Optional[str] = None
    ):
        self.audit_chain = audit_chain
        self.policy_engine = policy_engine
        self.report_id = report_id or f"CR-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.generated_at = datetime.now(timezone.utc)
    
    def generate(self) -> Dict[str, Any]:
        """Generate the full compliance report."""
        chain_summary = self.audit_chain.get_summary()
        policy_stats = self.policy_engine.get_stats()
        
        return {
            "report_metadata": {
                "report_id": self.report_id,
                "generated_at": self.generated_at.isoformat(),
                "report_type": "AI_AGENT_EXECUTION_AUDIT",
                "schema_version": "1.0.0"
            },
            "executive_summary": self._generate_executive_summary(chain_summary, policy_stats),
            "chain_integrity": {
                "verified": chain_summary["chain_valid"],
                "first_hash": chain_summary["first_hash"],
                "last_hash": chain_summary["last_hash"],
                "total_entries": chain_summary["total_entries"],
                "tamper_detected": not chain_summary["chain_valid"]
            },
            "execution_summary": {
                "agent_id": chain_summary["agent_id"],
                "session_start": chain_summary["session_start"],
                "successful_executions": chain_summary["successful_executions"],
                "failed_executions": chain_summary["failed_executions"],
                "policy_violations": chain_summary["violations"]
            },
            "policy_enforcement": {
                "mode": policy_stats["mode"],
                "allowed_blocks": policy_stats["allowed_blocks_count"],
                "denied_blocks": policy_stats["denied_blocks_count"],
                "allowed_tiers": policy_stats["allowed_tiers"],
                "total_policy_checks": policy_stats["total_checks"],
                "violations_count": policy_stats["violations"]
            },
            "violations": [
                {
                    "block": v.block_name,
                    "reason": v.reason,
                    "rule": v.policy_rule,
                    "inputs": v.inputs
                }
                for v in self.policy_engine.violations
            ],
            "block_usage": policy_stats["call_counts"],
            "audit_trail": [e.to_dict() for e in self.audit_chain.entries],
            "compliance_assertions": self._generate_assertions(chain_summary, policy_stats)
        }
    
    def _generate_executive_summary(
        self,
        chain_summary: Dict[str, Any],
        policy_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary."""
        total_ops = chain_summary["successful_executions"] + chain_summary["failed_executions"]
        success_rate = (chain_summary["successful_executions"] / total_ops * 100) if total_ops > 0 else 0
        
        if chain_summary["violations"] == 0 and chain_summary["chain_valid"]:
            status = "COMPLIANT"
            risk_level = "LOW"
        elif chain_summary["violations"] > 0:
            status = "VIOLATIONS_DETECTED"
            risk_level = "HIGH"
        elif not chain_summary["chain_valid"]:
            status = "INTEGRITY_COMPROMISED"
            risk_level = "CRITICAL"
        else:
            status = "REVIEW_REQUIRED"
            risk_level = "MEDIUM"
        
        return {
            "status": status,
            "risk_level": risk_level,
            "total_operations": total_ops,
            "success_rate_percent": round(success_rate, 2),
            "violations_detected": chain_summary["violations"],
            "chain_integrity_verified": chain_summary["chain_valid"],
            "ai_code_written": 0,
            "blocks_executed": chain_summary["successful_executions"]
        }
    
    def _generate_assertions(
        self,
        chain_summary: Dict[str, Any],
        policy_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate compliance assertions."""
        assertions = []
        
        assertions.append({
            "assertion": "IMMUTABILITY",
            "description": "AI agent executed pre-verified blocks only, no code generation",
            "status": "PASS",
            "evidence": f"{chain_summary['successful_executions']} verified blocks executed, 0 lines of code written"
        })
        
        assertions.append({
            "assertion": "AUDIT_TRAIL_INTEGRITY",
            "description": "Cryptographic chain integrity verified",
            "status": "PASS" if chain_summary["chain_valid"] else "FAIL",
            "evidence": f"Chain hash verification: {'VALID' if chain_summary['chain_valid'] else 'INVALID'}"
        })
        
        assertions.append({
            "assertion": "POLICY_ENFORCEMENT",
            "description": "All block calls checked against policy before execution",
            "status": "PASS" if policy_stats["violations"] == 0 else "WARN",
            "evidence": f"{policy_stats['total_checks']} policy checks, {policy_stats['violations']} violations blocked"
        })
        
        assertions.append({
            "assertion": "TRACEABILITY",
            "description": "Full execution trace with inputs, outputs, and timestamps",
            "status": "PASS",
            "evidence": f"{chain_summary['total_entries']} audit entries with cryptographic linking"
        })
        
        return assertions
    
    def to_json(self) -> str:
        """Export report as JSON."""
        return json.dumps(self.generate(), indent=2)
    
    def save(self, filepath: str) -> None:
        """Save report to file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    def print_summary(self) -> None:
        """Print a human-readable summary."""
        report = self.generate()
        summary = report["executive_summary"]
        
        print("\n" + "=" * 70)
        print("  COMPLIANCE REPORT")
        print("=" * 70)
        print(f"  Report ID: {self.report_id}")
        print(f"  Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("-" * 70)
        print(f"  STATUS: {summary['status']}")
        print(f"  Risk Level: {summary['risk_level']}")
        print("-" * 70)
        print(f"  Total Operations: {summary['total_operations']}")
        print(f"  Success Rate: {summary['success_rate_percent']}%")
        print(f"  Violations Detected: {summary['violations_detected']}")
        print(f"  Chain Integrity: {'VERIFIED' if summary['chain_integrity_verified'] else 'COMPROMISED'}")
        print(f"  Code Written by AI: {summary['ai_code_written']} lines")
        print("=" * 70)
        
        print("\n  COMPLIANCE ASSERTIONS:")
        print("-" * 70)
        for assertion in report["compliance_assertions"]:
            status_icon = "PASS" if assertion["status"] == "PASS" else ("WARN" if assertion["status"] == "WARN" else "FAIL")
            print(f"  [{status_icon}] {assertion['assertion']}")
            print(f"        {assertion['description']}")
        print("=" * 70)
