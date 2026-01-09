"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Form Utilities - Pure functions for form handling and validation.
All functions are pure, deterministic, and atomic.
"""

def build_form_field(name: str, field_type: str, label: str, required: bool, default_value) -> dict:
    """Build a form field definition."""
    return {
        "name": name,
        "type": field_type,
        "label": label,
        "required": required,
        "default": default_value,
        "validators": [],
        "errors": []
    }


def add_validator(field: dict, validator_type: str, params: dict, message: str) -> dict:
    """Add a validator to a form field."""
    result = dict(field)
    result["validators"] = list(field.get("validators", []))
    result["validators"].append({
        "type": validator_type,
        "params": params,
        "message": message
    })
    return result


def validate_required(value, message: str) -> dict:
    """Validate that field has a value."""
    is_valid = value is not None and str(value).strip() != ""
    return {"valid": is_valid, "error": None if is_valid else message}


def validate_min_length(value: str, min_len: int, message: str) -> dict:
    """Validate minimum string length."""
    is_valid = len(str(value)) >= min_len
    return {"valid": is_valid, "error": None if is_valid else message}


def validate_max_length(value: str, max_len: int, message: str) -> dict:
    """Validate maximum string length."""
    is_valid = len(str(value)) <= max_len
    return {"valid": is_valid, "error": None if is_valid else message}


def validate_pattern(value: str, pattern: str, message: str) -> dict:
    """Validate against regex pattern."""
    import re
    is_valid = bool(re.match(pattern, str(value)))
    return {"valid": is_valid, "error": None if is_valid else message}


def validate_email_format(value: str, message: str) -> dict:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return validate_pattern(value, pattern, message)


def validate_url_format(value: str, message: str) -> dict:
    """Validate URL format."""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return validate_pattern(value, pattern, message)


def validate_numeric(value, message: str) -> dict:
    """Validate that value is numeric."""
    try:
        float(value)
        return {"valid": True, "error": None}
    except (ValueError, TypeError):
        return {"valid": False, "error": message}


def validate_integer(value, message: str) -> dict:
    """Validate that value is an integer."""
    try:
        if float(value) == int(float(value)):
            return {"valid": True, "error": None}
        return {"valid": False, "error": message}
    except (ValueError, TypeError):
        return {"valid": False, "error": message}


def validate_min_value(value, min_val, message: str) -> dict:
    """Validate minimum numeric value."""
    try:
        is_valid = float(value) >= min_val
        return {"valid": is_valid, "error": None if is_valid else message}
    except (ValueError, TypeError):
        return {"valid": False, "error": message}


def validate_max_value(value, max_val, message: str) -> dict:
    """Validate maximum numeric value."""
    try:
        is_valid = float(value) <= max_val
        return {"valid": is_valid, "error": None if is_valid else message}
    except (ValueError, TypeError):
        return {"valid": False, "error": message}


def validate_in_list(value, allowed_values: list, message: str) -> dict:
    """Validate value is in allowed list."""
    is_valid = value in allowed_values
    return {"valid": is_valid, "error": None if is_valid else message}


def validate_date_format(value: str, format_pattern: str, message: str) -> dict:
    """Validate date format."""
    from datetime import datetime
    try:
        datetime.strptime(value, format_pattern)
        return {"valid": True, "error": None}
    except ValueError:
        return {"valid": False, "error": message}


def validate_date_range(value: str, min_date: str, max_date: str, message: str) -> dict:
    """Validate date is within range."""
    is_valid = min_date <= value <= max_date
    return {"valid": is_valid, "error": None if is_valid else message}


def validate_file_extension(filename: str, allowed_extensions: list, message: str) -> dict:
    """Validate file extension."""
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    is_valid = ext in [e.lower() for e in allowed_extensions]
    return {"valid": is_valid, "error": None if is_valid else message}


def validate_file_size(size_bytes: int, max_bytes: int, message: str) -> dict:
    """Validate file size."""
    is_valid = size_bytes <= max_bytes
    return {"valid": is_valid, "error": None if is_valid else message}


def run_field_validators(value, validators: list) -> list:
    """Run all validators on a field value."""
    errors = []
    for validator in validators:
        v_type = validator["type"]
        params = validator.get("params", {})
        message = validator.get("message", "Invalid value")
        result = None
        if v_type == "required":
            result = validate_required(value, message)
        elif v_type == "min_length":
            result = validate_min_length(value, params.get("min", 0), message)
        elif v_type == "max_length":
            result = validate_max_length(value, params.get("max", 0), message)
        elif v_type == "pattern":
            result = validate_pattern(value, params.get("pattern", ""), message)
        elif v_type == "email":
            result = validate_email_format(value, message)
        elif v_type == "numeric":
            result = validate_numeric(value, message)
        elif v_type == "min_value":
            result = validate_min_value(value, params.get("min", 0), message)
        elif v_type == "max_value":
            result = validate_max_value(value, params.get("max", 0), message)
        if result and not result["valid"]:
            errors.append(result["error"])
    return errors


def validate_form(form_data: dict, field_definitions: list) -> dict:
    """Validate entire form."""
    errors = {}
    is_valid = True
    for field in field_definitions:
        name = field["name"]
        value = form_data.get(name, field.get("default"))
        field_errors = []
        if field.get("required") and not value:
            field_errors.append(f"{field.get('label', name)} is required")
        if value and field.get("validators"):
            field_errors.extend(run_field_validators(value, field["validators"]))
        if field_errors:
            errors[name] = field_errors
            is_valid = False
    return {"valid": is_valid, "errors": errors}


def sanitize_form_input(value: str) -> str:
    """Sanitize form input to prevent XSS."""
    replacements = {"<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#x27;", "&": "&amp;"}
    result = value
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    return result


def normalize_form_data(form_data: dict, field_definitions: list) -> dict:
    """Normalize form data (trim, type conversion)."""
    result = {}
    for field in field_definitions:
        name = field["name"]
        value = form_data.get(name, field.get("default"))
        if isinstance(value, str):
            value = value.strip()
        if field["type"] == "number" and value:
            try:
                value = float(value)
            except ValueError:
                pass
        elif field["type"] == "integer" and value:
            try:
                value = int(value)
            except ValueError:
                pass
        elif field["type"] == "boolean":
            value = value in [True, "true", "1", "yes", "on"]
        result[name] = value
    return result


def build_form_state(fields: list, values: dict, errors: dict, submitted: bool) -> dict:
    """Build form state object."""
    return {
        "fields": fields,
        "values": values,
        "errors": errors,
        "submitted": submitted,
        "is_valid": len(errors) == 0 and submitted
    }


def get_field_error(errors: dict, field_name: str) -> str:
    """Get first error message for a field."""
    field_errors = errors.get(field_name, [])
    return field_errors[0] if field_errors else ""


def has_field_error(errors: dict, field_name: str) -> bool:
    """Check if field has any errors."""
    return field_name in errors and len(errors[field_name]) > 0


def format_validation_errors(errors: dict) -> str:
    """Format all validation errors as text."""
    lines = []
    for field, field_errors in errors.items():
        for error in field_errors:
            lines.append(f"- {field}: {error}")
    return "\n".join(lines)
