"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Data Integrity Utilities - Pure functions for data validation and integrity checks.
All functions are pure, deterministic, and atomic.
"""

def check_not_null(value, field_name: str) -> dict:
    """Check if a value is not null."""
    if value is None:
        return {"valid": False, "error": f"{field_name} cannot be null"}
    return {"valid": True, "error": None}


def check_not_empty(value: str, field_name: str) -> dict:
    """Check if a string value is not empty."""
    if not value or not value.strip():
        return {"valid": False, "error": f"{field_name} cannot be empty"}
    return {"valid": True, "error": None}


def check_min_length(value: str, min_len: int, field_name: str) -> dict:
    """Check if a string meets minimum length requirement."""
    if len(value) < min_len:
        return {"valid": False, "error": f"{field_name} must be at least {min_len} characters"}
    return {"valid": True, "error": None}


def check_max_length(value: str, max_len: int, field_name: str) -> dict:
    """Check if a string is within maximum length."""
    if len(value) > max_len:
        return {"valid": False, "error": f"{field_name} must be at most {max_len} characters"}
    return {"valid": True, "error": None}


def check_length_range(value: str, min_len: int, max_len: int, field_name: str) -> dict:
    """Check if a string length is within a range."""
    if len(value) < min_len or len(value) > max_len:
        return {"valid": False, "error": f"{field_name} must be between {min_len} and {max_len} characters"}
    return {"valid": True, "error": None}


def check_numeric_range(value: float, min_val: float, max_val: float, field_name: str) -> dict:
    """Check if a numeric value is within a range."""
    if value < min_val or value > max_val:
        return {"valid": False, "error": f"{field_name} must be between {min_val} and {max_val}"}
    return {"valid": True, "error": None}


def check_positive(value: float, field_name: str) -> dict:
    """Check if a numeric value is positive."""
    if value <= 0:
        return {"valid": False, "error": f"{field_name} must be positive"}
    return {"valid": True, "error": None}


def check_non_negative(value: float, field_name: str) -> dict:
    """Check if a numeric value is non-negative."""
    if value < 0:
        return {"valid": False, "error": f"{field_name} cannot be negative"}
    return {"valid": True, "error": None}


def check_in_list(value, allowed: list, field_name: str) -> dict:
    """Check if a value is in an allowed list."""
    if value not in allowed:
        return {"valid": False, "error": f"{field_name} must be one of: {', '.join(str(a) for a in allowed)}"}
    return {"valid": True, "error": None}


def check_not_in_list(value, forbidden: list, field_name: str) -> dict:
    """Check if a value is not in a forbidden list."""
    if value in forbidden:
        return {"valid": False, "error": f"{field_name} cannot be: {value}"}
    return {"valid": True, "error": None}


def check_pattern(value: str, pattern: str, field_name: str) -> dict:
    """Check if a string matches a regex pattern."""
    import re
    if not re.match(pattern, value):
        return {"valid": False, "error": f"{field_name} has invalid format"}
    return {"valid": True, "error": None}


def check_email_format(value: str, field_name: str) -> dict:
    """Check if a string is a valid email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, value):
        return {"valid": False, "error": f"{field_name} must be a valid email address"}
    return {"valid": True, "error": None}


def check_uuid_format(value: str, field_name: str) -> dict:
    """Check if a string is a valid UUID format."""
    import re
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(pattern, value.lower()):
        return {"valid": False, "error": f"{field_name} must be a valid UUID"}
    return {"valid": True, "error": None}


def check_date_format(value: str, format_str: str, field_name: str) -> dict:
    """Check if a string matches a date format."""
    from datetime import datetime
    try:
        datetime.strptime(value, format_str)
        return {"valid": True, "error": None}
    except ValueError:
        return {"valid": False, "error": f"{field_name} must be a valid date in format {format_str}"}


def check_date_range(value: str, min_date: str, max_date: str, field_name: str) -> dict:
    """Check if a date string is within a range."""
    if value < min_date or value > max_date:
        return {"valid": False, "error": f"{field_name} must be between {min_date} and {max_date}"}
    return {"valid": True, "error": None}


def check_future_date(value: str, reference_date: str, field_name: str) -> dict:
    """Check if a date is in the future relative to reference."""
    if value <= reference_date:
        return {"valid": False, "error": f"{field_name} must be in the future"}
    return {"valid": True, "error": None}


def check_past_date(value: str, reference_date: str, field_name: str) -> dict:
    """Check if a date is in the past relative to reference."""
    if value >= reference_date:
        return {"valid": False, "error": f"{field_name} must be in the past"}
    return {"valid": True, "error": None}


def check_unique_in_list(values: list, field_name: str) -> dict:
    """Check if all values in a list are unique."""
    if len(values) != len(set(values)):
        return {"valid": False, "error": f"{field_name} contains duplicates"}
    return {"valid": True, "error": None}


def check_list_not_empty(values: list, field_name: str) -> dict:
    """Check if a list is not empty."""
    if not values:
        return {"valid": False, "error": f"{field_name} cannot be empty"}
    return {"valid": True, "error": None}


def check_list_length(values: list, min_len: int, max_len: int, field_name: str) -> dict:
    """Check if a list length is within range."""
    if len(values) < min_len or len(values) > max_len:
        return {"valid": False, "error": f"{field_name} must have between {min_len} and {max_len} items"}
    return {"valid": True, "error": None}


def combine_validation_results(results: list) -> dict:
    """Combine multiple validation results into one."""
    errors = [r["error"] for r in results if not r["valid"]]
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_record(record: dict, rules: dict) -> dict:
    """Validate a record against a set of rules."""
    results = []
    for field, validators in rules.items():
        value = record.get(field)
        for validator_name, params in validators.items():
            if validator_name == "not_null":
                results.append(check_not_null(value, field))
            elif validator_name == "not_empty" and isinstance(value, str):
                results.append(check_not_empty(value, field))
            elif validator_name == "min_length" and isinstance(value, str):
                results.append(check_min_length(value, params, field))
            elif validator_name == "max_length" and isinstance(value, str):
                results.append(check_max_length(value, params, field))
            elif validator_name == "positive" and isinstance(value, (int, float)):
                results.append(check_positive(value, field))
            elif validator_name == "non_negative" and isinstance(value, (int, float)):
                results.append(check_non_negative(value, field))
            elif validator_name == "in_list":
                results.append(check_in_list(value, params, field))
            elif validator_name == "pattern" and isinstance(value, str):
                results.append(check_pattern(value, params, field))
    return combine_validation_results(results)


def check_referential_integrity(value, reference_values: set, field_name: str) -> dict:
    """Check if a value exists in a reference set (foreign key check)."""
    if value not in reference_values:
        return {"valid": False, "error": f"{field_name} references non-existent record"}
    return {"valid": True, "error": None}


def check_circular_reference(parent_id, child_id: str) -> dict:
    """Check if a parent-child relationship creates a circular reference."""
    if parent_id == child_id:
        return {"valid": False, "error": "Circular reference detected: item cannot be its own parent"}
    return {"valid": True, "error": None}


def generate_check_constraint(column: str, condition: str) -> str:
    """Generate a CHECK constraint SQL fragment."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CHECK ({condition})"


def generate_not_null_constraint(column: str) -> str:
    """Generate a NOT NULL constraint SQL fragment."""
    return "NOT NULL"


def generate_unique_constraint(columns: list, name: str) -> str:
    """Generate a UNIQUE constraint SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    col_list = ", ".join(escape_sql_identifier(c) for c in columns)
    return f"CONSTRAINT {escape_sql_identifier(name)} UNIQUE ({col_list})"


def generate_foreign_key_constraint_full(name: str, column: str, ref_table: str, ref_column: str, on_delete: str, on_update: str) -> str:
    """Generate a full FOREIGN KEY constraint SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    parts = [
        f"CONSTRAINT {escape_sql_identifier(name)}",
        f"FOREIGN KEY ({escape_sql_identifier(column)})",
        f"REFERENCES {escape_sql_identifier(ref_table)}({escape_sql_identifier(ref_column)})"
    ]
    if on_delete:
        parts.append(f"ON DELETE {on_delete.upper()}")
    if on_update:
        parts.append(f"ON UPDATE {on_update.upper()}")
    return " ".join(parts)


def generate_positive_check(column: str) -> str:
    """Generate a CHECK constraint for positive values."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CHECK ({escape_sql_identifier(column)} > 0)"


def generate_non_negative_check(column: str) -> str:
    """Generate a CHECK constraint for non-negative values."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CHECK ({escape_sql_identifier(column)} >= 0)"


def generate_range_check(column: str, min_val: float, max_val: float) -> str:
    """Generate a CHECK constraint for a numeric range."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CHECK ({escape_sql_identifier(column)} >= {min_val} AND {escape_sql_identifier(column)} <= {max_val})"


def generate_length_check(column: str, min_len: int, max_len: int) -> str:
    """Generate a CHECK constraint for string length."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CHECK (LENGTH({escape_sql_identifier(column)}) >= {min_len} AND LENGTH({escape_sql_identifier(column)}) <= {max_len})"


def generate_enum_check(column: str, allowed_values: list) -> str:
    """Generate a CHECK constraint for enum-like values."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, escape_sql_string
    values = ", ".join(f"'{escape_sql_string(v)}'" for v in allowed_values)
    return f"CHECK ({escape_sql_identifier(column)} IN ({values}))"


def generate_date_range_check(column: str, min_date: str, max_date: str) -> str:
    """Generate a CHECK constraint for date range."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CHECK ({escape_sql_identifier(column)} >= '{min_date}' AND {escape_sql_identifier(column)} <= '{max_date}')"


def generate_not_empty_check(column: str) -> str:
    """Generate a CHECK constraint for non-empty strings."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CHECK (LENGTH(TRIM({escape_sql_identifier(column)})) > 0)"


def generate_email_check(column: str) -> str:
    """Generate a CHECK constraint for email format."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CHECK ({escape_sql_identifier(column)} ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$')"


def is_valid_constraint_name(name: str) -> bool:
    """Check if a constraint name is valid."""
    import re
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))


def generate_constraint_name(table: str, columns: list, constraint_type: str) -> str:
    """Generate a standard constraint name."""
    col_part = "_".join(columns)
    type_abbr = {"primary_key": "pk", "foreign_key": "fk", "unique": "uq", "check": "ck"}
    abbr = type_abbr.get(constraint_type, constraint_type[:2])
    return f"{table}_{col_part}_{abbr}"


def calculate_data_checksum(values: list) -> str:
    """Calculate a checksum for a list of values."""
    import hashlib
    data = "|".join(str(v) for v in values)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def verify_data_checksum(values: list, expected_checksum: str) -> bool:
    """Verify data against an expected checksum."""
    return calculate_data_checksum(values) == expected_checksum


def detect_duplicate_keys(records: list, key_column: str) -> list:
    """Detect duplicate primary key values in a record list."""
    seen = {}
    duplicates = []
    for i, record in enumerate(records):
        key = record.get(key_column)
        if key in seen:
            duplicates.append({"key": key, "first_index": seen[key], "duplicate_index": i})
        else:
            seen[key] = i
    return duplicates


def detect_orphaned_references(child_records: list, parent_ids: set, fk_column: str) -> list:
    """Detect child records with invalid parent references."""
    orphans = []
    for i, record in enumerate(child_records):
        fk_value = record.get(fk_column)
        if fk_value is not None and fk_value not in parent_ids:
            orphans.append({"index": i, "fk_value": fk_value})
    return orphans


def generate_deferrable_constraint(constraint_sql: str, initially_deferred: bool) -> str:
    """Make a constraint deferrable."""
    deferred = "INITIALLY DEFERRED" if initially_deferred else "INITIALLY IMMEDIATE"
    return f"{constraint_sql} DEFERRABLE {deferred}"


def generate_exclude_constraint(table: str, column: str, operator: str, constraint_name: str) -> str:
    """Generate an EXCLUDE constraint SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"CONSTRAINT {escape_sql_identifier(constraint_name)} EXCLUDE USING gist ({escape_sql_identifier(column)} WITH {operator})"


def is_cascading_action(action: str) -> bool:
    """Check if a referential action is cascading."""
    return action.upper() in ("CASCADE", "SET NULL", "SET DEFAULT")


def get_referential_action_sql(action: str) -> str:
    """Get the SQL for a referential action."""
    valid_actions = {"CASCADE", "SET NULL", "SET DEFAULT", "RESTRICT", "NO ACTION"}
    upper = action.upper()
    return upper if upper in valid_actions else "NO ACTION"
