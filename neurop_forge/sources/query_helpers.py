"""
Query Helper Utilities - Pure functions for query manipulation and analysis.
All functions are pure, deterministic, and atomic.
"""

def normalize_whitespace(query: str) -> str:
    """Normalize whitespace in a SQL query (collapse multiple spaces)."""
    return ' '.join(query.split())


def remove_comments(query: str) -> str:
    """Remove SQL comments from a query."""
    import re
    query = re.sub(r'--[^\n]*', '', query)
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
    return query.strip()


def extract_query_type(query: str) -> str:
    """Extract the type of SQL query (SELECT, INSERT, UPDATE, DELETE, etc.)."""
    cleaned = remove_comments(query).strip().upper()
    keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", 
                "ALTER", "TRUNCATE", "GRANT", "REVOKE", "WITH"]
    for keyword in keywords:
        if cleaned.startswith(keyword):
            return keyword
    return "UNKNOWN"


def is_select_query(query: str) -> bool:
    """Check if a query is a SELECT query."""
    return extract_query_type(query) == "SELECT"


def is_mutating_query(query: str) -> bool:
    """Check if a query mutates data (INSERT, UPDATE, DELETE)."""
    return extract_query_type(query) in ("INSERT", "UPDATE", "DELETE", "TRUNCATE")


def is_ddl_query(query: str) -> bool:
    """Check if a query is a DDL statement (CREATE, DROP, ALTER)."""
    return extract_query_type(query) in ("CREATE", "DROP", "ALTER")


def count_query_statements(sql: str) -> int:
    """Count the number of statements in a SQL string."""
    cleaned = remove_comments(sql)
    statements = [s.strip() for s in cleaned.split(';') if s.strip()]
    return len(statements)


def split_query_statements(sql: str) -> list:
    """Split a SQL string into individual statements."""
    cleaned = remove_comments(sql)
    statements = [s.strip() for s in cleaned.split(';') if s.strip()]
    return statements


def extract_column_names(select_query: str) -> list:
    """Extract column names from a SELECT query (simple cases only)."""
    import re
    match = re.search(r'SELECT\s+(.*?)\s+FROM', select_query, re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    columns_str = match.group(1)
    if columns_str.strip() == '*':
        return ['*']
    columns = []
    for col in columns_str.split(','):
        col = col.strip()
        as_match = re.search(r'\bAS\s+["\']?(\w+)["\']?\s*$', col, re.IGNORECASE)
        if as_match:
            columns.append(as_match.group(1))
        else:
            parts = col.split('.')
            columns.append(parts[-1].strip('"').strip("'").strip())
    return columns


def has_where_clause(query: str) -> bool:
    """Check if a query has a WHERE clause."""
    return bool(re.search(r'\bWHERE\b', query, re.IGNORECASE))


def has_order_by(query: str) -> bool:
    """Check if a query has an ORDER BY clause."""
    import re
    return bool(re.search(r'\bORDER\s+BY\b', query, re.IGNORECASE))


def has_group_by(query: str) -> bool:
    """Check if a query has a GROUP BY clause."""
    import re
    return bool(re.search(r'\bGROUP\s+BY\b', query, re.IGNORECASE))


def has_having(query: str) -> bool:
    """Check if a query has a HAVING clause."""
    import re
    return bool(re.search(r'\bHAVING\b', query, re.IGNORECASE))


def has_join(query: str) -> bool:
    """Check if a query has any JOIN clause."""
    import re
    return bool(re.search(r'\bJOIN\b', query, re.IGNORECASE))


def has_subquery(query: str) -> bool:
    """Check if a query contains a subquery."""
    import re
    query_no_strings = re.sub(r"'[^']*'", '', query)
    paren_content = re.findall(r'\([^()]+\)', query_no_strings)
    for content in paren_content:
        if re.search(r'\bSELECT\b', content, re.IGNORECASE):
            return True
    return False


def has_limit(query: str) -> bool:
    """Check if a query has a LIMIT clause."""
    import re
    return bool(re.search(r'\bLIMIT\b', query, re.IGNORECASE))


def has_offset(query: str) -> bool:
    """Check if a query has an OFFSET clause."""
    import re
    return bool(re.search(r'\bOFFSET\b', query, re.IGNORECASE))


def has_distinct(query: str) -> bool:
    """Check if a query has DISTINCT."""
    import re
    return bool(re.search(r'\bDISTINCT\b', query, re.IGNORECASE))


def has_union(query: str) -> bool:
    """Check if a query has UNION."""
    import re
    return bool(re.search(r'\bUNION\b', query, re.IGNORECASE))


def has_cte(query: str) -> bool:
    """Check if a query uses a Common Table Expression (WITH clause)."""
    import re
    return bool(re.search(r'^\s*WITH\b', query, re.IGNORECASE))


def has_returning(query: str) -> bool:
    """Check if a query has a RETURNING clause."""
    import re
    return bool(re.search(r'\bRETURNING\b', query, re.IGNORECASE))


def has_window_function(query: str) -> bool:
    """Check if a query uses window functions."""
    import re
    window_funcs = r'\b(ROW_NUMBER|RANK|DENSE_RANK|NTILE|LAG|LEAD|FIRST_VALUE|LAST_VALUE|NTH_VALUE)\s*\('
    return bool(re.search(window_funcs, query, re.IGNORECASE)) or bool(re.search(r'\bOVER\s*\(', query, re.IGNORECASE))


def has_aggregate_function(query: str) -> bool:
    """Check if a query uses aggregate functions."""
    import re
    agg_funcs = r'\b(COUNT|SUM|AVG|MIN|MAX|ARRAY_AGG|STRING_AGG|BOOL_AND|BOOL_OR)\s*\('
    return bool(re.search(agg_funcs, query, re.IGNORECASE))


def estimate_query_complexity(query: str) -> str:
    """Estimate the complexity of a query (simple, medium, complex)."""
    score = 0
    if has_join(query):
        score += 2
    if has_subquery(query):
        score += 3
    if has_window_function(query):
        score += 2
    if has_cte(query):
        score += 2
    if has_group_by(query):
        score += 1
    if has_having(query):
        score += 1
    if has_union(query):
        score += 2
    if score <= 2:
        return "simple"
    if score <= 5:
        return "medium"
    return "complex"


def add_limit_to_query(query: str, limit: int) -> str:
    """Add a LIMIT clause to a query if not present."""
    if has_limit(query):
        return query
    return f"{query.rstrip().rstrip(';')} LIMIT {limit}"


def add_offset_to_query(query: str, offset: int) -> str:
    """Add an OFFSET clause to a query if not present."""
    if has_offset(query):
        return query
    return f"{query.rstrip().rstrip(';')} OFFSET {offset}"


def wrap_in_count(query: str) -> str:
    """Wrap a SELECT query in COUNT(*) to get row count."""
    cleaned = query.rstrip().rstrip(';')
    return f"SELECT COUNT(*) FROM ({cleaned}) AS count_subquery"


def wrap_in_exists(query: str) -> str:
    """Wrap a query in EXISTS to check for rows."""
    cleaned = query.rstrip().rstrip(';')
    return f"SELECT EXISTS ({cleaned})"


def remove_order_by(query: str) -> str:
    """Remove ORDER BY clause from a query."""
    import re
    return re.sub(r'\s+ORDER\s+BY\s+[^;]*?(?=\s+LIMIT|\s+OFFSET|\s+FOR|\s*;|\s*$)', '', query, flags=re.IGNORECASE)


def remove_limit_offset(query: str) -> str:
    """Remove LIMIT and OFFSET clauses from a query."""
    import re
    query = re.sub(r'\s+LIMIT\s+\d+', '', query, flags=re.IGNORECASE)
    query = re.sub(r'\s+OFFSET\s+\d+', '', query, flags=re.IGNORECASE)
    return query


def extract_table_names(query: str) -> list:
    """Extract all table names from a query."""
    import re
    tables = set()
    from_matches = re.findall(r'\bFROM\s+([^\s,;()]+)', query, re.IGNORECASE)
    tables.update(from_matches)
    join_matches = re.findall(r'\bJOIN\s+([^\s,;()]+)', query, re.IGNORECASE)
    tables.update(join_matches)
    into_matches = re.findall(r'\bINTO\s+([^\s,;()]+)', query, re.IGNORECASE)
    tables.update(into_matches)
    update_matches = re.findall(r'\bUPDATE\s+([^\s,;()]+)', query, re.IGNORECASE)
    tables.update(update_matches)
    cleaned = {t.strip('"').strip("'") for t in tables}
    keywords = {"SELECT", "SET", "VALUES", "WHERE", "AND", "OR"}
    return [t for t in cleaned if t.upper() not in keywords]


def extract_where_conditions(query: str) -> str:
    """Extract the WHERE clause content from a query."""
    import re
    match = re.search(r'\bWHERE\s+(.*?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+HAVING|\s+LIMIT|\s+OFFSET|\s*;|\s*$)', 
                      query, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def combine_where_conditions(conditions: list, operator: str) -> str:
    """Combine multiple WHERE conditions with AND or OR."""
    if not conditions:
        return ""
    if len(conditions) == 1:
        return conditions[0]
    op = operator.upper() if operator.upper() in ("AND", "OR") else "AND"
    return f" {op} ".join(f"({c})" for c in conditions)


def is_parameterized_query(query: str) -> bool:
    """Check if a query uses parameterized placeholders."""
    import re
    return bool(re.search(r'\$\d+|:\w+|%s|\?', query))


def validate_placeholder_count(query: str, param_count: int) -> bool:
    """Validate that the number of placeholders matches parameter count."""
    import re
    dollar_placeholders = re.findall(r'\$(\d+)', query)
    if dollar_placeholders:
        max_placeholder = max(int(p) for p in dollar_placeholders)
        return max_placeholder == param_count
    question_marks = query.count('?')
    if question_marks > 0:
        return question_marks == param_count
    percent_s = query.count('%s')
    if percent_s > 0:
        return percent_s == param_count
    return param_count == 0


def format_in_clause_values(values: list) -> str:
    """Format a list of values for an IN clause (with proper quoting)."""
    formatted = []
    for v in values:
        if isinstance(v, str):
            escaped = v.replace("'", "''")
            formatted.append(f"'{escaped}'")
        elif v is None:
            formatted.append("NULL")
        elif isinstance(v, bool):
            formatted.append("TRUE" if v else "FALSE")
        else:
            formatted.append(str(v))
    return ", ".join(formatted)


def is_read_only_query(query: str) -> bool:
    """Check if a query is read-only (SELECT without FOR UPDATE)."""
    query_type = extract_query_type(query)
    if query_type != "SELECT":
        return False
    import re
    return not bool(re.search(r'\bFOR\s+(UPDATE|SHARE)\b', query, re.IGNORECASE))


def has_for_update(query: str) -> bool:
    """Check if a query has FOR UPDATE clause."""
    import re
    return bool(re.search(r'\bFOR\s+UPDATE\b', query, re.IGNORECASE))


def add_for_update(query: str) -> str:
    """Add FOR UPDATE to a SELECT query."""
    if not is_select_query(query) or has_for_update(query):
        return query
    return f"{query.rstrip().rstrip(';')} FOR UPDATE"


def add_for_share(query: str) -> str:
    """Add FOR SHARE to a SELECT query."""
    import re
    if not is_select_query(query) or re.search(r'\bFOR\s+SHARE\b', query, re.IGNORECASE):
        return query
    return f"{query.rstrip().rstrip(';')} FOR SHARE"


def add_nowait(query: str) -> str:
    """Add NOWAIT to a FOR UPDATE/SHARE query."""
    import re
    if not re.search(r'\bFOR\s+(UPDATE|SHARE)\b', query, re.IGNORECASE):
        return query
    return f"{query.rstrip().rstrip(';')} NOWAIT"


def add_skip_locked(query: str) -> str:
    """Add SKIP LOCKED to a FOR UPDATE/SHARE query."""
    import re
    if not re.search(r'\bFOR\s+(UPDATE|SHARE)\b', query, re.IGNORECASE):
        return query
    return f"{query.rstrip().rstrip(';')} SKIP LOCKED"


def estimate_result_columns(query: str) -> int:
    """Estimate the number of result columns from a SELECT query."""
    import re
    if not is_select_query(query):
        return 0
    match = re.search(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
    if not match:
        return 0
    columns_str = match.group(1)
    if columns_str.strip() == '*':
        return -1
    depth = 0
    count = 1
    for char in columns_str:
        if char in '([':
            depth += 1
        elif char in ')]':
            depth -= 1
        elif char == ',' and depth == 0:
            count += 1
    return count


def get_query_tables_with_aliases(query: str) -> dict:
    """Extract tables with their aliases from a query."""
    import re
    result = {}
    patterns = [
        r'\bFROM\s+([^\s,;()]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?',
        r'\bJOIN\s+([^\s,;()]+)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        for table, alias in matches:
            clean_table = table.strip('"').strip("'")
            if clean_table.upper() not in ("SELECT", "ON", "AND", "OR", "WHERE"):
                result[clean_table] = alias if alias else clean_table
    return result


def is_safe_identifier(name: str) -> bool:
    """Check if a name is safe to use as a SQL identifier without escaping."""
    import re
    if not name or not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        return False
    reserved = {"SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "TABLE", "INDEX", "CREATE", "DROP"}
    return name.upper() not in reserved


def quote_identifier_if_needed(name: str) -> str:
    """Quote an identifier only if it contains special characters or is reserved."""
    if is_safe_identifier(name):
        return name
    return '"' + name.replace('"', '""') + '"'


def build_pagination_query(base_query: str, limit: int, offset: int) -> str:
    """Add pagination (LIMIT/OFFSET) to a query."""
    cleaned = remove_limit_offset(base_query).rstrip().rstrip(';')
    return f"{cleaned} LIMIT {limit} OFFSET {offset}"


def build_keyset_pagination_condition(column: str, last_value: str, direction: str) -> str:
    """Build a keyset pagination condition (WHERE id > last_id)."""
    from neurop_forge.sources.sql_building import escape_sql_identifier, escape_sql_string
    dir_upper = direction.upper()
    op = ">" if dir_upper == "ASC" else "<"
    escaped_value = escape_sql_string(last_value)
    return f"{escape_sql_identifier(column)} {op} '{escaped_value}'"


def extract_limit_value(query: str) -> int:
    """Extract the LIMIT value from a query."""
    import re
    match = re.search(r'\bLIMIT\s+(\d+)', query, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def extract_offset_value(query: str) -> int:
    """Extract the OFFSET value from a query."""
    import re
    match = re.search(r'\bOFFSET\s+(\d+)', query, re.IGNORECASE)
    return int(match.group(1)) if match else 0


import re
