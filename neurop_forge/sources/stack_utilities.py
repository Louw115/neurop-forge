"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Stack Utilities - Pure functions for stack data structures.
All functions are pure, deterministic, and atomic.
"""

def create_stack() -> dict:
    """Create an empty stack."""
    return {"items": [], "size": 0}


def stack_push(stack: dict, item) -> dict:
    """Push item onto stack."""
    return {
        "items": list(stack["items"]) + [item],
        "size": stack["size"] + 1
    }


def stack_pop(stack: dict) -> dict:
    """Pop item from stack."""
    if not stack["items"]:
        return {"stack": stack, "item": None}
    items = list(stack["items"])
    item = items.pop()
    return {
        "stack": {"items": items, "size": len(items)},
        "item": item
    }


def stack_peek(stack: dict):
    """Peek at top item without removing."""
    if stack["items"]:
        return stack["items"][-1]
    return None


def stack_is_empty(stack: dict) -> bool:
    """Check if stack is empty."""
    return stack["size"] == 0


def stack_size(stack: dict) -> int:
    """Get stack size."""
    return stack["size"]


def stack_clear(stack: dict) -> dict:
    """Clear the stack."""
    return {"items": [], "size": 0}


def stack_to_list(stack: dict) -> list:
    """Convert stack to list (top at end)."""
    return list(stack["items"])


def stack_from_list(items: list) -> dict:
    """Create stack from list."""
    return {"items": list(items), "size": len(items)}


def stack_reverse(stack: dict) -> dict:
    """Reverse stack order."""
    return {"items": list(reversed(stack["items"])), "size": stack["size"]}


def stack_contains(stack: dict, item) -> bool:
    """Check if stack contains item."""
    return item in stack["items"]


def stack_position(stack: dict, item) -> int:
    """Get position of item from top (0 = top)."""
    items = list(reversed(stack["items"]))
    try:
        return items.index(item)
    except ValueError:
        return -1


def stack_peek_at(stack: dict, position: int):
    """Peek at item at position from top."""
    if position < 0 or position >= len(stack["items"]):
        return None
    return stack["items"][-(position + 1)]


def stack_duplicate_top(stack: dict) -> dict:
    """Duplicate top item."""
    if not stack["items"]:
        return stack
    return stack_push(stack, stack["items"][-1])


def stack_swap_top_two(stack: dict) -> dict:
    """Swap top two items."""
    if len(stack["items"]) < 2:
        return stack
    items = list(stack["items"])
    items[-1], items[-2] = items[-2], items[-1]
    return {"items": items, "size": stack["size"]}


def stack_rotate(stack: dict, positions: int) -> dict:
    """Rotate stack by positions."""
    if not stack["items"]:
        return stack
    items = list(stack["items"])
    positions = positions % len(items)
    items = items[-positions:] + items[:-positions]
    return {"items": items, "size": stack["size"]}


def stack_push_multiple(stack: dict, items: list) -> dict:
    """Push multiple items onto stack."""
    return {
        "items": list(stack["items"]) + list(items),
        "size": stack["size"] + len(items)
    }


def stack_pop_multiple(stack: dict, count: int) -> dict:
    """Pop multiple items from stack."""
    if count <= 0:
        return {"stack": stack, "items": []}
    items = list(stack["items"])
    popped = items[-count:] if count <= len(items) else list(items)
    remaining = items[:-count] if count <= len(items) else []
    return {
        "stack": {"items": remaining, "size": len(remaining)},
        "items": list(reversed(popped))
    }


def create_min_stack() -> dict:
    """Create a stack that tracks minimum."""
    return {"items": [], "mins": []}


def min_stack_push(stack: dict, item) -> dict:
    """Push to min stack."""
    items = list(stack["items"]) + [item]
    mins = list(stack["mins"])
    if not mins or item <= mins[-1]:
        mins.append(item)
    else:
        mins.append(mins[-1])
    return {"items": items, "mins": mins}


def min_stack_pop(stack: dict) -> dict:
    """Pop from min stack."""
    if not stack["items"]:
        return {"stack": stack, "item": None}
    items = list(stack["items"])
    mins = list(stack["mins"])
    item = items.pop()
    mins.pop()
    return {
        "stack": {"items": items, "mins": mins},
        "item": item
    }


def min_stack_get_min(stack: dict):
    """Get minimum value in stack."""
    if stack["mins"]:
        return stack["mins"][-1]
    return None


def create_max_stack() -> dict:
    """Create a stack that tracks maximum."""
    return {"items": [], "maxs": []}


def max_stack_push(stack: dict, item) -> dict:
    """Push to max stack."""
    items = list(stack["items"]) + [item]
    maxs = list(stack["maxs"])
    if not maxs or item >= maxs[-1]:
        maxs.append(item)
    else:
        maxs.append(maxs[-1])
    return {"items": items, "maxs": maxs}


def max_stack_pop(stack: dict) -> dict:
    """Pop from max stack."""
    if not stack["items"]:
        return {"stack": stack, "item": None}
    items = list(stack["items"])
    maxs = list(stack["maxs"])
    item = items.pop()
    maxs.pop()
    return {
        "stack": {"items": items, "maxs": maxs},
        "item": item
    }


def max_stack_get_max(stack: dict):
    """Get maximum value in stack."""
    if stack["maxs"]:
        return stack["maxs"][-1]
    return None


def is_balanced_parentheses(s: str) -> bool:
    """Check if parentheses are balanced using stack logic."""
    stack = []
    pairs = {")": "(", "}": "{", "]": "["}
    for char in s:
        if char in "({[":
            stack.append(char)
        elif char in ")}]":
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return len(stack) == 0


def evaluate_postfix(tokens: list) -> float:
    """Evaluate postfix expression using stack."""
    stack = []
    for token in tokens:
        if isinstance(token, (int, float)):
            stack.append(token)
        elif token == "+":
            b, a = stack.pop(), stack.pop()
            stack.append(a + b)
        elif token == "-":
            b, a = stack.pop(), stack.pop()
            stack.append(a - b)
        elif token == "*":
            b, a = stack.pop(), stack.pop()
            stack.append(a * b)
        elif token == "/":
            b, a = stack.pop(), stack.pop()
            stack.append(a / b if b != 0 else 0)
    return stack[0] if stack else 0
