"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Search Patterns - Pure functions for search and filtering logic.
All functions are pure, deterministic, and atomic.
"""

def tokenize_query(query: str) -> list:
    """Tokenize a search query."""
    return [token.strip().lower() for token in query.split() if token.strip()]


def normalize_search_term(term: str) -> str:
    """Normalize a search term."""
    import re
    normalized = term.lower().strip()
    normalized = re.sub(r'[^\w\s]', '', normalized)
    return normalized


def build_search_query(terms: list, operator: str) -> dict:
    """Build a search query object."""
    return {
        "terms": terms,
        "operator": operator.upper(),
        "filters": [],
        "sort": None,
        "limit": 10,
        "offset": 0
    }


def add_filter_to_query(query: dict, field: str, operator: str, value) -> dict:
    """Add a filter to search query."""
    result = dict(query)
    result["filters"] = list(query.get("filters", []))
    result["filters"].append({
        "field": field,
        "operator": operator,
        "value": value
    })
    return result


def add_sort_to_query(query: dict, field: str, direction: str) -> dict:
    """Add sorting to search query."""
    result = dict(query)
    result["sort"] = {"field": field, "direction": direction}
    return result


def matches_term(text: str, term: str, exact: bool) -> bool:
    """Check if text matches search term."""
    text_lower = text.lower()
    term_lower = term.lower()
    if exact:
        return term_lower == text_lower
    return term_lower in text_lower


def matches_all_terms(text: str, terms: list) -> bool:
    """Check if text matches all search terms (AND)."""
    text_lower = text.lower()
    return all(term.lower() in text_lower for term in terms)


def matches_any_term(text: str, terms: list) -> bool:
    """Check if text matches any search term (OR)."""
    text_lower = text.lower()
    return any(term.lower() in text_lower for term in terms)


def calculate_term_frequency(text: str, term: str) -> int:
    """Calculate how many times a term appears in text."""
    return text.lower().count(term.lower())


def calculate_search_score(text: str, terms: list, weights: dict) -> float:
    """Calculate relevance score for search result."""
    score = 0.0
    text_lower = text.lower()
    for term in terms:
        term_lower = term.lower()
        if term_lower in text_lower:
            tf = calculate_term_frequency(text, term)
            weight = weights.get(term, 1.0)
            score += tf * weight
    return score


def rank_results(results: list, score_key: str, descending: bool) -> list:
    """Rank search results by score."""
    return sorted(results, key=lambda x: x.get(score_key, 0), reverse=descending)


def paginate_results(results: list, page: int, per_page: int) -> dict:
    """Paginate search results."""
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    items = results[start:end]
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
    }


def highlight_matches(text: str, terms: list, before: str, after: str) -> str:
    """Highlight matching terms in text."""
    import re
    result = text
    for term in terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        result = pattern.sub(f"{before}\\g<0>{after}", result)
    return result


def extract_snippets(text: str, terms: list, snippet_length: int) -> list:
    """Extract text snippets containing search terms."""
    snippets = []
    text_lower = text.lower()
    for term in terms:
        term_lower = term.lower()
        idx = text_lower.find(term_lower)
        while idx != -1:
            start = max(0, idx - snippet_length // 2)
            end = min(len(text), idx + len(term) + snippet_length // 2)
            snippet = text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
            if snippet not in snippets:
                snippets.append(snippet)
            idx = text_lower.find(term_lower, idx + 1)
    return snippets


def build_facet(field: str, values: list) -> dict:
    """Build a search facet."""
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return {
        "field": field,
        "values": [{"value": v, "count": c} for v, c in sorted(counts.items(), key=lambda x: -x[1])]
    }


def filter_by_facet(results: list, field: str, value) -> list:
    """Filter results by facet value."""
    return [r for r in results if r.get(field) == value]


def build_suggestion(query: str, suggestion: str, score: float) -> dict:
    """Build a search suggestion."""
    return {
        "query": query,
        "suggestion": suggestion,
        "score": score
    }


def calculate_levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return calculate_levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def find_similar_terms(query: str, dictionary: list, max_distance: int) -> list:
    """Find similar terms in dictionary."""
    similar = []
    for word in dictionary:
        distance = calculate_levenshtein_distance(query.lower(), word.lower())
        if distance <= max_distance:
            similar.append({"term": word, "distance": distance})
    return sorted(similar, key=lambda x: x["distance"])


def build_autocomplete_result(prefix: str, suggestions: list, limit: int) -> list:
    """Build autocomplete suggestions."""
    prefix_lower = prefix.lower()
    matching = [s for s in suggestions if s.lower().startswith(prefix_lower)]
    return matching[:limit]


def extract_search_filters(query: str) -> dict:
    """Extract filters from search query (e.g., 'category:books')."""
    import re
    filters = {}
    terms = []
    for part in query.split():
        match = re.match(r'(\w+):(.+)', part)
        if match:
            filters[match.group(1)] = match.group(2)
        else:
            terms.append(part)
    return {
        "terms": terms,
        "filters": filters,
        "cleaned_query": " ".join(terms)
    }


def build_boolean_query(must: list, should: list, must_not: list) -> dict:
    """Build a boolean search query."""
    return {
        "must": must,
        "should": should,
        "must_not": must_not
    }


def parse_boolean_query(query: str) -> dict:
    """Parse a boolean query string (AND, OR, NOT)."""
    must = []
    should = []
    must_not = []
    parts = query.split()
    current_list = must
    for i, part in enumerate(parts):
        upper = part.upper()
        if upper == "AND":
            current_list = must
        elif upper == "OR":
            current_list = should
        elif upper == "NOT":
            current_list = must_not
        else:
            current_list.append(part)
    return build_boolean_query(must, should, must_not)


def calculate_idf(doc_count: int, total_docs: int) -> float:
    """Calculate inverse document frequency."""
    import math
    if doc_count <= 0 or total_docs <= 0:
        return 0.0
    return math.log(total_docs / doc_count)


def calculate_tfidf(term_frequency: int, doc_length: int, doc_count: int, total_docs: int) -> float:
    """Calculate TF-IDF score."""
    if doc_length <= 0:
        return 0.0
    tf = term_frequency / doc_length
    idf = calculate_idf(doc_count, total_docs)
    return tf * idf


def build_search_result(item: dict, score: float, highlights: dict) -> dict:
    """Build a search result object."""
    return {
        "item": item,
        "score": score,
        "highlights": highlights
    }


def merge_search_results(results_list: list, score_key: str) -> list:
    """Merge multiple search result lists and deduplicate."""
    seen = set()
    merged = []
    for results in results_list:
        for result in results:
            item_id = result.get("item", {}).get("id")
            if item_id and item_id not in seen:
                seen.add(item_id)
                merged.append(result)
    return rank_results(merged, score_key, True)
