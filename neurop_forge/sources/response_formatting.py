"""
Response Formatting Utilities - Pure functions for API response formatting.
All functions are pure, deterministic, and atomic.
"""

def format_success_response(data, message: str) -> dict:
    """Format a success response."""
    response = {"success": True}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return response


def format_error_response(code: int, message: str, details: list) -> dict:
    """Format an error response."""
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    if details:
        response["error"]["details"] = details
    return response


def format_created_response(resource_type: str, resource_id: str, data: dict, location: str) -> dict:
    """Format a 201 Created response."""
    return {
        "success": True,
        "message": f"{resource_type} created successfully",
        "data": data,
        "id": resource_id,
        "location": location
    }


def format_deleted_response(resource_type: str, resource_id: str) -> dict:
    """Format a delete success response."""
    return {
        "success": True,
        "message": f"{resource_type} deleted successfully",
        "id": resource_id
    }


def format_paginated_response(items: list, page: int, per_page: int, total: int, links: dict) -> dict:
    """Format a paginated collection response."""
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "success": True,
        "data": items,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "links": links
    }


def format_cursor_paginated_response(items: list, next_cursor: str, prev_cursor: str, has_more: bool) -> dict:
    """Format a cursor-paginated response."""
    return {
        "success": True,
        "data": items,
        "meta": {
            "has_more": has_more,
            "next_cursor": next_cursor,
            "prev_cursor": prev_cursor
        }
    }


def format_batch_response(results: list, total_success: int, total_failed: int) -> dict:
    """Format a batch operation response."""
    return {
        "success": total_failed == 0,
        "data": {
            "results": results,
            "summary": {
                "total": total_success + total_failed,
                "successful": total_success,
                "failed": total_failed
            }
        }
    }


def format_async_accepted_response(job_id: str, status_url: str, estimated_time: int) -> dict:
    """Format a 202 Accepted response for async operations."""
    return {
        "success": True,
        "message": "Request accepted for processing",
        "data": {
            "job_id": job_id,
            "status_url": status_url,
            "estimated_time_seconds": estimated_time
        }
    }


def format_status_response(status: str, progress: int, message: str, result) -> dict:
    """Format a job status response."""
    response = {
        "success": True,
        "data": {
            "status": status,
            "progress": progress,
            "message": message
        }
    }
    if result is not None:
        response["data"]["result"] = result
    return response


def format_health_check_response(status: str, checks: dict, version: str) -> dict:
    """Format a health check response."""
    return {
        "status": status,
        "version": version,
        "checks": checks,
        "timestamp": ""
    }


def format_rate_limit_headers(limit: int, remaining: int, reset: int) -> dict:
    """Format rate limit response headers."""
    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset)
    }


def format_validation_errors(errors: list) -> dict:
    """Format validation errors response."""
    return {
        "success": False,
        "error": {
            "code": 422,
            "message": "Validation failed",
            "details": [
                {"field": e.get("field", ""), "message": e.get("message", "")}
                for e in errors
            ]
        }
    }


def format_not_found_response(resource_type: str, resource_id: str) -> dict:
    """Format a 404 Not Found response."""
    return {
        "success": False,
        "error": {
            "code": 404,
            "message": f"{resource_type} not found",
            "details": [f"No {resource_type} with ID '{resource_id}' exists"]
        }
    }


def format_unauthorized_response(message: str) -> dict:
    """Format a 401 Unauthorized response."""
    return {
        "success": False,
        "error": {
            "code": 401,
            "message": message or "Authentication required"
        }
    }


def format_forbidden_response(message: str) -> dict:
    """Format a 403 Forbidden response."""
    return {
        "success": False,
        "error": {
            "code": 403,
            "message": message or "Access denied"
        }
    }


def format_rate_limited_response(retry_after: int) -> dict:
    """Format a 429 Too Many Requests response."""
    return {
        "success": False,
        "error": {
            "code": 429,
            "message": "Too many requests",
            "retry_after": retry_after
        }
    }


def format_server_error_response(error_id: str) -> dict:
    """Format a 500 Server Error response (safe for clients)."""
    return {
        "success": False,
        "error": {
            "code": 500,
            "message": "An internal error occurred",
            "error_id": error_id
        }
    }


def format_service_unavailable_response(retry_after: int, message: str) -> dict:
    """Format a 503 Service Unavailable response."""
    return {
        "success": False,
        "error": {
            "code": 503,
            "message": message or "Service temporarily unavailable",
            "retry_after": retry_after
        }
    }


def add_metadata_to_response(response: dict, request_id: str, duration_ms: int) -> dict:
    """Add metadata to a response."""
    result = dict(response)
    result["_meta"] = {
        "request_id": request_id,
        "duration_ms": duration_ms
    }
    return result


def filter_response_fields(data: dict, fields: list) -> dict:
    """Filter response to only include specified fields."""
    if not fields:
        return data
    return {k: v for k, v in data.items() if k in fields}


def exclude_response_fields(data: dict, excluded: list) -> dict:
    """Exclude specified fields from response."""
    return {k: v for k, v in data.items() if k not in excluded}


def rename_response_fields(data: dict, field_map: dict) -> dict:
    """Rename fields in response according to mapping."""
    result = {}
    for key, value in data.items():
        new_key = field_map.get(key, key)
        result[new_key] = value
    return result


def format_resource_list(items: list, resource_type: str) -> dict:
    """Format a list of resources with type metadata."""
    return {
        "success": True,
        "data": items,
        "meta": {
            "type": resource_type,
            "count": len(items)
        }
    }


def format_resource_item(item: dict, resource_type: str, links: dict) -> dict:
    """Format a single resource with type and links."""
    return {
        "success": True,
        "data": item,
        "meta": {
            "type": resource_type
        },
        "links": links
    }


def format_diff_response(original: dict, updated: dict, changes: dict) -> dict:
    """Format a response showing changes between versions."""
    return {
        "success": True,
        "data": {
            "original": original,
            "updated": updated,
            "changes": changes
        }
    }


def format_count_response(count: int, resource_type: str) -> dict:
    """Format a count response."""
    return {
        "success": True,
        "data": {
            "count": count,
            "type": resource_type
        }
    }


def format_exists_response(exists: bool, resource_type: str, resource_id: str) -> dict:
    """Format an existence check response."""
    return {
        "success": True,
        "data": {
            "exists": exists,
            "type": resource_type,
            "id": resource_id
        }
    }


def wrap_jsonp(response: dict, callback: str) -> str:
    """Wrap JSON response for JSONP."""
    import json
    json_str = json.dumps(response)
    return f"{callback}({json_str});"


def format_csv_response(items: list, columns: list, delimiter: str) -> str:
    """Format response as CSV string."""
    lines = [delimiter.join(columns)]
    for item in items:
        values = [str(item.get(col, "")) for col in columns]
        lines.append(delimiter.join(values))
    return "\n".join(lines)


def format_xml_element(tag: str, value, attributes: dict) -> str:
    """Format a value as an XML element."""
    attrs = " ".join(f'{k}="{v}"' for k, v in attributes.items())
    if attrs:
        attrs = " " + attrs
    if isinstance(value, dict):
        children = "".join(format_xml_element(k, v, {}) for k, v in value.items())
        return f"<{tag}{attrs}>{children}</{tag}>"
    elif isinstance(value, list):
        children = "".join(format_xml_element("item", v, {}) for v in value)
        return f"<{tag}{attrs}>{children}</{tag}>"
    else:
        escaped = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<{tag}{attrs}>{escaped}</{tag}>"


def format_xml_response(data: dict, root_element: str) -> str:
    """Format response as XML string."""
    content = "".join(format_xml_element(k, v, {}) for k, v in data.items())
    return f'<?xml version="1.0" encoding="UTF-8"?><{root_element}>{content}</{root_element}>'


def calculate_response_etag(data: dict) -> str:
    """Calculate ETag for response data."""
    import hashlib
    import json
    content = json.dumps(data, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


def add_cache_headers(response_headers: dict, max_age: int, etag: str, last_modified: str) -> dict:
    """Add caching headers to response."""
    headers = dict(response_headers)
    if max_age > 0:
        headers["Cache-Control"] = f"max-age={max_age}"
    if etag:
        headers["ETag"] = f'"{etag}"'
    if last_modified:
        headers["Last-Modified"] = last_modified
    return headers


def format_partial_content_headers(start: int, end: int, total: int) -> dict:
    """Format headers for 206 Partial Content response."""
    return {
        "Content-Range": f"bytes {start}-{end}/{total}",
        "Accept-Ranges": "bytes"
    }
