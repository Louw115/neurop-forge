#!/usr/bin/env python3
"""
AI AGENT DEMO - GPT Calling Neurop Forge Blocks
================================================
This demo shows GPT acting as a controlled operator:
- GPT receives a natural language request
- GPT decides which Neurop Forge blocks to call
- Blocks execute and return results
- GPT summarizes the answer

THE KEY INSIGHT: GPT calls pre-verified blocks. GPT writes zero code.

Usage:
    python demos/ai_agent_demo.py
    python demos/ai_agent_demo.py "Validate this email: test@example.com"
    python demos/ai_agent_demo.py "Process this text: Hello World"
"""

import os
import sys
import json
from openai import OpenAI
from neurop_forge import execute_block

client = OpenAI(
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
)

AVAILABLE_BLOCKS = [
    {
        "type": "function",
        "function": {
            "name": "string_length",
            "description": "Get the length of a string",
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
    }
]

def execute_neurop_block(block_name: str, args: dict) -> dict:
    """Execute a Neurop Forge block and return result."""
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
    print(f"\n  USER REQUEST: \"{user_request}\"")
    print("-" * 70)
    
    messages = [
        {
            "role": "system",
            "content": """You are an AI assistant that uses Neurop Forge blocks to process data.
You can ONLY use the provided function tools - you cannot write code.
When the user asks you to process text or data, call the appropriate blocks.
After getting results, summarize what you found.
Always explain which blocks you're calling and why."""
        },
        {"role": "user", "content": user_request}
    ]
    
    blocks_called = []
    
    print("\n  AI AGENT THINKING...")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=AVAILABLE_BLOCKS,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    while message.tool_calls:
        print(f"\n  BLOCKS BEING CALLED:")
        
        tool_results = []
        for tool_call in message.tool_calls:
            block_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            print(f"    -> {block_name}({json.dumps(args)[:50]}...)")
            
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
            
            print(f"       Result: {result.get('result', result.get('error', 'N/A'))}")
        
        messages.append(message)
        messages.extend(tool_results)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=AVAILABLE_BLOCKS,
            tool_choice="auto"
        )
        message = response.choices[0].message
    
    print("\n" + "-" * 70)
    print("  AI AGENT RESPONSE:")
    print("-" * 70)
    print(f"\n  {message.content}")
    
    print("\n" + "=" * 70)
    print("  EXECUTION SUMMARY")
    print("=" * 70)
    print(f"  Blocks Called: {len(blocks_called)}")
    for bc in blocks_called:
        print(f"    - {bc['block']}: {bc['result'].get('result', 'error')}")
    print(f"  Lines of Code Written by AI: 0")
    print("=" * 70)
    print("\n  This is Neurop Forge: AI executes verified blocks.")
    print("  AI decided what to call. AI wrote zero code.\n")


def main():
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = "Analyze this text: 'Hello World! This is a test.' Tell me its length, word count, and what it looks like in uppercase."
    
    run_agent(user_request)


if __name__ == "__main__":
    main()
