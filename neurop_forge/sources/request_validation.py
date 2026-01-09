"""
Request Validation Utilities - Pure functions for API request validation.
All functions are pure, deterministic, and atomic.
"""

def validate_required_fields(data: dict, required: list) -> dict:
    """Validate that all required fields are present."""
    missing = [f for f in required if f not in data or data[f] is None]
    return {
        "valid": len(missing) == 0,
        "missing_fields": missing,
        "error": f"Missing required fields: {', '.join(missing)}" if missing else None
    }


def validate_field_types(data: dict, type_specs: dict) -> dict:
    """Validate field types match specifications."""
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict
    }
    errors = []
    for field, expected_type in type_specs.items():
        if field in data and data[field] is not None:
            python_type = type_map.get(expected_type)
            if python_type and not isinstance(data[field], python_type):
                errors.append(f"{field} must be {expected_type}")
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_string_length(value: str, min_len: int, max_len: int, field_name: str) -> dict:
    """Validate string length constraints."""
    if len(value) < min_len:
        return {"valid": False, "error": f"{field_name} must be at least {min_len} characters"}
    if len(value) > max_len:
        return {"valid": False, "error": f"{field_name} must be at most {max_len} characters"}
    return {"valid": True, "error": None}


def validate_numeric_range(value, min_val, max_val, field_name: str) -> dict:
    """Validate numeric range constraints."""
    if min_val is not None and value < min_val:
        return {"valid": False, "error": f"{field_name} must be at least {min_val}"}
    if max_val is not None and value > max_val:
        return {"valid": False, "error": f"{field_name} must be at most {max_val}"}
    return {"valid": True, "error": None}


def validate_enum(value: str, allowed_values: list, field_name: str) -> dict:
    """Validate value is one of allowed enum values."""
    if value not in allowed_values:
        return {
            "valid": False,
            "error": f"{field_name} must be one of: {', '.join(allowed_values)}"
        }
    return {"valid": True, "error": None}


def validate_email_format(email: str) -> dict:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return {"valid": False, "error": "Invalid email format"}
    return {"valid": True, "error": None}


def validate_url_format(url: str, require_https: bool) -> dict:
    """Validate URL format."""
    import re
    if require_https:
        if not url.startswith("https://"):
            return {"valid": False, "error": "URL must use HTTPS"}
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url):
        return {"valid": False, "error": "Invalid URL format"}
    return {"valid": True, "error": None}


def validate_uuid_format(value: str) -> dict:
    """Validate UUID format."""
    import re
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(pattern, value.lower()):
        return {"valid": False, "error": "Invalid UUID format"}
    return {"valid": True, "error": None}


def validate_date_format(value: str, format_str: str) -> dict:
    """Validate date string format."""
    from datetime import datetime
    try:
        datetime.strptime(value, format_str)
        return {"valid": True, "error": None}
    except ValueError:
        return {"valid": False, "error": f"Invalid date format, expected {format_str}"}


def validate_iso_datetime(value: str) -> dict:
    """Validate ISO 8601 datetime format."""
    import re
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$'
    if not re.match(pattern, value):
        return {"valid": False, "error": "Invalid ISO 8601 datetime format"}
    return {"valid": True, "error": None}


def validate_array_length(arr: list, min_len: int, max_len: int, field_name: str) -> dict:
    """Validate array length constraints."""
    if len(arr) < min_len:
        return {"valid": False, "error": f"{field_name} must have at least {min_len} items"}
    if max_len > 0 and len(arr) > max_len:
        return {"valid": False, "error": f"{field_name} must have at most {max_len} items"}
    return {"valid": True, "error": None}


def validate_array_items(arr: list, item_type: str, field_name: str) -> dict:
    """Validate all items in array are of expected type."""
    type_map = {"string": str, "integer": int, "number": (int, float), "boolean": bool}
    python_type = type_map.get(item_type)
    if not python_type:
        return {"valid": True, "error": None}
    for i, item in enumerate(arr):
        if not isinstance(item, python_type):
            return {"valid": False, "error": f"{field_name}[{i}] must be {item_type}"}
    return {"valid": True, "error": None}


def validate_unique_array(arr: list, field_name: str) -> dict:
    """Validate array contains unique values."""
    try:
        if len(arr) != len(set(arr)):
            return {"valid": False, "error": f"{field_name} contains duplicate values"}
    except TypeError:
        pass
    return {"valid": True, "error": None}


def validate_pattern(value: str, pattern: str, field_name: str) -> dict:
    """Validate string matches regex pattern."""
    import re
    if not re.match(pattern, value):
        return {"valid": False, "error": f"{field_name} has invalid format"}
    return {"valid": True, "error": None}


def validate_phone_format(phone: str) -> dict:
    """Validate phone number format (basic)."""
    import re
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    if not re.match(r'^\+?[0-9]{7,15}$', cleaned):
        return {"valid": False, "error": "Invalid phone number format"}
    return {"valid": True, "error": None}


def validate_credit_card_luhn(number: str) -> dict:
    """Validate credit card number using Luhn algorithm."""
    digits = [int(d) for d in number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return {"valid": False, "error": "Invalid card number length"}
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    if checksum % 10 != 0:
        return {"valid": False, "error": "Invalid card number"}
    return {"valid": True, "error": None}


def validate_ip_address(ip: str, version: int) -> dict:
    """Validate IP address format."""
    import re
    if version == 4:
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(pattern, ip):
            return {"valid": False, "error": "Invalid IPv4 address"}
    elif version == 6:
        pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        if not re.match(pattern, ip):
            return {"valid": False, "error": "Invalid IPv6 address"}
    return {"valid": True, "error": None}


def validate_json_body(body: str) -> dict:
    """Validate string is valid JSON."""
    import json
    try:
        json.loads(body)
        return {"valid": True, "error": None, "data": json.loads(body)}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON: {str(e)}", "data": None}


def validate_content_type(header: str, expected_types: list) -> dict:
    """Validate Content-Type header matches expected."""
    if not header:
        return {"valid": False, "error": "Content-Type header required"}
    content_type = header.split(';')[0].strip().lower()
    if content_type not in [t.lower() for t in expected_types]:
        return {"valid": False, "error": f"Unsupported Content-Type. Expected: {', '.join(expected_types)}"}
    return {"valid": True, "error": None}


def validate_accept_header(header: str, supported_types: list) -> dict:
    """Validate Accept header can be satisfied."""
    if not header or header == "*/*":
        return {"valid": True, "error": None}
    accepted = [t.strip().lower() for t in header.split(',')]
    for supported in supported_types:
        if supported.lower() in accepted:
            return {"valid": True, "error": None}
    return {"valid": False, "error": f"Cannot satisfy Accept header. Supported: {', '.join(supported_types)}"}


def validate_pagination_params(page: int, per_page: int, max_per_page: int) -> dict:
    """Validate pagination parameters."""
    errors = []
    if page < 1:
        errors.append("page must be at least 1")
    if per_page < 1:
        errors.append("per_page must be at least 1")
    if per_page > max_per_page:
        errors.append(f"per_page must be at most {max_per_page}")
    return {"valid": len(errors) == 0, "errors": errors}


def validate_sort_param(sort: str, allowed_fields: list) -> dict:
    """Validate sort parameter."""
    if not sort:
        return {"valid": True, "error": None}
    field = sort.lstrip('-').lstrip('+')
    if field not in allowed_fields:
        return {"valid": False, "error": f"Cannot sort by {field}. Allowed: {', '.join(allowed_fields)}"}
    return {"valid": True, "error": None}


def validate_filter_operators(filters: dict, allowed_operators: list) -> dict:
    """Validate filter operators are allowed."""
    errors = []
    for key in filters.keys():
        if "__" in key:
            _, operator = key.rsplit("__", 1)
            if operator not in allowed_operators:
                errors.append(f"Operator '{operator}' not allowed")
    return {"valid": len(errors) == 0, "errors": errors}


def sanitize_string_input(value: str, max_length: int, strip_html: bool) -> str:
    """Sanitize string input."""
    import re
    result = value.strip()
    if strip_html:
        result = re.sub(r'<[^>]+>', '', result)
    if len(result) > max_length:
        result = result[:max_length]
    return result


def sanitize_html_entities(value: str) -> str:
    """Escape HTML entities in a string."""
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;'
    }
    for char, entity in replacements.items():
        value = value.replace(char, entity)
    return value


def combine_validation_results(results: list) -> dict:
    """Combine multiple validation results."""
    all_errors = []
    for result in results:
        if not result.get("valid"):
            if "error" in result and result["error"]:
                all_errors.append(result["error"])
            if "errors" in result:
                all_errors.extend(result["errors"])
    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors
    }


def build_validation_error_response(errors: list) -> dict:
    """Build a validation error response."""
    return {
        "success": False,
        "error": {
            "code": 400,
            "message": "Validation failed",
            "details": errors
        }
    }


def extract_field_from_path(path: str, data: dict):
    """Extract a field value using dot notation path."""
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def validate_nested_object(data: dict, schema: dict, prefix: str) -> dict:
    """Validate a nested object against a schema."""
    errors = []
    for field, rules in schema.items():
        full_path = f"{prefix}.{field}" if prefix else field
        value = extract_field_from_path(field, data)
        if rules.get("required") and value is None:
            errors.append(f"{full_path} is required")
            continue
        if value is not None:
            if "type" in rules:
                type_result = validate_field_types({field: value}, {field: rules["type"]})
                if not type_result["valid"]:
                    errors.extend([f"{full_path}: {e}" for e in type_result["errors"]])
            if "min_length" in rules and isinstance(value, str):
                if len(value) < rules["min_length"]:
                    errors.append(f"{full_path} must be at least {rules['min_length']} characters")
            if "max_length" in rules and isinstance(value, str):
                if len(value) > rules["max_length"]:
                    errors.append(f"{full_path} must be at most {rules['max_length']} characters")
    return {"valid": len(errors) == 0, "errors": errors}
