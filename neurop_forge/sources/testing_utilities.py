"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Testing Utilities - Pure functions for test data generation and assertions.
All functions are pure, deterministic, and atomic.
"""

def generate_test_string(length: int, seed: int) -> str:
    """Generate a deterministic test string."""
    import hashlib
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    result = []
    for i in range(length):
        hash_val = hashlib.sha256(f"{seed}:{i}".encode()).digest()
        idx = hash_val[0] % len(chars)
        result.append(chars[idx])
    return "".join(result)


def generate_test_email(seed: int) -> str:
    """Generate a deterministic test email."""
    username = generate_test_string(8, seed).lower()
    domain = generate_test_string(6, seed + 1000).lower()
    return f"{username}@{domain}.test"


def generate_test_phone(seed: int) -> str:
    """Generate a deterministic test phone number."""
    import hashlib
    hash_val = hashlib.sha256(f"phone:{seed}".encode()).hexdigest()
    digits = "".join(c for c in hash_val if c.isdigit())[:10]
    return f"+1{digits}"


def generate_test_uuid(seed: int) -> str:
    """Generate a deterministic test UUID."""
    import hashlib
    hash_val = hashlib.sha256(f"uuid:{seed}".encode()).hexdigest()
    return f"{hash_val[:8]}-{hash_val[8:12]}-4{hash_val[13:16]}-a{hash_val[17:20]}-{hash_val[20:32]}"


def generate_test_date(base_date: str, offset_days: int) -> str:
    """Generate a test date with offset from base."""
    from datetime import datetime, timedelta
    base = datetime.fromisoformat(base_date)
    result = base + timedelta(days=offset_days)
    return result.strftime("%Y-%m-%d")


def generate_test_timestamp(base_timestamp: int, offset_seconds: int) -> int:
    """Generate a test timestamp with offset."""
    return base_timestamp + offset_seconds


def generate_test_integer(min_val: int, max_val: int, seed: int) -> int:
    """Generate a deterministic test integer in range."""
    import hashlib
    hash_val = hashlib.sha256(f"int:{seed}".encode()).digest()
    val = int.from_bytes(hash_val[:4], 'big')
    return min_val + (val % (max_val - min_val + 1))


def generate_test_float(min_val: float, max_val: float, seed: int) -> float:
    """Generate a deterministic test float in range."""
    import hashlib
    hash_val = hashlib.sha256(f"float:{seed}".encode()).digest()
    normalized = int.from_bytes(hash_val[:4], 'big') / (2**32)
    return min_val + (normalized * (max_val - min_val))


def generate_test_boolean(seed: int) -> bool:
    """Generate a deterministic test boolean."""
    import hashlib
    hash_val = hashlib.sha256(f"bool:{seed}".encode()).digest()
    return hash_val[0] % 2 == 0


def generate_test_list(length: int, item_generator: str, seed: int) -> list:
    """Generate a deterministic test list."""
    result = []
    for i in range(length):
        if item_generator == "string":
            result.append(generate_test_string(10, seed + i))
        elif item_generator == "integer":
            result.append(generate_test_integer(0, 1000, seed + i))
        elif item_generator == "boolean":
            result.append(generate_test_boolean(seed + i))
    return result


def build_test_record(schema: dict, seed: int) -> dict:
    """Build a test record from a schema."""
    record = {}
    for field, field_type in schema.items():
        if field_type == "string":
            record[field] = generate_test_string(10, seed)
        elif field_type == "integer":
            record[field] = generate_test_integer(0, 1000, seed)
        elif field_type == "float":
            record[field] = generate_test_float(0, 100, seed)
        elif field_type == "boolean":
            record[field] = generate_test_boolean(seed)
        elif field_type == "email":
            record[field] = generate_test_email(seed)
        elif field_type == "uuid":
            record[field] = generate_test_uuid(seed)
        seed += 1
    return record


def build_test_dataset(schema: dict, count: int, base_seed: int) -> list:
    """Build a test dataset with multiple records."""
    return [build_test_record(schema, base_seed + i * 100) for i in range(count)]


def assert_equals(actual, expected, message: str) -> dict:
    """Assert two values are equal."""
    passed = actual == expected
    return {
        "passed": passed,
        "message": message,
        "actual": str(actual),
        "expected": str(expected),
        "error": None if passed else f"Expected {expected}, got {actual}"
    }


def assert_not_equals(actual, expected, message: str) -> dict:
    """Assert two values are not equal."""
    passed = actual != expected
    return {
        "passed": passed,
        "message": message,
        "actual": str(actual),
        "expected": f"not {expected}",
        "error": None if passed else f"Expected not {expected}, but got {actual}"
    }


def assert_true(value: bool, message: str) -> dict:
    """Assert value is true."""
    return {
        "passed": value is True,
        "message": message,
        "actual": str(value),
        "expected": "True",
        "error": None if value is True else "Expected True"
    }


def assert_false(value: bool, message: str) -> dict:
    """Assert value is false."""
    return {
        "passed": value is False,
        "message": message,
        "actual": str(value),
        "expected": "False",
        "error": None if value is False else "Expected False"
    }


def assert_none(value, message: str) -> dict:
    """Assert value is None."""
    return {
        "passed": value is None,
        "message": message,
        "actual": str(value),
        "expected": "None",
        "error": None if value is None else f"Expected None, got {value}"
    }


def assert_not_none(value, message: str) -> dict:
    """Assert value is not None."""
    return {
        "passed": value is not None,
        "message": message,
        "actual": str(value),
        "expected": "not None",
        "error": None if value is not None else "Expected not None"
    }


def assert_in(value, container, message: str) -> dict:
    """Assert value is in container."""
    passed = value in container
    return {
        "passed": passed,
        "message": message,
        "actual": str(value),
        "expected": f"in {container}",
        "error": None if passed else f"{value} not found in container"
    }


def assert_not_in(value, container, message: str) -> dict:
    """Assert value is not in container."""
    passed = value not in container
    return {
        "passed": passed,
        "message": message,
        "actual": str(value),
        "expected": f"not in {container}",
        "error": None if passed else f"{value} unexpectedly found in container"
    }


def assert_greater_than(value, threshold, message: str) -> dict:
    """Assert value is greater than threshold."""
    passed = value > threshold
    return {
        "passed": passed,
        "message": message,
        "actual": str(value),
        "expected": f"> {threshold}",
        "error": None if passed else f"{value} is not greater than {threshold}"
    }


def assert_less_than(value, threshold, message: str) -> dict:
    """Assert value is less than threshold."""
    passed = value < threshold
    return {
        "passed": passed,
        "message": message,
        "actual": str(value),
        "expected": f"< {threshold}",
        "error": None if passed else f"{value} is not less than {threshold}"
    }


def assert_between(value, min_val, max_val, message: str) -> dict:
    """Assert value is between min and max (inclusive)."""
    passed = min_val <= value <= max_val
    return {
        "passed": passed,
        "message": message,
        "actual": str(value),
        "expected": f"between {min_val} and {max_val}",
        "error": None if passed else f"{value} is not between {min_val} and {max_val}"
    }


def assert_length(value, expected_length: int, message: str) -> dict:
    """Assert value has expected length."""
    actual_length = len(value)
    passed = actual_length == expected_length
    return {
        "passed": passed,
        "message": message,
        "actual": str(actual_length),
        "expected": str(expected_length),
        "error": None if passed else f"Expected length {expected_length}, got {actual_length}"
    }


def assert_empty(value, message: str) -> dict:
    """Assert value is empty."""
    passed = len(value) == 0
    return {
        "passed": passed,
        "message": message,
        "actual": str(len(value)),
        "expected": "0",
        "error": None if passed else f"Expected empty, got length {len(value)}"
    }


def assert_not_empty(value, message: str) -> dict:
    """Assert value is not empty."""
    passed = len(value) > 0
    return {
        "passed": passed,
        "message": message,
        "actual": str(len(value)),
        "expected": "> 0",
        "error": None if passed else "Expected not empty"
    }


def assert_type(value, expected_type: str, message: str) -> dict:
    """Assert value is of expected type."""
    type_name = type(value).__name__
    passed = type_name == expected_type
    return {
        "passed": passed,
        "message": message,
        "actual": type_name,
        "expected": expected_type,
        "error": None if passed else f"Expected type {expected_type}, got {type_name}"
    }


def assert_matches_pattern(value: str, pattern: str, message: str) -> dict:
    """Assert string matches regex pattern."""
    import re
    passed = bool(re.match(pattern, value))
    return {
        "passed": passed,
        "message": message,
        "actual": value,
        "expected": f"matches {pattern}",
        "error": None if passed else f"Value does not match pattern {pattern}"
    }


def combine_test_results(results: list) -> dict:
    """Combine multiple test results into a summary."""
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    failed = total - passed
    failures = [r for r in results if not r.get("passed")]
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": (passed / total * 100) if total > 0 else 0,
        "failures": failures
    }


def format_test_result(result: dict) -> str:
    """Format a single test result for display."""
    status = "PASS" if result.get("passed") else "FAIL"
    message = result.get("message", "")
    if result.get("passed"):
        return f"[{status}] {message}"
    error = result.get("error", "")
    return f"[{status}] {message}: {error}"


def format_test_summary(summary: dict) -> str:
    """Format a test summary for display."""
    lines = [
        f"Tests: {summary['total']}",
        f"Passed: {summary['passed']}",
        f"Failed: {summary['failed']}",
        f"Pass Rate: {summary['pass_rate']:.1f}%"
    ]
    if summary['failures']:
        lines.append("\nFailures:")
        for failure in summary['failures']:
            lines.append(f"  - {format_test_result(failure)}")
    return "\n".join(lines)


def build_mock_response(status_code: int, body: dict, headers: dict) -> dict:
    """Build a mock HTTP response."""
    return {
        "status_code": status_code,
        "body": body,
        "headers": headers
    }


def build_mock_request(method: str, path: str, body: dict, headers: dict, query_params: dict) -> dict:
    """Build a mock HTTP request."""
    return {
        "method": method,
        "path": path,
        "body": body,
        "headers": headers,
        "query_params": query_params
    }


def generate_test_name(prefix: str, seed: int) -> str:
    """Generate a test name like 'John Doe'."""
    first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    import hashlib
    hash_val = hashlib.sha256(f"name:{seed}".encode()).digest()
    first = first_names[hash_val[0] % len(first_names)]
    last = last_names[hash_val[1] % len(last_names)]
    return f"{prefix}{first} {last}" if prefix else f"{first} {last}"


def generate_test_address(seed: int) -> dict:
    """Generate a test address."""
    streets = ["Main St", "Oak Ave", "Maple Dr", "Pine Rd", "Cedar Ln"]
    cities = ["Springfield", "Riverside", "Georgetown", "Fairview", "Madison"]
    states = ["CA", "NY", "TX", "FL", "IL"]
    import hashlib
    hash_val = hashlib.sha256(f"addr:{seed}".encode()).digest()
    return {
        "street": f"{(hash_val[0] % 999) + 1} {streets[hash_val[1] % len(streets)]}",
        "city": cities[hash_val[2] % len(cities)],
        "state": states[hash_val[3] % len(states)],
        "zip": f"{10000 + (int.from_bytes(hash_val[4:6], 'big') % 90000)}"
    }


def calculate_test_checksum(data: dict) -> str:
    """Calculate a checksum for test data verification."""
    import hashlib
    import json
    content = json.dumps(data, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def verify_test_checksum(data: dict, expected_checksum: str) -> bool:
    """Verify test data matches expected checksum."""
    return calculate_test_checksum(data) == expected_checksum
