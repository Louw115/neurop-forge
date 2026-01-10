"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
String Algorithms - Pure functions for string algorithms.
All functions are pure, deterministic, and atomic.
"""

def longest_common_prefix(strings: list) -> str:
    """Find longest common prefix of strings."""
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def longest_common_suffix(strings: list) -> str:
    """Find longest common suffix of strings."""
    if not strings:
        return ""
    suffix = strings[0]
    for s in strings[1:]:
        while not s.endswith(suffix):
            suffix = suffix[1:]
            if not suffix:
                return ""
    return suffix


def longest_common_substring(s1: str, s2: str) -> str:
    """Find longest common substring."""
    if not s1 or not s2:
        return ""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0
    end_pos = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end_pos = i
    return s1[end_pos-max_len:end_pos]


def longest_palindrome_substring(s: str) -> str:
    """Find longest palindromic substring."""
    if len(s) < 2:
        return s
    def expand_around_center(left: int, right: int) -> str:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left+1:right]
    longest = ""
    for i in range(len(s)):
        odd = expand_around_center(i, i)
        even = expand_around_center(i, i + 1)
        if len(odd) > len(longest):
            longest = odd
        if len(even) > len(longest):
            longest = even
    return longest


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein edit distance."""
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    if not s2:
        return len(s1)
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def hamming_distance(s1: str, s2: str) -> int:
    """Calculate Hamming distance."""
    if len(s1) != len(s2):
        return -1
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def jaro_similarity(s1: str, s2: str) -> float:
    """Calculate Jaro similarity."""
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    match_dist = max(len1, len2) // 2 - 1
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    transpositions = 0
    for i in range(len1):
        start = max(0, i - match_dist)
        end = min(i + match_dist + 1, len2)
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
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    return (matches/len1 + matches/len2 + (matches-transpositions/2)/matches) / 3


def jaro_winkler_similarity(s1: str, s2: str, p: float) -> float:
    """Calculate Jaro-Winkler similarity."""
    jaro_sim = jaro_similarity(s1, s2)
    prefix = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break
    return jaro_sim + prefix * p * (1 - jaro_sim)


def is_anagram(s1: str, s2: str) -> bool:
    """Check if two strings are anagrams."""
    s1_clean = s1.lower().replace(" ", "")
    s2_clean = s2.lower().replace(" ", "")
    return sorted(s1_clean) == sorted(s2_clean)


def is_palindrome(s: str) -> bool:
    """Check if string is a palindrome."""
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]


def is_rotation(s1: str, s2: str) -> bool:
    """Check if s2 is a rotation of s1."""
    if len(s1) != len(s2):
        return False
    return s2 in (s1 + s1)


def count_vowels(s: str) -> int:
    """Count vowels in string."""
    return sum(1 for c in s.lower() if c in 'aeiou')


def count_consonants(s: str) -> int:
    """Count consonants in string."""
    return sum(1 for c in s.lower() if c.isalpha() and c not in 'aeiou')


def kmp_search(text: str, pattern: str) -> list:
    """KMP pattern search algorithm."""
    if not pattern:
        return []
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    matches = []
    i = j = 0
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches


def rabin_karp_search(text: str, pattern: str) -> list:
    """Rabin-Karp pattern search algorithm."""
    if not pattern or len(pattern) > len(text):
        return []
    d = 256
    q = 101
    m, n = len(pattern), len(text)
    h = pow(d, m - 1) % q
    p = t = 0
    matches = []
    for i in range(m):
        p = (d * p + ord(pattern[i])) % q
        t = (d * t + ord(text[i])) % q
    for i in range(n - m + 1):
        if p == t:
            if text[i:i+m] == pattern:
                matches.append(i)
        if i < n - m:
            t = (d * (t - ord(text[i]) * h) + ord(text[i + m])) % q
            if t < 0:
                t += q
    return matches


def z_function(s: str) -> list:
    """Calculate Z-function."""
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z
