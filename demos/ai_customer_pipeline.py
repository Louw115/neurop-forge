#!/usr/bin/env python3
"""
AI CUSTOMER ONBOARDING PIPELINE
===============================
Demonstrates how an AI agent uses Neurop Forge to process customer data
through a verified block pipeline — without writing a single line of code.

This is what AI-controlled execution looks like:
- AI receives customer data
- AI composes a block graph
- AI executes verified blocks
- AI returns structured results
- AI modifies ZERO code

Usage:
    python demos/ai_customer_pipeline.py
    python demos/ai_customer_pipeline.py --raw  # Show raw block outputs
"""

import sys
import json
from datetime import datetime
from neurop_forge import NeuropForge, execute_block

# Simulated customer submissions (like an AI would receive from a form/API)
SAMPLE_CUSTOMERS = [
    {
        "name": "  JOHN DOE  ",
        "email": "JOHN.DOE@EXAMPLE.COM",
        "phone": "555-123-4567",
        "company": "acme corp",
        "notes": "Interested in enterprise plan. Contact ASAP!!!"
    },
    {
        "name": "jane smith",
        "email": "jane@invalid",
        "phone": "123",
        "company": "  ",
        "notes": "needs demo"
    },
    {
        "name": "",
        "email": "valid@company.org",
        "phone": "+1 (800) 555-0199",
        "company": "Global Industries LLC",
        "notes": "VIP customer - handle with care. Budget: $50,000"
    }
]


class AICustomerProcessor:
    """
    Simulates an AI agent that processes customer data using ONLY
    verified Neurop Forge blocks. The AI cannot write code — it can
    only compose and execute pre-verified blocks.
    """
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.blocks_executed = 0
        self.pipeline_trace = []
    
    def log(self, step, block_name, input_val, output_val, tier="A"):
        """Record execution trace."""
        self.blocks_executed += 1
        entry = {
            "step": step,
            "block": block_name,
            "tier": tier,
            "input": str(input_val)[:50],
            "output": str(output_val)[:50] if output_val is not None else "None"
        }
        self.pipeline_trace.append(entry)
        if self.verbose:
            print(f"    [{tier}] {block_name}: {output_val}")
    
    def run_block(self, name, inputs, step_name=""):
        """Execute a verified block and return result."""
        result = execute_block(name, inputs)
        output = result.get("result") if result.get("success") else None
        self.log(step_name, name, inputs, output)
        return output
    
    def validate_customer(self, customer):
        """
        AI-composed validation pipeline using verified blocks.
        Returns validation report with all issues found.
        """
        issues = []
        validated = {}
        
        # === STAGE 1: Name Processing ===
        name = customer.get("name", "")
        
        # Check if empty
        is_empty = self.run_block("is_empty", {"value": name}, "name_check")
        if is_empty:
            issues.append("Name is required")
            validated["name"] = None
        else:
            # Normalize: trim and title case
            cleaned = self.run_block("capitalize_words", {"text": name}, "name_normalize")
            if cleaned:
                cleaned = cleaned.strip()
            validated["name"] = cleaned
            
            # Validate length
            length = self.run_block("string_length", {"text": cleaned or ""}, "name_length")
            if length and length < 2:
                issues.append("Name too short")
        
        # === STAGE 2: Email Validation ===
        email = customer.get("email", "")
        
        is_empty = self.run_block("is_empty", {"value": email}, "email_check")
        if is_empty:
            issues.append("Email is required")
            validated["email"] = None
        else:
            # Normalize to lowercase
            email_clean = self.run_block("to_lowercase", {"text": email}, "email_normalize")
            validated["email"] = email_clean
            
            # Check for @ symbol (basic validation)
            has_at = self.run_block("contains_substring", {"text": email_clean or "", "substring": "@"}, "email_at_check")
            has_dot = self.run_block("contains_substring", {"text": email_clean or "", "substring": "."}, "email_dot_check")
            
            if not has_at or not has_dot:
                issues.append("Invalid email format")
        
        # === STAGE 3: Phone Processing ===
        phone = customer.get("phone", "")
        
        is_empty = self.run_block("is_empty", {"value": phone}, "phone_check")
        if is_empty:
            validated["phone"] = None
            issues.append("Phone is recommended")
        else:
            validated["phone_original"] = phone
            
            # Check phone length (basic validation)
            phone_len = self.run_block("string_length", {"text": phone}, "phone_length")
            validated["phone_length"] = phone_len
            
            # Check for digits present
            has_digits = self.run_block("contains_digit", {"text": phone}, "phone_has_digits")
            if not has_digits:
                issues.append("Phone must contain digits")
            elif phone_len and phone_len < 10:
                issues.append("Phone number too short")
        
        # === STAGE 4: Company Processing ===
        company = customer.get("company", "")
        
        is_empty = self.run_block("is_empty", {"value": company.strip()}, "company_check")
        if is_empty:
            validated["company"] = None
        else:
            # Title case the company name
            company_clean = self.run_block("capitalize_words", {"text": company.strip()}, "company_normalize")
            validated["company"] = company_clean
        
        # === STAGE 5: Notes Analysis ===
        notes = customer.get("notes", "")
        
        if notes:
            # Word count for notes
            word_count = self.run_block("word_count", {"text": notes}, "notes_words")
            validated["notes_word_count"] = word_count
            
            # Check for urgency indicators
            notes_lower = self.run_block("to_lowercase", {"text": notes}, "notes_lower")
            has_urgent = self.run_block("contains_substring", {"text": notes_lower or "", "substring": "asap"}, "notes_urgent")
            has_vip = self.run_block("contains_substring", {"text": notes_lower or "", "substring": "vip"}, "notes_vip")
            
            validated["is_urgent"] = has_urgent
            validated["is_vip"] = has_vip
            validated["notes"] = notes
        else:
            validated["notes"] = None
            validated["is_urgent"] = False
            validated["is_vip"] = False
        
        # === STAGE 6: Generate Customer ID ===
        # Create a simple ID from email (first part + length)
        if validated.get("email"):
            # Get email length as part of ID
            email_len = self.run_block("string_length", {"text": validated["email"]}, "email_len_for_id")
            # Get uppercase version for ID prefix
            email_upper = self.run_block("to_uppercase", {"text": validated["email"]}, "email_upper_for_id")
            if email_upper and email_len:
                # Take first 8 chars + length as ID
                prefix = email_upper.split("@")[0][:8] if "@" in email_upper else email_upper[:8]
                validated["customer_id"] = f"CUS-{prefix}-{email_len}"
            else:
                validated["customer_id"] = "CUS-UNKNOWN"
        else:
            validated["customer_id"] = "CUS-INVALID"
        
        # Determine validity: no critical issues (required fields OR invalid format)
        critical_keywords = ["required", "invalid", "too short", "must contain"]
        has_critical_issues = any(
            any(kw in issue.lower() for kw in critical_keywords)
            for issue in issues
        )
        
        return {
            "validated_data": validated,
            "issues": issues,
            "is_valid": not has_critical_issues,
            "blocks_executed": self.blocks_executed
        }
    
    def process_batch(self, customers):
        """Process multiple customers and return summary."""
        results = []
        
        for i, customer in enumerate(customers):
            self.pipeline_trace = []
            start_blocks = self.blocks_executed
            
            result = self.validate_customer(customer)
            result["customer_index"] = i + 1
            result["blocks_for_customer"] = self.blocks_executed - start_blocks
            result["trace"] = self.pipeline_trace.copy()
            results.append(result)
        
        return results


def print_banner():
    print()
    print("=" * 70)
    print("  NEUROP FORGE - AI CUSTOMER ONBOARDING PIPELINE")
    print("  Demonstrating: AI executes verified blocks, writes zero code")
    print("=" * 70)
    print()


def print_customer_result(result, show_trace=False):
    data = result["validated_data"]
    issues = result["issues"]
    
    status = "VALID" if result["is_valid"] else "INVALID"
    priority = ""
    if data.get("is_vip"):
        priority = " [VIP]"
    elif data.get("is_urgent"):
        priority = " [URGENT]"
    
    print(f"\n  Customer #{result['customer_index']}: {status}{priority}")
    print(f"  {'-' * 40}")
    print(f"  ID:      {data.get('customer_id', 'N/A')}")
    print(f"  Name:    {data.get('name') or '(missing)'}")
    print(f"  Email:   {data.get('email') or '(missing)'}")
    print(f"  Phone:   {data.get('phone_original') or '(missing)'}")
    print(f"  Company: {data.get('company') or '(none)'}")
    
    if issues:
        print(f"  Issues:  {', '.join(issues)}")
    
    print(f"  Blocks:  {result['blocks_for_customer']} executed")
    
    if show_trace:
        print(f"\n  Execution Trace:")
        for entry in result["trace"]:
            print(f"    [{entry['tier']}] {entry['block']}: {entry['output']}")


def main():
    show_trace = "--raw" in sys.argv
    
    print_banner()
    
    print("  INPUT: 3 customer submissions (simulating AI receiving form data)")
    print("  TASK:  Validate, normalize, and classify each customer")
    print("  RULE:  AI uses ONLY verified Tier-A blocks — no code generation")
    print()
    
    # Initialize processor (simulating an AI agent)
    processor = AICustomerProcessor(verbose=False)
    
    # Process all customers
    print("  Processing customers through verified block pipeline...")
    results = processor.process_batch(SAMPLE_CUSTOMERS)
    
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)
    
    for result in results:
        print_customer_result(result, show_trace)
    
    # Summary
    valid_count = sum(1 for r in results if r["is_valid"])
    vip_count = sum(1 for r in results if r["validated_data"].get("is_vip"))
    urgent_count = sum(1 for r in results if r["validated_data"].get("is_urgent"))
    total_blocks = processor.blocks_executed
    
    print("\n" + "=" * 70)
    print("  PIPELINE SUMMARY")
    print("=" * 70)
    print(f"  Customers Processed: {len(results)}")
    print(f"  Valid Submissions:   {valid_count}/{len(results)}")
    print(f"  VIP Customers:       {vip_count}")
    print(f"  Urgent Requests:     {urgent_count}")
    print(f"  Total Blocks Run:    {total_blocks}")
    print(f"  Lines of Code Written by AI: 0")
    print("=" * 70)
    print()
    print("  This is Neurop Forge: AI executes verified blocks.")
    print("  AI composed the pipeline. AI wrote zero code.")
    print()


if __name__ == "__main__":
    main()
