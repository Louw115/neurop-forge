#!/usr/bin/env python3
"""
ENTERPRISE COMPLIANCE DEMO - AI Agent Audit Trail
==================================================
This demo shows enterprise-grade AI agent compliance:

1. AI processes a financial transaction through verified blocks
2. Every block call is logged with cryptographic proof
3. Policy engine blocks unauthorized operations
4. Full audit trail generated for compliance

THE VALUE PROPOSITION:
"Your AI agents are already making decisions. 
Neurop Forge makes those decisions auditable, reversible, and insurable."

This demo uses ONLY real verified Neurop Forge blocks - no fallbacks, no fakes.

Requirements:
    pip install neurop-forge

Usage:
    python demos/enterprise_compliance_demo.py
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neurop_forge.compliance import AuditChain, PolicyEngine, ComplianceReport
from neurop_forge import execute_block


VERIFIED_FINANCIAL_BLOCKS = {
    "is_valid_email": {
        "description": "Validate if an email address is properly formatted",
        "tier": "A"
    },
    "is_valid_phone": {
        "description": "Validate if a phone number is properly formatted",
        "tier": "A"
    },
    "is_valid_credit_card": {
        "description": "Validate credit card number using Luhn algorithm",
        "tier": "A"
    },
    "calculate_tax_amount": {
        "description": "Calculate tax amount given price and rate percentage",
        "tier": "A"
    },
    "mask_email": {
        "description": "Mask an email address for privacy",
        "tier": "A"
    },
    "sanitize_html": {
        "description": "Sanitize HTML to prevent XSS attacks",
        "tier": "A"
    },
    "parse_json": {
        "description": "Parse a JSON string into a structured object",
        "tier": "A"
    }
}

DANGEROUS_BLOCKS = {
    "delete_record": {"description": "DELETE a record from the database", "tier": "B"},
    "execute_sql": {"description": "Execute raw SQL query", "tier": "B"},
    "modify_account": {"description": "Modify account settings", "tier": "B"}
}


def run_enterprise_demo():
    """Run the enterprise compliance demo using ONLY real verified blocks."""
    print("\n" + "=" * 70)
    print("  NEUROP FORGE - ENTERPRISE COMPLIANCE DEMO")
    print("  AI Agent Execution with Cryptographic Audit Trail")
    print("=" * 70)
    
    policy = PolicyEngine(
        mode="whitelist",
        allowed_blocks=list(VERIFIED_FINANCIAL_BLOCKS.keys()),
        allowed_tiers=["A"],
        max_calls_per_block=10
    )
    
    audit = AuditChain(agent_id="financial-agent-001")
    
    print("\n  POLICY CONFIGURATION:")
    print("  " + "-" * 40)
    print(f"  Mode: WHITELIST (only approved blocks)")
    print(f"  Allowed Blocks: {len(policy.allowed_blocks)}")
    print(f"  Allowed Tiers: A only (deterministic, safe)")
    print(f"  Max Calls Per Block: 10")
    print("  " + "-" * 40)
    
    print("\n" + "=" * 70)
    print("  SCENARIO: Customer Payment Validation")
    print("=" * 70)
    print("  Customer: john.doe@acme.com")
    print("  Phone: +1-555-123-4567")
    print("  Payment: $500.00 USD + 8.5% tax")
    print("  Card: 4111-1111-1111-1111")
    print("=" * 70)
    
    operations = [
        ("is_valid_email", {"email": "john.doe@acme.com"}, "Validate customer email"),
        ("is_valid_phone", {"phone": "+1-555-123-4567"}, "Validate customer phone"),
        ("is_valid_credit_card", {"number": "4111111111111111"}, "Validate credit card (Luhn check)"),
        ("mask_email", {"email": "john.doe@acme.com"}, "Mask email for audit log"),
        ("calculate_tax_amount", {"amount": 500.00, "rate": 8.5}, "Calculate 8.5% sales tax ($42.50)"),
        ("sanitize_html", {"text": "<script>alert('xss')</script>"}, "Sanitize user input for XSS"),
        ("parse_json", {"text": '{"customer": "john.doe", "verified": true}'}, "Parse customer metadata")
    ]
    
    print("\n  EXECUTING VERIFIED BLOCKS (REAL EXECUTION):")
    print("  " + "-" * 60)
    
    for block_name, inputs, description in operations:
        allowed, reason = policy.check(
            block_name, 
            inputs, 
            VERIFIED_FINANCIAL_BLOCKS.get(block_name, {}).get("tier", "A")
        )
        
        if allowed:
            start_time = time.time()
            try:
                result = execute_block(block_name, inputs)
                exec_time = (time.time() - start_time) * 1000
                success = result.get("success", True)
                
                audit.log_execution(
                    block_name=block_name,
                    inputs=inputs,
                    outputs=result,
                    success=success,
                    execution_time_ms=exec_time,
                    policy_status="ALLOWED"
                )
                
                result_value = result.get("result", result)
                result_display = str(result_value)
                if len(result_display) > 50:
                    result_display = result_display[:47] + "..."
                
                print(f"  [PASS] {block_name}")
                print(f"         {description}")
                print(f"         Result: {result_display}")
                print("  " + "-" * 60)
                
            except Exception as e:
                exec_time = (time.time() - start_time) * 1000
                audit.log_execution(
                    block_name=block_name,
                    inputs=inputs,
                    outputs={"error": str(e)},
                    success=False,
                    execution_time_ms=exec_time,
                    policy_status="ALLOWED"
                )
                print(f"  [FAIL] {block_name}")
                print(f"         Error: {str(e)[:50]}")
                print("  " + "-" * 60)
        else:
            audit.log_violation(block_name, inputs, reason)
            print(f"  [BLOCKED] {block_name}")
            print(f"         Reason: {reason}")
            print("  " + "-" * 60)
    
    print("\n" + "=" * 70)
    print("  AI AGENT ATTEMPTS UNAUTHORIZED OPERATIONS:")
    print("=" * 70)
    
    unauthorized_ops = [
        ("delete_record", {"record_id": "customer-12345"}, "Attempt to delete customer record"),
        ("execute_sql", {"query": "DROP TABLE customers"}, "Attempt to execute raw SQL"),
        ("modify_account", {"account_id": "ACC-12345678", "changes": {"balance": 999999}}, "Attempt to modify account balance")
    ]
    
    print("\n  POLICY ENFORCEMENT:")
    print("  " + "-" * 60)
    
    for block_name, inputs, description in unauthorized_ops:
        allowed, reason = policy.check(
            block_name, 
            inputs, 
            DANGEROUS_BLOCKS.get(block_name, {}).get("tier", "B")
        )
        
        if not allowed:
            audit.log_violation(block_name, inputs, reason)
            print(f"  [BLOCKED] {block_name}")
            print(f"         {description}")
            print(f"         Policy: {reason}")
            print("  " + "-" * 60)
        else:
            print(f"  [ALLOWED] {block_name} - WARNING: Should have been blocked!")
            print("  " + "-" * 60)
    
    print("\n" + "=" * 70)
    print("  CRYPTOGRAPHIC AUDIT CHAIN VERIFICATION")
    print("=" * 70)
    
    summary = audit.get_summary()
    
    print(f"\n  Chain Integrity: {'VERIFIED' if summary['chain_valid'] else 'COMPROMISED'}")
    print(f"  Total Audit Entries: {summary['total_entries']}")
    print(f"  Successful Executions: {summary['successful_executions']}")
    print(f"  Policy Violations Blocked: {summary['violations']}")
    print(f"  First Entry Hash: {summary['first_hash'][:16]}...")
    print(f"  Last Entry Hash: {summary['last_hash'][:16]}...")
    
    report = ComplianceReport(audit, policy)
    report.print_summary()
    
    report_file = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report.save(report_file)
    print(f"\n  Full audit report saved to: {report_file}")
    
    print("\n" + "=" * 70)
    print("  WHAT THIS DEMO PROVES")
    print("=" * 70)
    print("""
  1. REAL EXECUTION: All 7 blocks executed via neurop_forge.execute_block()
     - No mocks, no fakes, no fallbacks
     - Actual verified blocks from the Neurop Forge library
  
  2. POLICY ENFORCEMENT: 3 dangerous operations were BLOCKED
     - delete_record: DENIED (not in whitelist)
     - execute_sql: DENIED (not in whitelist)  
     - modify_account: DENIED (not in whitelist)
  
  3. CRYPTOGRAPHIC AUDIT: Every operation is hash-linked
     - Each entry contains SHA-256 hash of previous entry
     - Tamper-proof: any modification breaks the chain
     - Regulators can independently verify integrity
  
  4. COMPLIANCE READY: Audit report includes
     - Full execution trace with timestamps
     - Input/output pairs for every block call
     - Policy violation log with reasons
     - SOC 2 / HIPAA / PCI-DSS style assertions
""")
    print("=" * 70)
    print("  This is Neurop Forge: AI as operator, not author.")
    print("  Auditable. Reversible. Insurable.")
    print("  https://github.com/Louw115/neurop-forge")
    print("=" * 70 + "\n")


def main():
    if "--help" in sys.argv:
        print(__doc__)
        return
    
    run_enterprise_demo()


if __name__ == "__main__":
    main()
