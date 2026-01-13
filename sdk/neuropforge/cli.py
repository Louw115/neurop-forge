"""
Neurop Forge CLI - Command-line interface for testing blocks.

Usage:
    nf health                              # Check API health
    nf blocks --limit 10                   # List available blocks
    nf search "validate email"             # Search for blocks
    nf exec to_uppercase --input text=hello  # Execute a block
"""
import argparse
import json
import os
import sys
from typing import Optional

try:
    from .client import NeuropForge, NeuropForgeError, BlockNotFoundError
except ImportError:
    from client import NeuropForge, NeuropForgeError, BlockNotFoundError


def color(text: str, code: str) -> str:
    """Add ANSI color codes if terminal supports it."""
    if not sys.stdout.isatty():
        return text
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "bold": "\033[1m",
        "reset": "\033[0m"
    }
    return f"{colors.get(code, '')}{text}{colors['reset']}"


def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def cmd_health(client: NeuropForge, args):
    """Check API health."""
    health = client.health()
    status = health.get("status", "unknown")
    block_count = health.get("block_count", 0)
    
    if status == "healthy":
        print(color("✓ API is healthy", "green"))
        print(f"  Blocks loaded: {color(str(block_count), 'bold')}")
        print(f"  Version: {health.get('version', 'unknown')}")
    else:
        print(color("✗ API is unhealthy", "red"))
        print_json(health)


def cmd_blocks(client: NeuropForge, args):
    """List available blocks."""
    blocks = client.list_blocks(limit=args.limit, category=args.category)
    
    print(color(f"Found {len(blocks)} blocks:", "bold"))
    for block in blocks:
        print(f"  {color(block.name, 'blue')} ({block.category})")
        if args.verbose:
            print(f"    {block.description}")
            print(f"    Inputs: {', '.join(block.inputs)}")


def cmd_search(client: NeuropForge, args):
    """Search for blocks."""
    results = client.search(args.query, limit=args.limit)
    
    if not results:
        print(color("No blocks found.", "yellow"))
        return
    
    print(color(f"Found {len(results)} matching blocks:", "bold"))
    for r in results:
        print(f"  {color(r.name, 'blue')} ({r.domain}/{r.operation})")
        if args.verbose:
            print(f"    {r.why_selected}")


def cmd_exec(client: NeuropForge, args):
    """Execute a block."""
    inputs = {}
    for inp in (args.input or []):
        if "=" not in inp:
            print(color(f"Invalid input format: {inp} (use key=value)", "red"))
            sys.exit(1)
        key, value = inp.split("=", 1)
        try:
            inputs[key] = json.loads(value)
        except json.JSONDecodeError:
            inputs[key] = value
    
    if args.json_input:
        try:
            inputs = json.loads(args.json_input)
        except json.JSONDecodeError as e:
            print(color(f"Invalid JSON input: {e}", "red"))
            sys.exit(1)
    
    try:
        result = client.execute(args.block, **inputs)
        
        print(color("✓ Execution successful", "green"))
        print(f"  Block: {color(result.block_name, 'blue')}")
        print(f"  Result: {color(json.dumps(result.result), 'bold')}")
        print(f"  Time: {result.execution_time_ms:.2f}ms")
        if result.block_id:
            print(f"  Block ID: {result.block_id}")
            
    except BlockNotFoundError as e:
        print(color(f"✗ Block not found: {args.block}", "red"))
        sys.exit(1)
    except NeuropForgeError as e:
        print(color(f"✗ Execution failed: {e}", "red"))
        sys.exit(1)


def cmd_stats(client: NeuropForge, args):
    """Get library statistics."""
    stats = client.stats()
    print_json(stats)


def cmd_audit(client: NeuropForge, args):
    """Get audit chain info."""
    audit = client.audit_chain()
    
    valid = audit.get("integrity_valid", False)
    if valid:
        print(color("✓ Audit chain integrity valid", "green"))
    else:
        print(color("✗ Audit chain integrity INVALID", "red"))
    
    print(f"  Events: {audit.get('event_count', 0)}")
    print(f"  Chain hash: {audit.get('chain_hash', 'N/A')[:16]}...")


def main():
    parser = argparse.ArgumentParser(
        prog="nf",
        description="Neurop Forge CLI - Execute pre-verified function blocks"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="API key (or set NEUROP_API_KEY env var)"
    )
    parser.add_argument(
        "--host", "-H",
        default=None,
        help="API host URL"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    p_health = subparsers.add_parser("health", help="Check API health")
    
    p_blocks = subparsers.add_parser("blocks", help="List available blocks")
    p_blocks.add_argument("--limit", "-l", type=int, default=20, help="Max blocks to show")
    p_blocks.add_argument("--category", "-c", help="Filter by category")
    p_blocks.add_argument("--verbose", "-v", action="store_true", help="Show details")
    
    p_search = subparsers.add_parser("search", help="Search for blocks")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    p_search.add_argument("--verbose", "-v", action="store_true", help="Show details")
    
    p_exec = subparsers.add_parser("exec", help="Execute a block")
    p_exec.add_argument("block", help="Block name to execute")
    p_exec.add_argument("--input", "-i", action="append", help="Input as key=value")
    p_exec.add_argument("--json", "-j", dest="json_input", help="Inputs as JSON object")
    
    p_stats = subparsers.add_parser("stats", help="Get library statistics")
    
    p_audit = subparsers.add_parser("audit", help="Get audit chain info")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    api_key = args.api_key or os.environ.get("NEUROP_API_KEY")
    if not api_key:
        print(color("Error: API key required. Use --api-key or set NEUROP_API_KEY", "red"))
        sys.exit(1)
    
    try:
        client = NeuropForge(api_key=api_key, base_url=args.host)
    except NeuropForgeError as e:
        print(color(f"Error: {e}", "red"))
        sys.exit(1)
    
    commands = {
        "health": cmd_health,
        "blocks": cmd_blocks,
        "search": cmd_search,
        "exec": cmd_exec,
        "stats": cmd_stats,
        "audit": cmd_audit,
    }
    
    try:
        commands[args.command](client, args)
    except NeuropForgeError as e:
        print(color(f"Error: {e}", "red"))
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
