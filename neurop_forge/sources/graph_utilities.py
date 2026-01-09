"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Graph Utilities - Pure functions for graph data structures.
All functions are pure, deterministic, and atomic.
"""

def create_graph(directed: bool) -> dict:
    """Create an empty graph."""
    return {
        "directed": directed,
        "nodes": {},
        "edges": []
    }


def add_node(graph: dict, node_id: str, data: dict) -> dict:
    """Add a node to the graph."""
    result = {
        "directed": graph["directed"],
        "nodes": dict(graph["nodes"]),
        "edges": list(graph["edges"])
    }
    result["nodes"][node_id] = data
    return result


def remove_node(graph: dict, node_id: str) -> dict:
    """Remove a node and its edges from the graph."""
    result = {
        "directed": graph["directed"],
        "nodes": {k: v for k, v in graph["nodes"].items() if k != node_id},
        "edges": [e for e in graph["edges"] if e["from"] != node_id and e["to"] != node_id]
    }
    return result


def add_edge(graph: dict, from_node: str, to_node: str, weight: float, data: dict) -> dict:
    """Add an edge to the graph."""
    result = {
        "directed": graph["directed"],
        "nodes": dict(graph["nodes"]),
        "edges": list(graph["edges"])
    }
    result["edges"].append({
        "from": from_node,
        "to": to_node,
        "weight": weight,
        "data": data
    })
    return result


def remove_edge(graph: dict, from_node: str, to_node: str) -> dict:
    """Remove an edge from the graph."""
    result = {
        "directed": graph["directed"],
        "nodes": dict(graph["nodes"]),
        "edges": [e for e in graph["edges"] if not (e["from"] == from_node and e["to"] == to_node)]
    }
    return result


def get_neighbors(graph: dict, node_id: str) -> list:
    """Get neighboring nodes."""
    neighbors = []
    for edge in graph["edges"]:
        if edge["from"] == node_id:
            neighbors.append(edge["to"])
        elif not graph["directed"] and edge["to"] == node_id:
            neighbors.append(edge["from"])
    return neighbors


def get_in_degree(graph: dict, node_id: str) -> int:
    """Get in-degree of a node (for directed graphs)."""
    return sum(1 for e in graph["edges"] if e["to"] == node_id)


def get_out_degree(graph: dict, node_id: str) -> int:
    """Get out-degree of a node (for directed graphs)."""
    return sum(1 for e in graph["edges"] if e["from"] == node_id)


def get_degree(graph: dict, node_id: str) -> int:
    """Get degree of a node."""
    if graph["directed"]:
        return get_in_degree(graph, node_id) + get_out_degree(graph, node_id)
    return sum(1 for e in graph["edges"] if e["from"] == node_id or e["to"] == node_id)


def has_edge(graph: dict, from_node: str, to_node: str) -> bool:
    """Check if edge exists."""
    for edge in graph["edges"]:
        if edge["from"] == from_node and edge["to"] == to_node:
            return True
        if not graph["directed"] and edge["from"] == to_node and edge["to"] == from_node:
            return True
    return False


def get_edge_weight(graph: dict, from_node: str, to_node: str) -> float:
    """Get weight of an edge."""
    for edge in graph["edges"]:
        if edge["from"] == from_node and edge["to"] == to_node:
            return edge["weight"]
        if not graph["directed"] and edge["from"] == to_node and edge["to"] == from_node:
            return edge["weight"]
    return 0.0


def count_nodes(graph: dict) -> int:
    """Count nodes in graph."""
    return len(graph["nodes"])


def count_edges(graph: dict) -> int:
    """Count edges in graph."""
    return len(graph["edges"])


def get_all_node_ids(graph: dict) -> list:
    """Get all node IDs."""
    return list(graph["nodes"].keys())


def build_adjacency_list(graph: dict) -> dict:
    """Build adjacency list representation."""
    adj = {node_id: [] for node_id in graph["nodes"]}
    for edge in graph["edges"]:
        adj[edge["from"]].append(edge["to"])
        if not graph["directed"]:
            adj[edge["to"]].append(edge["from"])
    return adj


def find_path_bfs(graph: dict, start: str, end: str) -> list:
    """Find path using BFS."""
    if start not in graph["nodes"] or end not in graph["nodes"]:
        return []
    adj = build_adjacency_list(graph)
    visited = {start}
    queue = [(start, [start])]
    while queue:
        current, path = queue.pop(0)
        if current == end:
            return path
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []


def find_all_paths(graph: dict, start: str, end: str, max_depth: int) -> list:
    """Find all paths between two nodes up to max depth."""
    if start not in graph["nodes"] or end not in graph["nodes"]:
        return []
    adj = build_adjacency_list(graph)
    all_paths = []
    def dfs(current, path, depth):
        if depth > max_depth:
            return
        if current == end:
            all_paths.append(list(path))
            return
        for neighbor in adj.get(current, []):
            if neighbor not in path:
                path.append(neighbor)
                dfs(neighbor, path, depth + 1)
                path.pop()
    dfs(start, [start], 0)
    return all_paths


def detect_cycle(graph: dict) -> bool:
    """Detect if graph has a cycle."""
    if not graph["directed"]:
        visited = set()
        def dfs(node, parent):
            visited.add(node)
            adj = build_adjacency_list(graph)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, node):
                        return True
                elif neighbor != parent:
                    return True
            return False
        for node in graph["nodes"]:
            if node not in visited:
                if dfs(node, None):
                    return True
        return False
    else:
        white, gray, black = set(graph["nodes"].keys()), set(), set()
        adj = build_adjacency_list(graph)
        def dfs(node):
            white.discard(node)
            gray.add(node)
            for neighbor in adj.get(node, []):
                if neighbor in gray:
                    return True
                if neighbor in white and dfs(neighbor):
                    return True
            gray.discard(node)
            black.add(node)
            return False
        while white:
            if dfs(next(iter(white))):
                return True
        return False


def topological_sort(graph: dict) -> list:
    """Topological sort for DAG."""
    if not graph["directed"]:
        return []
    in_degree = {node: 0 for node in graph["nodes"]}
    for edge in graph["edges"]:
        in_degree[edge["to"]] += 1
    queue = [node for node, deg in in_degree.items() if deg == 0]
    result = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for edge in graph["edges"]:
            if edge["from"] == node:
                in_degree[edge["to"]] -= 1
                if in_degree[edge["to"]] == 0:
                    queue.append(edge["to"])
    return result if len(result) == len(graph["nodes"]) else []


def find_connected_components(graph: dict) -> list:
    """Find connected components in undirected graph."""
    if graph["directed"]:
        return []
    visited = set()
    components = []
    adj = build_adjacency_list(graph)
    def dfs(node, component):
        visited.add(node)
        component.append(node)
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, component)
    for node in graph["nodes"]:
        if node not in visited:
            component = []
            dfs(node, component)
            components.append(component)
    return components


def is_connected(graph: dict) -> bool:
    """Check if graph is connected."""
    if not graph["nodes"]:
        return True
    components = find_connected_components(graph)
    return len(components) <= 1


def get_graph_density(graph: dict) -> float:
    """Calculate graph density."""
    n = count_nodes(graph)
    if n <= 1:
        return 0.0
    e = count_edges(graph)
    max_edges = n * (n - 1) if graph["directed"] else n * (n - 1) // 2
    return e / max_edges if max_edges > 0 else 0.0


def reverse_graph(graph: dict) -> dict:
    """Reverse a directed graph."""
    if not graph["directed"]:
        return graph
    return {
        "directed": True,
        "nodes": dict(graph["nodes"]),
        "edges": [{"from": e["to"], "to": e["from"], "weight": e["weight"], "data": e["data"]} for e in graph["edges"]]
    }
