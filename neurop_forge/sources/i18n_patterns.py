"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Internationalization Patterns - Pure functions for i18n/l10n.
All functions are pure, deterministic, and atomic.
"""

def get_locale_language(locale: str) -> str:
    """Extract language code from locale."""
    return locale.split("-")[0].split("_")[0].lower()


def get_locale_region(locale: str) -> str:
    """Extract region code from locale."""
    parts = locale.replace("_", "-").split("-")
    return parts[1].upper() if len(parts) > 1 else ""


def normalize_locale(locale: str) -> str:
    """Normalize locale to standard format (e.g., en-US)."""
    parts = locale.replace("_", "-").split("-")
    lang = parts[0].lower()
    if len(parts) > 1:
        region = parts[1].upper()
        return f"{lang}-{region}"
    return lang


def is_rtl_language(language_code: str) -> bool:
    """Check if language is right-to-left."""
    rtl_languages = {"ar", "he", "fa", "ur", "yi", "ps", "sd"}
    return language_code.lower() in rtl_languages


def get_text_direction(language_code: str) -> str:
    """Get text direction for language."""
    return "rtl" if is_rtl_language(language_code) else "ltr"


def format_number_locale(number: float, locale: str, decimals: int) -> str:
    """Format number according to locale conventions."""
    decimal_sep = "," if locale.startswith(("de", "fr", "es", "it", "pt", "nl")) else "."
    thousands_sep = "." if decimal_sep == "," else ","
    formatted = f"{number:,.{decimals}f}"
    if decimal_sep == ",":
        formatted = formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    return formatted


def format_currency_locale(amount: float, currency: str, locale: str) -> str:
    """Format currency according to locale conventions."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CNY": "¥"}
    symbol = symbols.get(currency, currency)
    formatted = format_number_locale(amount, locale, 2)
    symbol_before = locale.startswith(("en", "zh", "ja"))
    if symbol_before:
        return f"{symbol}{formatted}"
    return f"{formatted} {symbol}"


def format_date_locale(year: int, month: int, day: int, locale: str) -> str:
    """Format date according to locale conventions."""
    if locale.startswith("en-US"):
        return f"{month:02d}/{day:02d}/{year}"
    elif locale.startswith("en"):
        return f"{day:02d}/{month:02d}/{year}"
    elif locale.startswith(("de", "ru", "nl")):
        return f"{day:02d}.{month:02d}.{year}"
    elif locale.startswith(("ja", "zh", "ko")):
        return f"{year}/{month:02d}/{day:02d}"
    return f"{year}-{month:02d}-{day:02d}"


def format_time_locale(hour: int, minute: int, locale: str, use_24h: bool) -> str:
    """Format time according to locale conventions."""
    if use_24h or not locale.startswith("en"):
        return f"{hour:02d}:{minute:02d}"
    period = "AM" if hour < 12 else "PM"
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12
    return f"{hour_12}:{minute:02d} {period}"


def get_weekday_name(weekday: int, locale: str, short: bool) -> str:
    """Get weekday name in locale."""
    days_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_short_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    days_de = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    days_short_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    days_short_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    lang = get_locale_language(locale)
    if lang == "de":
        return days_short_de[weekday] if short else days_de[weekday]
    elif lang == "es":
        return days_short_es[weekday] if short else days_es[weekday]
    return days_short_en[weekday] if short else days_en[weekday]


def get_month_name(month: int, locale: str, short: bool) -> str:
    """Get month name in locale."""
    months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    months_short_en = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    lang = get_locale_language(locale)
    if lang == "en":
        return months_short_en[month - 1] if short else months_en[month - 1]
    return months_short_en[month - 1] if short else months_en[month - 1]


def pluralize_locale(count: int, singular: str, plural: str, locale: str) -> str:
    """Pluralize word according to locale rules."""
    lang = get_locale_language(locale)
    if lang == "ru":
        if count % 10 == 1 and count % 100 != 11:
            return singular
        return plural
    return singular if count == 1 else plural


def translate_key(key: str, translations: dict, locale: str, fallback_locale: str) -> str:
    """Translate a key using translation dictionary."""
    locale_trans = translations.get(locale, {})
    if key in locale_trans:
        return locale_trans[key]
    fallback_trans = translations.get(fallback_locale, {})
    return fallback_trans.get(key, key)


def interpolate_translation(template: str, variables: dict) -> str:
    """Interpolate variables into translation template."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
        result = result.replace(f"{{{{ {key} }}}}", str(value))
    return result


def get_country_name(country_code: str, locale: str) -> str:
    """Get country name in locale."""
    countries_en = {
        "US": "United States", "GB": "United Kingdom", "CA": "Canada",
        "DE": "Germany", "FR": "France", "ES": "Spain", "IT": "Italy",
        "JP": "Japan", "CN": "China", "BR": "Brazil", "AU": "Australia"
    }
    return countries_en.get(country_code.upper(), country_code)


def get_language_name(language_code: str, display_locale: str) -> str:
    """Get language name in display locale."""
    languages = {
        "en": "English", "de": "German", "fr": "French", "es": "Spanish",
        "it": "Italian", "pt": "Portuguese", "ja": "Japanese", "zh": "Chinese"
    }
    return languages.get(language_code.lower(), language_code)


def build_locale_selector_options(supported_locales: list) -> list:
    """Build locale selector options."""
    return [{"value": loc, "label": get_language_name(get_locale_language(loc), "en")} for loc in supported_locales]


def detect_locale_from_header(accept_language: str, supported_locales: list, default_locale: str) -> str:
    """Detect best locale from Accept-Language header."""
    if not accept_language:
        return default_locale
    for part in accept_language.split(","):
        locale = part.split(";")[0].strip()
        normalized = normalize_locale(locale)
        if normalized in supported_locales:
            return normalized
        lang = get_locale_language(locale)
        for supported in supported_locales:
            if supported.startswith(lang):
                return supported
    return default_locale


def merge_translations(base: dict, override: dict) -> dict:
    """Merge translation dictionaries."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_translations(result[key], value)
        else:
            result[key] = value
    return result


def find_missing_translations(base_translations: dict, locale_translations: dict) -> list:
    """Find missing translations compared to base."""
    missing = []
    for key in base_translations:
        if key not in locale_translations:
            missing.append(key)
    return missing


def calculate_translation_coverage(total_keys: int, translated_keys: int) -> float:
    """Calculate translation coverage percentage."""
    if total_keys <= 0:
        return 0.0
    return (translated_keys / total_keys) * 100


def format_list_locale(items: list, locale: str, style: str) -> str:
    """Format a list according to locale."""
    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])
    lang = get_locale_language(locale)
    if style == "or":
        conjunction = "oder" if lang == "de" else "o" if lang == "es" else "or"
    else:
        conjunction = "und" if lang == "de" else "y" if lang == "es" else "and"
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return ", ".join(str(i) for i in items[:-1]) + f", {conjunction} {items[-1]}"
