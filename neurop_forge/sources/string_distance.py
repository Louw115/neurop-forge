"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
String Distance - Pure functions for string similarity and distance metrics.
All functions are pure, deterministic, and atomic.
"""

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein edit distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        prev_row = current_row
    return prev_row[-1]


def hamming_distance(s1: str, s2: str) -> int:
    """Calculate Hamming distance (strings must be same length)."""
    if len(s1) != len(s2):
        return -1
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def jaro_similarity(s1: str, s2: str) -> float:
    """Calculate Jaro similarity."""
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    match_distance = max(len(s1), len(s2)) // 2 - 1
    if match_distance < 0:
        match_distance = 0
    s1_matches = [False] * len(s1)
    s2_matches = [False] * len(s2)
    matches = 0
    transpositions = 0
    for i in range(len(s1)):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len(s2))
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    k = 0
    for i in range(len(s1)):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    return (matches / len(s1) + matches / len(s2) + (matches - transpositions / 2) / matches) / 3


def jaro_winkler_similarity(s1: str, s2: str, prefix_scale: float) -> float:
    """Calculate Jaro-Winkler similarity."""
    jaro = jaro_similarity(s1, s2)
    prefix_len = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break
    return jaro + prefix_len * prefix_scale * (1 - jaro)


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Damerau-Levenshtein distance (allows transposition)."""
    len1, len2 = len(s1), len(s2)
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)
    return d[len1][len2]


def longest_common_subsequence(s1: str, s2: str) -> str:
    """Find longest common subsequence."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            lcs.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(lcs))


def lcs_length(s1: str, s2: str) -> int:
    """Calculate length of longest common subsequence."""
    return len(longest_common_subsequence(s1, s2))


def longest_common_substring(s1: str, s2: str) -> str:
    """Find longest common substring."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0
    end_pos = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end_pos = i
    return s1[end_pos - max_len:end_pos]


def normalized_levenshtein(s1: str, s2: str) -> float:
    """Calculate normalized Levenshtein similarity (0-1)."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1 - levenshtein_distance(s1, s2) / max_len


def sorensen_dice_coefficient(s1: str, s2: str, n: int) -> float:
    """Calculate Sorensen-Dice coefficient using n-grams."""
    if not s1 or not s2:
        return 0.0
    ngrams1 = set(s1[i:i + n] for i in range(len(s1) - n + 1))
    ngrams2 = set(s2[i:i + n] for i in range(len(s2) - n + 1))
    intersection = len(ngrams1 & ngrams2)
    return 2 * intersection / (len(ngrams1) + len(ngrams2))


def jaccard_similarity_strings(s1: str, s2: str, n: int) -> float:
    """Calculate Jaccard similarity using n-grams."""
    if not s1 or not s2:
        return 0.0
    ngrams1 = set(s1[i:i + n] for i in range(len(s1) - n + 1))
    ngrams2 = set(s2[i:i + n] for i in range(len(s2) - n + 1))
    intersection = len(ngrams1 & ngrams2)
    union = len(ngrams1 | ngrams2)
    return intersection / union if union > 0 else 0.0


def overlap_coefficient_strings(s1: str, s2: str, n: int) -> float:
    """Calculate overlap coefficient using n-grams."""
    if not s1 or not s2:
        return 0.0
    ngrams1 = set(s1[i:i + n] for i in range(len(s1) - n + 1))
    ngrams2 = set(s2[i:i + n] for i in range(len(s2) - n + 1))
    intersection = len(ngrams1 & ngrams2)
    min_size = min(len(ngrams1), len(ngrams2))
    return intersection / min_size if min_size > 0 else 0.0


def cosine_similarity_strings(s1: str, s2: str, n: int) -> float:
    """Calculate cosine similarity using n-gram vectors."""
    if not s1 or not s2:
        return 0.0
    ngrams1 = {}
    for i in range(len(s1) - n + 1):
        ng = s1[i:i + n]
        ngrams1[ng] = ngrams1.get(ng, 0) + 1
    ngrams2 = {}
    for i in range(len(s2) - n + 1):
        ng = s2[i:i + n]
        ngrams2[ng] = ngrams2.get(ng, 0) + 1
    all_ngrams = set(ngrams1.keys()) | set(ngrams2.keys())
    dot_product = sum(ngrams1.get(ng, 0) * ngrams2.get(ng, 0) for ng in all_ngrams)
    mag1 = sum(v ** 2 for v in ngrams1.values()) ** 0.5
    mag2 = sum(v ** 2 for v in ngrams2.values()) ** 0.5
    return dot_product / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0.0


def find_best_match(query: str, candidates: list) -> dict:
    """Find best matching candidate using normalized Levenshtein."""
    if not candidates:
        return {"match": None, "score": 0.0}
    best_match = None
    best_score = 0.0
    for candidate in candidates:
        score = normalized_levenshtein(query.lower(), candidate.lower())
        if score > best_score:
            best_score = score
            best_match = candidate
    return {"match": best_match, "score": best_score}


def fuzzy_match_threshold(s1: str, s2: str, threshold: float) -> bool:
    """Check if strings fuzzy match above threshold."""
    return normalized_levenshtein(s1.lower(), s2.lower()) >= threshold


def get_edit_operations(s1: str, s2: str) -> list:
    """Get sequence of edit operations to transform s1 to s2."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    ops = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j - 1] <= dp[i - 1][j] and dp[i][j - 1] <= dp[i - 1][j - 1]):
            ops.append({"op": "insert", "char": s2[j - 1], "pos": i})
            j -= 1
        elif i > 0 and (j == 0 or dp[i - 1][j] <= dp[i][j - 1] and dp[i - 1][j] <= dp[i - 1][j - 1]):
            ops.append({"op": "delete", "char": s1[i - 1], "pos": i - 1})
            i -= 1
        else:
            ops.append({"op": "replace", "from": s1[i - 1], "to": s2[j - 1], "pos": i - 1})
            i -= 1
            j -= 1
    return list(reversed(ops))
