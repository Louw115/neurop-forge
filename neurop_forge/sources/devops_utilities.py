"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
DevOps Utilities - Pure functions for CI/CD and deployment patterns.
All functions are pure, deterministic, and atomic.
"""

def parse_semver(version: str) -> dict:
    """Parse a semantic version string."""
    import re
    pattern = r'^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'
    match = re.match(pattern, version)
    if not match:
        return {"valid": False, "major": 0, "minor": 0, "patch": 0}
    return {
        "valid": True,
        "major": int(match.group(1)),
        "minor": int(match.group(2)),
        "patch": int(match.group(3)),
        "prerelease": match.group(4) or "",
        "build": match.group(5) or ""
    }


def format_semver(major: int, minor: int, patch: int, prerelease: str, build: str) -> str:
    """Format a semantic version string."""
    version = f"{major}.{minor}.{patch}"
    if prerelease:
        version += f"-{prerelease}"
    if build:
        version += f"+{build}"
    return version


def compare_semver(v1: str, v2: str) -> int:
    """Compare two semantic versions. Returns -1, 0, or 1."""
    p1 = parse_semver(v1)
    p2 = parse_semver(v2)
    for key in ["major", "minor", "patch"]:
        if p1[key] < p2[key]:
            return -1
        if p1[key] > p2[key]:
            return 1
    return 0


def increment_semver(version: str, increment_type: str) -> str:
    """Increment a semantic version."""
    parsed = parse_semver(version)
    if not parsed["valid"]:
        return version
    if increment_type == "major":
        return format_semver(parsed["major"] + 1, 0, 0, "", "")
    elif increment_type == "minor":
        return format_semver(parsed["major"], parsed["minor"] + 1, 0, "", "")
    elif increment_type == "patch":
        return format_semver(parsed["major"], parsed["minor"], parsed["patch"] + 1, "", "")
    return version


def is_breaking_change(old_version: str, new_version: str) -> bool:
    """Check if version change is a breaking change (major bump)."""
    old = parse_semver(old_version)
    new = parse_semver(new_version)
    return new["major"] > old["major"]


def generate_build_number(timestamp: str, commit_hash: str) -> str:
    """Generate a build number from timestamp and commit."""
    date_part = timestamp[:10].replace("-", "")
    commit_part = commit_hash[:7] if commit_hash else "0000000"
    return f"{date_part}.{commit_part}"


def parse_git_commit_hash(commit: str) -> dict:
    """Parse a git commit hash."""
    import re
    if re.match(r'^[0-9a-f]{40}$', commit.lower()):
        return {"valid": True, "full": commit.lower(), "short": commit[:7].lower()}
    if re.match(r'^[0-9a-f]{7,}$', commit.lower()):
        return {"valid": True, "full": None, "short": commit[:7].lower()}
    return {"valid": False, "full": None, "short": None}


def format_git_tag(version: str, prefix: str) -> str:
    """Format a git tag from version."""
    return f"{prefix}{version}"


def parse_git_tag(tag: str, prefix: str) -> str:
    """Parse version from a git tag."""
    if tag.startswith(prefix):
        return tag[len(prefix):]
    return tag


def build_docker_image_tag(registry: str, repository: str, tag: str) -> str:
    """Build a full Docker image tag."""
    if registry:
        return f"{registry}/{repository}:{tag}"
    return f"{repository}:{tag}"


def parse_docker_image_tag(full_tag: str) -> dict:
    """Parse a Docker image tag into components."""
    parts = full_tag.split("/")
    if len(parts) == 1:
        repo_tag = parts[0]
        registry = ""
    elif len(parts) == 2:
        if "." in parts[0] or ":" in parts[0]:
            registry = parts[0]
            repo_tag = parts[1]
        else:
            registry = ""
            repo_tag = full_tag
    else:
        registry = parts[0]
        repo_tag = "/".join(parts[1:])
    if ":" in repo_tag:
        repository, tag = repo_tag.rsplit(":", 1)
    else:
        repository, tag = repo_tag, "latest"
    return {"registry": registry, "repository": repository, "tag": tag}


def generate_dockerfile_from(base_image: str, tag: str) -> str:
    """Generate a Dockerfile FROM instruction."""
    return f"FROM {base_image}:{tag}"


def generate_dockerfile_copy(src: str, dest: str) -> str:
    """Generate a Dockerfile COPY instruction."""
    return f"COPY {src} {dest}"


def generate_dockerfile_run(command: str) -> str:
    """Generate a Dockerfile RUN instruction."""
    return f"RUN {command}"


def generate_dockerfile_env(key: str, value: str) -> str:
    """Generate a Dockerfile ENV instruction."""
    return f'ENV {key}="{value}"'


def generate_dockerfile_expose(port: int) -> str:
    """Generate a Dockerfile EXPOSE instruction."""
    return f"EXPOSE {port}"


def generate_dockerfile_cmd(command: list) -> str:
    """Generate a Dockerfile CMD instruction."""
    import json
    return f"CMD {json.dumps(command)}"


def generate_dockerfile_entrypoint(command: list) -> str:
    """Generate a Dockerfile ENTRYPOINT instruction."""
    import json
    return f"ENTRYPOINT {json.dumps(command)}"


def generate_dockerfile_workdir(path: str) -> str:
    """Generate a Dockerfile WORKDIR instruction."""
    return f"WORKDIR {path}"


def build_env_file_content(env_vars: dict) -> str:
    """Build .env file content from dictionary."""
    lines = []
    for key, value in sorted(env_vars.items()):
        if " " in str(value) or "=" in str(value):
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines)


def parse_env_file_content(content: str) -> dict:
    """Parse .env file content into dictionary."""
    result = {}
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            result[key.strip()] = value
    return result


def calculate_deployment_window(start_hour: int, end_hour: int, current_hour: int) -> bool:
    """Check if current hour is within deployment window."""
    if start_hour <= end_hour:
        return start_hour <= current_hour < end_hour
    return current_hour >= start_hour or current_hour < end_hour


def is_deployment_frozen(freeze_periods: list, current_date: str) -> bool:
    """Check if current date is in a freeze period."""
    for period in freeze_periods:
        if period.get("start") <= current_date <= period.get("end"):
            return True
    return False


def calculate_rollout_percentage(current_step: int, total_steps: int) -> float:
    """Calculate gradual rollout percentage."""
    if total_steps <= 0:
        return 100.0
    return min(100.0, (current_step / total_steps) * 100)


def build_health_check_config(path: str, port: int, interval_seconds: int, timeout_seconds: int, retries: int) -> dict:
    """Build a health check configuration."""
    return {
        "path": path,
        "port": port,
        "interval": interval_seconds,
        "timeout": timeout_seconds,
        "retries": retries,
        "type": "http"
    }


def is_healthy(health_checks: list) -> bool:
    """Check if all health checks are passing."""
    return all(check.get("status") == "healthy" for check in health_checks)


def calculate_uptime_percentage(uptime_seconds: int, total_seconds: int) -> float:
    """Calculate uptime percentage."""
    if total_seconds <= 0:
        return 100.0
    return (uptime_seconds / total_seconds) * 100


def format_uptime(seconds: int) -> str:
    """Format uptime in human-readable form."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def build_resource_limits(cpu_cores: float, memory_mb: int) -> dict:
    """Build resource limits configuration."""
    return {
        "cpu": f"{cpu_cores}",
        "memory": f"{memory_mb}Mi"
    }


def calculate_replica_count(target_cpu_percent: int, current_cpu_percent: int, current_replicas: int, min_replicas: int, max_replicas: int) -> int:
    """Calculate desired replica count for autoscaling."""
    if current_cpu_percent <= 0:
        return current_replicas
    ratio = current_cpu_percent / target_cpu_percent
    desired = int(current_replicas * ratio)
    return max(min_replicas, min(max_replicas, desired))


def should_scale_up(current_cpu: float, threshold: float, cooldown_remaining: int) -> bool:
    """Check if should scale up."""
    return current_cpu > threshold and cooldown_remaining <= 0


def should_scale_down(current_cpu: float, threshold: float, cooldown_remaining: int) -> bool:
    """Check if should scale down."""
    return current_cpu < threshold and cooldown_remaining <= 0


def build_deployment_manifest(name: str, image: str, replicas: int, port: int, env_vars: dict) -> dict:
    """Build a deployment manifest."""
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": name},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": {"app": name}},
                "spec": {
                    "containers": [{
                        "name": name,
                        "image": image,
                        "ports": [{"containerPort": port}],
                        "env": [{"name": k, "value": v} for k, v in env_vars.items()]
                    }]
                }
            }
        }
    }


def build_service_manifest(name: str, port: int, target_port: int, service_type: str) -> dict:
    """Build a service manifest."""
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": name},
        "spec": {
            "type": service_type,
            "ports": [{"port": port, "targetPort": target_port}],
            "selector": {"app": name}
        }
    }


def format_deployment_status(name: str, ready: int, desired: int, updated: int) -> str:
    """Format deployment status for display."""
    return f"{name}: {ready}/{desired} ready, {updated} updated"


def is_deployment_complete(ready: int, desired: int, updated: int) -> bool:
    """Check if deployment is complete."""
    return ready == desired == updated and desired > 0


def calculate_deployment_progress(ready: int, desired: int) -> float:
    """Calculate deployment progress percentage."""
    if desired <= 0:
        return 0.0
    return (ready / desired) * 100


def build_pipeline_stage(name: str, commands: list, depends_on: list) -> dict:
    """Build a CI/CD pipeline stage."""
    return {
        "name": name,
        "commands": commands,
        "depends_on": depends_on,
        "status": "pending"
    }


def get_pipeline_order(stages: list) -> list:
    """Get execution order for pipeline stages (topological sort)."""
    result = []
    remaining = list(stages)
    completed = set()
    while remaining:
        for stage in remaining[:]:
            deps = set(stage.get("depends_on", []))
            if deps.issubset(completed):
                result.append(stage["name"])
                completed.add(stage["name"])
                remaining.remove(stage)
                break
        else:
            break
    return result


def is_pipeline_blocked(stage: dict, completed_stages: set) -> bool:
    """Check if a pipeline stage is blocked by dependencies."""
    deps = set(stage.get("depends_on", []))
    return not deps.issubset(completed_stages)
