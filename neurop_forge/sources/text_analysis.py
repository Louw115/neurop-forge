"""
Text Analysis Functions - Pure functions for analyzing text content.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def word_count(text: str) -> int:
    """Count the number of words in a text."""
    if not text:
        return 0
    return len(text.split())


def character_count(text: str) -> int:
    """Count the total number of characters in a text."""
    return len(text)


def character_count_no_spaces(text: str) -> int:
    """Count characters excluding whitespace."""
    if not text:
        return 0
    return len(text.replace(" ", "").replace("\t", "").replace("\n", ""))


def sentence_count(text: str) -> int:
    """Count the number of sentences in a text."""
    if not text:
        return 0
    count = 0
    for char in text:
        if char in '.!?':
            count += 1
    return max(count, 1) if text.strip() else 0


def paragraph_count(text: str) -> int:
    """Count the number of paragraphs in a text."""
    if not text:
        return 0
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    return len(paragraphs)


def line_count(text: str) -> int:
    """Count the number of lines in a text."""
    if not text:
        return 0
    return len(text.splitlines())


def average_word_length(text: str) -> float:
    """Calculate the average length of words in a text."""
    if not text:
        return 0.0
    words = text.split()
    if not words:
        return 0.0
    total_length = sum(len(word) for word in words)
    return total_length / len(words)


def average_sentence_length(text: str) -> float:
    """Calculate the average number of words per sentence."""
    words = word_count(text)
    sentences = sentence_count(text)
    if sentences == 0:
        return 0.0
    return words / sentences


def reading_time_minutes(text: str, words_per_minute: int) -> float:
    """Estimate reading time in minutes."""
    if not text or words_per_minute <= 0:
        return 0.0
    words = word_count(text)
    return words / words_per_minute


def speaking_time_minutes(text: str, words_per_minute: int) -> float:
    """Estimate speaking time in minutes."""
    if not text or words_per_minute <= 0:
        return 0.0
    words = word_count(text)
    return words / words_per_minute


def unique_word_count(text: str) -> int:
    """Count the number of unique words in a text."""
    if not text:
        return 0
    words = text.lower().split()
    return len(set(words))


def word_frequency(text: str) -> dict:
    """Calculate the frequency of each word in a text."""
    if not text:
        return {}
    words = text.lower().split()
    freq = {}
    for word in words:
        cleaned = ''.join(c for c in word if c.isalnum())
        if cleaned:
            freq[cleaned] = freq.get(cleaned, 0) + 1
    return freq


def most_common_word(text: str) -> str:
    """Find the most common word in a text."""
    freq = word_frequency(text)
    if not freq:
        return ""
    return max(freq.keys(), key=lambda k: freq[k])


def lexical_diversity(text: str) -> float:
    """Calculate lexical diversity (unique words / total words)."""
    if not text:
        return 0.0
    words = text.lower().split()
    if not words:
        return 0.0
    unique = len(set(words))
    return unique / len(words)


def count_uppercase_words(text: str) -> int:
    """Count words that are entirely uppercase."""
    if not text:
        return 0
    words = text.split()
    return sum(1 for word in words if word.isupper() and word.isalpha())


def count_capitalized_words(text: str) -> int:
    """Count words that start with an uppercase letter."""
    if not text:
        return 0
    words = text.split()
    return sum(1 for word in words if word and word[0].isupper())


def count_numbers_in_text(text: str) -> int:
    """Count numeric tokens in text."""
    if not text:
        return 0
    words = text.split()
    return sum(1 for word in words if word.replace('.', '').replace(',', '').isdigit())


def extract_sentences(text: str) -> list:
    """Extract sentences from text."""
    if not text:
        return []
    sentences = []
    current = ""
    for char in text:
        current += char
        if char in '.!?':
            if current.strip():
                sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return sentences


def get_first_n_words(text: str, n: int) -> str:
    """Get the first n words from text."""
    if not text or n <= 0:
        return ""
    words = text.split()
    return ' '.join(words[:n])


def get_last_n_words(text: str, n: int) -> str:
    """Get the last n words from text."""
    if not text or n <= 0:
        return ""
    words = text.split()
    return ' '.join(words[-n:])


def truncate_to_words(text: str, max_words: int, suffix: str) -> str:
    """Truncate text to a maximum number of words with suffix."""
    if not text or max_words <= 0:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + suffix


def contains_word(text: str, word: str) -> bool:
    """Check if text contains a specific word (case-insensitive)."""
    if not text or not word:
        return False
    words = text.lower().split()
    return word.lower() in words


def count_word_occurrences(text: str, word: str) -> int:
    """Count occurrences of a specific word (case-insensitive)."""
    if not text or not word:
        return 0
    words = text.lower().split()
    return words.count(word.lower())


def is_palindrome_text(text: str) -> bool:
    """Check if text is a palindrome (ignoring spaces and case)."""
    if not text:
        return False
    cleaned = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]


def count_vowels(text: str) -> int:
    """Count the number of vowels in text."""
    if not text:
        return 0
    vowels = 'aeiouAEIOU'
    return sum(1 for c in text if c in vowels)


def count_consonants(text: str) -> int:
    """Count the number of consonants in text."""
    if not text:
        return 0
    consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
    return sum(1 for c in text if c in consonants)


def vowel_ratio(text: str) -> float:
    """Calculate the ratio of vowels to total letters."""
    if not text:
        return 0.0
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    vowels = count_vowels(text)
    return vowels / len(letters)


def has_repeated_words(text: str) -> bool:
    """Check if text has any repeated consecutive words."""
    if not text:
        return False
    words = text.lower().split()
    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            return True
    return False


def find_longest_word(text: str) -> str:
    """Find the longest word in text."""
    if not text:
        return ""
    words = text.split()
    if not words:
        return ""
    return max(words, key=len)


def find_shortest_word(text: str) -> str:
    """Find the shortest word in text."""
    if not text:
        return ""
    words = [w for w in text.split() if w]
    if not words:
        return ""
    return min(words, key=len)
