"""
SQL Building Utilities - Pure functions for constructing SQL query components.
All functions are pure, deterministic, and atomic.
No actual database connections - just SQL string/structure manipulation.
"""

def escape_sql_string(value: str) -> str:
    """Escape a string for safe SQL inclusion (single quotes)."""
    return value.replace("'", "''")


def escape_sql_identifier(name: str) -> str:
    """Escape a SQL identifier (table/column name) with double quotes."""
    return '"' + name.replace('"', '""') + '"'


def escape_sql_like(pattern: str) -> str:
    """Escape special characters in a LIKE pattern."""
    return pattern.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def build_placeholder_list(count: int, start: int) -> str:
    """Build a comma-separated list of numbered placeholders ($1, $2, ...)."""
    if count <= 0:
        return ""
    return ", ".join(f"${i}" for i in range(start, start + count))


def build_named_placeholder_list(names: list) -> str:
    """Build a comma-separated list of named placeholders (:name)."""
    return ", ".join(f":{name}" for name in names)


def build_column_list(columns: list) -> str:
    """Build a comma-separated list of escaped column names."""
    return ", ".join(escape_sql_identifier(col) for col in columns)


def build_insert_columns(columns: list) -> str:
    """Build the column portion of an INSERT statement."""
    return "(" + build_column_list(columns) + ")"


def build_insert_values_placeholders(column_count: int, row_count: int) -> str:
    """Build VALUES placeholders for multi-row INSERT."""
    if column_count <= 0 or row_count <= 0:
        return ""
    rows = []
    placeholder_num = 1
    for _ in range(row_count):
        row_placeholders = ", ".join(f"${i}" for i in range(placeholder_num, placeholder_num + column_count))
        rows.append(f"({row_placeholders})")
        placeholder_num += column_count
    return ", ".join(rows)


def build_update_set_clause(columns: list, start_placeholder: int) -> str:
    """Build the SET clause for an UPDATE statement."""
    parts = []
    for i, col in enumerate(columns):
        parts.append(f"{escape_sql_identifier(col)} = ${start_placeholder + i}")
    return ", ".join(parts)


def build_where_equals(column: str, placeholder_num: int) -> str:
    """Build a WHERE clause for equality check."""
    return f"WHERE {escape_sql_identifier(column)} = ${placeholder_num}"


def build_where_in(column: str, count: int, start_placeholder: int) -> str:
    """Build a WHERE ... IN clause."""
    if count <= 0:
        return f"WHERE 1 = 0"
    placeholders = ", ".join(f"${i}" for i in range(start_placeholder, start_placeholder + count))
    return f"WHERE {escape_sql_identifier(column)} IN ({placeholders})"


def build_where_between(column: str, start_placeholder: int) -> str:
    """Build a WHERE ... BETWEEN clause."""
    return f"WHERE {escape_sql_identifier(column)} BETWEEN ${start_placeholder} AND ${start_placeholder + 1}"


def build_where_like(column: str, placeholder_num: int) -> str:
    """Build a WHERE ... LIKE clause."""
    return f"WHERE {escape_sql_identifier(column)} LIKE ${placeholder_num}"


def build_where_ilike(column: str, placeholder_num: int) -> str:
    """Build a WHERE ... ILIKE clause (case-insensitive)."""
    return f"WHERE {escape_sql_identifier(column)} ILIKE ${placeholder_num}"


def build_where_null(column: str) -> str:
    """Build a WHERE ... IS NULL clause."""
    return f"WHERE {escape_sql_identifier(column)} IS NULL"


def build_where_not_null(column: str) -> str:
    """Build a WHERE ... IS NOT NULL clause."""
    return f"WHERE {escape_sql_identifier(column)} IS NOT NULL"


def build_order_by(columns: list, directions: list) -> str:
    """Build an ORDER BY clause with directions (ASC/DESC)."""
    if not columns:
        return ""
    parts = []
    for i, col in enumerate(columns):
        direction = directions[i].upper() if i < len(directions) else "ASC"
        if direction not in ("ASC", "DESC"):
            direction = "ASC"
        parts.append(f"{escape_sql_identifier(col)} {direction}")
    return "ORDER BY " + ", ".join(parts)


def build_limit_offset(limit: int, offset: int) -> str:
    """Build a LIMIT ... OFFSET clause."""
    parts = []
    if limit > 0:
        parts.append(f"LIMIT {limit}")
    if offset > 0:
        parts.append(f"OFFSET {offset}")
    return " ".join(parts)


def build_select_query(table: str, columns: list) -> str:
    """Build a basic SELECT query."""
    col_list = build_column_list(columns) if columns else "*"
    return f"SELECT {col_list} FROM {escape_sql_identifier(table)}"


def build_count_query(table: str, column: str) -> str:
    """Build a COUNT query."""
    if column == "*":
        return f"SELECT COUNT(*) FROM {escape_sql_identifier(table)}"
    return f"SELECT COUNT({escape_sql_identifier(column)}) FROM {escape_sql_identifier(table)}"


def build_distinct_query(table: str, column: str) -> str:
    """Build a SELECT DISTINCT query."""
    return f"SELECT DISTINCT {escape_sql_identifier(column)} FROM {escape_sql_identifier(table)}"


def build_insert_query(table: str, columns: list) -> str:
    """Build an INSERT query with placeholders."""
    col_list = build_insert_columns(columns)
    placeholders = "(" + build_placeholder_list(len(columns), 1) + ")"
    return f"INSERT INTO {escape_sql_identifier(table)} {col_list} VALUES {placeholders}"


def build_insert_returning(table: str, columns: list, returning_columns: list) -> str:
    """Build an INSERT ... RETURNING query."""
    base = build_insert_query(table, columns)
    ret_cols = build_column_list(returning_columns) if returning_columns else "*"
    return f"{base} RETURNING {ret_cols}"


def build_update_query(table: str, set_columns: list, where_column: str) -> str:
    """Build an UPDATE query with WHERE clause."""
    set_clause = build_update_set_clause(set_columns, 1)
    where_placeholder = len(set_columns) + 1
    return f"UPDATE {escape_sql_identifier(table)} SET {set_clause} WHERE {escape_sql_identifier(where_column)} = ${where_placeholder}"


def build_delete_query(table: str, where_column: str) -> str:
    """Build a DELETE query with WHERE clause."""
    return f"DELETE FROM {escape_sql_identifier(table)} WHERE {escape_sql_identifier(where_column)} = $1"


def build_upsert_query(table: str, columns: list, conflict_column: str, update_columns: list) -> str:
    """Build an INSERT ... ON CONFLICT DO UPDATE query."""
    insert_part = build_insert_query(table, columns)
    update_parts = []
    for col in update_columns:
        update_parts.append(f"{escape_sql_identifier(col)} = EXCLUDED.{escape_sql_identifier(col)}")
    update_clause = ", ".join(update_parts)
    return f"{insert_part} ON CONFLICT ({escape_sql_identifier(conflict_column)}) DO UPDATE SET {update_clause}"


def build_join_clause(join_type: str, table: str, left_col: str, right_col: str) -> str:
    """Build a JOIN clause."""
    valid_types = ("INNER", "LEFT", "RIGHT", "FULL", "CROSS")
    jt = join_type.upper() if join_type.upper() in valid_types else "INNER"
    return f"{jt} JOIN {escape_sql_identifier(table)} ON {escape_sql_identifier(left_col)} = {escape_sql_identifier(right_col)}"


def build_left_join(table: str, left_col: str, right_col: str) -> str:
    """Build a LEFT JOIN clause."""
    return build_join_clause("LEFT", table, left_col, right_col)


def build_inner_join(table: str, left_col: str, right_col: str) -> str:
    """Build an INNER JOIN clause."""
    return build_join_clause("INNER", table, left_col, right_col)


def build_group_by(columns: list) -> str:
    """Build a GROUP BY clause."""
    if not columns:
        return ""
    return "GROUP BY " + ", ".join(escape_sql_identifier(col) for col in columns)


def build_having(condition: str) -> str:
    """Build a HAVING clause with a condition string."""
    return f"HAVING {condition}"


def build_union(query1: str, query2: str, all_rows: bool) -> str:
    """Build a UNION or UNION ALL query."""
    union_type = "UNION ALL" if all_rows else "UNION"
    return f"({query1}) {union_type} ({query2})"


def build_cte(name: str, query: str) -> str:
    """Build a Common Table Expression (WITH clause)."""
    return f"WITH {escape_sql_identifier(name)} AS ({query})"


def build_exists_subquery(subquery: str) -> str:
    """Build an EXISTS subquery condition."""
    return f"EXISTS ({subquery})"


def build_not_exists_subquery(subquery: str) -> str:
    """Build a NOT EXISTS subquery condition."""
    return f"NOT EXISTS ({subquery})"


def build_case_when(conditions: list, values: list, else_value: str) -> str:
    """Build a CASE WHEN expression."""
    if not conditions or len(conditions) != len(values):
        return else_value
    parts = ["CASE"]
    for cond, val in zip(conditions, values):
        parts.append(f"WHEN {cond} THEN {val}")
    if else_value:
        parts.append(f"ELSE {else_value}")
    parts.append("END")
    return " ".join(parts)


def build_coalesce(columns: list) -> str:
    """Build a COALESCE expression."""
    return f"COALESCE({', '.join(escape_sql_identifier(col) for col in columns)})"


def build_nullif(col1: str, col2: str) -> str:
    """Build a NULLIF expression."""
    return f"NULLIF({escape_sql_identifier(col1)}, {escape_sql_identifier(col2)})"


def build_cast(column: str, target_type: str) -> str:
    """Build a CAST expression."""
    return f"CAST({escape_sql_identifier(column)} AS {target_type})"


def build_aggregate(func: str, column: str) -> str:
    """Build an aggregate function call (SUM, AVG, MIN, MAX, etc.)."""
    valid_funcs = ("SUM", "AVG", "MIN", "MAX", "COUNT", "ARRAY_AGG", "STRING_AGG")
    f = func.upper() if func.upper() in valid_funcs else "COUNT"
    if column == "*":
        return f"{f}(*)"
    return f"{f}({escape_sql_identifier(column)})"


def build_alias(expression: str, alias: str) -> str:
    """Build an expression with an alias."""
    return f"{expression} AS {escape_sql_identifier(alias)}"


def build_table_alias(table: str, alias: str) -> str:
    """Build a table reference with an alias."""
    return f"{escape_sql_identifier(table)} AS {escape_sql_identifier(alias)}"


def build_qualified_column(table_alias: str, column: str) -> str:
    """Build a fully qualified column reference (table.column)."""
    return f"{escape_sql_identifier(table_alias)}.{escape_sql_identifier(column)}"


def is_valid_sql_identifier(name: str) -> bool:
    """Check if a string is a valid SQL identifier (alphanumeric + underscore, starts with letter)."""
    if not name or not name[0].isalpha():
        return False
    return all(c.isalnum() or c == '_' for c in name)


def is_reserved_sql_word(word: str) -> bool:
    """Check if a word is a SQL reserved keyword."""
    reserved = {
        "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP",
        "ALTER", "TABLE", "INDEX", "VIEW", "DATABASE", "SCHEMA", "GRANT", "REVOKE",
        "AND", "OR", "NOT", "NULL", "TRUE", "FALSE", "IN", "BETWEEN", "LIKE",
        "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "JOIN", "LEFT",
        "RIGHT", "INNER", "OUTER", "FULL", "CROSS", "ON", "AS", "DISTINCT",
        "ALL", "ANY", "EXISTS", "CASE", "WHEN", "THEN", "ELSE", "END", "UNION",
        "INTERSECT", "EXCEPT", "VALUES", "SET", "INTO", "RETURNING", "WITH",
        "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "UNIQUE", "CHECK", "DEFAULT",
        "CONSTRAINT", "CASCADE", "RESTRICT", "NULLS", "FIRST", "LAST", "ASC", "DESC"
    }
    return word.upper() in reserved


def sanitize_table_name(name: str) -> str:
    """Sanitize a table name by removing invalid characters."""
    sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized
    return sanitized.lower()


def sanitize_column_name(name: str) -> str:
    """Sanitize a column name by removing invalid characters."""
    return sanitize_table_name(name)


def build_create_table_column(name: str, data_type: str, nullable: bool, default: str) -> str:
    """Build a column definition for CREATE TABLE."""
    parts = [escape_sql_identifier(name), data_type]
    if not nullable:
        parts.append("NOT NULL")
    if default:
        parts.append(f"DEFAULT {default}")
    return " ".join(parts)


def build_primary_key_constraint(columns: list) -> str:
    """Build a PRIMARY KEY constraint."""
    col_list = ", ".join(escape_sql_identifier(col) for col in columns)
    return f"PRIMARY KEY ({col_list})"


def build_foreign_key_constraint(column: str, ref_table: str, ref_column: str) -> str:
    """Build a FOREIGN KEY constraint."""
    return f"FOREIGN KEY ({escape_sql_identifier(column)}) REFERENCES {escape_sql_identifier(ref_table)}({escape_sql_identifier(ref_column)})"


def build_unique_constraint(columns: list) -> str:
    """Build a UNIQUE constraint."""
    col_list = ", ".join(escape_sql_identifier(col) for col in columns)
    return f"UNIQUE ({col_list})"


def build_check_constraint(name: str, condition: str) -> str:
    """Build a CHECK constraint."""
    return f"CONSTRAINT {escape_sql_identifier(name)} CHECK ({condition})"


def build_create_index(index_name: str, table: str, columns: list, unique: bool) -> str:
    """Build a CREATE INDEX statement."""
    unique_keyword = "UNIQUE " if unique else ""
    col_list = ", ".join(escape_sql_identifier(col) for col in columns)
    return f"CREATE {unique_keyword}INDEX {escape_sql_identifier(index_name)} ON {escape_sql_identifier(table)} ({col_list})"


def build_drop_index(index_name: str, if_exists: bool) -> str:
    """Build a DROP INDEX statement."""
    if_exists_clause = "IF EXISTS " if if_exists else ""
    return f"DROP INDEX {if_exists_clause}{escape_sql_identifier(index_name)}"


def build_drop_table(table: str, if_exists: bool, cascade: bool) -> str:
    """Build a DROP TABLE statement."""
    if_exists_clause = "IF EXISTS " if if_exists else ""
    cascade_clause = " CASCADE" if cascade else ""
    return f"DROP TABLE {if_exists_clause}{escape_sql_identifier(table)}{cascade_clause}"


def build_truncate_table(table: str, restart_identity: bool) -> str:
    """Build a TRUNCATE TABLE statement."""
    restart_clause = " RESTART IDENTITY" if restart_identity else ""
    return f"TRUNCATE TABLE {escape_sql_identifier(table)}{restart_clause}"


def build_alter_add_column(table: str, column_def: str) -> str:
    """Build an ALTER TABLE ADD COLUMN statement."""
    return f"ALTER TABLE {escape_sql_identifier(table)} ADD COLUMN {column_def}"


def build_alter_drop_column(table: str, column: str) -> str:
    """Build an ALTER TABLE DROP COLUMN statement."""
    return f"ALTER TABLE {escape_sql_identifier(table)} DROP COLUMN {escape_sql_identifier(column)}"


def build_alter_rename_column(table: str, old_name: str, new_name: str) -> str:
    """Build an ALTER TABLE RENAME COLUMN statement."""
    return f"ALTER TABLE {escape_sql_identifier(table)} RENAME COLUMN {escape_sql_identifier(old_name)} TO {escape_sql_identifier(new_name)}"


def build_alter_rename_table(old_name: str, new_name: str) -> str:
    """Build an ALTER TABLE RENAME statement."""
    return f"ALTER TABLE {escape_sql_identifier(old_name)} RENAME TO {escape_sql_identifier(new_name)}"


def build_comment_on_table(table: str, comment: str) -> str:
    """Build a COMMENT ON TABLE statement."""
    escaped_comment = escape_sql_string(comment)
    return f"COMMENT ON TABLE {escape_sql_identifier(table)} IS '{escaped_comment}'"


def build_comment_on_column(table: str, column: str, comment: str) -> str:
    """Build a COMMENT ON COLUMN statement."""
    escaped_comment = escape_sql_string(comment)
    return f"COMMENT ON COLUMN {escape_sql_identifier(table)}.{escape_sql_identifier(column)} IS '{escaped_comment}'"


def extract_table_name(query: str) -> str:
    """Extract the main table name from a simple SQL query."""
    query_upper = query.upper()
    if "FROM" in query_upper:
        parts = query.split()
        try:
            from_idx = [p.upper() for p in parts].index("FROM")
            if from_idx + 1 < len(parts):
                table = parts[from_idx + 1]
                return table.strip('"').strip("'").strip()
        except ValueError:
            pass
    if "INTO" in query_upper:
        parts = query.split()
        try:
            into_idx = [p.upper() for p in parts].index("INTO")
            if into_idx + 1 < len(parts):
                table = parts[into_idx + 1]
                return table.strip('"').strip("'").strip()
        except ValueError:
            pass
    return ""


def count_placeholders(query: str) -> int:
    """Count the number of positional placeholders ($1, $2, ...) in a query."""
    import re
    matches = re.findall(r'\$(\d+)', query)
    if not matches:
        return 0
    return max(int(m) for m in matches)


def count_named_placeholders(query: str) -> int:
    """Count the number of named placeholders (:name) in a query."""
    import re
    matches = re.findall(r':([a-zA-Z_][a-zA-Z0-9_]*)', query)
    return len(set(matches))


def replace_placeholder_style(query: str, from_style: str, to_style: str) -> str:
    """Replace placeholder style (%s to $n or vice versa)."""
    import re
    if from_style == "%s" and to_style == "$n":
        count = [0]
        def replacer(match):
            count[0] += 1
            return f"${count[0]}"
        return re.sub(r'%s', replacer, query)
    elif from_style == "$n" and to_style == "%s":
        return re.sub(r'\$\d+', '%s', query)
    return query


def build_batch_insert_query(table: str, columns: list, row_count: int) -> str:
    """Build a batch INSERT query for multiple rows."""
    col_list = build_insert_columns(columns)
    values = build_insert_values_placeholders(len(columns), row_count)
    return f"INSERT INTO {escape_sql_identifier(table)} {col_list} VALUES {values}"


def build_conditional_where(conditions: list, operators: list) -> str:
    """Build a WHERE clause with multiple conditions joined by AND/OR."""
    if not conditions:
        return ""
    if len(conditions) == 1:
        return f"WHERE {conditions[0]}"
    parts = [conditions[0]]
    for i, cond in enumerate(conditions[1:]):
        op = operators[i].upper() if i < len(operators) else "AND"
        if op not in ("AND", "OR"):
            op = "AND"
        parts.append(f"{op} {cond}")
    return "WHERE " + " ".join(parts)


def build_subquery(query: str, alias: str) -> str:
    """Wrap a query as a subquery with an alias."""
    return f"({query}) AS {escape_sql_identifier(alias)}"


def build_lateral_join(subquery: str, alias: str) -> str:
    """Build a LATERAL join clause."""
    return f"CROSS JOIN LATERAL ({subquery}) AS {escape_sql_identifier(alias)}"


def build_window_function(func: str, column: str, partition_by: list, order_by: list) -> str:
    """Build a window function expression."""
    base = build_aggregate(func, column) if column else func
    parts = []
    if partition_by:
        parts.append("PARTITION BY " + ", ".join(escape_sql_identifier(c) for c in partition_by))
    if order_by:
        parts.append("ORDER BY " + ", ".join(escape_sql_identifier(c) for c in order_by))
    window_clause = " ".join(parts)
    return f"{base} OVER ({window_clause})"


def build_row_number(partition_by: list, order_by: list) -> str:
    """Build a ROW_NUMBER() window function."""
    return build_window_function("ROW_NUMBER()", "", partition_by, order_by)


def build_rank(partition_by: list, order_by: list) -> str:
    """Build a RANK() window function."""
    return build_window_function("RANK()", "", partition_by, order_by)


def build_dense_rank(partition_by: list, order_by: list) -> str:
    """Build a DENSE_RANK() window function."""
    return build_window_function("DENSE_RANK()", "", partition_by, order_by)


def build_lag(column: str, offset: int, default: str, partition_by: list, order_by: list) -> str:
    """Build a LAG() window function."""
    func = f"LAG({escape_sql_identifier(column)}, {offset}, {default})"
    return build_window_function(func, "", partition_by, order_by)


def build_lead(column: str, offset: int, default: str, partition_by: list, order_by: list) -> str:
    """Build a LEAD() window function."""
    func = f"LEAD({escape_sql_identifier(column)}, {offset}, {default})"
    return build_window_function(func, "", partition_by, order_by)


def build_first_value(column: str, partition_by: list, order_by: list) -> str:
    """Build a FIRST_VALUE() window function."""
    func = f"FIRST_VALUE({escape_sql_identifier(column)})"
    return build_window_function(func, "", partition_by, order_by)


def build_last_value(column: str, partition_by: list, order_by: list) -> str:
    """Build a LAST_VALUE() window function."""
    func = f"LAST_VALUE({escape_sql_identifier(column)})"
    return build_window_function(func, "", partition_by, order_by)
