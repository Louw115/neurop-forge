"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Semantic Version - Pure functions for semantic versioning.
All functions are pure, deterministic, and atomic.
"""

import re


def parse_version(version: str) -> dict:
    """Parse semantic version string."""
    pattern = r'^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'
    match = re.match(pattern, version)
    if not match:
        return None
    return {
        "major": int(match.group(1)),
        "minor": int(match.group(2)),
        "patch": int(match.group(3)),
        "prerelease": match.group(4) or "",
        "build": match.group(5) or ""
    }


def format_version(version: dict) -> str:
    """Format version dict to string."""
    result = f"{version['major']}.{version['minor']}.{version['patch']}"
    if version.get('prerelease'):
        result += f"-{version['prerelease']}"
    if version.get('build'):
        result += f"+{version['build']}"
    return result


def is_valid_version(version: str) -> bool:
    """Check if string is valid semantic version."""
    return parse_version(version) is not None


def compare_versions(v1: str, v2: str) -> int:
    """Compare two versions. Returns -1, 0, or 1."""
    p1 = parse_version(v1)
    p2 = parse_version(v2)
    if not p1 or not p2:
        return 0
    if p1['major'] != p2['major']:
        return -1 if p1['major'] < p2['major'] else 1
    if p1['minor'] != p2['minor']:
        return -1 if p1['minor'] < p2['minor'] else 1
    if p1['patch'] != p2['patch']:
        return -1 if p1['patch'] < p2['patch'] else 1
    pre1 = p1.get('prerelease', '')
    pre2 = p2.get('prerelease', '')
    if not pre1 and pre2:
        return 1
    if pre1 and not pre2:
        return -1
    if pre1 != pre2:
        return -1 if pre1 < pre2 else 1
    return 0


def is_greater(v1: str, v2: str) -> bool:
    """Check if v1 is greater than v2."""
    return compare_versions(v1, v2) > 0


def is_less(v1: str, v2: str) -> bool:
    """Check if v1 is less than v2."""
    return compare_versions(v1, v2) < 0


def is_equal(v1: str, v2: str) -> bool:
    """Check if versions are equal."""
    return compare_versions(v1, v2) == 0


def increment_major(version: str) -> str:
    """Increment major version."""
    p = parse_version(version)
    if not p:
        return version
    return f"{p['major'] + 1}.0.0"


def increment_minor(version: str) -> str:
    """Increment minor version."""
    p = parse_version(version)
    if not p:
        return version
    return f"{p['major']}.{p['minor'] + 1}.0"


def increment_patch(version: str) -> str:
    """Increment patch version."""
    p = parse_version(version)
    if not p:
        return version
    return f"{p['major']}.{p['minor']}.{p['patch'] + 1}"


def set_prerelease(version: str, prerelease: str) -> str:
    """Set prerelease tag."""
    p = parse_version(version)
    if not p:
        return version
    p['prerelease'] = prerelease
    return format_version(p)


def set_build(version: str, build: str) -> str:
    """Set build metadata."""
    p = parse_version(version)
    if not p:
        return version
    p['build'] = build
    return format_version(p)


def strip_prerelease(version: str) -> str:
    """Remove prerelease tag."""
    p = parse_version(version)
    if not p:
        return version
    return f"{p['major']}.{p['minor']}.{p['patch']}"


def is_prerelease(version: str) -> bool:
    """Check if version is prerelease."""
    p = parse_version(version)
    return p is not None and bool(p.get('prerelease'))


def is_stable(version: str) -> bool:
    """Check if version is stable (not prerelease)."""
    p = parse_version(version)
    return p is not None and not p.get('prerelease')


def satisfies_range(version: str, range_spec: str) -> bool:
    """Check if version satisfies simple range."""
    if range_spec.startswith('>='):
        return not is_less(version, range_spec[2:].strip())
    if range_spec.startswith('<='):
        return not is_greater(version, range_spec[2:].strip())
    if range_spec.startswith('>'):
        return is_greater(version, range_spec[1:].strip())
    if range_spec.startswith('<'):
        return is_less(version, range_spec[1:].strip())
    if range_spec.startswith('='):
        return is_equal(version, range_spec[1:].strip())
    if range_spec.startswith('^'):
        base = parse_version(range_spec[1:].strip())
        v = parse_version(version)
        if not base or not v:
            return False
        if v['major'] != base['major']:
            return False
        return not is_less(version, range_spec[1:].strip())
    if range_spec.startswith('~'):
        base = parse_version(range_spec[1:].strip())
        v = parse_version(version)
        if not base or not v:
            return False
        if v['major'] != base['major'] or v['minor'] != base['minor']:
            return False
        return not is_less(version, range_spec[1:].strip())
    return is_equal(version, range_spec)


def max_version(versions: list) -> str:
    """Find maximum version in list."""
    if not versions:
        return None
    max_v = versions[0]
    for v in versions[1:]:
        if is_greater(v, max_v):
            max_v = v
    return max_v


def min_version(versions: list) -> str:
    """Find minimum version in list."""
    if not versions:
        return None
    min_v = versions[0]
    for v in versions[1:]:
        if is_less(v, min_v):
            min_v = v
    return min_v


def sort_versions(versions: list, descending: bool) -> list:
    """Sort versions."""
    sorted_list = sorted(versions, key=lambda v: (
        parse_version(v)['major'],
        parse_version(v)['minor'],
        parse_version(v)['patch']
    ) if parse_version(v) else (0, 0, 0))
    return list(reversed(sorted_list)) if descending else sorted_list


def diff_versions(v1: str, v2: str) -> dict:
    """Get difference between versions."""
    p1 = parse_version(v1)
    p2 = parse_version(v2)
    if not p1 or not p2:
        return {"type": "invalid"}
    if p1['major'] != p2['major']:
        return {"type": "major", "from": v1, "to": v2}
    if p1['minor'] != p2['minor']:
        return {"type": "minor", "from": v1, "to": v2}
    if p1['patch'] != p2['patch']:
        return {"type": "patch", "from": v1, "to": v2}
    return {"type": "none", "from": v1, "to": v2}
