"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Document Utilities - Pure functions for document handling.
All functions are pure, deterministic, and atomic.
"""

import re


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def character_count(text: str, include_spaces: bool) -> int:
    """Count characters in text."""
    if include_spaces:
        return len(text)
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))


def sentence_count(text: str) -> int:
    """Count sentences in text."""
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])


def paragraph_count(text: str) -> int:
    """Count paragraphs in text."""
    paragraphs = re.split(r'\n\s*\n', text)
    return len([p for p in paragraphs if p.strip()])


def line_count(text: str) -> int:
    """Count lines in text."""
    return len(text.split("\n"))


def average_word_length(text: str) -> float:
    """Calculate average word length."""
    words = text.split()
    if not words:
        return 0
    return sum(len(w) for w in words) / len(words)


def reading_time_minutes(text: str, wpm: int) -> float:
    """Estimate reading time in minutes."""
    words = word_count(text)
    return words / wpm


def speaking_time_minutes(text: str, wpm: int) -> float:
    """Estimate speaking time in minutes."""
    words = word_count(text)
    return words / wpm


def flesch_reading_ease(text: str) -> float:
    """Calculate Flesch reading ease score."""
    words = word_count(text)
    sentences = sentence_count(text)
    syllables = sum(count_syllables(word) for word in text.split())
    if sentences == 0 or words == 0:
        return 0
    return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)


def count_syllables(word: str) -> int:
    """Count syllables in a word."""
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e"):
        count -= 1
    return max(1, count)


def extract_emails(text: str) -> list:
    """Extract email addresses from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def extract_phone_numbers(text: str) -> list:
    """Extract phone numbers from text."""
    pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{4,10}'
    return re.findall(pattern, text)


def extract_dates(text: str) -> list:
    """Extract date patterns from text."""
    patterns = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{1,2}/\d{1,2}/\d{2,4}',
        r'\d{1,2}-\d{1,2}-\d{2,4}'
    ]
    dates = []
    for pattern in patterns:
        dates.extend(re.findall(pattern, text))
    return dates


def extract_numbers(text: str) -> list:
    """Extract numbers from text."""
    return [float(n) if '.' in n else int(n) 
            for n in re.findall(r'-?\d+\.?\d*', text)]


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace to single spaces."""
    return " ".join(text.split())


def remove_extra_newlines(text: str) -> str:
    """Remove extra blank lines."""
    return re.sub(r'\n{3,}', '\n\n', text)


def extract_headings(text: str) -> list:
    """Extract markdown headings."""
    return re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)


def extract_links(text: str) -> list:
    """Extract markdown links."""
    return re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)


def extract_code_blocks(text: str) -> list:
    """Extract fenced code blocks."""
    return re.findall(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)


def count_unique_words(text: str) -> int:
    """Count unique words."""
    words = re.findall(r'\b\w+\b', text.lower())
    return len(set(words))


def get_word_frequency(text: str) -> dict:
    """Get word frequency distribution."""
    words = re.findall(r'\b\w+\b', text.lower())
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq


def top_words(text: str, n: int) -> list:
    """Get top n most frequent words."""
    freq = get_word_frequency(text)
    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    return sorted_words[:n]


def summarize_stats(text: str) -> dict:
    """Get document statistics."""
    return {
        "words": word_count(text),
        "characters": character_count(text, True),
        "characters_no_spaces": character_count(text, False),
        "sentences": sentence_count(text),
        "paragraphs": paragraph_count(text),
        "lines": line_count(text),
        "unique_words": count_unique_words(text),
        "avg_word_length": round(average_word_length(text), 2)
    }


def detect_language_hint(text: str) -> str:
    """Detect language based on common words."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["the", "is", "are", "and"]):
        return "en"
    if any(w in text_lower for w in ["le", "la", "les", "est"]):
        return "fr"
    if any(w in text_lower for w in ["der", "die", "das", "und"]):
        return "de"
    if any(w in text_lower for w in ["el", "la", "los", "las"]):
        return "es"
    return "unknown"


def truncate_at_sentence(text: str, max_length: int) -> str:
    """Truncate at sentence boundary."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_period = truncated.rfind(".")
    if last_period > max_length // 2:
        return truncated[:last_period + 1]
    return truncated + "..."
