#!/usr/bin/env python3
"""
AI AGENT DEMO - GPT Calling Neurop Forge Verified Blocks
=========================================================
This demo shows GPT acting as a CONTROLLED OPERATOR:
- GPT receives a natural language request
- GPT decides which verified blocks to call
- Blocks execute deterministically
- GPT summarizes the results

THE KEY INSIGHT: GPT calls pre-verified, immutable blocks.
GPT writes ZERO code. GPT can EXECUTE but never MODIFY.

This is Neurop Forge: 2,700+ verified blocks that AI can
call but never change.

Requirements:
    pip install openai neurop-forge
    export OPENAI_API_KEY="your-api-key-here"

Usage:
    python demos/ai_agent_demo.py
    python demos/ai_agent_demo.py "Validate this email: test@company.com"
    python demos/ai_agent_demo.py "Is 4111111111111111 a valid credit card?"

Example Requests:
    - "Validate my customer data: email is john@example.com and phone is +1-555-123-4567"
    - "Check if racecar is a palindrome and count its vowels"
    - "Parse this JSON and tell me what's in it: {\"name\": \"John\", \"age\": 30}"
    - "Sanitize this HTML for safety: <script>alert('hack')</script>"
    - "Calculate 8% tax on $1250.00"
"""

import os
import sys
import json
from openai import OpenAI
from neurop_forge import execute_block

API_KEY = os.environ.get("OPENAI_API_KEY")

if not API_KEY:
    print("=" * 70)
    print("  ERROR: OpenAI API key not configured.")
    print("=" * 70)
    print("\n  Please set your OPENAI_API_KEY environment variable:\n")
    print("    export OPENAI_API_KEY='your-api-key-here'\n")
    print("  Get your API key at: https://platform.openai.com/api-keys")
    print("=" * 70)
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

AVAILABLE_BLOCKS = [
    {
        "type": "function",
        "function": {
            "name": "is_valid_email",
            "description": "Validate if an email address is properly formatted",
            "parameters": {
                "type": "object",
                "properties": {"email": {"type": "string", "description": "The email address to validate"}},
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "is_valid_url",
            "description": "Validate if a URL is properly formatted",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "The URL to validate"}},
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "is_valid_phone",
            "description": "Validate if a phone number is properly formatted",
            "parameters": {
                "type": "object",
                "properties": {"phone": {"type": "string", "description": "The phone number to validate (e.g., +1-555-123-4567)"}},
                "required": ["phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "is_valid_credit_card",
            "description": "Validate if a credit card number passes the Luhn algorithm check",
            "parameters": {
                "type": "object",
                "properties": {"number": {"type": "string", "description": "The credit card number to validate"}},
                "required": ["number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mask_email",
            "description": "Mask an email address for privacy (e.g., j**n@example.com)",
            "parameters": {
                "type": "object",
                "properties": {"email": {"type": "string", "description": "The email address to mask"}},
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sanitize_html",
            "description": "Sanitize HTML to prevent XSS attacks by escaping dangerous characters",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The HTML text to sanitize"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "parse_json",
            "description": "Parse a JSON string into a structured object",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The JSON string to parse"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_json",
            "description": "Convert data to a JSON string",
            "parameters": {
                "type": "object",
                "properties": {"data": {"type": "object", "description": "The data to convert to JSON"}},
                "required": ["data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_tax_amount",
            "description": "Calculate tax amount given a price and tax rate",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "The base amount"},
                    "rate": {"type": "number", "description": "The tax rate as a decimal (e.g., 0.08 for 8%)"}
                },
                "required": ["amount", "rate"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "word_count",
            "description": "Count the number of words in text",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to count words in"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "string_length",
            "description": "Get the length of a string in characters",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to measure"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "is_palindrome",
            "description": "Check if a string is a palindrome (reads the same forwards and backwards)",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to check"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_vowels",
            "description": "Count the number of vowels in text",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to count vowels in"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_occurrences",
            "description": "Count how many times a substring appears in text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to search in"},
                    "substring": {"type": "string", "description": "The substring to count"}
                },
                "required": ["text", "substring"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "is_numeric",
            "description": "Check if a string contains only numeric characters",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to check"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "is_alpha",
            "description": "Check if a string contains only alphabetic characters",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to check"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "truncate_string",
            "description": "Truncate a string to a maximum length",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to truncate"},
                    "max_length": {"type": "integer", "description": "Maximum length"}
                },
                "required": ["text", "max_length"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reverse_string",
            "description": "Reverse a string",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to reverse"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_uppercase",
            "description": "Convert text to uppercase",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to convert"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_lowercase",
            "description": "Convert text to lowercase",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to convert"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "capitalize_words",
            "description": "Capitalize the first letter of each word (title case)",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to capitalize"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "contains_digit",
            "description": "Check if text contains any digits",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "The text to check"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "contains_substring",
            "description": "Check if text contains a specific substring",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to search in"},
                    "substring": {"type": "string", "description": "The substring to look for"}
                },
                "required": ["text", "substring"]
            }
        }
    }
]


def execute_neurop_block(block_name: str, args: dict) -> dict:
    """Execute a Neurop Forge verified block and return result."""
    try:
        result = execute_block(block_name, args)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_agent(user_request: str):
    """Run the AI agent with a user request."""
    print("\n" + "=" * 70)
    print("  NEUROP FORGE - AI AGENT DEMO")
    print("  GPT as a Controlled Operator (Not a Code Writer)")
    print("=" * 70)
    print(f"\n  USER REQUEST:")
    print(f"  \"{user_request}\"")
    print("-" * 70)
    
    messages = [
        {
            "role": "system",
            "content": """You are an AI assistant powered by Neurop Forge - a library of 2,700+ verified, immutable code blocks.

IMPORTANT: You can ONLY use the function tools provided. You CANNOT write code.
When the user asks you to process data, call the appropriate blocks.

Available capabilities:
- VALIDATION: Check emails, URLs, phone numbers, credit cards
- SECURITY: Sanitize HTML, mask sensitive data
- DATA: Parse JSON, convert to JSON
- BUSINESS: Calculate tax amounts
- TEXT ANALYSIS: Word count, palindrome check, vowel count, character analysis

After getting results, provide a clear summary of what you found.
Always explain which blocks you're calling and why."""
        },
        {"role": "user", "content": user_request}
    ]
    
    blocks_called = []
    
    print("\n  AI AGENT REASONING...")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=AVAILABLE_BLOCKS,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    while message.tool_calls:
        print(f"\n  EXECUTING VERIFIED BLOCKS:")
        print("  " + "-" * 40)
        
        tool_results = []
        for tool_call in message.tool_calls:
            block_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            args_str = json.dumps(args)
            if len(args_str) > 50:
                args_str = args_str[:47] + "..."
            print(f"  | Block: {block_name}")
            print(f"  | Input: {args_str}")
            
            result = execute_neurop_block(block_name, args)
            blocks_called.append({
                "block": block_name,
                "args": args,
                "result": result
            })
            
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps(result)
            })
            
            result_str = str(result.get('result', result.get('error', 'N/A')))
            if len(result_str) > 50:
                result_str = result_str[:47] + "..."
            print(f"  | Output: {result_str}")
            print("  " + "-" * 40)
        
        messages.append(message)
        messages.extend(tool_results)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=AVAILABLE_BLOCKS,
            tool_choice="auto"
        )
        message = response.choices[0].message
    
    print("\n" + "=" * 70)
    print("  AI AGENT RESPONSE:")
    print("=" * 70)
    print(f"\n  {message.content}")
    
    print("\n" + "=" * 70)
    print("  EXECUTION SUMMARY")
    print("=" * 70)
    print(f"  Verified Blocks Called: {len(blocks_called)}")
    for i, bc in enumerate(blocks_called, 1):
        result_str = str(bc['result'].get('result', 'error'))
        if len(result_str) > 40:
            result_str = result_str[:37] + "..."
        print(f"    {i}. {bc['block']}: {result_str}")
    print(f"\n  Lines of Code Written by AI: 0")
    print(f"  All blocks are: VERIFIED, IMMUTABLE, DETERMINISTIC")
    print("=" * 70)
    print("\n  This is Neurop Forge: AI executes verified blocks.")
    print("  AI decided what to call. AI wrote zero code.")
    print("  Learn more: https://github.com/Louw115/neurop-forge\n")


def main():
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = (
            "I need to validate some customer data. "
            "Check if the email john.doe@company.com is valid, "
            "verify the phone number +1-555-867-5309, "
            "and also sanitize this HTML input: <script>alert('xss')</script>"
        )
    
    run_agent(user_request)


if __name__ == "__main__":
    main()
