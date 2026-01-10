"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Search Helpers - Pure functions for search operations.
All functions are pure, deterministic, and atomic.
"""

import re


def normalize_query(query: str) -> str:
    """Normalize search query."""
    query = query.lower().strip()
    query = re.sub(r'\s+', ' ', query)
    return query


def tokenize_query(query: str) -> list:
    """Tokenize search query into terms."""
    return [t.strip() for t in query.split() if t.strip()]


def extract_quoted_phrases(query: str) -> list:
    """Extract quoted phrases from query."""
    return re.findall(r'"([^"]+)"', query)


def remove_quoted_phrases(query: str) -> str:
    """Remove quoted phrases from query."""
    return re.sub(r'"[^"]+"', '', query).strip()


def parse_search_operators(query: str) -> dict:
    """Parse search operators (AND, OR, NOT)."""
    result = {"required": [], "optional": [], "excluded": []}
    for term in tokenize_query(query):
        if term.startswith("+"):
            result["required"].append(term[1:])
        elif term.startswith("-"):
            result["excluded"].append(term[1:])
        else:
            result["optional"].append(term)
    return result


def build_search_pattern(terms: list, match_all: bool) -> str:
    """Build regex pattern from terms."""
    escaped = [re.escape(t) for t in terms]
    if match_all:
        return "".join(f"(?=.*{t})" for t in escaped)
    return "|".join(escaped)


def highlight_matches(text: str, terms: list, open_tag: str, close_tag: str) -> str:
    """Highlight matching terms in text."""
    result = text
    for term in terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        result = pattern.sub(f"{open_tag}\\g<0>{close_tag}", result)
    return result


def calculate_relevance(text: str, terms: list) -> float:
    """Calculate relevance score."""
    text_lower = text.lower()
    matches = sum(1 for t in terms if t.lower() in text_lower)
    return matches / len(terms) if terms else 0


def rank_results(results: list, terms: list) -> list:
    """Rank results by relevance."""
    scored = []
    for result in results:
        text = result.get("text", "") or result.get("title", "")
        score = calculate_relevance(text, terms)
        scored.append({"result": result, "score": score})
    return sorted(scored, key=lambda x: -x["score"])


def fuzzy_match_score(query: str, target: str) -> float:
    """Calculate fuzzy match score."""
    query = query.lower()
    target = target.lower()
    if query == target:
        return 1.0
    if query in target:
        return 0.8
    matches = sum(1 for c in query if c in target)
    return matches / len(query) if query else 0


def filter_by_field(items: list, field: str, value: str) -> list:
    """Filter items by field value."""
    return [i for i in items if i.get(field) == value]


def filter_by_range(items: list, field: str, min_val, max_val) -> list:
    """Filter items by field range."""
    return [i for i in items if min_val <= i.get(field, 0) <= max_val]


def paginate_results(results: list, page: int, per_page: int) -> dict:
    """Paginate search results."""
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "results": results[start:end],
        "total": len(results),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(results) + per_page - 1) // per_page
    }


def create_search_facet(items: list, field: str) -> dict:
    """Create search facet counts."""
    facet = {}
    for item in items:
        value = item.get(field, "unknown")
        facet[value] = facet.get(value, 0) + 1
    return facet


def apply_facet_filter(items: list, facets: dict) -> list:
    """Apply facet filters to items."""
    result = items
    for field, values in facets.items():
        result = [i for i in result if i.get(field) in values]
    return result


def get_search_suggestions(query: str, index: list, limit: int) -> list:
    """Get search suggestions from index."""
    query_lower = query.lower()
    matches = [t for t in index if t.lower().startswith(query_lower)]
    return sorted(matches, key=len)[:limit]


def create_search_context(query: str, text: str, context_size: int) -> str:
    """Create search result context snippet."""
    query_lower = query.lower()
    text_lower = text.lower()
    pos = text_lower.find(query_lower)
    if pos == -1:
        return text[:context_size * 2]
    start = max(0, pos - context_size)
    end = min(len(text), pos + len(query) + context_size)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def escape_search_term(term: str) -> str:
    """Escape special characters in search term."""
    special = r'[\^$.|?*+()[]{}'
    return "".join(f"\\{c}" if c in special else c for c in term)


def validate_search_query(query: str, min_length: int, max_length: int) -> dict:
    """Validate search query."""
    if len(query) < min_length:
        return {"valid": False, "error": "Query too short"}
    if len(query) > max_length:
        return {"valid": False, "error": "Query too long"}
    return {"valid": True, "error": None}
