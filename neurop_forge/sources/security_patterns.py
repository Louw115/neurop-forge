"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Security Patterns - Pure functions for security and access control.
All functions are pure, deterministic, and atomic.
"""

def hash_password(password: str, salt: str, iterations: int) -> str:
    """Hash a password with PBKDF2."""
    import hashlib
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations)
    return dk.hex()


def generate_salt(seed: str, length: int) -> str:
    """Generate a deterministic salt."""
    import hashlib
    return hashlib.sha256(seed.encode()).hexdigest()[:length]


def verify_password_hash(password: str, salt: str, iterations: int, expected_hash: str) -> bool:
    """Verify a password against its hash."""
    actual_hash = hash_password(password, salt, iterations)
    return constant_time_compare(actual_hash, expected_hash)


def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    return result == 0


def calculate_entropy(password: str) -> float:
    """Calculate password entropy in bits."""
    import math
    charset_size = 0
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        charset_size += 32
    if charset_size == 0:
        return 0
    return len(password) * math.log2(charset_size)


def is_password_strong(password: str, min_entropy: float) -> bool:
    """Check if password has sufficient entropy."""
    return calculate_entropy(password) >= min_entropy


def detect_common_password(password: str, common_passwords: list) -> bool:
    """Check if password is in common passwords list."""
    return password.lower() in [p.lower() for p in common_passwords]


def build_permission(resource: str, action: str) -> str:
    """Build a permission string."""
    return f"{resource}:{action}"


def parse_permission(permission: str) -> dict:
    """Parse a permission string."""
    if ":" in permission:
        resource, action = permission.split(":", 1)
        return {"resource": resource, "action": action}
    return {"resource": permission, "action": "*"}


def has_permission(user_permissions: list, required_permission: str) -> bool:
    """Check if user has required permission."""
    required = parse_permission(required_permission)
    for perm in user_permissions:
        parsed = parse_permission(perm)
        if parsed["resource"] == "*":
            return True
        if parsed["resource"] == required["resource"]:
            if parsed["action"] == "*" or parsed["action"] == required["action"]:
                return True
    return False


def has_all_permissions(user_permissions: list, required_permissions: list) -> bool:
    """Check if user has all required permissions."""
    return all(has_permission(user_permissions, req) for req in required_permissions)


def has_any_permission(user_permissions: list, required_permissions: list) -> bool:
    """Check if user has any of the required permissions."""
    return any(has_permission(user_permissions, req) for req in required_permissions)


def build_role(name: str, permissions: list, inherits: list) -> dict:
    """Build a role definition."""
    return {
        "name": name,
        "permissions": permissions,
        "inherits": inherits
    }


def expand_role_permissions(role: dict, all_roles: dict) -> list:
    """Expand role permissions including inherited roles."""
    permissions = list(role.get("permissions", []))
    for inherited_name in role.get("inherits", []):
        if inherited_name in all_roles:
            inherited_perms = expand_role_permissions(all_roles[inherited_name], all_roles)
            permissions.extend(inherited_perms)
    return list(set(permissions))


def build_access_policy(effect: str, principals: list, resources: list, actions: list, conditions: dict) -> dict:
    """Build an access policy."""
    return {
        "effect": effect,
        "principals": principals,
        "resources": resources,
        "actions": actions,
        "conditions": conditions
    }


def evaluate_policy(policy: dict, principal: str, resource: str, action: str, context: dict) -> str:
    """Evaluate a policy against a request."""
    if principal not in policy["principals"] and "*" not in policy["principals"]:
        return "no_match"
    if resource not in policy["resources"] and "*" not in policy["resources"]:
        return "no_match"
    if action not in policy["actions"] and "*" not in policy["actions"]:
        return "no_match"
    return policy["effect"]


def evaluate_policies(policies: list, principal: str, resource: str, action: str, context: dict) -> bool:
    """Evaluate multiple policies (deny overrides allow)."""
    allowed = False
    for policy in policies:
        result = evaluate_policy(policy, principal, resource, action, context)
        if result == "deny":
            return False
        if result == "allow":
            allowed = True
    return allowed


def sanitize_html(html: str) -> str:
    """Sanitize HTML to prevent XSS."""
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    result = html.replace('&', '&amp;')
    for char, entity in replacements.items():
        result = result.replace(char, entity)
    return result


def detect_sql_injection(input_str: str) -> bool:
    """Detect potential SQL injection patterns."""
    patterns = [
        "' OR ", "' AND ", "'; DROP", "; DELETE", "UNION SELECT",
        "1=1", "1 = 1", "/*", "*/", "--", "xp_", "exec(",
        "EXECUTE", "TRUNCATE", "INSERT INTO"
    ]
    input_upper = input_str.upper()
    return any(pattern.upper() in input_upper for pattern in patterns)


def detect_xss(input_str: str) -> bool:
    """Detect potential XSS patterns."""
    patterns = [
        "<script", "javascript:", "onerror=", "onload=", "onclick=",
        "onmouseover=", "eval(", "document.cookie", "document.write",
        "innerHTML", "outerHTML"
    ]
    input_lower = input_str.lower()
    return any(pattern.lower() in input_lower for pattern in patterns)


def detect_path_traversal(path: str) -> bool:
    """Detect path traversal attempts."""
    dangerous = ["../", "..\\", "%2e%2e", "%2e%2e%2f", "..%2f", "%2e%2e/"]
    path_lower = path.lower()
    return any(pattern in path_lower for pattern in dangerous)


def detect_command_injection(input_str: str) -> bool:
    """Detect command injection patterns."""
    patterns = [";", "|", "&", "`", "$(", "${", "\n", "\r"]
    return any(pattern in input_str for pattern in patterns)


def validate_content_type(content_type: str, allowed_types: list) -> bool:
    """Validate Content-Type against whitelist."""
    base_type = content_type.split(";")[0].strip().lower()
    return base_type in [t.lower() for t in allowed_types]


def build_csp_directive(directive: str, sources: list) -> str:
    """Build a CSP directive."""
    return f"{directive} {' '.join(sources)}"


def build_csp_header(directives: dict) -> str:
    """Build a full Content-Security-Policy header."""
    parts = []
    for directive, sources in directives.items():
        parts.append(build_csp_directive(directive, sources))
    return "; ".join(parts)


def generate_nonce(seed: str) -> str:
    """Generate a CSP nonce."""
    import hashlib
    import base64
    hash_val = hashlib.sha256(seed.encode()).digest()
    return base64.b64encode(hash_val[:16]).decode()


def validate_origin(origin: str, allowed_origins: list) -> bool:
    """Validate an origin against allowed list."""
    if "*" in allowed_origins:
        return True
    return origin in allowed_origins


def mask_sensitive_data(data: str, visible_chars: int, mask_char: str) -> str:
    """Mask sensitive data showing only last N characters."""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    return mask_char * (len(data) - visible_chars) + data[-visible_chars:]


def mask_email(email: str) -> str:
    """Mask an email address."""
    if "@" not in email:
        return mask_sensitive_data(email, 2, "*")
    local, domain = email.rsplit("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_credit_card(number: str) -> str:
    """Mask a credit card number."""
    digits = "".join(c for c in number if c.isdigit())
    if len(digits) < 4:
        return "*" * len(number)
    return "*" * (len(digits) - 4) + digits[-4:]


def is_ip_in_range(ip: str, cidr: str) -> bool:
    """Check if IP is in CIDR range."""
    def ip_to_int(ip_str):
        parts = ip_str.split(".")
        return sum(int(p) << (24 - 8 * i) for i, p in enumerate(parts))
    
    if "/" not in cidr:
        return ip == cidr
    
    network, mask_bits = cidr.split("/")
    mask_bits = int(mask_bits)
    mask = (0xFFFFFFFF << (32 - mask_bits)) & 0xFFFFFFFF
    
    return (ip_to_int(ip) & mask) == (ip_to_int(network) & mask)


def is_ip_blocked(ip: str, blocklist: list) -> bool:
    """Check if IP is in blocklist."""
    for entry in blocklist:
        if is_ip_in_range(ip, entry):
            return True
    return False


def is_ip_allowed(ip: str, allowlist: list) -> bool:
    """Check if IP is in allowlist."""
    for entry in allowlist:
        if is_ip_in_range(ip, entry):
            return True
    return False


def calculate_risk_score(factors: dict) -> float:
    """Calculate a risk score from factors."""
    score = 0.0
    weights = {
        "failed_logins": 10.0,
        "new_device": 20.0,
        "new_location": 15.0,
        "unusual_time": 5.0,
        "high_value_action": 25.0
    }
    for factor, weight in weights.items():
        if factors.get(factor, False):
            score += weight
    return min(100.0, score)


def should_require_mfa(risk_score: float, threshold: float) -> bool:
    """Check if MFA should be required based on risk."""
    return risk_score >= threshold


def build_audit_event(event_type: str, actor: str, resource: str, action: str, outcome: str, details: dict) -> dict:
    """Build a security audit event."""
    return {
        "event_type": event_type,
        "actor": actor,
        "resource": resource,
        "action": action,
        "outcome": outcome,
        "details": details
    }


def format_audit_log(event: dict, timestamp: str) -> str:
    """Format an audit event for logging."""
    return f"[{timestamp}] {event['event_type']}: {event['actor']} {event['action']} {event['resource']} -> {event['outcome']}"
