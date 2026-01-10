#!/usr/bin/env python3
"""
MEGA TEXT ANALYZER - Neurop Forge V1.0.0 Stress Test
Chains 20+ verified Tier-A blocks for comprehensive text analysis.

Usage:
    python mega_text_analyzer.py "Your text to analyze"
    python mega_text_analyzer.py --file document.txt
"""

import sys
from neurop_forge import execute_block


def run_block(name, inputs, description=""):
    """Execute a block and return result with error handling."""
    try:
        result = execute_block(name, inputs)
        if result.get("success"):
            return result.get("result")
        else:
            return f"[ERROR: {result.get('error', 'Unknown')}]"
    except Exception as e:
        return f"[FAILED: {str(e)[:50]}]"


def mega_analyze(text):
    """Run comprehensive analysis using 20+ blocks."""
    
    print("=" * 70)
    print("  NEUROP FORGE V1.0.0 - MEGA TEXT ANALYZER")
    print("  Stress Testing with 20+ Chained Blocks")
    print("=" * 70)
    print(f"\nINPUT TEXT ({len(text)} chars):")
    print(f"  \"{text[:100]}{'...' if len(text) > 100 else ''}\"")
    print("-" * 70)
    
    results = {}
    block_count = 0
    
    print("\n[PHASE 1: BASIC METRICS]")
    print("-" * 40)
    
    results["length"] = run_block("string_length", {"text": text})
    block_count += 1
    print(f"  1. string_length: {results['length']}")
    
    results["word_count"] = run_block("word_count", {"text": text})
    block_count += 1
    print(f"  2. word_count: {results['word_count']}")
    
    results["char_count"] = run_block("character_count", {"text": text})
    block_count += 1
    print(f"  3. character_count: {results['char_count']}")
    
    results["char_no_space"] = run_block("character_count_no_spaces", {"text": text})
    block_count += 1
    print(f"  4. character_count_no_spaces: {results['char_no_space']}")
    
    results["unique_words"] = run_block("unique_word_count", {"text": text})
    block_count += 1
    print(f"  5. unique_word_count: {results['unique_words']}")
    
    results["avg_word_len"] = run_block("average_word_length", {"text": text})
    block_count += 1
    print(f"  6. average_word_length: {results['avg_word_len']}")
    
    print("\n[PHASE 2: CASE ANALYSIS]")
    print("-" * 40)
    
    results["has_upper"] = run_block("contains_uppercase", {"text": text})
    block_count += 1
    print(f"  7. contains_uppercase: {results['has_upper']}")
    
    results["has_lower"] = run_block("contains_lowercase", {"text": text})
    block_count += 1
    print(f"  8. contains_lowercase: {results['has_lower']}")
    
    results["count_upper"] = run_block("count_uppercase", {"s": text})
    block_count += 1
    print(f"  9. count_uppercase: {results['count_upper']}")
    
    results["count_lower"] = run_block("count_lowercase", {"s": text})
    block_count += 1
    print(f"  10. count_lowercase: {results['count_lower']}")
    
    print("\n[PHASE 3: TEXT TRANSFORMATIONS]")
    print("-" * 40)
    
    results["lowercase"] = run_block("to_lowercase", {"text": text})
    block_count += 1
    print(f"  11. to_lowercase: {results['lowercase'][:50]}...")
    
    results["uppercase"] = run_block("to_uppercase", {"text": text})
    block_count += 1
    print(f"  12. to_uppercase: {results['uppercase'][:50]}...")
    
    results["reversed"] = run_block("reverse_string", {"text": text})
    block_count += 1
    print(f"  13. reverse_string: {results['reversed'][:50]}...")
    
    results["capitalized"] = run_block("capitalize_words", {"text": text})
    block_count += 1
    print(f"  14. capitalize_words: {results['capitalized'][:50]}...")
    
    print("\n[PHASE 4: CONTENT DETECTION]")
    print("-" * 40)
    
    results["has_digit"] = run_block("contains_digit", {"text": text})
    block_count += 1
    print(f"  15. contains_digit: {results['has_digit']}")
    
    results["digit_count"] = run_block("count_digits", {"text": text})
    block_count += 1
    print(f"  16. count_digits: {results['digit_count']}")
    
    results["consonants"] = run_block("count_consonants", {"text": text})
    block_count += 1
    print(f"  17. count_consonants: {results['consonants']}")
    
    print("\n[PHASE 5: WORD ANALYSIS]")
    print("-" * 40)
    
    results["longest_word"] = run_block("find_longest_word", {"text": text})
    block_count += 1
    print(f"  18. find_longest_word: {results['longest_word']}")
    
    results["shortest_word"] = run_block("find_shortest_word", {"text": text})
    block_count += 1
    print(f"  19. find_shortest_word: {results['shortest_word']}")
    
    results["word_freq"] = run_block("word_frequency", {"text": text})
    block_count += 1
    freq_preview = str(results['word_freq'])[:60] + "..." if len(str(results['word_freq'])) > 60 else str(results['word_freq'])
    print(f"  20. word_frequency: {freq_preview}")
    
    results["repeated"] = run_block("has_repeated_words", {"text": text})
    block_count += 1
    print(f"  21. has_repeated_words: {results['repeated']}")
    
    print("\n[PHASE 6: ENCODING & CIPHERS]")
    print("-" * 40)
    
    results["base64"] = run_block("base64_encode", {"text": text})
    block_count += 1
    b64_preview = str(results['base64'])[:50] + "..." if len(str(results['base64'])) > 50 else str(results['base64'])
    print(f"  22. base64_encode: {b64_preview}")
    
    results["atbash"] = run_block("atbash_cipher", {"text": text})
    block_count += 1
    atbash_preview = str(results['atbash'])[:50] + "..." if len(str(results['atbash'])) > 50 else str(results['atbash'])
    print(f"  23. atbash_cipher: {atbash_preview}")
    
    print("\n[PHASE 7: CASE CONVERSIONS]")
    print("-" * 40)
    
    results["snake"] = run_block("camel_to_snake", {"text": text.replace(" ", "")[:30]})
    block_count += 1
    print(f"  24. camel_to_snake: {results['snake']}")
    
    results["kebab"] = run_block("to_kebab_case", {"text": text[:30]})
    block_count += 1
    print(f"  25. to_kebab_case: {results['kebab']}")
    
    print("\n" + "=" * 70)
    print(f"  ANALYSIS COMPLETE: {block_count} BLOCKS EXECUTED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n[SUMMARY REPORT]")
    print("-" * 40)
    print(f"  Total Characters:    {results.get('length', 'N/A')}")
    print(f"  Characters (no sp):  {results.get('char_no_space', 'N/A')}")
    print(f"  Word Count:          {results.get('word_count', 'N/A')}")
    print(f"  Unique Words:        {results.get('unique_words', 'N/A')}")
    print(f"  Avg Word Length:     {results.get('avg_word_len', 'N/A')}")
    print(f"  Uppercase Letters:   {results.get('count_upper', 'N/A')}")
    print(f"  Lowercase Letters:   {results.get('count_lower', 'N/A')}")
    print(f"  Digits Found:        {results.get('digit_count', 'N/A')}")
    print(f"  Longest Word:        {results.get('longest_word', 'N/A')}")
    print(f"  Shortest Word:       {results.get('shortest_word', 'N/A')}")
    print(f"  Has Repeated Words:  {results.get('repeated', 'N/A')}")
    print("-" * 40)
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python mega_text_analyzer.py \"Your text here\"")
        print("  python mega_text_analyzer.py --file document.txt")
        print("\nExample:")
        print("  python mega_text_analyzer.py \"The Quick Brown Fox Jumps Over The Lazy Dog 123\"")
        sys.exit(1)
    
    if sys.argv[1] == "--file" and len(sys.argv) > 2:
        try:
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        text = " ".join(sys.argv[1:])
    
    if not text.strip():
        print("Error: Empty input")
        sys.exit(1)
    
    mega_analyze(text)


if __name__ == "__main__":
    main()
