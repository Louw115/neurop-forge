"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Permission Utilities - Pure functions for permission and access control.
All functions are pure, deterministic, and atomic.
"""

def build_permission(resource: str, action: str) -> str:
    """Build a permission string."""
    return f"{resource}:{action}"


def parse_permission(permission: str) -> dict:
    """Parse a permission string."""
    if ":" in permission:
        parts = permission.split(":", 1)
        return {"resource": parts[0], "action": parts[1]}
    return {"resource": permission, "action": "*"}


def build_role(role_id: str, name: str, permissions: list) -> dict:
    """Build a role definition."""
    return {
        "id": role_id,
        "name": name,
        "permissions": permissions,
        "inherits": []
    }


def add_permission_to_role(role: dict, permission: str) -> dict:
    """Add a permission to a role."""
    result = dict(role)
    result["permissions"] = list(role.get("permissions", []))
    if permission not in result["permissions"]:
        result["permissions"].append(permission)
    return result


def remove_permission_from_role(role: dict, permission: str) -> dict:
    """Remove a permission from a role."""
    result = dict(role)
    result["permissions"] = [p for p in role.get("permissions", []) if p != permission]
    return result


def add_role_inheritance(role: dict, parent_role_id: str) -> dict:
    """Add role inheritance."""
    result = dict(role)
    result["inherits"] = list(role.get("inherits", []))
    if parent_role_id not in result["inherits"]:
        result["inherits"].append(parent_role_id)
    return result


def expand_role_permissions(role: dict, all_roles: dict) -> list:
    """Expand permissions including inherited roles."""
    permissions = set(role.get("permissions", []))
    for parent_id in role.get("inherits", []):
        if parent_id in all_roles:
            parent_perms = expand_role_permissions(all_roles[parent_id], all_roles)
            permissions.update(parent_perms)
    return list(permissions)


def has_permission(user_permissions: list, required_permission: str) -> bool:
    """Check if user has required permission."""
    required = parse_permission(required_permission)
    for perm in user_permissions:
        parsed = parse_permission(perm)
        if parsed["resource"] == "*" and parsed["action"] == "*":
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


def get_missing_permissions(user_permissions: list, required_permissions: list) -> list:
    """Get list of missing permissions."""
    return [req for req in required_permissions if not has_permission(user_permissions, req)]


def build_user_permissions(user_roles: list, all_roles: dict) -> list:
    """Build complete permission list from user's roles."""
    permissions = set()
    for role_id in user_roles:
        if role_id in all_roles:
            role_perms = expand_role_permissions(all_roles[role_id], all_roles)
            permissions.update(role_perms)
    return list(permissions)


def build_access_rule(resource: str, action: str, condition: dict) -> dict:
    """Build an access rule with condition."""
    return {
        "resource": resource,
        "action": action,
        "condition": condition,
        "effect": "allow"
    }


def evaluate_condition(condition: dict, context: dict) -> bool:
    """Evaluate an access condition."""
    operator = condition.get("operator")
    field = condition.get("field")
    value = condition.get("value")
    context_value = context.get(field)
    if operator == "equals":
        return context_value == value
    elif operator == "not_equals":
        return context_value != value
    elif operator == "in":
        return context_value in value
    elif operator == "not_in":
        return context_value not in value
    elif operator == "contains":
        return value in context_value if context_value else False
    elif operator == "greater_than":
        return context_value > value if context_value else False
    elif operator == "less_than":
        return context_value < value if context_value else False
    return False


def evaluate_access_rule(rule: dict, context: dict) -> str:
    """Evaluate an access rule against context."""
    condition = rule.get("condition")
    if not condition:
        return rule.get("effect", "allow")
    if evaluate_condition(condition, context):
        return rule.get("effect", "allow")
    return "no_match"


def check_resource_access(rules: list, resource: str, action: str, context: dict) -> bool:
    """Check if access is allowed for resource action."""
    for rule in rules:
        if rule["resource"] == resource and rule["action"] in [action, "*"]:
            result = evaluate_access_rule(rule, context)
            if result == "deny":
                return False
            if result == "allow":
                return True
    return False


def build_permission_group(group_id: str, name: str, permissions: list) -> dict:
    """Build a permission group."""
    return {
        "id": group_id,
        "name": name,
        "permissions": permissions
    }


def get_resource_permissions(permissions: list, resource: str) -> list:
    """Get all permissions for a specific resource."""
    return [p for p in permissions if parse_permission(p)["resource"] == resource]


def get_unique_resources(permissions: list) -> list:
    """Get unique resources from permissions."""
    resources = set()
    for perm in permissions:
        parsed = parse_permission(perm)
        resources.add(parsed["resource"])
    return list(resources)


def build_permission_matrix(roles: dict, resources: list, actions: list) -> dict:
    """Build a permission matrix for roles."""
    matrix = {}
    for role_id, role in roles.items():
        matrix[role_id] = {}
        role_perms = expand_role_permissions(role, roles)
        for resource in resources:
            matrix[role_id][resource] = {}
            for action in actions:
                perm = build_permission(resource, action)
                matrix[role_id][resource][action] = has_permission(role_perms, perm)
    return matrix


def is_admin(user_permissions: list) -> bool:
    """Check if user has admin access."""
    return has_permission(user_permissions, "*:*")


def build_permission_scope(scope_type: str, scope_value: str) -> dict:
    """Build a permission scope."""
    return {"type": scope_type, "value": scope_value}


def is_permission_scoped(permission: str, scope: dict, context: dict) -> bool:
    """Check if permission applies within scope."""
    scope_type = scope.get("type")
    scope_value = scope.get("value")
    if scope_type == "organization":
        return context.get("organization_id") == scope_value
    elif scope_type == "team":
        return context.get("team_id") == scope_value
    elif scope_type == "project":
        return context.get("project_id") == scope_value
    elif scope_type == "self":
        return context.get("user_id") == scope_value
    return True
