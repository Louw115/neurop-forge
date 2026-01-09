"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Network Utilities - Pure functions for network and IP patterns.
All functions are pure, deterministic, and atomic.
"""

def validate_ipv4(ip: str) -> bool:
    """Validate IPv4 address."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True


def validate_ipv6(ip: str) -> bool:
    """Validate IPv6 address (simplified)."""
    if "::" in ip:
        parts = ip.split("::")
        if len(parts) > 2:
            return False
    groups = ip.replace("::", ":").split(":")
    for group in groups:
        if group and len(group) > 4:
            return False
        if group:
            try:
                int(group, 16)
            except ValueError:
                return False
    return True


def ip_to_int(ip: str) -> int:
    """Convert IPv4 address to integer."""
    parts = ip.split(".")
    return sum(int(p) << (24 - 8 * i) for i, p in enumerate(parts))


def int_to_ip(num: int) -> str:
    """Convert integer to IPv4 address."""
    return ".".join(str((num >> (24 - 8 * i)) & 255) for i in range(4))


def parse_cidr(cidr: str) -> dict:
    """Parse CIDR notation."""
    if "/" not in cidr:
        return {"network": cidr, "prefix": 32, "valid": validate_ipv4(cidr)}
    parts = cidr.split("/")
    network = parts[0]
    prefix = int(parts[1])
    return {
        "network": network,
        "prefix": prefix,
        "valid": validate_ipv4(network) and 0 <= prefix <= 32
    }


def calculate_subnet_mask(prefix: int) -> str:
    """Calculate subnet mask from prefix length."""
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return int_to_ip(mask)


def calculate_network_address(ip: str, prefix: int) -> str:
    """Calculate network address from IP and prefix."""
    ip_int = ip_to_int(ip)
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return int_to_ip(ip_int & mask)


def calculate_broadcast_address(ip: str, prefix: int) -> str:
    """Calculate broadcast address from IP and prefix."""
    ip_int = ip_to_int(ip)
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    broadcast = ip_int | (~mask & 0xFFFFFFFF)
    return int_to_ip(broadcast)


def calculate_host_count(prefix: int) -> int:
    """Calculate number of usable hosts in subnet."""
    if prefix >= 31:
        return 0
    return (2 ** (32 - prefix)) - 2


def is_ip_in_subnet(ip: str, cidr: str) -> bool:
    """Check if IP is in subnet."""
    parsed = parse_cidr(cidr)
    if not parsed["valid"]:
        return False
    network = calculate_network_address(parsed["network"], parsed["prefix"])
    ip_network = calculate_network_address(ip, parsed["prefix"])
    return network == ip_network


def is_private_ip(ip: str) -> bool:
    """Check if IP is in private range."""
    private_ranges = [
        ("10.0.0.0", 8),
        ("172.16.0.0", 12),
        ("192.168.0.0", 16),
        ("127.0.0.0", 8)
    ]
    for network, prefix in private_ranges:
        if is_ip_in_subnet(ip, f"{network}/{prefix}"):
            return True
    return False


def is_loopback_ip(ip: str) -> bool:
    """Check if IP is loopback."""
    return is_ip_in_subnet(ip, "127.0.0.0/8")


def validate_port(port: int) -> bool:
    """Validate port number."""
    return 0 <= port <= 65535


def is_privileged_port(port: int) -> bool:
    """Check if port is privileged (< 1024)."""
    return 0 < port < 1024


def get_service_port(service: str) -> int:
    """Get standard port for common services."""
    ports = {
        "http": 80, "https": 443, "ftp": 21, "ssh": 22, "telnet": 23,
        "smtp": 25, "dns": 53, "pop3": 110, "imap": 143, "mysql": 3306,
        "postgresql": 5432, "redis": 6379, "mongodb": 27017
    }
    return ports.get(service.lower(), 0)


def build_socket_address(host: str, port: int) -> str:
    """Build socket address string."""
    if ":" in host:
        return f"[{host}]:{port}"
    return f"{host}:{port}"


def parse_socket_address(address: str) -> dict:
    """Parse socket address string."""
    if address.startswith("["):
        end = address.find("]")
        host = address[1:end]
        port = int(address[end + 2:]) if end + 2 < len(address) else 0
    else:
        parts = address.rsplit(":", 1)
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 0
    return {"host": host, "port": port}


def validate_mac_address(mac: str) -> bool:
    """Validate MAC address."""
    import re
    patterns = [
        r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$',
        r'^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$',
        r'^[0-9A-Fa-f]{12}$'
    ]
    return any(re.match(p, mac) for p in patterns)


def normalize_mac_address(mac: str, separator: str) -> str:
    """Normalize MAC address format."""
    clean = mac.replace(":", "").replace("-", "").lower()
    if len(clean) != 12:
        return mac
    return separator.join(clean[i:i+2] for i in range(0, 12, 2))


def calculate_bandwidth(bytes_count: int, seconds: float) -> float:
    """Calculate bandwidth in Mbps."""
    if seconds <= 0:
        return 0.0
    return (bytes_count * 8) / (seconds * 1000000)


def format_bandwidth(mbps: float) -> str:
    """Format bandwidth for display."""
    if mbps >= 1000:
        return f"{mbps / 1000:.2f} Gbps"
    return f"{mbps:.2f} Mbps"


def calculate_transfer_time(size_bytes: int, bandwidth_mbps: float) -> float:
    """Calculate transfer time in seconds."""
    if bandwidth_mbps <= 0:
        return 0.0
    bits = size_bytes * 8
    return bits / (bandwidth_mbps * 1000000)


def calculate_latency_stats(latencies: list) -> dict:
    """Calculate latency statistics."""
    if not latencies:
        return {"min": 0, "max": 0, "avg": 0, "jitter": 0}
    sorted_latencies = sorted(latencies)
    avg = sum(latencies) / len(latencies)
    jitter = sum(abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))) / max(1, len(latencies) - 1)
    return {
        "min": sorted_latencies[0],
        "max": sorted_latencies[-1],
        "avg": avg,
        "jitter": jitter
    }


def build_dns_record(record_type: str, name: str, value: str, ttl: int) -> dict:
    """Build a DNS record."""
    return {
        "type": record_type.upper(),
        "name": name,
        "value": value,
        "ttl": ttl
    }


def validate_hostname(hostname: str) -> bool:
    """Validate hostname."""
    import re
    if len(hostname) > 253:
        return False
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}$'
    return bool(re.match(pattern, hostname))


def extract_domain(hostname: str) -> str:
    """Extract domain from hostname."""
    parts = hostname.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return hostname


def extract_subdomain(hostname: str) -> str:
    """Extract subdomain from hostname."""
    parts = hostname.split(".")
    if len(parts) > 2:
        return ".".join(parts[:-2])
    return ""


def is_tld(part: str) -> bool:
    """Check if part is a TLD."""
    common_tlds = {"com", "org", "net", "edu", "gov", "io", "co", "app", "dev"}
    return part.lower() in common_tlds
