"""
Neurop Block Forge CLI

Command-line interface for block execution, workflow running, and block discovery.

Usage:
    neurop-forge execute <block_id> --input '{"key": "value"}'
    neurop-forge workflow <workflow_id> [--input '{"key": "value"}']
    neurop-forge list [--category <cat>] [--tier A|B] [--limit N]
    neurop-forge info <block_id>
    neurop-forge workflows
    neurop-forge stats
"""

import argparse
import json
import sys
from typing import Optional

from neurop_forge import __version__
from neurop_forge.api import NeuropForge
from neurop_forge.validation.block_compatibility_tester import BlockCompatibilityTester
from neurop_forge.deduplication import (
    DeduplicationProcessor,
    DeduplicationPolicy,
    DeduplicationReport,
)
from neurop_forge.standardization import (
    InterfaceNormalizer,
    ParameterMapper,
)


def cmd_execute(args) -> int:
    """Execute a single block."""
    try:
        inputs = json.loads(args.input) if args.input else {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        return 1
    
    try:
        forge = NeuropForge()
        result = forge.execute_block(
            args.block_id,
            inputs,
            tier_a_only=not args.allow_tier_b
        )
        
        if result["success"]:
            print(json.dumps({"result": result["result"]}, indent=2, default=str))
            return 0
        else:
            print(f"Execution failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
            return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_workflow(args) -> int:
    """Run a reference workflow."""
    try:
        inputs = json.loads(args.input) if args.input else None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        return 1
    
    try:
        forge = NeuropForge()
        result = forge.run_workflow(args.workflow_id, inputs)
        
        output = {
            "success": result["success"],
            "steps": f"{result['steps_succeeded']}/{result['steps_executed']}",
            "duration_ms": round(result["duration_ms"], 2),
            "outputs": result["outputs"]
        }
        print(json.dumps(output, indent=2, default=str))
        return 0 if result["success"] else 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args) -> int:
    """List verified blocks."""
    try:
        forge = NeuropForge()
        blocks = forge.list_verified_blocks(
            category=args.category,
            tier=args.tier,
            limit=args.limit
        )
        
        if args.json:
            print(json.dumps(blocks, indent=2))
        else:
            if not blocks:
                print("No blocks found matching criteria.")
                return 0
            
            print(f"{'ID':<35} {'Category':<15} {'Tier':<5} Description")
            print("-" * 80)
            for block in blocks:
                desc = block["description"][:30] + "..." if len(block["description"]) > 30 else block["description"]
                print(f"{block['id']:<35} {block['category']:<15} {block['tier']:<5} {desc}")
            print(f"\nShowing {len(blocks)} blocks")
        
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args) -> int:
    """Get detailed block information."""
    try:
        forge = NeuropForge()
        info = forge.get_block_info(args.block_id)
        print(json.dumps(info, indent=2, default=str))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_workflows(args) -> int:
    """List available workflows."""
    try:
        forge = NeuropForge()
        workflows = forge.list_workflows()
        
        if args.json:
            print(json.dumps(workflows, indent=2))
        else:
            print(f"{'ID':<25} {'Steps':<7} Description")
            print("-" * 60)
            for wf in workflows:
                desc = wf["description"][:35] + "..." if len(wf["description"]) > 35 else wf["description"]
                print(f"{wf['id']:<25} {wf['steps']:<7} {desc}")
        
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_stats(args) -> int:
    """Show library statistics."""
    try:
        forge = NeuropForge()
        stats = forge.stats
        
        print(f"Neurop Block Forge v{__version__}")
        print("=" * 40)
        print(f"Total Verified Blocks: {stats['total_verified']}")
        print(f"  Tier-A (Deterministic): {stats['tier_a']}")
        print(f"  Tier-B (Context-dependent): {stats['tier_b']}")
        print()
        print("Available Workflows:")
        for wf in forge.list_workflows():
            print(f"  - {wf['id']}: {wf['steps']} steps")
        
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_test(args) -> int:
    """Run block compatibility tests."""
    print("Running block compatibility tests...")
    print()
    
    try:
        tester = BlockCompatibilityTester()
        report = tester.run_full_test(tier_a_only=not args.all)
        print(tester.generate_text_report(report))
        
        if args.json:
            import json
            json_report = {
                "total": report.total_blocks,
                "passed": report.passed,
                "failed": report.failed,
                "pass_rate": round(report.passed / report.total_blocks * 100, 1) if report.total_blocks > 0 else 0,
                "duplicate_names": list(report.duplicate_names.keys()),
                "execution_failures": [(n, e) for _, n, e in report.execution_failures]
            }
            print("\n[JSON OUTPUT]")
            print(json.dumps(json_report, indent=2))
        
        return 0 if report.failed == 0 else 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_dedup(args) -> int:
    """Analyze and remove duplicate blocks."""
    policy_map = {
        "keep_best": DeduplicationPolicy.KEEP_BEST,
        "namespace": DeduplicationPolicy.NAMESPACE,
        "quarantine": DeduplicationPolicy.QUARANTINE,
    }
    policy = policy_map.get(args.policy, DeduplicationPolicy.KEEP_BEST)
    
    print(f"Running deduplication analysis (policy: {args.policy})...")
    print()
    
    try:
        processor = DeduplicationProcessor(policy=policy)
        result = processor.run(execute=args.execute)
        report = DeduplicationReport(processor.get_hasher(), result)
        
        if args.json:
            print(json.dumps(report.generate_json_report(), indent=2))
        elif args.detailed:
            print(report.generate_detailed_report())
        else:
            print(report.generate_summary())
        
        if args.execute:
            print(f"\nDeduplicated library created at: .neurop_deduplicated_library/")
            print(f"To use: Update library_path in your code or copy files.")
        else:
            print("\nThis was a dry run. Use --execute to create deduplicated library.")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_standardize(args) -> int:
    """Analyze and standardize parameter names."""
    print("Running parameter standardization analysis...")
    print()
    
    try:
        normalizer = InterfaceNormalizer(library_path=".neurop_expanded_library")
        
        if args.execute:
            result = normalizer.normalize(execute=True, preserve_aliases=True)
            
            print("=" * 60)
            print("  PARAMETER STANDARDIZATION RESULT")
            print("=" * 60)
            print()
            print(f"  Blocks processed:       {result.blocks_processed}")
            print(f"  Blocks modified:        {result.blocks_modified}")
            print(f"  Parameters normalized:  {result.parameters_normalized}")
            print(f"  Parameters unchanged:   {result.parameters_unchanged}")
            print(f"  Parameters unmapped:    {result.parameters_unmapped}")
            
            if result.errors:
                print(f"\n  Errors: {len(result.errors)}")
                for err in result.errors[:5]:
                    print(f"    - {err}")
            
            print("\nStandardization complete. Original names preserved as aliases.")
        else:
            stats = normalizer.analyze()
            
            print("=" * 60)
            print("  PARAMETER STANDARDIZATION ANALYSIS")
            print("=" * 60)
            print()
            print(f"  Blocks analyzed:        {stats.get('blocks_analyzed', 0)}")
            print(f"  Blocks with changes:    {stats.get('blocks_with_changes', 0)}")
            print(f"  Total parameters:       {stats.get('total_parameters', 0)}")
            print(f"  Can be mapped:          {stats.get('mapped', 0)}")
            print(f"  Already canonical:      {stats.get('unchanged', 0)}")
            print(f"  Unmapped:               {stats.get('unmapped', 0)}")
            print(f"  Mapping rate:           {stats.get('mapping_rate', 0)}%")
            
            if args.detailed:
                print("\n  Top Mappings:")
                for mapping, count in stats.get('top_mappings', [])[:15]:
                    print(f"    {mapping}: {count}")
            
            print("\nThis was a dry run. Use --execute to apply standardization.")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="neurop-forge",
        description="Neurop Block Forge - Semantic block composition engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    exec_parser = subparsers.add_parser("execute", help="Execute a single block")
    exec_parser.add_argument("block_id", help="Block ID to execute")
    exec_parser.add_argument("--input", "-i", help="JSON input dictionary")
    exec_parser.add_argument("--allow-tier-b", action="store_true", 
                            help="Allow Tier-B blocks (context-dependent)")
    exec_parser.set_defaults(func=cmd_execute)
    
    wf_parser = subparsers.add_parser("workflow", help="Run a reference workflow")
    wf_parser.add_argument("workflow_id", help="Workflow ID to run")
    wf_parser.add_argument("--input", "-i", help="JSON input dictionary (optional)")
    wf_parser.set_defaults(func=cmd_workflow)
    
    list_parser = subparsers.add_parser("list", help="List verified blocks")
    list_parser.add_argument("--category", "-c", help="Filter by category")
    list_parser.add_argument("--tier", "-t", choices=["A", "B"], help="Filter by tier")
    list_parser.add_argument("--limit", "-l", type=int, default=50, help="Max results")
    list_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    list_parser.set_defaults(func=cmd_list)
    
    info_parser = subparsers.add_parser("info", help="Get block details")
    info_parser.add_argument("block_id", help="Block ID to inspect")
    info_parser.set_defaults(func=cmd_info)
    
    wfs_parser = subparsers.add_parser("workflows", help="List available workflows")
    wfs_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    wfs_parser.set_defaults(func=cmd_workflows)
    
    stats_parser = subparsers.add_parser("stats", help="Show library statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    test_parser = subparsers.add_parser("test", help="Run block compatibility tests")
    test_parser.add_argument("--all", "-a", action="store_true", 
                            help="Test all blocks (not just Tier-A)")
    test_parser.add_argument("--json", "-j", action="store_true", 
                            help="Output JSON summary")
    test_parser.set_defaults(func=cmd_test)
    
    dedup_parser = subparsers.add_parser("dedup", help="Analyze and remove duplicate blocks")
    dedup_parser.add_argument("--policy", "-p", 
                             choices=["keep_best", "namespace", "quarantine"],
                             default="keep_best",
                             help="Deduplication policy (default: keep_best)")
    dedup_parser.add_argument("--execute", "-x", action="store_true",
                             help="Actually execute deduplication (creates new library)")
    dedup_parser.add_argument("--detailed", "-d", action="store_true",
                             help="Show detailed report with duplicate groups")
    dedup_parser.add_argument("--json", "-j", action="store_true",
                             help="Output JSON report")
    dedup_parser.set_defaults(func=cmd_dedup)
    
    std_parser = subparsers.add_parser("standardize", help="Standardize parameter names")
    std_parser.add_argument("--execute", "-x", action="store_true",
                           help="Apply standardization (modifies blocks)")
    std_parser.add_argument("--detailed", "-d", action="store_true",
                           help="Show detailed mapping analysis")
    std_parser.set_defaults(func=cmd_standardize)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
