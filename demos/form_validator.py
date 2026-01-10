#!/usr/bin/env python3
"""
Form Input Validator - Demo using Neurop Forge blocks
This chains multiple blocks together to validate and sanitize input.

Usage:
    python demos/form_validator.py "  TEST@EMAIL.COM  "
    python demos/form_validator.py ""
    python demos/form_validator.py "hello world"
"""

import sys
import json
from neurop_forge import NeuropForge, execute_block


def validate_and_sanitize(input_text: str) -> dict:
    """Chain multiple blocks to validate and sanitize input."""
    
    report = {
        "original_input": input_text,
        "steps": [],
        "final_result": None,
        "is_valid": True,
        "errors": []
    }
    
    current_value = input_text
    
    step1 = execute_block("is_empty", {"value": current_value})
    is_empty = step1.get("result", True) if step1.get("success") else True
    report["steps"].append({
        "block": "is_empty",
        "input": current_value,
        "output": is_empty,
        "description": "Check if input is empty"
    })
    
    if is_empty:
        report["is_valid"] = False
        report["errors"].append("Input is empty")
        report["final_result"] = None
        return report
    
    step2 = execute_block("to_lowercase", {"text": current_value})
    if step2.get("success"):
        current_value = step2.get("result", current_value)
    report["steps"].append({
        "block": "to_lowercase",
        "input": report["original_input"],
        "output": current_value,
        "description": "Normalize to lowercase"
    })
    
    step3 = execute_block("word_count", {"text": current_value})
    word_count = step3.get("result", 0) if step3.get("success") else 0
    report["steps"].append({
        "block": "word_count",
        "input": current_value,
        "output": word_count,
        "description": "Count words in input"
    })
    
    step4 = execute_block("is_not_none", {"value": current_value})
    is_not_none = step4.get("result", False) if step4.get("success") else False
    report["steps"].append({
        "block": "is_not_none",
        "input": current_value,
        "output": is_not_none,
        "description": "Verify value exists"
    })
    
    step5 = execute_block("reverse_string", {"text": current_value})
    reversed_text = step5.get("result", "") if step5.get("success") else ""
    report["steps"].append({
        "block": "reverse_string",
        "input": current_value,
        "output": reversed_text,
        "description": "Reverse string (to verify processing)"
    })
    
    report["final_result"] = {
        "cleaned_input": current_value,
        "word_count": word_count,
        "reversed": reversed_text,
        "is_not_none": is_not_none
    }
    report["is_valid"] = is_not_none and word_count > 0
    
    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python demos/form_validator.py \"your input text\"")
        print("\nExamples:")
        print("  python demos/form_validator.py \"  HELLO WORLD  \"")
        print("  python demos/form_validator.py \"test@email.com\"")
        print("  python demos/form_validator.py \"\"")
        sys.exit(1)
    
    input_text = sys.argv[1]
    
    print("=" * 60)
    print("NEUROP FORGE - Form Input Validator Demo")
    print("=" * 60)
    print(f"\nInput: \"{input_text}\"")
    print("-" * 60)
    
    result = validate_and_sanitize(input_text)
    
    print("\nValidation Steps:")
    for i, step in enumerate(result["steps"], 1):
        print(f"  {i}. {step['block']}: {step['description']}")
        print(f"     Input: {step['input']!r}")
        print(f"     Output: {step['output']!r}")
        print()
    
    print("-" * 60)
    print(f"Valid: {'YES' if result['is_valid'] else 'NO'}")
    
    if result["errors"]:
        print(f"Errors: {', '.join(result['errors'])}")
    
    if result["final_result"]:
        print(f"\nFinal Result:")
        print(f"  Cleaned: {result['final_result']['cleaned_input']!r}")
        print(f"  Words: {result['final_result']['word_count']}")
        print(f"  Reversed: {result['final_result']['reversed']!r}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
