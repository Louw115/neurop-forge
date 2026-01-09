"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Migration Helper Utilities - Pure functions for database migration operations.
All functions are pure, deterministic, and atomic.
No actual database connections - just migration string/structure manipulation.
"""

def generate_migration_id(timestamp: str, name: str) -> str:
    """Generate a migration identifier from timestamp and name."""
    cleaned_name = name.lower().replace(' ', '_').replace('-', '_')
    cleaned_name = ''.join(c for c in cleaned_name if c.isalnum() or c == '_')
    return f"{timestamp}_{cleaned_name}"


def parse_migration_id(migration_id: str) -> tuple:
    """Parse a migration ID into timestamp and name components."""
    parts = migration_id.split('_', 1)
    if len(parts) == 2:
        return (parts[0], parts[1])
    return (migration_id, "")


def compare_migration_ids(id1: str, id2: str) -> int:
    """Compare two migration IDs. Returns -1, 0, or 1."""
    ts1, _ = parse_migration_id(id1)
    ts2, _ = parse_migration_id(id2)
    if ts1 < ts2:
        return -1
    if ts1 > ts2:
        return 1
    return 0


def sort_migration_ids(migration_ids: list) -> list:
    """Sort migration IDs by timestamp."""
    return sorted(migration_ids, key=lambda x: parse_migration_id(x)[0])


def get_pending_migrations(all_migrations: list, applied_migrations: list) -> list:
    """Get list of pending migrations that haven't been applied."""
    applied_set = set(applied_migrations)
    pending = [m for m in all_migrations if m not in applied_set]
    return sort_migration_ids(pending)


def get_migrations_to_rollback(applied_migrations: list, target: str) -> list:
    """Get list of migrations to rollback to reach target state."""
    sorted_applied = sort_migration_ids(applied_migrations)
    if target not in sorted_applied:
        return []
    target_idx = sorted_applied.index(target)
    return list(reversed(sorted_applied[target_idx + 1:]))


def generate_add_column_sql(table: str, column: str, data_type: str, nullable: bool, default: str) -> str:
    """Generate ALTER TABLE ADD COLUMN SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    parts = [f"ALTER TABLE {escape_sql_identifier(table)} ADD COLUMN {escape_sql_identifier(column)} {data_type}"]
    if not nullable:
        parts.append("NOT NULL")
    if default:
        parts.append(f"DEFAULT {default}")
    return " ".join(parts)


def generate_drop_column_sql(table: str, column: str) -> str:
    """Generate ALTER TABLE DROP COLUMN SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(table)} DROP COLUMN {escape_sql_identifier(column)}"


def generate_rename_column_sql(table: str, old_name: str, new_name: str) -> str:
    """Generate ALTER TABLE RENAME COLUMN SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(table)} RENAME COLUMN {escape_sql_identifier(old_name)} TO {escape_sql_identifier(new_name)}"


def generate_change_type_sql(table: str, column: str, new_type: str, using: str) -> str:
    """Generate ALTER TABLE ALTER COLUMN TYPE SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    sql = f"ALTER TABLE {escape_sql_identifier(table)} ALTER COLUMN {escape_sql_identifier(column)} TYPE {new_type}"
    if using:
        sql += f" USING {using}"
    return sql


def generate_set_not_null_sql(table: str, column: str) -> str:
    """Generate ALTER TABLE SET NOT NULL SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(table)} ALTER COLUMN {escape_sql_identifier(column)} SET NOT NULL"


def generate_drop_not_null_sql(table: str, column: str) -> str:
    """Generate ALTER TABLE DROP NOT NULL SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(table)} ALTER COLUMN {escape_sql_identifier(column)} DROP NOT NULL"


def generate_set_default_sql(table: str, column: str, default: str) -> str:
    """Generate ALTER TABLE SET DEFAULT SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(table)} ALTER COLUMN {escape_sql_identifier(column)} SET DEFAULT {default}"


def generate_drop_default_sql(table: str, column: str) -> str:
    """Generate ALTER TABLE DROP DEFAULT SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(table)} ALTER COLUMN {escape_sql_identifier(column)} DROP DEFAULT"


def generate_create_table_sql(table: str, columns: list, primary_key: list) -> str:
    """Generate CREATE TABLE SQL from column definitions."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    col_defs = ", ".join(columns)
    if primary_key:
        pk_cols = ", ".join(escape_sql_identifier(c) for c in primary_key)
        col_defs += f", PRIMARY KEY ({pk_cols})"
    return f"CREATE TABLE {escape_sql_identifier(table)} ({col_defs})"


def generate_drop_table_sql(table: str, if_exists: bool, cascade: bool) -> str:
    """Generate DROP TABLE SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    parts = ["DROP TABLE"]
    if if_exists:
        parts.append("IF EXISTS")
    parts.append(escape_sql_identifier(table))
    if cascade:
        parts.append("CASCADE")
    return " ".join(parts)


def generate_rename_table_sql(old_name: str, new_name: str) -> str:
    """Generate ALTER TABLE RENAME SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(old_name)} RENAME TO {escape_sql_identifier(new_name)}"


def generate_add_index_sql(index_name: str, table: str, columns: list, unique: bool, method: str) -> str:
    """Generate CREATE INDEX SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    unique_keyword = "UNIQUE " if unique else ""
    method_clause = f" USING {method}" if method else ""
    col_list = ", ".join(escape_sql_identifier(c) for c in columns)
    return f"CREATE {unique_keyword}INDEX {escape_sql_identifier(index_name)} ON {escape_sql_identifier(table)}{method_clause} ({col_list})"


def generate_drop_index_sql(index_name: str, if_exists: bool) -> str:
    """Generate DROP INDEX SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    if_exists_clause = "IF EXISTS " if if_exists else ""
    return f"DROP INDEX {if_exists_clause}{escape_sql_identifier(index_name)}"


def generate_add_constraint_sql(table: str, constraint_name: str, constraint_def: str) -> str:
    """Generate ALTER TABLE ADD CONSTRAINT SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(table)} ADD CONSTRAINT {escape_sql_identifier(constraint_name)} {constraint_def}"


def generate_drop_constraint_sql(table: str, constraint_name: str) -> str:
    """Generate ALTER TABLE DROP CONSTRAINT SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"ALTER TABLE {escape_sql_identifier(table)} DROP CONSTRAINT {escape_sql_identifier(constraint_name)}"


def generate_add_foreign_key_sql(table: str, column: str, ref_table: str, ref_column: str, constraint_name: str, on_delete: str, on_update: str) -> str:
    """Generate ALTER TABLE ADD FOREIGN KEY SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    fk_def = f"FOREIGN KEY ({escape_sql_identifier(column)}) REFERENCES {escape_sql_identifier(ref_table)}({escape_sql_identifier(ref_column)})"
    if on_delete:
        fk_def += f" ON DELETE {on_delete.upper()}"
    if on_update:
        fk_def += f" ON UPDATE {on_update.upper()}"
    return f"ALTER TABLE {escape_sql_identifier(table)} ADD CONSTRAINT {escape_sql_identifier(constraint_name)} {fk_def}"


def generate_create_schema_sql(schema_name: str, if_not_exists: bool) -> str:
    """Generate CREATE SCHEMA SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    if_clause = "IF NOT EXISTS " if if_not_exists else ""
    return f"CREATE SCHEMA {if_clause}{escape_sql_identifier(schema_name)}"


def generate_drop_schema_sql(schema_name: str, if_exists: bool, cascade: bool) -> str:
    """Generate DROP SCHEMA SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    parts = ["DROP SCHEMA"]
    if if_exists:
        parts.append("IF EXISTS")
    parts.append(escape_sql_identifier(schema_name))
    if cascade:
        parts.append("CASCADE")
    return " ".join(parts)


def generate_grant_sql(privileges: list, on_object: str, to_role: str) -> str:
    """Generate GRANT SQL."""
    privs = ", ".join(privileges)
    return f"GRANT {privs} ON {on_object} TO {to_role}"


def generate_revoke_sql(privileges: list, on_object: str, from_role: str) -> str:
    """Generate REVOKE SQL."""
    privs = ", ".join(privileges)
    return f"REVOKE {privs} ON {on_object} FROM {from_role}"


def is_reversible_migration(up_sql: str, down_sql: str) -> bool:
    """Check if a migration has both up and down SQL (is reversible)."""
    return bool(up_sql and up_sql.strip() and down_sql and down_sql.strip())


def validate_migration_sql(sql: str) -> dict:
    """Validate migration SQL and return issues."""
    issues = []
    sql_upper = sql.upper()
    if "DROP DATABASE" in sql_upper:
        issues.append("Contains DROP DATABASE which is dangerous")
    if "TRUNCATE" in sql_upper and "CASCADE" in sql_upper:
        issues.append("Contains TRUNCATE CASCADE which may delete related data")
    if sql.count(';') > 100:
        issues.append("Contains more than 100 statements, consider splitting")
    return {"valid": len(issues) == 0, "issues": issues}


def generate_migration_table_sql() -> str:
    """Generate SQL to create migrations tracking table."""
    return """CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64)
)"""


def generate_insert_migration_sql(version: str, checksum: str) -> str:
    """Generate SQL to record a migration as applied."""
    from neurop_forge.sources.sql_building import escape_sql_string
    return f"INSERT INTO schema_migrations (version, checksum) VALUES ('{escape_sql_string(version)}', '{escape_sql_string(checksum)}')"


def generate_delete_migration_sql(version: str) -> str:
    """Generate SQL to remove a migration record (for rollback)."""
    from neurop_forge.sources.sql_building import escape_sql_string
    return f"DELETE FROM schema_migrations WHERE version = '{escape_sql_string(version)}'"


def calculate_migration_checksum(sql: str) -> str:
    """Calculate a checksum for migration SQL content."""
    import hashlib
    normalized = ' '.join(sql.split()).strip()
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def detect_breaking_changes(old_columns: list, new_columns: list) -> list:
    """Detect breaking changes between column lists."""
    old_set = set(old_columns)
    new_set = set(new_columns)
    removed = old_set - new_set
    return list(removed)


def generate_backfill_sql(table: str, column: str, expression: str, batch_size: int) -> str:
    """Generate SQL for backfilling a column in batches."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"""UPDATE {escape_sql_identifier(table)} 
SET {escape_sql_identifier(column)} = {expression}
WHERE ctid IN (
    SELECT ctid FROM {escape_sql_identifier(table)}
    WHERE {escape_sql_identifier(column)} IS NULL
    LIMIT {batch_size}
)"""


def generate_data_copy_sql(from_table: str, to_table: str, columns: list) -> str:
    """Generate SQL to copy data between tables."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, build_column_list
    col_list = build_column_list(columns)
    return f"INSERT INTO {escape_sql_identifier(to_table)} ({col_list}) SELECT {col_list} FROM {escape_sql_identifier(from_table)}"


def wrap_in_transaction(sql: str) -> str:
    """Wrap SQL statements in a transaction."""
    return f"BEGIN;\n{sql}\nCOMMIT;"


def generate_concurrent_index_sql(index_name: str, table: str, columns: list, unique: bool) -> str:
    """Generate CREATE INDEX CONCURRENTLY SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    unique_keyword = "UNIQUE " if unique else ""
    col_list = ", ".join(escape_sql_identifier(c) for c in columns)
    return f"CREATE {unique_keyword}INDEX CONCURRENTLY {escape_sql_identifier(index_name)} ON {escape_sql_identifier(table)} ({col_list})"


def generate_drop_concurrent_index_sql(index_name: str) -> str:
    """Generate DROP INDEX CONCURRENTLY SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier
    return f"DROP INDEX CONCURRENTLY {escape_sql_identifier(index_name)}"


def is_safe_migration(sql: str) -> bool:
    """Check if a migration is safe (no data loss risk)."""
    sql_upper = sql.upper()
    dangerous_patterns = [
        "DROP TABLE", "DROP COLUMN", "TRUNCATE",
        "DELETE FROM", "DROP DATABASE", "DROP SCHEMA"
    ]
    return not any(pattern in sql_upper for pattern in dangerous_patterns)


def get_migration_dependencies(sql: str) -> list:
    """Extract table dependencies from migration SQL."""
    from neurop_forge.sources.query_helpers import extract_table_names
    return extract_table_names(sql)


def format_migration_file_content(version: str, description: str, up_sql: str, down_sql: str) -> str:
    """Format migration content as a structured file."""
    return f"""-- Migration: {version}
-- Description: {description}
-- Created: AUTO

-- UP
{up_sql}

-- DOWN
{down_sql}
"""


def parse_migration_file(content: str) -> dict:
    """Parse a migration file into up and down SQL."""
    import re
    up_match = re.search(r'-- UP\n(.*?)(?:-- DOWN|$)', content, re.DOTALL)
    down_match = re.search(r'-- DOWN\n(.*?)$', content, re.DOTALL)
    return {
        "up": up_match.group(1).strip() if up_match else "",
        "down": down_match.group(1).strip() if down_match else ""
    }


def generate_enum_type_sql(type_name: str, values: list) -> str:
    """Generate CREATE TYPE ... AS ENUM SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, escape_sql_string
    values_str = ", ".join(f"'{escape_sql_string(v)}'" for v in values)
    return f"CREATE TYPE {escape_sql_identifier(type_name)} AS ENUM ({values_str})"


def generate_add_enum_value_sql(type_name: str, new_value: str, after_value: str) -> str:
    """Generate ALTER TYPE ADD VALUE SQL."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, escape_sql_string
    after_clause = f" AFTER '{escape_sql_string(after_value)}'" if after_value else ""
    return f"ALTER TYPE {escape_sql_identifier(type_name)} ADD VALUE '{escape_sql_string(new_value)}'{after_clause}"


def generate_extension_sql(extension_name: str, if_not_exists: bool) -> str:
    """Generate CREATE EXTENSION SQL."""
    if_clause = "IF NOT EXISTS " if if_not_exists else ""
    return f"CREATE EXTENSION {if_clause}{extension_name}"


def generate_drop_extension_sql(extension_name: str, if_exists: bool) -> str:
    """Generate DROP EXTENSION SQL."""
    if_clause = "IF EXISTS " if if_exists else ""
    return f"DROP EXTENSION {if_clause}{extension_name}"
