"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
SQL Type Utilities - Pure functions for SQL type handling and conversion.
All functions are pure, deterministic, and atomic.
"""

def get_postgres_type(python_type: str) -> str:
    """Map a Python type name to PostgreSQL type."""
    type_map = {
        "str": "TEXT",
        "int": "INTEGER",
        "float": "DOUBLE PRECISION",
        "bool": "BOOLEAN",
        "bytes": "BYTEA",
        "datetime": "TIMESTAMP",
        "date": "DATE",
        "time": "TIME",
        "timedelta": "INTERVAL",
        "Decimal": "NUMERIC",
        "dict": "JSONB",
        "list": "JSONB",
        "uuid": "UUID",
    }
    return type_map.get(python_type, "TEXT")


def get_mysql_type(python_type: str) -> str:
    """Map a Python type name to MySQL type."""
    type_map = {
        "str": "VARCHAR(255)",
        "int": "INT",
        "float": "DOUBLE",
        "bool": "TINYINT(1)",
        "bytes": "BLOB",
        "datetime": "DATETIME",
        "date": "DATE",
        "time": "TIME",
        "Decimal": "DECIMAL(10,2)",
        "dict": "JSON",
        "list": "JSON",
        "uuid": "CHAR(36)",
    }
    return type_map.get(python_type, "VARCHAR(255)")


def get_sqlite_type(python_type: str) -> str:
    """Map a Python type name to SQLite type."""
    type_map = {
        "str": "TEXT",
        "int": "INTEGER",
        "float": "REAL",
        "bool": "INTEGER",
        "bytes": "BLOB",
        "datetime": "TEXT",
        "date": "TEXT",
        "time": "TEXT",
        "Decimal": "TEXT",
        "dict": "TEXT",
        "list": "TEXT",
        "uuid": "TEXT",
    }
    return type_map.get(python_type, "TEXT")


def is_numeric_type(sql_type: str) -> bool:
    """Check if a SQL type is numeric."""
    numeric_types = {
        "INTEGER", "INT", "SMALLINT", "BIGINT", "TINYINT",
        "DECIMAL", "NUMERIC", "REAL", "FLOAT", "DOUBLE", "DOUBLE PRECISION",
        "SERIAL", "BIGSERIAL", "SMALLSERIAL"
    }
    return sql_type.upper().split("(")[0] in numeric_types


def is_text_type(sql_type: str) -> bool:
    """Check if a SQL type is text-based."""
    text_types = {
        "TEXT", "VARCHAR", "CHAR", "CHARACTER VARYING", "CHARACTER",
        "NVARCHAR", "NCHAR", "CLOB", "NCLOB"
    }
    return sql_type.upper().split("(")[0] in text_types


def is_temporal_type(sql_type: str) -> bool:
    """Check if a SQL type is temporal (date/time)."""
    temporal_types = {
        "DATE", "TIME", "TIMESTAMP", "DATETIME", "INTERVAL",
        "TIMESTAMPTZ", "TIMETZ"
    }
    return sql_type.upper().split("(")[0] in temporal_types


def is_binary_type(sql_type: str) -> bool:
    """Check if a SQL type is binary."""
    binary_types = {"BYTEA", "BLOB", "BINARY", "VARBINARY", "BIT"}
    return sql_type.upper().split("(")[0] in binary_types


def is_boolean_type(sql_type: str) -> bool:
    """Check if a SQL type is boolean."""
    return sql_type.upper() in ("BOOLEAN", "BOOL", "TINYINT(1)")


def is_json_type(sql_type: str) -> bool:
    """Check if a SQL type is JSON."""
    return sql_type.upper() in ("JSON", "JSONB")


def is_uuid_type(sql_type: str) -> bool:
    """Check if a SQL type is UUID."""
    return sql_type.upper() == "UUID"


def is_array_type(sql_type: str) -> bool:
    """Check if a SQL type is an array."""
    return sql_type.upper().endswith("[]") or sql_type.upper().startswith("ARRAY")


def extract_varchar_length(sql_type: str) -> int:
    """Extract the length from a VARCHAR(n) type definition."""
    import re
    match = re.search(r'\((\d+)\)', sql_type)
    return int(match.group(1)) if match else 0


def extract_numeric_precision(sql_type: str) -> tuple:
    """Extract precision and scale from NUMERIC(p,s) type definition."""
    import re
    match = re.search(r'\((\d+)(?:,\s*(\d+))?\)', sql_type)
    if match:
        precision = int(match.group(1))
        scale = int(match.group(2)) if match.group(2) else 0
        return (precision, scale)
    return (0, 0)


def format_decimal_type(precision: int, scale: int) -> str:
    """Format a DECIMAL/NUMERIC type definition."""
    if scale > 0:
        return f"NUMERIC({precision},{scale})"
    elif precision > 0:
        return f"NUMERIC({precision})"
    return "NUMERIC"


def format_varchar_type(length: int) -> str:
    """Format a VARCHAR type definition."""
    if length > 0:
        return f"VARCHAR({length})"
    return "TEXT"


def format_char_type(length: int) -> str:
    """Format a CHAR type definition."""
    return f"CHAR({length})" if length > 0 else "CHAR(1)"


def get_type_size_bytes(sql_type: str) -> int:
    """Get the approximate size in bytes for a SQL type."""
    sizes = {
        "BOOLEAN": 1, "BOOL": 1, "TINYINT": 1,
        "SMALLINT": 2, "SMALLSERIAL": 2,
        "INTEGER": 4, "INT": 4, "SERIAL": 4, "REAL": 4, "FLOAT": 4,
        "BIGINT": 8, "BIGSERIAL": 8, "DOUBLE PRECISION": 8, "DOUBLE": 8,
        "UUID": 16, "DATE": 4, "TIME": 8, "TIMESTAMP": 8, "TIMESTAMPTZ": 8,
        "INTERVAL": 16,
    }
    base_type = sql_type.upper().split("(")[0]
    return sizes.get(base_type, 0)


def is_variable_length_type(sql_type: str) -> bool:
    """Check if a SQL type has variable length."""
    variable_types = {"TEXT", "VARCHAR", "BYTEA", "BLOB", "JSON", "JSONB", "CLOB"}
    base_type = sql_type.upper().split("(")[0]
    return base_type in variable_types or is_array_type(sql_type)


def get_default_value_literal(sql_type: str) -> str:
    """Get a default value literal for a SQL type."""
    if is_numeric_type(sql_type):
        return "0"
    if is_text_type(sql_type):
        return "''"
    if is_boolean_type(sql_type):
        return "FALSE"
    if is_json_type(sql_type):
        return "'{}'"
    if sql_type.upper() == "DATE":
        return "CURRENT_DATE"
    if "TIMESTAMP" in sql_type.upper():
        return "CURRENT_TIMESTAMP"
    if sql_type.upper() == "TIME":
        return "CURRENT_TIME"
    if is_uuid_type(sql_type):
        return "gen_random_uuid()"
    return "NULL"


def can_cast_safely(from_type: str, to_type: str) -> bool:
    """Check if a SQL type can be safely cast to another type."""
    from_type = from_type.upper().split("(")[0]
    to_type = to_type.upper().split("(")[0]
    safe_casts = {
        "INTEGER": {"BIGINT", "NUMERIC", "DOUBLE PRECISION", "TEXT"},
        "SMALLINT": {"INTEGER", "BIGINT", "NUMERIC", "DOUBLE PRECISION", "TEXT"},
        "BIGINT": {"NUMERIC", "DOUBLE PRECISION", "TEXT"},
        "REAL": {"DOUBLE PRECISION", "TEXT"},
        "TEXT": set(),
        "VARCHAR": {"TEXT"},
        "CHAR": {"VARCHAR", "TEXT"},
        "BOOLEAN": {"TEXT"},
        "DATE": {"TIMESTAMP", "TIMESTAMPTZ", "TEXT"},
        "TIME": {"TEXT"},
        "TIMESTAMP": {"TIMESTAMPTZ", "TEXT"},
    }
    if from_type == to_type:
        return True
    return to_type in safe_casts.get(from_type, set())


def requires_explicit_cast(from_type: str, to_type: str) -> bool:
    """Check if casting between types requires explicit CAST."""
    if can_cast_safely(from_type, to_type):
        return False
    return from_type.upper() != to_type.upper()


def get_array_element_type(array_type: str) -> str:
    """Extract the element type from an array type."""
    if array_type.endswith("[]"):
        return array_type[:-2]
    if array_type.upper().startswith("ARRAY"):
        import re
        match = re.search(r'ARRAY\[(.+)\]', array_type, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def format_array_type(element_type: str) -> str:
    """Format an array type definition."""
    return f"{element_type}[]"


def is_comparable_type(sql_type: str) -> bool:
    """Check if a SQL type supports comparison operators (<, >, etc.)."""
    return (is_numeric_type(sql_type) or is_temporal_type(sql_type) or 
            is_text_type(sql_type) or sql_type.upper() == "UUID")


def is_sortable_type(sql_type: str) -> bool:
    """Check if a SQL type can be used in ORDER BY."""
    return is_comparable_type(sql_type) or is_boolean_type(sql_type)


def is_aggregatable_type(sql_type: str) -> bool:
    """Check if a SQL type supports aggregate functions like SUM, AVG."""
    return is_numeric_type(sql_type)


def get_max_value(sql_type: str) -> int:
    """Get the maximum value for an integer SQL type."""
    max_values = {
        "TINYINT": 127,
        "SMALLINT": 32767,
        "SMALLSERIAL": 32767,
        "INTEGER": 2147483647,
        "INT": 2147483647,
        "SERIAL": 2147483647,
        "BIGINT": 9223372036854775807,
        "BIGSERIAL": 9223372036854775807,
    }
    return max_values.get(sql_type.upper(), 0)


def get_min_value(sql_type: str) -> int:
    """Get the minimum value for an integer SQL type."""
    min_values = {
        "TINYINT": -128,
        "SMALLINT": -32768,
        "SMALLSERIAL": 1,
        "INTEGER": -2147483648,
        "INT": -2147483648,
        "SERIAL": 1,
        "BIGINT": -9223372036854775808,
        "BIGSERIAL": 1,
    }
    return min_values.get(sql_type.upper(), 0)


def infer_type_from_value(value: str) -> str:
    """Infer a SQL type from a string value."""
    if value.lower() in ("true", "false"):
        return "BOOLEAN"
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        int_val = int(value)
        if -32768 <= int_val <= 32767:
            return "SMALLINT"
        if -2147483648 <= int_val <= 2147483647:
            return "INTEGER"
        return "BIGINT"
    try:
        float(value)
        return "DOUBLE PRECISION"
    except ValueError:
        pass
    import re
    if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return "DATE"
    if re.match(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', value):
        return "TIMESTAMP"
    if re.match(r'^\d{2}:\d{2}:\d{2}', value):
        return "TIME"
    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value.lower()):
        return "UUID"
    return "TEXT"


def normalize_type_name(sql_type: str) -> str:
    """Normalize a SQL type name to a standard form."""
    type_aliases = {
        "INT": "INTEGER",
        "INT4": "INTEGER",
        "INT8": "BIGINT",
        "INT2": "SMALLINT",
        "FLOAT4": "REAL",
        "FLOAT8": "DOUBLE PRECISION",
        "BOOL": "BOOLEAN",
        "CHARACTER VARYING": "VARCHAR",
        "CHARACTER": "CHAR",
        "TIMESTAMPTZ": "TIMESTAMP WITH TIME ZONE",
        "TIMETZ": "TIME WITH TIME ZONE",
    }
    base_type = sql_type.upper().split("(")[0].strip()
    normalized = type_aliases.get(base_type, base_type)
    if "(" in sql_type:
        params = sql_type[sql_type.index("("):]
        return normalized + params.upper()
    return normalized


def is_primary_key_candidate(sql_type: str) -> bool:
    """Check if a SQL type is suitable as a primary key."""
    good_pk_types = {
        "INTEGER", "BIGINT", "SERIAL", "BIGSERIAL", "UUID", "TEXT", "VARCHAR"
    }
    base_type = sql_type.upper().split("(")[0]
    return base_type in good_pk_types


def get_index_method(sql_type: str) -> str:
    """Get the recommended index method for a SQL type."""
    if is_json_type(sql_type):
        return "GIN"
    if is_text_type(sql_type):
        return "BTREE"
    if is_array_type(sql_type):
        return "GIN"
    return "BTREE"


def format_type_with_constraints(sql_type: str, not_null: bool, default: str, unique: bool) -> str:
    """Format a complete column type definition with constraints."""
    parts = [sql_type]
    if not_null:
        parts.append("NOT NULL")
    if default:
        parts.append(f"DEFAULT {default}")
    if unique:
        parts.append("UNIQUE")
    return " ".join(parts)
