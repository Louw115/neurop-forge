"""
NoSQL Helper Utilities - Pure functions for NoSQL/document database patterns.
All functions are pure, deterministic, and atomic.
"""

def build_mongodb_filter(field: str, operator: str, value) -> dict:
    """Build a MongoDB filter condition."""
    operator_map = {
        "eq": "$eq",
        "ne": "$ne",
        "gt": "$gt",
        "gte": "$gte",
        "lt": "$lt",
        "lte": "$lte",
        "in": "$in",
        "nin": "$nin",
        "exists": "$exists",
        "regex": "$regex"
    }
    mongo_op = operator_map.get(operator, "$eq")
    if operator == "eq":
        return {field: value}
    return {field: {mongo_op: value}}


def build_mongodb_and(conditions: list) -> dict:
    """Build a MongoDB $and condition."""
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def build_mongodb_or(conditions: list) -> dict:
    """Build a MongoDB $or condition."""
    if len(conditions) == 1:
        return conditions[0]
    return {"$or": conditions}


def build_mongodb_not(condition: dict) -> dict:
    """Build a MongoDB $not condition."""
    field = list(condition.keys())[0]
    value = condition[field]
    if isinstance(value, dict):
        return {field: {"$not": value}}
    return {field: {"$not": {"$eq": value}}}


def build_mongodb_projection(include_fields: list, exclude_fields: list) -> dict:
    """Build a MongoDB projection document."""
    projection = {}
    for field in include_fields:
        projection[field] = 1
    for field in exclude_fields:
        projection[field] = 0
    return projection


def build_mongodb_sort(field: str, direction: str) -> list:
    """Build a MongoDB sort specification."""
    dir_value = 1 if direction.lower() == "asc" else -1
    return [(field, dir_value)]


def build_mongodb_multi_sort(fields: list, directions: list) -> list:
    """Build a MongoDB multi-field sort specification."""
    result = []
    for i, field in enumerate(fields):
        direction = directions[i] if i < len(directions) else "asc"
        dir_value = 1 if direction.lower() == "asc" else -1
        result.append((field, dir_value))
    return result


def build_mongodb_limit_skip(limit: int, skip: int) -> dict:
    """Build MongoDB pagination parameters."""
    return {"limit": limit, "skip": skip}


def build_mongodb_update(field: str, value, operator: str) -> dict:
    """Build a MongoDB update operation."""
    operator_map = {
        "set": "$set",
        "unset": "$unset",
        "inc": "$inc",
        "push": "$push",
        "pull": "$pull",
        "addToSet": "$addToSet",
        "pop": "$pop",
        "rename": "$rename",
        "min": "$min",
        "max": "$max",
        "mul": "$mul"
    }
    mongo_op = operator_map.get(operator, "$set")
    return {mongo_op: {field: value}}


def merge_mongodb_updates(updates: list) -> dict:
    """Merge multiple MongoDB update operations."""
    result = {}
    for update in updates:
        for op, fields in update.items():
            if op not in result:
                result[op] = {}
            result[op].update(fields)
    return result


def build_mongodb_aggregate_match(conditions: dict) -> dict:
    """Build a MongoDB $match aggregation stage."""
    return {"$match": conditions}


def build_mongodb_aggregate_group(group_id, accumulators: dict) -> dict:
    """Build a MongoDB $group aggregation stage."""
    return {"$group": {"_id": group_id, **accumulators}}


def build_mongodb_aggregate_sort(sort_spec: list) -> dict:
    """Build a MongoDB $sort aggregation stage."""
    sort_dict = {field: direction for field, direction in sort_spec}
    return {"$sort": sort_dict}


def build_mongodb_aggregate_project(projection: dict) -> dict:
    """Build a MongoDB $project aggregation stage."""
    return {"$project": projection}


def build_mongodb_aggregate_limit(limit: int) -> dict:
    """Build a MongoDB $limit aggregation stage."""
    return {"$limit": limit}


def build_mongodb_aggregate_skip(skip: int) -> dict:
    """Build a MongoDB $skip aggregation stage."""
    return {"$skip": skip}


def build_mongodb_aggregate_unwind(field: str, preserve_null: bool) -> dict:
    """Build a MongoDB $unwind aggregation stage."""
    if preserve_null:
        return {"$unwind": {"path": f"${field}", "preserveNullAndEmptyArrays": True}}
    return {"$unwind": f"${field}"}


def build_mongodb_aggregate_lookup(from_collection: str, local_field: str, foreign_field: str, as_field: str) -> dict:
    """Build a MongoDB $lookup aggregation stage."""
    return {
        "$lookup": {
            "from": from_collection,
            "localField": local_field,
            "foreignField": foreign_field,
            "as": as_field
        }
    }


def build_mongodb_text_search(query: str) -> dict:
    """Build a MongoDB text search filter."""
    return {"$text": {"$search": query}}


def build_mongodb_regex_filter(field: str, pattern: str, options: str) -> dict:
    """Build a MongoDB regex filter."""
    return {field: {"$regex": pattern, "$options": options}}


def build_redis_key(prefix: str, parts: list, separator: str) -> str:
    """Build a Redis key from parts."""
    all_parts = [prefix] + [str(p) for p in parts]
    return separator.join(all_parts)


def parse_redis_key(key: str, separator: str) -> list:
    """Parse a Redis key into parts."""
    return key.split(separator)


def build_redis_hash_key(entity_type: str, entity_id: str) -> str:
    """Build a Redis hash key for an entity."""
    return f"{entity_type}:{entity_id}"


def build_redis_set_key(entity_type: str, group: str) -> str:
    """Build a Redis set key for grouping entities."""
    return f"{entity_type}:set:{group}"


def build_redis_sorted_set_key(entity_type: str, sort_field: str) -> str:
    """Build a Redis sorted set key."""
    return f"{entity_type}:zset:{sort_field}"


def build_redis_list_key(entity_type: str, list_name: str) -> str:
    """Build a Redis list key."""
    return f"{entity_type}:list:{list_name}"


def build_redis_stream_key(entity_type: str, stream_name: str) -> str:
    """Build a Redis stream key."""
    return f"{entity_type}:stream:{stream_name}"


def build_redis_lock_key(resource: str) -> str:
    """Build a Redis lock key."""
    return f"lock:{resource}"


def build_redis_rate_limit_key(identifier: str, window: str) -> str:
    """Build a Redis rate limit key."""
    return f"ratelimit:{identifier}:{window}"


def build_redis_cache_key(cache_name: str, key_parts: list) -> str:
    """Build a Redis cache key."""
    key_str = ":".join(str(p) for p in key_parts)
    return f"cache:{cache_name}:{key_str}"


def build_redis_session_key(session_id: str) -> str:
    """Build a Redis session key."""
    return f"session:{session_id}"


def build_redis_pubsub_channel(topic: str, subtopic: str) -> str:
    """Build a Redis pub/sub channel name."""
    if subtopic:
        return f"channel:{topic}:{subtopic}"
    return f"channel:{topic}"


def calculate_redis_ttl_seconds(minutes: int) -> int:
    """Calculate Redis TTL in seconds from minutes."""
    return minutes * 60


def calculate_redis_expiry_timestamp(current_timestamp: int, ttl_seconds: int) -> int:
    """Calculate Redis expiry timestamp."""
    return current_timestamp + ttl_seconds


def is_redis_key_pattern(key: str) -> bool:
    """Check if a Redis key contains pattern characters."""
    return '*' in key or '?' in key or '[' in key


def build_dynamodb_key(partition_key: str, pk_value: str, sort_key: str, sk_value: str) -> dict:
    """Build a DynamoDB key dictionary."""
    key = {partition_key: pk_value}
    if sort_key and sk_value:
        key[sort_key] = sk_value
    return key


def build_dynamodb_condition_expression(conditions: list) -> str:
    """Build a DynamoDB condition expression."""
    return " AND ".join(conditions)


def build_dynamodb_update_expression(set_fields: list, remove_fields: list) -> str:
    """Build a DynamoDB update expression."""
    parts = []
    if set_fields:
        set_expr = ", ".join(f"#{f} = :{f}" for f in set_fields)
        parts.append(f"SET {set_expr}")
    if remove_fields:
        remove_expr = ", ".join(f"#{f}" for f in remove_fields)
        parts.append(f"REMOVE {remove_expr}")
    return " ".join(parts)


def build_dynamodb_expression_names(fields: list) -> dict:
    """Build DynamoDB expression attribute names."""
    return {f"#{f}": f for f in fields}


def build_dynamodb_expression_values(field_values: dict) -> dict:
    """Build DynamoDB expression attribute values."""
    return {f":{k}": v for k, v in field_values.items()}


def build_dynamodb_query_key_condition(partition_key: str, sort_key: str, sort_operator: str) -> str:
    """Build a DynamoDB query key condition expression."""
    pk_cond = f"#{partition_key} = :{partition_key}"
    if sort_key and sort_operator:
        ops = {
            "eq": "=",
            "lt": "<",
            "lte": "<=",
            "gt": ">",
            "gte": ">=",
            "between": "BETWEEN",
            "begins_with": "begins_with"
        }
        op = ops.get(sort_operator, "=")
        if sort_operator == "between":
            sk_cond = f"#{sort_key} BETWEEN :{sort_key}_start AND :{sort_key}_end"
        elif sort_operator == "begins_with":
            sk_cond = f"begins_with(#{sort_key}, :{sort_key})"
        else:
            sk_cond = f"#{sort_key} {op} :{sort_key}"
        return f"{pk_cond} AND {sk_cond}"
    return pk_cond


def is_valid_document_id(doc_id: str) -> bool:
    """Check if a document ID is valid (alphanumeric with common separators)."""
    import re
    return bool(re.match(r'^[a-zA-Z0-9_\-:]+$', doc_id))


def generate_document_id_from_parts(parts: list) -> str:
    """Generate a document ID from multiple parts."""
    return "_".join(str(p) for p in parts)


def extract_document_id_parts(doc_id: str, separator: str) -> list:
    """Extract parts from a document ID."""
    return doc_id.split(separator)


def build_elasticsearch_match_query(field: str, query: str) -> dict:
    """Build an Elasticsearch match query."""
    return {"match": {field: query}}


def build_elasticsearch_term_query(field: str, value) -> dict:
    """Build an Elasticsearch term query."""
    return {"term": {field: value}}


def build_elasticsearch_range_query(field: str, gte, lte) -> dict:
    """Build an Elasticsearch range query."""
    range_params = {}
    if gte is not None:
        range_params["gte"] = gte
    if lte is not None:
        range_params["lte"] = lte
    return {"range": {field: range_params}}


def build_elasticsearch_bool_query(must: list, should: list, must_not: list) -> dict:
    """Build an Elasticsearch bool query."""
    bool_params = {}
    if must:
        bool_params["must"] = must
    if should:
        bool_params["should"] = should
    if must_not:
        bool_params["must_not"] = must_not
    return {"bool": bool_params}


def build_elasticsearch_aggs(agg_name: str, agg_type: str, field: str) -> dict:
    """Build an Elasticsearch aggregation."""
    return {agg_name: {agg_type: {"field": field}}}


def format_json_path(path_parts: list) -> str:
    """Format a JSON path from parts."""
    result = "$"
    for part in path_parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}"
    return result


def parse_json_path(path: str) -> list:
    """Parse a JSON path into parts."""
    import re
    if not path.startswith("$"):
        return []
    parts = []
    for match in re.finditer(r'\.([a-zA-Z_][a-zA-Z0-9_]*)|\[(\d+)\]', path):
        if match.group(1):
            parts.append(match.group(1))
        else:
            parts.append(int(match.group(2)))
    return parts


def get_nested_value(data: dict, path_parts: list, default):
    """Get a nested value from a document using path parts."""
    current = data
    for part in path_parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and isinstance(part, int) and 0 <= part < len(current):
            current = current[part]
        else:
            return default
    return current


def set_nested_value(data: dict, path_parts: list, value) -> dict:
    """Set a nested value in a document (returns new dict)."""
    if not path_parts:
        return data
    result = dict(data)
    current = result
    for i, part in enumerate(path_parts[:-1]):
        if isinstance(current, dict):
            if part not in current:
                next_part = path_parts[i + 1]
                current[part] = [] if isinstance(next_part, int) else {}
            current = current[part]
    if path_parts:
        current[path_parts[-1]] = value
    return result
