"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Heap Utilities - Pure functions for heap/priority queue operations.
All functions are pure, deterministic, and atomic.
"""

def create_min_heap() -> dict:
    """Create an empty min heap."""
    return {"type": "min", "items": []}


def create_max_heap() -> dict:
    """Create an empty max heap."""
    return {"type": "max", "items": []}


def heap_size(heap: dict) -> int:
    """Get number of items in heap."""
    return len(heap["items"])


def heap_is_empty(heap: dict) -> bool:
    """Check if heap is empty."""
    return len(heap["items"]) == 0


def heap_peek(heap: dict):
    """Peek at top item without removing."""
    if heap["items"]:
        return heap["items"][0]
    return None


def _parent_index(index: int) -> int:
    """Get parent index."""
    return (index - 1) // 2


def _left_child_index(index: int) -> int:
    """Get left child index."""
    return 2 * index + 1


def _right_child_index(index: int) -> int:
    """Get right child index."""
    return 2 * index + 2


def _should_swap(heap_type: str, parent_val, child_val) -> bool:
    """Determine if parent and child should swap."""
    if heap_type == "min":
        return child_val < parent_val
    return child_val > parent_val


def _heapify_up(items: list, heap_type: str, index: int) -> list:
    """Bubble up to maintain heap property."""
    result = list(items)
    while index > 0:
        parent = _parent_index(index)
        if _should_swap(heap_type, result[parent], result[index]):
            result[parent], result[index] = result[index], result[parent]
            index = parent
        else:
            break
    return result


def _heapify_down(items: list, heap_type: str, index: int) -> list:
    """Bubble down to maintain heap property."""
    result = list(items)
    size = len(result)
    while True:
        target = index
        left = _left_child_index(index)
        right = _right_child_index(index)
        if left < size and _should_swap(heap_type, result[target], result[left]):
            target = left
        if right < size and _should_swap(heap_type, result[target], result[right]):
            target = right
        if target == index:
            break
        result[index], result[target] = result[target], result[index]
        index = target
    return result


def heap_push(heap: dict, value) -> dict:
    """Push value onto heap."""
    result = {
        "type": heap["type"],
        "items": list(heap["items"]) + [value]
    }
    result["items"] = _heapify_up(result["items"], result["type"], len(result["items"]) - 1)
    return result


def heap_pop(heap: dict) -> dict:
    """Pop top value from heap."""
    if not heap["items"]:
        return {"heap": heap, "value": None}
    items = list(heap["items"])
    value = items[0]
    if len(items) == 1:
        return {"heap": {"type": heap["type"], "items": []}, "value": value}
    items[0] = items[-1]
    items.pop()
    items = _heapify_down(items, heap["type"], 0)
    return {"heap": {"type": heap["type"], "items": items}, "value": value}


def heap_push_pop(heap: dict, value) -> dict:
    """Push value and pop top (more efficient)."""
    if not heap["items"] or not _should_swap(heap["type"], value, heap["items"][0]):
        return {"heap": heap, "value": value}
    items = list(heap["items"])
    top = items[0]
    items[0] = value
    items = _heapify_down(items, heap["type"], 0)
    return {"heap": {"type": heap["type"], "items": items}, "value": top}


def heapify(values: list, heap_type: str) -> dict:
    """Build heap from list of values."""
    items = list(values)
    for i in range(len(items) // 2 - 1, -1, -1):
        items = _heapify_down(items, heap_type, i)
    return {"type": heap_type, "items": items}


def heap_to_sorted_list(heap: dict) -> list:
    """Extract all items in sorted order."""
    result = []
    current = {"type": heap["type"], "items": list(heap["items"])}
    while current["items"]:
        pop_result = heap_pop(current)
        result.append(pop_result["value"])
        current = pop_result["heap"]
    return result


def merge_heaps(heap1: dict, heap2: dict) -> dict:
    """Merge two heaps of same type."""
    combined = heap1["items"] + heap2["items"]
    return heapify(combined, heap1["type"])


def heap_replace(heap: dict, index: int, new_value) -> dict:
    """Replace value at index and reheapify."""
    if index < 0 or index >= len(heap["items"]):
        return heap
    items = list(heap["items"])
    old_value = items[index]
    items[index] = new_value
    if _should_swap(heap["type"], old_value, new_value):
        items = _heapify_up(items, heap["type"], index)
    else:
        items = _heapify_down(items, heap["type"], index)
    return {"type": heap["type"], "items": items}


def get_top_n(heap: dict, n: int) -> list:
    """Get top n items from heap."""
    result = []
    current = {"type": heap["type"], "items": list(heap["items"])}
    for _ in range(min(n, len(current["items"]))):
        pop_result = heap_pop(current)
        result.append(pop_result["value"])
        current = pop_result["heap"]
    return result


def build_priority_queue_item(priority: int, value) -> dict:
    """Build a priority queue item."""
    return {"priority": priority, "value": value}


def priority_compare(item1: dict, item2: dict) -> int:
    """Compare two priority queue items."""
    return item1["priority"] - item2["priority"]


def find_k_smallest(values: list, k: int) -> list:
    """Find k smallest values using heap."""
    if k <= 0:
        return []
    heap = heapify(values, "min")
    return get_top_n(heap, k)


def find_k_largest(values: list, k: int) -> list:
    """Find k largest values using heap."""
    if k <= 0:
        return []
    heap = heapify(values, "max")
    return get_top_n(heap, k)


def running_median_state() -> dict:
    """Create state for running median calculation."""
    return {
        "low_heap": create_max_heap(),
        "high_heap": create_min_heap()
    }


def running_median_add(state: dict, value: float) -> dict:
    """Add value to running median state."""
    low = state["low_heap"]
    high = state["high_heap"]
    if heap_is_empty(low) or value <= heap_peek(low):
        low = heap_push(low, value)
    else:
        high = heap_push(high, value)
    if heap_size(low) > heap_size(high) + 1:
        pop_result = heap_pop(low)
        low = pop_result["heap"]
        high = heap_push(high, pop_result["value"])
    elif heap_size(high) > heap_size(low):
        pop_result = heap_pop(high)
        high = pop_result["heap"]
        low = heap_push(low, pop_result["value"])
    return {"low_heap": low, "high_heap": high}


def running_median_get(state: dict) -> float:
    """Get current median from running median state."""
    low = state["low_heap"]
    high = state["high_heap"]
    if heap_is_empty(low):
        return 0.0
    if heap_size(low) > heap_size(high):
        return heap_peek(low)
    return (heap_peek(low) + heap_peek(high)) / 2
