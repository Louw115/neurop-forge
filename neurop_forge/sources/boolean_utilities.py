"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Boolean Utilities - Pure functions for boolean logic operations.
All functions are pure, deterministic, and atomic.
"""

def logical_and(a: bool, b: bool) -> bool:
    """Logical AND operation."""
    return a and b


def logical_or(a: bool, b: bool) -> bool:
    """Logical OR operation."""
    return a or b


def logical_not(a: bool) -> bool:
    """Logical NOT operation."""
    return not a


def logical_xor(a: bool, b: bool) -> bool:
    """Logical XOR operation."""
    return a != b


def logical_nand(a: bool, b: bool) -> bool:
    """Logical NAND operation."""
    return not (a and b)


def logical_nor(a: bool, b: bool) -> bool:
    """Logical NOR operation."""
    return not (a or b)


def logical_xnor(a: bool, b: bool) -> bool:
    """Logical XNOR operation."""
    return a == b


def logical_implies(a: bool, b: bool) -> bool:
    """Logical implication (a implies b)."""
    return (not a) or b


def all_true(values: list) -> bool:
    """Check if all values are true."""
    return all(values)


def any_true(values: list) -> bool:
    """Check if any value is true."""
    return any(values)


def none_true(values: list) -> bool:
    """Check if no values are true."""
    return not any(values)


def exactly_one_true(values: list) -> bool:
    """Check if exactly one value is true."""
    return sum(1 for v in values if v) == 1


def at_least_n_true(values: list, n: int) -> bool:
    """Check if at least n values are true."""
    return sum(1 for v in values if v) >= n


def at_most_n_true(values: list, n: int) -> bool:
    """Check if at most n values are true."""
    return sum(1 for v in values if v) <= n


def count_true(values: list) -> int:
    """Count number of true values."""
    return sum(1 for v in values if v)


def count_false(values: list) -> int:
    """Count number of false values."""
    return sum(1 for v in values if not v)


def majority_true(values: list) -> bool:
    """Check if majority are true."""
    return count_true(values) > len(values) / 2


def toggle(value: bool) -> bool:
    """Toggle boolean value."""
    return not value


def to_int(value: bool) -> int:
    """Convert boolean to int."""
    return 1 if value else 0


def from_int(value: int) -> bool:
    """Convert int to boolean."""
    return value != 0


def to_string(value: bool) -> str:
    """Convert boolean to string."""
    return "true" if value else "false"


def from_string(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ["true", "1", "yes", "on"]


def coalesce(values: list, default: bool) -> bool:
    """Return first non-None boolean or default."""
    for v in values:
        if v is not None:
            return v
    return default


def chain_and(*values) -> bool:
    """Chain AND across multiple values."""
    return all(values)


def chain_or(*values) -> bool:
    """Chain OR across multiple values."""
    return any(values)


def ternary(condition: bool, if_true, if_false):
    """Ternary operator."""
    return if_true if condition else if_false


def safe_and(a, b) -> bool:
    """Safe AND handling None values."""
    if a is None or b is None:
        return False
    return a and b


def safe_or(a, b) -> bool:
    """Safe OR handling None values."""
    if a is None and b is None:
        return False
    if a is None:
        return bool(b)
    if b is None:
        return bool(a)
    return a or b


def equals(a: bool, b: bool) -> bool:
    """Check if booleans are equal."""
    return a == b


def evaluate_expression(expression: str, values: dict) -> bool:
    """Evaluate boolean expression with variables."""
    for key, value in values.items():
        expression = expression.replace(key, str(value).lower())
    expression = expression.replace("and", " and ").replace("or", " or ").replace("not", " not ")
    try:
        return eval(expression, {"__builtins__": {}}, {})
    except:
        return False


def truth_table_row(inputs: list, operation: str) -> dict:
    """Generate truth table row for operation."""
    if operation == "and":
        result = all(inputs)
    elif operation == "or":
        result = any(inputs)
    elif operation == "xor":
        result = sum(inputs) % 2 == 1
    else:
        result = False
    return {"inputs": inputs, "result": result}


def is_tautology(values: list) -> bool:
    """Check if all possible values are true."""
    return all(values)


def is_contradiction(values: list) -> bool:
    """Check if all possible values are false."""
    return not any(values)


def is_satisfiable(values: list) -> bool:
    """Check if at least one value is true."""
    return any(values)


def partition_by_boolean(items: list, predicate) -> dict:
    """Partition items by boolean predicate."""
    true_items = []
    false_items = []
    for item in items:
        if predicate(item):
            true_items.append(item)
        else:
            false_items.append(item)
    return {"true": true_items, "false": false_items}
