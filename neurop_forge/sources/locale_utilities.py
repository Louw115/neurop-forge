"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Locale Utilities - Pure functions for locale operations.
All functions are pure, deterministic, and atomic.
"""


def parse_locale(locale: str) -> dict:
    """Parse locale string into components."""
    parts = locale.replace("-", "_").split("_")
    return {
        "language": parts[0].lower() if parts else "",
        "region": parts[1].upper() if len(parts) > 1 else "",
        "script": parts[2] if len(parts) > 2 else ""
    }


def format_locale(language: str, region: str) -> str:
    """Format locale string."""
    if region:
        return f"{language.lower()}-{region.upper()}"
    return language.lower()


def normalize_locale(locale: str) -> str:
    """Normalize locale to standard format."""
    parsed = parse_locale(locale)
    return format_locale(parsed["language"], parsed["region"])


def get_language_code(locale: str) -> str:
    """Get language code from locale."""
    return parse_locale(locale)["language"]


def get_region_code(locale: str) -> str:
    """Get region code from locale."""
    return parse_locale(locale)["region"]


def is_valid_language_code(code: str) -> bool:
    """Check if valid ISO 639-1 language code."""
    return len(code) == 2 and code.isalpha()


def is_valid_region_code(code: str) -> bool:
    """Check if valid ISO 3166-1 region code."""
    return len(code) == 2 and code.isalpha()


def is_valid_locale(locale: str) -> bool:
    """Validate locale format."""
    parsed = parse_locale(locale)
    if not is_valid_language_code(parsed["language"]):
        return False
    if parsed["region"] and not is_valid_region_code(parsed["region"]):
        return False
    return True


def get_fallback_locales(locale: str) -> list:
    """Get fallback locale chain."""
    parsed = parse_locale(locale)
    fallbacks = []
    if parsed["region"]:
        fallbacks.append(format_locale(parsed["language"], parsed["region"]))
    fallbacks.append(parsed["language"])
    if parsed["language"] != "en":
        fallbacks.append("en")
    return fallbacks


def match_locale(requested: str, available: list) -> str:
    """Match requested locale to available ones."""
    fallbacks = get_fallback_locales(requested)
    for fallback in fallbacks:
        if fallback in available:
            return fallback
        for avail in available:
            if avail.startswith(fallback):
                return avail
    return available[0] if available else ""


def get_text_direction(locale: str) -> str:
    """Get text direction for locale."""
    rtl_languages = ["ar", "he", "fa", "ur"]
    language = get_language_code(locale)
    return "rtl" if language in rtl_languages else "ltr"


def get_decimal_separator(locale: str) -> str:
    """Get decimal separator for locale."""
    period_locales = ["en", "ja", "ko", "zh"]
    language = get_language_code(locale)
    return "." if language in period_locales else ","


def get_thousands_separator(locale: str) -> str:
    """Get thousands separator for locale."""
    comma_locales = ["en", "ja", "ko", "zh"]
    language = get_language_code(locale)
    return "," if language in comma_locales else " "


def get_date_format(locale: str) -> str:
    """Get date format for locale."""
    us_locales = ["en-US"]
    if locale in us_locales:
        return "MM/DD/YYYY"
    return "DD/MM/YYYY"


def get_currency_symbol(locale: str, currency: str) -> str:
    """Get currency symbol for locale."""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥"
    }
    return symbols.get(currency, currency)


def get_currency_position(locale: str) -> str:
    """Get currency position for locale."""
    suffix_locales = ["de", "fr", "es", "it"]
    language = get_language_code(locale)
    return "suffix" if language in suffix_locales else "prefix"


def format_number_locale(value: float, locale: str) -> str:
    """Format number for locale."""
    decimal_sep = get_decimal_separator(locale)
    thousands_sep = get_thousands_separator(locale)
    int_part, dec_part = f"{value:.2f}".split(".")
    int_part = format_thousands(int_part, thousands_sep)
    return f"{int_part}{decimal_sep}{dec_part}"


def format_thousands(value: str, separator: str) -> str:
    """Format number with thousands separator."""
    return separator.join([value[max(0, i-3):i] for i in range(len(value), 0, -3)][::-1])


def get_first_day_of_week(locale: str) -> int:
    """Get first day of week (0=Sun, 1=Mon)."""
    sunday_first = ["en-US", "en-CA"]
    return 0 if locale in sunday_first else 1


def compare_locales(locale1: str, locale2: str) -> bool:
    """Compare if locales are equivalent."""
    return normalize_locale(locale1) == normalize_locale(locale2)


def get_language_name(code: str, names: dict) -> str:
    """Get language name from code."""
    return names.get(code.lower(), code)


def create_locale_config(locale: str) -> dict:
    """Create locale configuration."""
    return {
        "locale": normalize_locale(locale),
        "language": get_language_code(locale),
        "region": get_region_code(locale),
        "direction": get_text_direction(locale),
        "decimal_separator": get_decimal_separator(locale),
        "thousands_separator": get_thousands_separator(locale),
        "date_format": get_date_format(locale)
    }
