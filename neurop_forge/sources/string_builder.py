"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
String Builder - Pure functions for efficient string construction.
All functions are pure, deterministic, and atomic.
"""

def create_builder() -> dict:
    """Create a string builder."""
    return {"parts": [], "length": 0}


def append(builder: dict, text: str) -> dict:
    """Append text to builder."""
    return {
        "parts": builder["parts"] + [text],
        "length": builder["length"] + len(text)
    }


def append_line(builder: dict, text: str) -> dict:
    """Append text with newline."""
    return append(builder, text + "\n")


def append_format(builder: dict, template: str, *args) -> dict:
    """Append formatted text."""
    return append(builder, template.format(*args))


def append_join(builder: dict, items: list, separator: str) -> dict:
    """Append items joined by separator."""
    return append(builder, separator.join(str(item) for item in items))


def append_repeated(builder: dict, text: str, count: int) -> dict:
    """Append text repeated count times."""
    return append(builder, text * count)


def prepend(builder: dict, text: str) -> dict:
    """Prepend text to builder."""
    return {
        "parts": [text] + builder["parts"],
        "length": builder["length"] + len(text)
    }


def insert(builder: dict, index: int, text: str) -> dict:
    """Insert text at position (by parts)."""
    parts = list(builder["parts"])
    if index <= 0:
        parts.insert(0, text)
    elif index >= len(parts):
        parts.append(text)
    else:
        parts.insert(index, text)
    return {"parts": parts, "length": builder["length"] + len(text)}


def clear(builder: dict) -> dict:
    """Clear the builder."""
    return create_builder()


def build(builder: dict) -> str:
    """Build the final string."""
    return "".join(builder["parts"])


def builder_length(builder: dict) -> int:
    """Get total length."""
    return builder["length"]


def is_empty(builder: dict) -> bool:
    """Check if builder is empty."""
    return builder["length"] == 0


def reverse(builder: dict) -> dict:
    """Reverse the order of parts."""
    return {"parts": list(reversed(builder["parts"])), "length": builder["length"]}


def trim_parts(builder: dict) -> dict:
    """Trim whitespace from each part."""
    trimmed = [p.strip() for p in builder["parts"]]
    return {"parts": trimmed, "length": sum(len(p) for p in trimmed)}


def create_html_builder() -> dict:
    """Create an HTML builder."""
    return {"parts": [], "length": 0, "indent": 0}


def open_tag(builder: dict, tag: str, attrs: dict) -> dict:
    """Open an HTML tag."""
    attr_str = ""
    for k, v in attrs.items():
        attr_str += f' {k}="{v}"'
    indent = "  " * builder.get("indent", 0)
    text = f"{indent}<{tag}{attr_str}>\n"
    return {
        "parts": builder["parts"] + [text],
        "length": builder["length"] + len(text),
        "indent": builder.get("indent", 0) + 1
    }


def close_tag(builder: dict, tag: str) -> dict:
    """Close an HTML tag."""
    indent = "  " * max(0, builder.get("indent", 1) - 1)
    text = f"{indent}</{tag}>\n"
    return {
        "parts": builder["parts"] + [text],
        "length": builder["length"] + len(text),
        "indent": max(0, builder.get("indent", 1) - 1)
    }


def self_closing_tag(builder: dict, tag: str, attrs: dict) -> dict:
    """Add self-closing HTML tag."""
    attr_str = ""
    for k, v in attrs.items():
        attr_str += f' {k}="{v}"'
    indent = "  " * builder.get("indent", 0)
    text = f"{indent}<{tag}{attr_str} />\n"
    return {
        "parts": builder["parts"] + [text],
        "length": builder["length"] + len(text),
        "indent": builder.get("indent", 0)
    }


def add_text(builder: dict, text: str) -> dict:
    """Add text content."""
    indent = "  " * builder.get("indent", 0)
    full_text = f"{indent}{text}\n"
    return {
        "parts": builder["parts"] + [full_text],
        "length": builder["length"] + len(full_text),
        "indent": builder.get("indent", 0)
    }


def create_sql_builder() -> dict:
    """Create a SQL query builder."""
    return {"clauses": [], "params": []}


def sql_select(builder: dict, columns: list) -> dict:
    """Add SELECT clause."""
    clause = "SELECT " + ", ".join(columns)
    return {**builder, "clauses": builder["clauses"] + [clause]}


def sql_from(builder: dict, table: str) -> dict:
    """Add FROM clause."""
    clause = f"FROM {table}"
    return {**builder, "clauses": builder["clauses"] + [clause]}


def sql_where(builder: dict, condition: str, param) -> dict:
    """Add WHERE clause."""
    clause = f"WHERE {condition}"
    return {**builder, "clauses": builder["clauses"] + [clause], "params": builder["params"] + [param]}


def sql_and(builder: dict, condition: str, param) -> dict:
    """Add AND condition."""
    clause = f"AND {condition}"
    return {**builder, "clauses": builder["clauses"] + [clause], "params": builder["params"] + [param]}


def sql_or(builder: dict, condition: str, param) -> dict:
    """Add OR condition."""
    clause = f"OR {condition}"
    return {**builder, "clauses": builder["clauses"] + [clause], "params": builder["params"] + [param]}


def sql_order_by(builder: dict, column: str, direction: str) -> dict:
    """Add ORDER BY clause."""
    clause = f"ORDER BY {column} {direction.upper()}"
    return {**builder, "clauses": builder["clauses"] + [clause]}


def sql_limit(builder: dict, limit: int) -> dict:
    """Add LIMIT clause."""
    clause = f"LIMIT {limit}"
    return {**builder, "clauses": builder["clauses"] + [clause]}


def build_sql(builder: dict) -> dict:
    """Build SQL query."""
    query = " ".join(builder["clauses"])
    return {"query": query, "params": builder["params"]}


def create_json_builder() -> dict:
    """Create a JSON builder."""
    return {"stack": [{}], "current_key": None}


def json_add(builder: dict, key: str, value) -> dict:
    """Add key-value to current object."""
    stack = list(builder["stack"])
    if isinstance(stack[-1], dict):
        stack[-1] = {**stack[-1], key: value}
    return {**builder, "stack": stack}


def build_json(builder: dict) -> dict:
    """Build JSON object."""
    return builder["stack"][0] if builder["stack"] else {}
