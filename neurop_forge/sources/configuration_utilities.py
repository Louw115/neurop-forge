"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Configuration Utilities - Pure functions for configuration parsing and feature flags.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""


def parse_env_string(value: str, default: str) -> str:
    """Parse an environment variable string value."""
    return value if value else default


def parse_env_int(value: str, default: int) -> int:
    """Parse an environment variable as integer."""
    try:
        return int(value) if value else default
    except (ValueError, TypeError):
        return default


def parse_env_float(value: str, default: float) -> float:
    """Parse an environment variable as float."""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default


def parse_env_bool(value: str, default: bool) -> bool:
    """Parse an environment variable as boolean."""
    if not value:
        return default
    return value.lower() in ('true', '1', 'yes', 'on', 'enabled')


def parse_env_list(value: str, delimiter: str, default: list) -> list:
    """Parse an environment variable as a list."""
    if not value:
        return default
    return [item.strip() for item in value.split(delimiter) if item.strip()]


def parse_env_dict(value: str, item_delimiter: str, key_delimiter: str, default: dict) -> dict:
    """Parse an environment variable as a dictionary."""
    if not value:
        return default
    result = {}
    for item in value.split(item_delimiter):
        if key_delimiter in item:
            key, val = item.split(key_delimiter, 1)
            result[key.strip()] = val.strip()
    return result


def is_feature_enabled(flags: dict, feature_name: str, default: bool) -> bool:
    """Check if a feature flag is enabled."""
    return flags.get(feature_name, default)


def get_feature_value(flags: dict, feature_name: str, default: str) -> str:
    """Get the value of a feature flag."""
    return str(flags.get(feature_name, default))


def is_feature_enabled_for_user(flags: dict, feature_name: str, user_id: str, rollout_percent: int) -> bool:
    """Check if a feature is enabled for a specific user based on rollout percentage."""
    if not flags.get(feature_name, False):
        return False
    import hashlib
    hash_bytes = hashlib.sha256(f"{feature_name}:{user_id}".encode()).digest()
    hash_value = int.from_bytes(hash_bytes[:4], 'big') % 100
    return hash_value < rollout_percent


def get_config_value(config: dict, key: str, default: str) -> str:
    """Get a configuration value with default fallback."""
    return str(config.get(key, default))


def get_nested_config(config: dict, keys: list, default) -> any:
    """Get a nested configuration value using a list of keys."""
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def merge_configs(base: dict, override: dict) -> dict:
    """Merge two configuration dictionaries (override takes precedence)."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result


def flatten_config(config: dict, separator: str, prefix: str) -> dict:
    """Flatten a nested configuration dictionary."""
    result = {}
    for key, value in config.items():
        full_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_config(value, separator, full_key))
        else:
            result[full_key] = value
    return result


def unflatten_config(flat_config: dict, separator: str) -> dict:
    """Unflatten a flat configuration dictionary."""
    result = {}
    for key, value in flat_config.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def validate_required_keys(config: dict, required_keys: list) -> dict:
    """Validate that required keys exist in config."""
    missing = [key for key in required_keys if key not in config]
    return {'valid': len(missing) == 0, 'missing': missing}


def get_env_prefix_vars(env_vars: dict, prefix: str) -> dict:
    """Get all environment variables with a specific prefix."""
    result = {}
    for key, value in env_vars.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):].lstrip('_')
            result[new_key] = value
    return result


def parse_connection_string(conn_str: str) -> dict:
    """Parse a connection string into components."""
    result = {'raw': conn_str}
    if '://' in conn_str:
        protocol, rest = conn_str.split('://', 1)
        result['protocol'] = protocol
        if '@' in rest:
            auth, host_part = rest.rsplit('@', 1)
            result['auth'] = auth
            rest = host_part
        if '/' in rest:
            host_port, path = rest.split('/', 1)
            result['path'] = path
        else:
            host_port = rest
        if ':' in host_port:
            host, port = host_port.rsplit(':', 1)
            result['host'] = host
            result['port'] = port
        else:
            result['host'] = host_port
    return result


def build_connection_string(protocol: str, host: str, port: int, path: str, auth: str) -> str:
    """Build a connection string from components."""
    result = f"{protocol}://"
    if auth:
        result += f"{auth}@"
    result += host
    if port:
        result += f":{port}"
    if path:
        result += f"/{path}"
    return result


def parse_dsn(dsn: str) -> dict:
    """Parse a DSN (Data Source Name) string."""
    result = parse_connection_string(dsn)
    if 'auth' in result and ':' in result['auth']:
        user, password = result['auth'].split(':', 1)
        result['user'] = user
        result['password'] = password
    if 'path' in result and '?' in result['path']:
        path, query = result['path'].split('?', 1)
        result['path'] = path
        result['database'] = path
        params = {}
        for pair in query.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v
        result['params'] = params
    return result


def is_development_env(env_name: str) -> bool:
    """Check if environment is development."""
    return env_name.lower() in ('dev', 'development', 'local')


def is_production_env(env_name: str) -> bool:
    """Check if environment is production."""
    return env_name.lower() in ('prod', 'production', 'live')


def is_staging_env(env_name: str) -> bool:
    """Check if environment is staging."""
    return env_name.lower() in ('stage', 'staging', 'uat', 'preprod')


def is_test_env(env_name: str) -> bool:
    """Check if environment is test."""
    return env_name.lower() in ('test', 'testing', 'ci')


def get_env_tier(env_name: str) -> str:
    """Get the tier classification of an environment."""
    name = env_name.lower()
    if name in ('prod', 'production', 'live'):
        return 'production'
    if name in ('stage', 'staging', 'uat', 'preprod'):
        return 'staging'
    if name in ('test', 'testing', 'ci'):
        return 'testing'
    return 'development'


def should_enable_debug(env_name: str) -> bool:
    """Determine if debug mode should be enabled based on environment."""
    return not is_production_env(env_name)


def get_log_level_for_env(env_name: str) -> str:
    """Get appropriate log level for environment."""
    if is_production_env(env_name):
        return 'WARNING'
    if is_staging_env(env_name):
        return 'INFO'
    return 'DEBUG'


def parse_log_level(level: str, default: str) -> str:
    """Parse and validate a log level string."""
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    upper = level.upper() if level else default
    return upper if upper in valid_levels else default


def format_config_key(key: str, case_style: str) -> str:
    """Format a configuration key in specified style."""
    if case_style == 'upper':
        return key.upper()
    if case_style == 'lower':
        return key.lower()
    if case_style == 'snake':
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    if case_style == 'camel':
        parts = key.replace('-', '_').split('_')
        return parts[0].lower() + ''.join(p.title() for p in parts[1:])
    return key


def sanitize_config_value(value: str) -> str:
    """Sanitize a configuration value by stripping whitespace and quotes."""
    return value.strip().strip('"').strip("'")


def mask_sensitive_value(value: str, visible_chars: int) -> str:
    """Mask a sensitive configuration value."""
    if len(value) <= visible_chars:
        return '*' * len(value)
    return value[:visible_chars] + '*' * (len(value) - visible_chars)


def is_sensitive_key(key: str) -> bool:
    """Check if a configuration key appears to be sensitive."""
    sensitive_patterns = ['password', 'secret', 'key', 'token', 'auth', 'credential', 'private']
    lower_key = key.lower()
    return any(pattern in lower_key for pattern in sensitive_patterns)


def redact_sensitive_config(config: dict) -> dict:
    """Redact sensitive values in a configuration dictionary."""
    result = {}
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = redact_sensitive_config(value)
        elif is_sensitive_key(key):
            result[key] = '[REDACTED]'
        else:
            result[key] = value
    return result


def compare_configs(config1: dict, config2: dict) -> dict:
    """Compare two configurations and return differences."""
    added = {k: v for k, v in config2.items() if k not in config1}
    removed = {k: v for k, v in config1.items() if k not in config2}
    changed = {k: {'old': config1[k], 'new': config2[k]} 
               for k in config1 if k in config2 and config1[k] != config2[k]}
    return {'added': added, 'removed': removed, 'changed': changed}


def config_has_key(config: dict, key: str) -> bool:
    """Check if a configuration has a specific key."""
    return key in config


def config_has_value(config: dict, key: str) -> bool:
    """Check if a configuration has a non-empty value for a key."""
    return key in config and config[key] not in (None, '', [])


def get_all_keys(config: dict, include_nested: bool) -> list:
    """Get all keys from a configuration."""
    keys = list(config.keys())
    if include_nested:
        for value in config.values():
            if isinstance(value, dict):
                keys.extend(get_all_keys(value, True))
    return keys
