"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
ORM Pattern Utilities - Pure functions for ORM-style data patterns.
All functions are pure, deterministic, and atomic.
"""

def to_snake_case(name: str) -> str:
    """Convert a string to snake_case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_camel_case(name: str) -> str:
    """Convert a string to camelCase."""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_pascal_case(name: str) -> str:
    """Convert a string to PascalCase."""
    return ''.join(x.title() for x in name.split('_'))


def pluralize(word: str) -> str:
    """Pluralize an English word (basic rules)."""
    if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    if word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    if word.endswith('f'):
        return word[:-1] + 'ves'
    if word.endswith('fe'):
        return word[:-2] + 'ves'
    return word + 's'


def singularize(word: str) -> str:
    """Singularize an English word (basic rules)."""
    if word.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'
    if word.endswith('ves'):
        return word[:-3] + 'f'
    if word.endswith('es') and word[-3] in 'sxz':
        return word[:-2]
    if word.endswith('es') and word[-4:-2] in ('ch', 'sh'):
        return word[:-2]
    if word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word


def model_to_table_name(model_name: str) -> str:
    """Convert a model name to a table name."""
    snake = to_snake_case(model_name)
    return pluralize(snake)


def table_to_model_name(table_name: str) -> str:
    """Convert a table name to a model name."""
    singular = singularize(table_name)
    return to_pascal_case(singular)


def column_to_attribute_name(column_name: str) -> str:
    """Convert a column name to an attribute name."""
    return to_snake_case(column_name)


def attribute_to_column_name(attribute_name: str) -> str:
    """Convert an attribute name to a column name."""
    return to_snake_case(attribute_name)


def foreign_key_name(table: str, column: str) -> str:
    """Generate a foreign key column name."""
    singular = singularize(table)
    return f"{singular}_{column}"


def join_table_name(table1: str, table2: str) -> str:
    """Generate a many-to-many join table name."""
    tables = sorted([table1, table2])
    return f"{tables[0]}_{tables[1]}"


def inverse_relation_name(table: str) -> str:
    """Generate an inverse relation name."""
    return pluralize(singularize(table))


def build_model_dict(columns: list, values: list) -> dict:
    """Build a model dictionary from columns and values."""
    return dict(zip(columns, values))


def model_dict_to_insert_values(model: dict, columns: list) -> list:
    """Extract values from a model dict in column order."""
    return [model.get(col) for col in columns]


def filter_model_fields(model: dict, allowed_fields: list) -> dict:
    """Filter a model dict to only allowed fields."""
    return {k: v for k, v in model.items() if k in allowed_fields}


def exclude_model_fields(model: dict, excluded_fields: list) -> dict:
    """Exclude specific fields from a model dict."""
    return {k: v for k, v in model.items() if k not in excluded_fields}


def get_changed_fields(original: dict, updated: dict) -> dict:
    """Get fields that have changed between two model versions."""
    changed = {}
    for key, value in updated.items():
        if key in original and original[key] != value:
            changed[key] = {"old": original[key], "new": value}
    return changed


def get_dirty_fields(original: dict, updated: dict) -> list:
    """Get list of field names that have changed."""
    return [k for k in updated if k in original and original[k] != updated[k]]


def is_dirty(original: dict, updated: dict) -> bool:
    """Check if a model has any changed fields."""
    return len(get_dirty_fields(original, updated)) > 0


def merge_models(base: dict, updates: dict) -> dict:
    """Merge updates into a base model."""
    result = dict(base)
    result.update(updates)
    return result


def set_timestamps(model: dict, timestamp: str, is_new: bool) -> dict:
    """Set created_at and updated_at timestamps on a model."""
    result = dict(model)
    if is_new:
        result["created_at"] = timestamp
    result["updated_at"] = timestamp
    return result


def add_soft_delete(model: dict, timestamp: str) -> dict:
    """Add soft delete timestamp to a model."""
    result = dict(model)
    result["deleted_at"] = timestamp
    return result


def is_soft_deleted(model: dict) -> bool:
    """Check if a model is soft deleted."""
    return model.get("deleted_at") is not None


def restore_soft_deleted(model: dict) -> dict:
    """Restore a soft deleted model."""
    result = dict(model)
    result["deleted_at"] = None
    return result


def increment_version(model: dict) -> dict:
    """Increment the version field of a model."""
    result = dict(model)
    result["version"] = result.get("version", 0) + 1
    return result


def build_select_columns(table: str, columns: list, prefix: bool) -> list:
    """Build SELECT column list with optional table prefix."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    if prefix:
        return [f"{escape_sql_identifier(table)}.{escape_sql_identifier(c)}" for c in columns]
    return [escape_sql_identifier(c) for c in columns]


def build_where_from_model(model: dict, columns: list) -> tuple:
    """Build WHERE clause conditions from model values."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    conditions = []
    values = []
    placeholder = 1
    for col in columns:
        if col in model:
            conditions.append(f"{escape_sql_identifier(col)} = ${placeholder}")
            values.append(model[col])
            placeholder += 1
    return (" AND ".join(conditions), values)


def build_update_from_model(model: dict, columns: list, skip_columns: list) -> tuple:
    """Build UPDATE SET clause from model values."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    sets = []
    values = []
    placeholder = 1
    for col in columns:
        if col in model and col not in skip_columns:
            sets.append(f"{escape_sql_identifier(col)} = ${placeholder}")
            values.append(model[col])
            placeholder += 1
    return (", ".join(sets), values)


def serialize_for_json(model: dict) -> dict:
    """Serialize a model for JSON output (handle special types)."""
    result = {}
    for key, value in model.items():
        if hasattr(value, 'isoformat'):
            result[key] = value.isoformat()
        elif isinstance(value, bytes):
            result[key] = value.hex()
        else:
            result[key] = value
    return result


def deserialize_from_json(data: dict, date_fields: list, bytes_fields: list) -> dict:
    """Deserialize JSON data to model types."""
    from datetime import datetime
    result = dict(data)
    for field in date_fields:
        if field in result and isinstance(result[field], str):
            try:
                result[field] = datetime.fromisoformat(result[field])
            except ValueError:
                pass
    for field in bytes_fields:
        if field in result and isinstance(result[field], str):
            try:
                result[field] = bytes.fromhex(result[field])
            except ValueError:
                pass
    return result


def build_eager_load_query(main_table: str, main_columns: list, relation: str, relation_columns: list, fk_column: str, pk_column: str) -> str:
    """Build a query for eager loading a relation."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_column_list
    main_cols = ", ".join(f"{escape_sql_identifier(main_table)}.{escape_sql_identifier(c)}" for c in main_columns)
    rel_cols = ", ".join(f"{escape_sql_identifier(relation)}.{escape_sql_identifier(c)}" for c in relation_columns)
    return f"""SELECT {main_cols}, {rel_cols}
FROM {escape_sql_identifier(main_table)}
LEFT JOIN {escape_sql_identifier(relation)} ON {escape_sql_identifier(main_table)}.{escape_sql_identifier(pk_column)} = {escape_sql_identifier(relation)}.{escape_sql_identifier(fk_column)}"""


def group_by_parent(records: list, parent_key: str, child_key: str) -> dict:
    """Group child records by parent key."""
    result = {}
    for record in records:
        parent_id = record.get(parent_key)
        if parent_id not in result:
            result[parent_id] = []
        child_data = {k: v for k, v in record.items() if k != parent_key}
        if any(v is not None for v in child_data.values()):
            result[parent_id].append(child_data)
    return result


def build_has_many_subquery(parent_table: str, child_table: str, fk_column: str, pk_column: str) -> str:
    """Build a subquery to check if parent has any children."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"""EXISTS (
    SELECT 1 FROM {escape_sql_identifier(child_table)}
    WHERE {escape_sql_identifier(child_table)}.{escape_sql_identifier(fk_column)} = {escape_sql_identifier(parent_table)}.{escape_sql_identifier(pk_column)}
)"""


def build_count_subquery(parent_table: str, child_table: str, fk_column: str, pk_column: str, alias: str) -> str:
    """Build a subquery to count children."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"""(
    SELECT COUNT(*) FROM {escape_sql_identifier(child_table)}
    WHERE {escape_sql_identifier(child_table)}.{escape_sql_identifier(fk_column)} = {escape_sql_identifier(parent_table)}.{escape_sql_identifier(pk_column)}
) AS {escape_sql_identifier(alias)}"""


def generate_scope_condition(scope_name: str, scope_params: dict) -> str:
    """Generate a WHERE condition for a named scope."""
    scopes = {
        "active": "deleted_at IS NULL",
        "deleted": "deleted_at IS NOT NULL",
        "recent": "created_at >= CURRENT_DATE - INTERVAL '7 days'",
        "today": "DATE(created_at) = CURRENT_DATE",
        "this_month": "EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM CURRENT_DATE)"
    }
    return scopes.get(scope_name, "1=1")


def build_polymorphic_condition(type_column: str, type_value: str, id_column: str) -> str:
    """Build a condition for polymorphic associations."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, escape_sql_string
    return f"{escape_sql_identifier(type_column)} = '{escape_sql_string(type_value)}' AND {escape_sql_identifier(id_column)} = $1"


def calculate_association_key(from_type: str, from_id: str, to_type: str, to_id: str) -> str:
    """Calculate a unique key for an association."""
    return f"{from_type}:{from_id}:{to_type}:{to_id}"


def parse_association_key(key: str) -> dict:
    """Parse an association key into components."""
    parts = key.split(":")
    if len(parts) == 4:
        return {
            "from_type": parts[0],
            "from_id": parts[1],
            "to_type": parts[2],
            "to_id": parts[3]
        }
    return {}


def build_batch_find_query(table: str, columns: list, id_column: str, id_count: int) -> str:
    """Build a query to find multiple records by IDs."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_column_list, build_where_in
    col_list = build_column_list(columns)
    where_in = build_where_in(id_column, id_count, 1)
    return f"SELECT {col_list} FROM {escape_sql_identifier(table)} {where_in}"


def order_by_ids(records: list, ids: list, id_column: str) -> list:
    """Order records to match the order of provided IDs."""
    id_to_record = {r[id_column]: r for r in records}
    return [id_to_record[id] for id in ids if id in id_to_record]


def default_values(model: dict, defaults: dict) -> dict:
    """Apply default values to a model where fields are missing."""
    result = dict(defaults)
    result.update({k: v for k, v in model.items() if v is not None})
    return result


def validate_model_schema(model: dict, required_fields: list, field_types: dict) -> dict:
    """Validate a model against a schema."""
    errors = []
    for field in required_fields:
        if field not in model or model[field] is None:
            errors.append(f"Missing required field: {field}")
    for field, expected_type in field_types.items():
        if field in model and model[field] is not None:
            if expected_type == "string" and not isinstance(model[field], str):
                errors.append(f"{field} must be a string")
            elif expected_type == "integer" and not isinstance(model[field], int):
                errors.append(f"{field} must be an integer")
            elif expected_type == "number" and not isinstance(model[field], (int, float)):
                errors.append(f"{field} must be a number")
            elif expected_type == "boolean" and not isinstance(model[field], bool):
                errors.append(f"{field} must be a boolean")
    return {"valid": len(errors) == 0, "errors": errors}
