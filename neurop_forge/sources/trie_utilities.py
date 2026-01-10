"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Trie Utilities - Pure functions for trie (prefix tree) operations.
All functions are pure, deterministic, and atomic.
"""

def create_trie_node() -> dict:
    """Create an empty trie node."""
    return {"children": {}, "is_end": False, "value": None}


def create_trie() -> dict:
    """Create an empty trie."""
    return {"root": create_trie_node(), "size": 0}


def trie_insert(trie: dict, key: str, value) -> dict:
    """Insert a key-value pair into trie."""
    def insert_helper(node: dict, key: str, pos: int, value) -> dict:
        result = {
            "children": dict(node["children"]),
            "is_end": node["is_end"],
            "value": node["value"]
        }
        if pos == len(key):
            result["is_end"] = True
            result["value"] = value
            return result
        char = key[pos]
        if char in result["children"]:
            result["children"][char] = insert_helper(result["children"][char], key, pos + 1, value)
        else:
            new_node = create_trie_node()
            result["children"][char] = insert_helper(new_node, key, pos + 1, value)
        return result
    new_root = insert_helper(trie["root"], key, 0, value)
    return {"root": new_root, "size": trie["size"] + 1}


def trie_search(trie: dict, key: str) -> dict:
    """Search for a key in trie."""
    node = trie["root"]
    for char in key:
        if char not in node["children"]:
            return {"found": False, "value": None}
        node = node["children"][char]
    if node["is_end"]:
        return {"found": True, "value": node["value"]}
    return {"found": False, "value": None}


def trie_starts_with(trie: dict, prefix: str) -> bool:
    """Check if any key starts with prefix."""
    node = trie["root"]
    for char in prefix:
        if char not in node["children"]:
            return False
        node = node["children"][char]
    return True


def trie_get_node(trie: dict, prefix: str) -> dict:
    """Get node at prefix position."""
    node = trie["root"]
    for char in prefix:
        if char not in node["children"]:
            return None
        node = node["children"][char]
    return node


def trie_keys_with_prefix(trie: dict, prefix: str) -> list:
    """Get all keys with given prefix."""
    node = trie_get_node(trie, prefix)
    if not node:
        return []
    def collect_keys(node: dict, current_prefix: str, keys: list):
        if node["is_end"]:
            keys.append(current_prefix)
        for char, child in node["children"].items():
            collect_keys(child, current_prefix + char, keys)
    keys = []
    collect_keys(node, prefix, keys)
    return keys


def trie_count_with_prefix(trie: dict, prefix: str) -> int:
    """Count keys with given prefix."""
    node = trie_get_node(trie, prefix)
    if not node:
        return 0
    def count_keys(node: dict) -> int:
        count = 1 if node["is_end"] else 0
        for child in node["children"].values():
            count += count_keys(child)
        return count
    return count_keys(node)


def trie_delete(trie: dict, key: str) -> dict:
    """Delete a key from trie."""
    def delete_helper(node: dict, key: str, pos: int) -> dict:
        result = {
            "children": dict(node["children"]),
            "is_end": node["is_end"],
            "value": node["value"]
        }
        if pos == len(key):
            result["is_end"] = False
            result["value"] = None
            return result
        char = key[pos]
        if char not in result["children"]:
            return result
        result["children"][char] = delete_helper(result["children"][char], key, pos + 1)
        child = result["children"][char]
        if not child["is_end"] and not child["children"]:
            del result["children"][char]
        return result
    if not trie_search(trie, key)["found"]:
        return trie
    new_root = delete_helper(trie["root"], key, 0)
    return {"root": new_root, "size": trie["size"] - 1}


def trie_all_keys(trie: dict) -> list:
    """Get all keys in trie."""
    return trie_keys_with_prefix(trie, "")


def trie_is_empty(trie: dict) -> bool:
    """Check if trie is empty."""
    return trie["size"] == 0


def trie_longest_prefix(trie: dict, text: str) -> str:
    """Find longest prefix in trie that matches start of text."""
    node = trie["root"]
    longest = ""
    current = ""
    for char in text:
        if char not in node["children"]:
            break
        current += char
        node = node["children"][char]
        if node["is_end"]:
            longest = current
    return longest


def trie_autocomplete(trie: dict, prefix: str, max_results: int) -> list:
    """Get autocomplete suggestions."""
    keys = trie_keys_with_prefix(trie, prefix)
    return sorted(keys)[:max_results]


def trie_fuzzy_search(trie: dict, pattern: str, max_distance: int) -> list:
    """Fuzzy search in trie with max edit distance."""
    results = []
    def search_helper(node: dict, current: str, pattern: str, distance: int):
        if distance > max_distance:
            return
        if not pattern:
            if node["is_end"]:
                results.append({"key": current, "distance": max_distance - distance + len(pattern)})
            for char, child in node["children"].items():
                search_helper(child, current + char, "", distance)
            return
        if node["is_end"] and distance >= len(pattern):
            results.append({"key": current, "distance": len(pattern)})
        for char, child in node["children"].items():
            if char == pattern[0]:
                search_helper(child, current + char, pattern[1:], distance)
            else:
                search_helper(child, current + char, pattern[1:], distance - 1)
                search_helper(child, current + char, pattern, distance - 1)
        search_helper(node, current, pattern[1:], distance - 1)
    search_helper(trie["root"], "", pattern, max_distance)
    return sorted(results, key=lambda x: x["distance"])


def build_trie_from_list(words: list) -> dict:
    """Build trie from list of words."""
    trie = create_trie()
    for word in words:
        trie = trie_insert(trie, word, word)
    return trie


def trie_to_dict(trie: dict) -> dict:
    """Convert trie to dictionary of key-value pairs."""
    result = {}
    def collect(node: dict, prefix: str):
        if node["is_end"]:
            result[prefix] = node["value"]
        for char, child in node["children"].items():
            collect(child, prefix + char)
    collect(trie["root"], "")
    return result


def merge_tries(trie1: dict, trie2: dict) -> dict:
    """Merge two tries."""
    result = {"root": dict(trie1["root"]), "size": trie1["size"]}
    for key, value in trie_to_dict(trie2).items():
        if not trie_search(result, key)["found"]:
            result = trie_insert(result, key, value)
    return result


def trie_depth(trie: dict) -> int:
    """Get maximum depth of trie."""
    def max_depth(node: dict) -> int:
        if not node["children"]:
            return 0
        return 1 + max(max_depth(child) for child in node["children"].values())
    return max_depth(trie["root"])


def trie_node_count(trie: dict) -> int:
    """Count total nodes in trie."""
    def count_nodes(node: dict) -> int:
        return 1 + sum(count_nodes(child) for child in node["children"].values())
    return count_nodes(trie["root"])
