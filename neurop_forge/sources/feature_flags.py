"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Feature Flags - Pure functions for feature flag management.
All functions are pure, deterministic, and atomic.
"""

def build_feature_flag(flag_id: str, name: str, description: str, enabled: bool) -> dict:
    """Build a feature flag definition."""
    return {
        "id": flag_id,
        "name": name,
        "description": description,
        "enabled": enabled,
        "rules": [],
        "default_value": enabled
    }


def is_flag_enabled(flag: dict) -> bool:
    """Check if feature flag is enabled."""
    return flag.get("enabled", False)


def set_flag_enabled(flag: dict, enabled: bool) -> dict:
    """Set feature flag enabled state."""
    result = dict(flag)
    result["enabled"] = enabled
    return result


def add_targeting_rule(flag: dict, rule: dict) -> dict:
    """Add a targeting rule to feature flag."""
    result = dict(flag)
    result["rules"] = list(flag.get("rules", []))
    result["rules"].append(rule)
    return result


def build_targeting_rule(rule_id: str, attribute: str, operator: str, value, enabled: bool) -> dict:
    """Build a targeting rule."""
    return {
        "id": rule_id,
        "attribute": attribute,
        "operator": operator,
        "value": value,
        "enabled": enabled
    }


def evaluate_targeting_rule(rule: dict, user_context: dict) -> bool:
    """Evaluate a targeting rule against user context."""
    attribute = rule.get("attribute")
    operator = rule.get("operator")
    value = rule.get("value")
    user_value = user_context.get(attribute)
    if operator == "equals":
        return user_value == value
    elif operator == "not_equals":
        return user_value != value
    elif operator == "in":
        return user_value in value
    elif operator == "not_in":
        return user_value not in value
    elif operator == "contains":
        return value in str(user_value) if user_value else False
    elif operator == "starts_with":
        return str(user_value).startswith(value) if user_value else False
    elif operator == "ends_with":
        return str(user_value).endswith(value) if user_value else False
    elif operator == "greater_than":
        return user_value > value if user_value is not None else False
    elif operator == "less_than":
        return user_value < value if user_value is not None else False
    elif operator == "regex":
        import re
        return bool(re.match(value, str(user_value))) if user_value else False
    return False


def evaluate_feature_flag(flag: dict, user_context: dict) -> bool:
    """Evaluate feature flag for user context."""
    if not flag.get("enabled"):
        return False
    rules = flag.get("rules", [])
    if not rules:
        return flag.get("default_value", True)
    for rule in rules:
        if rule.get("enabled", True) and evaluate_targeting_rule(rule, user_context):
            return True
    return flag.get("default_value", False)


def build_percentage_rollout(flag: dict, percentage: int) -> dict:
    """Configure percentage-based rollout."""
    result = dict(flag)
    result["rollout_percentage"] = percentage
    return result


def is_in_rollout(user_id: str, percentage: int) -> bool:
    """Check if user is in percentage rollout."""
    import hashlib
    hash_val = hashlib.sha256(user_id.encode()).digest()
    user_bucket = hash_val[0] % 100
    return user_bucket < percentage


def evaluate_with_rollout(flag: dict, user_context: dict) -> bool:
    """Evaluate feature flag with percentage rollout."""
    if not flag.get("enabled"):
        return False
    percentage = flag.get("rollout_percentage", 100)
    user_id = user_context.get("user_id", "")
    if not is_in_rollout(user_id, percentage):
        return False
    return evaluate_feature_flag(flag, user_context)


def build_variant(variant_id: str, name: str, weight: int, value) -> dict:
    """Build a feature variant."""
    return {
        "id": variant_id,
        "name": name,
        "weight": weight,
        "value": value
    }


def add_variant_to_flag(flag: dict, variant: dict) -> dict:
    """Add a variant to feature flag."""
    result = dict(flag)
    result["variants"] = list(flag.get("variants", []))
    result["variants"].append(variant)
    return result


def select_variant(flag: dict, user_id: str) -> dict:
    """Select variant for user based on weights."""
    variants = flag.get("variants", [])
    if not variants:
        return {}
    import hashlib
    hash_val = hashlib.sha256(f"{flag['id']}:{user_id}".encode()).digest()
    bucket = int.from_bytes(hash_val[:4], 'big') % 100
    total_weight = sum(v.get("weight", 0) for v in variants)
    if total_weight == 0:
        return variants[0]
    cumulative = 0
    for variant in variants:
        weight_percent = (variant.get("weight", 0) / total_weight) * 100
        cumulative += weight_percent
        if bucket < cumulative:
            return variant
    return variants[-1]


def build_flag_context(user_id: str, attributes: dict) -> dict:
    """Build user context for flag evaluation."""
    return {
        "user_id": user_id,
        **attributes
    }


def get_all_flag_values(flags: dict, user_context: dict) -> dict:
    """Get all flag values for user."""
    result = {}
    for flag_id, flag in flags.items():
        result[flag_id] = evaluate_feature_flag(flag, user_context)
    return result


def build_flag_override(flag_id: str, user_id: str, value: bool) -> dict:
    """Build a flag override for specific user."""
    return {
        "flag_id": flag_id,
        "user_id": user_id,
        "value": value
    }


def apply_overrides(flags: dict, overrides: list, user_id: str) -> dict:
    """Apply user-specific overrides to flags."""
    result = dict(flags)
    for override in overrides:
        if override["user_id"] == user_id and override["flag_id"] in result:
            result[override["flag_id"]] = dict(result[override["flag_id"]])
            result[override["flag_id"]]["enabled"] = override["value"]
    return result


def build_flag_summary(flag: dict) -> dict:
    """Build summary of feature flag."""
    return {
        "id": flag.get("id"),
        "name": flag.get("name"),
        "enabled": flag.get("enabled"),
        "rule_count": len(flag.get("rules", [])),
        "variant_count": len(flag.get("variants", [])),
        "rollout_percentage": flag.get("rollout_percentage", 100)
    }


def filter_enabled_flags(flags: dict) -> dict:
    """Filter to only enabled flags."""
    return {k: v for k, v in flags.items() if v.get("enabled")}


def filter_disabled_flags(flags: dict) -> dict:
    """Filter to only disabled flags."""
    return {k: v for k, v in flags.items() if not v.get("enabled")}


def calculate_flag_stats(flags: dict) -> dict:
    """Calculate statistics about feature flags."""
    total = len(flags)
    enabled = sum(1 for f in flags.values() if f.get("enabled"))
    with_rules = sum(1 for f in flags.values() if f.get("rules"))
    with_variants = sum(1 for f in flags.values() if f.get("variants"))
    return {
        "total": total,
        "enabled": enabled,
        "disabled": total - enabled,
        "with_rules": with_rules,
        "with_variants": with_variants
    }
