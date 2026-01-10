"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Diff Utilities - Pure functions for computing differences.
All functions are pure, deterministic, and atomic.
"""

def compute_lcs_length(a: list, b: list) -> list:
    """Compute LCS length matrix."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp


def compute_diff(a: list, b: list) -> list:
    """Compute diff operations."""
    dp = compute_lcs_length(a, b)
    ops = []
    i, j = len(a), len(b)
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            ops.append({"op": "equal", "value": a[i - 1], "a_index": i - 1, "b_index": j - 1})
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
            ops.append({"op": "insert", "value": b[j - 1], "b_index": j - 1})
            j -= 1
        else:
            ops.append({"op": "delete", "value": a[i - 1], "a_index": i - 1})
            i -= 1
    return list(reversed(ops))


def compute_line_diff(text_a: str, text_b: str) -> list:
    """Compute line-by-line diff."""
    lines_a = text_a.split("\n")
    lines_b = text_b.split("\n")
    return compute_diff(lines_a, lines_b)


def count_diff_changes(diff: list) -> dict:
    """Count insertions, deletions, and unchanged."""
    inserts = sum(1 for op in diff if op["op"] == "insert")
    deletes = sum(1 for op in diff if op["op"] == "delete")
    equals = sum(1 for op in diff if op["op"] == "equal")
    return {"insertions": inserts, "deletions": deletes, "unchanged": equals}


def apply_diff(original: list, diff: list) -> list:
    """Apply diff operations to original list."""
    result = []
    for op in diff:
        if op["op"] == "equal":
            result.append(op["value"])
        elif op["op"] == "insert":
            result.append(op["value"])
    return result


def reverse_diff(diff: list) -> list:
    """Reverse diff operations."""
    reversed_ops = []
    for op in diff:
        if op["op"] == "insert":
            reversed_ops.append({"op": "delete", "value": op["value"]})
        elif op["op"] == "delete":
            reversed_ops.append({"op": "insert", "value": op["value"]})
        else:
            reversed_ops.append(op)
    return reversed_ops


def format_unified_diff(diff: list, context_lines: int) -> str:
    """Format diff as unified diff."""
    lines = []
    for op in diff:
        if op["op"] == "equal":
            lines.append(f" {op['value']}")
        elif op["op"] == "insert":
            lines.append(f"+{op['value']}")
        elif op["op"] == "delete":
            lines.append(f"-{op['value']}")
    return "\n".join(lines)


def compute_word_diff(text_a: str, text_b: str) -> list:
    """Compute word-by-word diff."""
    words_a = text_a.split()
    words_b = text_b.split()
    return compute_diff(words_a, words_b)


def compute_char_diff(text_a: str, text_b: str) -> list:
    """Compute character-by-character diff."""
    return compute_diff(list(text_a), list(text_b))


def diff_similarity(diff: list) -> float:
    """Calculate similarity from diff."""
    counts = count_diff_changes(diff)
    total = counts["insertions"] + counts["deletions"] + counts["unchanged"]
    if total == 0:
        return 1.0
    return counts["unchanged"] / total


def group_diff_by_operation(diff: list) -> list:
    """Group consecutive operations."""
    if not diff:
        return []
    groups = []
    current_op = diff[0]["op"]
    current_values = [diff[0]["value"]]
    for op in diff[1:]:
        if op["op"] == current_op:
            current_values.append(op["value"])
        else:
            groups.append({"op": current_op, "values": current_values})
            current_op = op["op"]
            current_values = [op["value"]]
    groups.append({"op": current_op, "values": current_values})
    return groups


def compute_dict_diff(dict_a: dict, dict_b: dict) -> dict:
    """Compute difference between two dictionaries."""
    keys_a = set(dict_a.keys())
    keys_b = set(dict_b.keys())
    added = {k: dict_b[k] for k in keys_b - keys_a}
    removed = {k: dict_a[k] for k in keys_a - keys_b}
    common = keys_a & keys_b
    modified = {}
    unchanged = {}
    for k in common:
        if dict_a[k] != dict_b[k]:
            modified[k] = {"old": dict_a[k], "new": dict_b[k]}
        else:
            unchanged[k] = dict_a[k]
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged
    }


def apply_dict_diff(original: dict, diff: dict) -> dict:
    """Apply dictionary diff to original."""
    result = dict(original)
    for k in diff.get("removed", {}):
        if k in result:
            del result[k]
    for k, v in diff.get("added", {}).items():
        result[k] = v
    for k, changes in diff.get("modified", {}).items():
        result[k] = changes["new"]
    return result


def compute_list_diff(list_a: list, list_b: list) -> dict:
    """Compute difference between two lists (by index)."""
    max_len = max(len(list_a), len(list_b))
    added = []
    removed = []
    modified = []
    unchanged = []
    for i in range(max_len):
        if i >= len(list_a):
            added.append({"index": i, "value": list_b[i]})
        elif i >= len(list_b):
            removed.append({"index": i, "value": list_a[i]})
        elif list_a[i] != list_b[i]:
            modified.append({"index": i, "old": list_a[i], "new": list_b[i]})
        else:
            unchanged.append({"index": i, "value": list_a[i]})
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged
    }


def merge_diffs(diff1: list, diff2: list) -> list:
    """Merge two diffs sequentially."""
    return diff1 + diff2


def patch_is_applicable(original: list, diff: list) -> bool:
    """Check if diff can be applied to original."""
    for op in diff:
        if op["op"] == "delete" or op["op"] == "equal":
            idx = op.get("a_index", -1)
            if idx >= 0 and (idx >= len(original) or original[idx] != op["value"]):
                return False
    return True


def create_patch(original: list, modified: list) -> dict:
    """Create a patch from original to modified."""
    diff = compute_diff(original, modified)
    return {
        "original_length": len(original),
        "modified_length": len(modified),
        "operations": diff
    }


def describe_changes(diff: list) -> str:
    """Create human-readable description of changes."""
    counts = count_diff_changes(diff)
    parts = []
    if counts["insertions"] > 0:
        parts.append(f"{counts['insertions']} added")
    if counts["deletions"] > 0:
        parts.append(f"{counts['deletions']} removed")
    if counts["unchanged"] > 0:
        parts.append(f"{counts['unchanged']} unchanged")
    return ", ".join(parts) if parts else "no changes"
