"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
API Pattern Utilities - Pure functions for REST/HTTP API patterns.
All functions are pure, deterministic, and atomic.
"""

def build_rest_endpoint(base_path: str, resource: str, resource_id: str, action: str) -> str:
    """Build a RESTful endpoint path."""
    path = base_path.rstrip('/')
    if resource:
        path += f"/{resource}"
    if resource_id:
        path += f"/{resource_id}"
    if action:
        path += f"/{action}"
    return path


def build_collection_endpoint(base_path: str, resource: str) -> str:
    """Build an endpoint for a resource collection."""
    return f"{base_path.rstrip('/')}/{resource}"


def build_item_endpoint(base_path: str, resource: str, item_id: str) -> str:
    """Build an endpoint for a single resource item."""
    return f"{base_path.rstrip('/')}/{resource}/{item_id}"


def build_nested_endpoint(base_path: str, parent: str, parent_id: str, child: str) -> str:
    """Build an endpoint for nested resources."""
    return f"{base_path.rstrip('/')}/{parent}/{parent_id}/{child}"


def get_http_method_for_action(action: str) -> str:
    """Get the appropriate HTTP method for an action."""
    action_methods = {
        "list": "GET",
        "get": "GET",
        "show": "GET",
        "create": "POST",
        "store": "POST",
        "update": "PUT",
        "replace": "PUT",
        "patch": "PATCH",
        "modify": "PATCH",
        "delete": "DELETE",
        "destroy": "DELETE",
        "search": "GET",
        "export": "GET",
        "import": "POST",
    }
    return action_methods.get(action.lower(), "GET")


def is_safe_method(method: str) -> bool:
    """Check if an HTTP method is safe (no side effects)."""
    return method.upper() in ("GET", "HEAD", "OPTIONS")


def is_idempotent_method(method: str) -> bool:
    """Check if an HTTP method is idempotent."""
    return method.upper() in ("GET", "HEAD", "OPTIONS", "PUT", "DELETE")


def build_link_header(links: dict) -> str:
    """Build a Link header value from a dictionary of rel->url."""
    parts = []
    for rel, url in links.items():
        parts.append(f'<{url}>; rel="{rel}"')
    return ", ".join(parts)


def parse_link_header(header: str) -> dict:
    """Parse a Link header value into a dictionary."""
    import re
    result = {}
    for match in re.finditer(r'<([^>]+)>;\s*rel="([^"]+)"', header):
        result[match.group(2)] = match.group(1)
    return result


def build_pagination_links(base_url: str, page: int, per_page: int, total: int) -> dict:
    """Build pagination link URLs."""
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    links = {
        "self": f"{base_url}?page={page}&per_page={per_page}",
        "first": f"{base_url}?page=1&per_page={per_page}",
        "last": f"{base_url}?page={total_pages}&per_page={per_page}",
    }
    if page > 1:
        links["prev"] = f"{base_url}?page={page - 1}&per_page={per_page}"
    if page < total_pages:
        links["next"] = f"{base_url}?page={page + 1}&per_page={per_page}"
    return links


def build_hateoas_links(resource_type: str, resource_id: str, base_url: str, actions: list) -> list:
    """Build HATEOAS links for a resource."""
    links = [
        {"rel": "self", "href": f"{base_url}/{resource_type}/{resource_id}", "method": "GET"}
    ]
    for action in actions:
        method = get_http_method_for_action(action)
        if action in ("update", "delete"):
            href = f"{base_url}/{resource_type}/{resource_id}"
        else:
            href = f"{base_url}/{resource_type}/{resource_id}/{action}"
        links.append({"rel": action, "href": href, "method": method})
    return links


def build_api_version_header(version: str, header_name: str) -> dict:
    """Build an API version header."""
    return {header_name: version}


def extract_api_version_from_path(path: str) -> str:
    """Extract API version from a path like /v1/users."""
    import re
    match = re.match(r'^/v(\d+(?:\.\d+)?)', path)
    return match.group(1) if match else ""


def build_versioned_path(path: str, version: str) -> str:
    """Build a versioned API path."""
    clean_path = path.lstrip('/')
    return f"/v{version}/{clean_path}"


def is_valid_api_version(version: str) -> bool:
    """Check if a version string is valid."""
    import re
    return bool(re.match(r'^v?\d+(\.\d+)?(\.\d+)?$', version))


def compare_api_versions(v1: str, v2: str) -> int:
    """Compare two API versions. Returns -1, 0, or 1."""
    def parse_version(v):
        v = v.lstrip('v')
        parts = [int(p) for p in v.split('.')]
        while len(parts) < 3:
            parts.append(0)
        return parts
    p1, p2 = parse_version(v1), parse_version(v2)
    for a, b in zip(p1, p2):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0


def format_json_api_resource(resource_type: str, resource_id: str, attributes: dict) -> dict:
    """Format a resource in JSON:API format."""
    return {
        "type": resource_type,
        "id": str(resource_id),
        "attributes": attributes
    }


def format_json_api_collection(resource_type: str, items: list) -> dict:
    """Format a collection in JSON:API format."""
    data = []
    for item in items:
        item_id = item.pop("id", "")
        data.append({
            "type": resource_type,
            "id": str(item_id),
            "attributes": item
        })
    return {"data": data}


def format_json_api_error(status: int, title: str, detail: str, source: str) -> dict:
    """Format an error in JSON:API format."""
    return {
        "errors": [{
            "status": str(status),
            "title": title,
            "detail": detail,
            "source": {"pointer": source} if source else {}
        }]
    }


def format_problem_detail(status: int, title: str, detail: str, instance: str, error_type: str) -> dict:
    """Format an error in RFC 7807 Problem Detail format."""
    return {
        "type": error_type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance
    }


def build_error_response(status_code: int, message: str, errors: list) -> dict:
    """Build a standard error response."""
    return {
        "success": False,
        "error": {
            "code": status_code,
            "message": message,
            "details": errors
        }
    }


def build_success_response(data: dict, meta: dict) -> dict:
    """Build a standard success response."""
    response = {"success": True, "data": data}
    if meta:
        response["meta"] = meta
    return response


def build_collection_response(items: list, total: int, page: int, per_page: int) -> dict:
    """Build a paginated collection response."""
    return {
        "success": True,
        "data": items,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
        }
    }


def extract_sort_params(sort_string: str) -> list:
    """Extract sort parameters from a query string value."""
    if not sort_string:
        return []
    result = []
    for field in sort_string.split(','):
        field = field.strip()
        if field.startswith('-'):
            result.append({"field": field[1:], "direction": "desc"})
        elif field.startswith('+'):
            result.append({"field": field[1:], "direction": "asc"})
        else:
            result.append({"field": field, "direction": "asc"})
    return result


def build_sort_string(sort_params: list) -> str:
    """Build a sort query string value from parameters."""
    parts = []
    for param in sort_params:
        field = param.get("field", "")
        direction = param.get("direction", "asc")
        if direction == "desc":
            parts.append(f"-{field}")
        else:
            parts.append(field)
    return ",".join(parts)


def extract_filter_params(filter_dict: dict) -> list:
    """Convert filter dictionary to list of conditions."""
    conditions = []
    for key, value in filter_dict.items():
        if "__" in key:
            field, operator = key.rsplit("__", 1)
        else:
            field, operator = key, "eq"
        conditions.append({
            "field": field,
            "operator": operator,
            "value": value
        })
    return conditions


def build_filter_query_string(filters: list) -> str:
    """Build filter query string from conditions."""
    parts = []
    for f in filters:
        field = f.get("field", "")
        operator = f.get("operator", "eq")
        value = f.get("value", "")
        if operator == "eq":
            parts.append(f"filter[{field}]={value}")
        else:
            parts.append(f"filter[{field}__{operator}]={value}")
    return "&".join(parts)


def extract_fields_param(fields_string: str, resource_type: str) -> list:
    """Extract sparse fieldsets from query parameter."""
    if not fields_string:
        return []
    return [f.strip() for f in fields_string.split(',')]


def build_fields_query_string(resource_fields: dict) -> str:
    """Build fields query string for sparse fieldsets."""
    parts = []
    for resource_type, fields in resource_fields.items():
        fields_str = ",".join(fields)
        parts.append(f"fields[{resource_type}]={fields_str}")
    return "&".join(parts)


def extract_include_param(include_string: str) -> list:
    """Extract relationship includes from query parameter."""
    if not include_string:
        return []
    return [r.strip() for r in include_string.split(',')]


def is_valid_resource_name(name: str) -> bool:
    """Check if a resource name follows REST conventions."""
    import re
    return bool(re.match(r'^[a-z][a-z0-9_-]*$', name))


def pluralize_resource(name: str) -> str:
    """Pluralize a resource name for collection endpoints."""
    if name.endswith('y') and len(name) > 1 and name[-2] not in 'aeiou':
        return name[:-1] + 'ies'
    if name.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return name + 'es'
    return name + 's'


def singularize_resource(name: str) -> str:
    """Singularize a resource name."""
    if name.endswith('ies'):
        return name[:-3] + 'y'
    if name.endswith('es') and len(name) > 3 and name[-3] in 'sxz':
        return name[:-2]
    if name.endswith('s') and not name.endswith('ss'):
        return name[:-1]
    return name


def build_content_type_header(media_type: str, charset: str, params: dict) -> str:
    """Build a Content-Type header value."""
    value = media_type
    if charset:
        value += f"; charset={charset}"
    for key, val in params.items():
        value += f"; {key}={val}"
    return value


def parse_accept_header(accept: str) -> list:
    """Parse Accept header into prioritized list of media types."""
    import re
    types = []
    for part in accept.split(','):
        part = part.strip()
        match = re.match(r'([^;]+)(?:;\s*q=([0-9.]+))?', part)
        if match:
            media_type = match.group(1).strip()
            quality = float(match.group(2)) if match.group(2) else 1.0
            types.append({"type": media_type, "quality": quality})
    types.sort(key=lambda x: x["quality"], reverse=True)
    return types


def negotiate_content_type(accept_header: str, supported_types: list) -> str:
    """Negotiate content type based on Accept header and supported types."""
    accepted = parse_accept_header(accept_header)
    for item in accepted:
        media_type = item["type"]
        if media_type in supported_types:
            return media_type
        if media_type == "*/*" and supported_types:
            return supported_types[0]
        if media_type.endswith("/*"):
            prefix = media_type[:-2]
            for supported in supported_types:
                if supported.startswith(prefix):
                    return supported
    return supported_types[0] if supported_types else ""


def build_cache_control(max_age: int, private: bool, no_store: bool, no_cache: bool, must_revalidate: bool) -> str:
    """Build a Cache-Control header value."""
    directives = []
    if no_store:
        directives.append("no-store")
    elif no_cache:
        directives.append("no-cache")
    else:
        if private:
            directives.append("private")
        else:
            directives.append("public")
        if max_age >= 0:
            directives.append(f"max-age={max_age}")
    if must_revalidate:
        directives.append("must-revalidate")
    return ", ".join(directives)


def build_cors_headers(origin: str, methods: list, headers: list, max_age: int, credentials: bool) -> dict:
    """Build CORS response headers."""
    cors_headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": ", ".join(methods),
        "Access-Control-Allow-Headers": ", ".join(headers),
        "Access-Control-Max-Age": str(max_age),
    }
    if credentials:
        cors_headers["Access-Control-Allow-Credentials"] = "true"
    return cors_headers


def is_cors_preflight(method: str, origin_header: str, request_method_header: str) -> bool:
    """Check if request is a CORS preflight request."""
    return (method.upper() == "OPTIONS" and 
            bool(origin_header) and 
            bool(request_method_header))


def validate_origin(origin: str, allowed_origins: list) -> bool:
    """Validate if an origin is allowed."""
    if "*" in allowed_origins:
        return True
    return origin in allowed_origins


def build_retry_after_header(seconds: int) -> str:
    """Build a Retry-After header value."""
    return str(seconds)


def build_location_header(base_url: str, resource_type: str, resource_id: str) -> str:
    """Build a Location header for created resources."""
    return f"{base_url}/{resource_type}/{resource_id}"
