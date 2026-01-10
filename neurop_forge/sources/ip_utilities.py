"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
IP Utilities - Pure functions for IP address manipulation.
All functions are pure, deterministic, and atomic.
"""

import re


def is_valid_ipv4(ip: str) -> bool:
    """Check if string is valid IPv4 address."""
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip)
    if not match:
        return False
    return all(0 <= int(g) <= 255 for g in match.groups())


def is_valid_ipv6(ip: str) -> bool:
    """Check if string is valid IPv6 address."""
    pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    if re.match(pattern, ip):
        return True
    if '::' in ip:
        parts = ip.split('::')
        if len(parts) != 2:
            return False
        left = parts[0].split(':') if parts[0] else []
        right = parts[1].split(':') if parts[1] else []
        if len(left) + len(right) > 7:
            return False
        return all(len(p) <= 4 and all(c in '0123456789abcdefABCDEF' for c in p) 
                   for p in left + right if p)
    return False


def ipv4_to_int(ip: str) -> int:
    """Convert IPv4 to integer."""
    parts = ip.split('.')
    return sum(int(part) << (24 - i * 8) for i, part in enumerate(parts))


def int_to_ipv4(num: int) -> str:
    """Convert integer to IPv4."""
    return '.'.join(str((num >> (24 - i * 8)) & 255) for i in range(4))


def ipv4_to_binary(ip: str) -> str:
    """Convert IPv4 to binary string."""
    parts = ip.split('.')
    return ''.join(format(int(p), '08b') for p in parts)


def is_private_ip(ip: str) -> bool:
    """Check if IP is in private range."""
    parts = [int(p) for p in ip.split('.')]
    if parts[0] == 10:
        return True
    if parts[0] == 172 and 16 <= parts[1] <= 31:
        return True
    if parts[0] == 192 and parts[1] == 168:
        return True
    return False


def is_loopback(ip: str) -> bool:
    """Check if IP is loopback address."""
    if ip.startswith('127.'):
        return True
    return ip == '::1'


def is_link_local(ip: str) -> bool:
    """Check if IP is link-local."""
    parts = [int(p) for p in ip.split('.')]
    return parts[0] == 169 and parts[1] == 254


def is_multicast(ip: str) -> bool:
    """Check if IP is multicast address."""
    first = int(ip.split('.')[0])
    return 224 <= first <= 239


def is_broadcast(ip: str) -> bool:
    """Check if IP is broadcast address."""
    return ip == '255.255.255.255'


def get_network_address(ip: str, cidr: int) -> str:
    """Get network address from IP and CIDR."""
    ip_int = ipv4_to_int(ip)
    mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    return int_to_ipv4(ip_int & mask)


def get_broadcast_address(ip: str, cidr: int) -> str:
    """Get broadcast address from IP and CIDR."""
    ip_int = ipv4_to_int(ip)
    mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    host_mask = ~mask & 0xFFFFFFFF
    return int_to_ipv4((ip_int & mask) | host_mask)


def cidr_to_netmask(cidr: int) -> str:
    """Convert CIDR notation to subnet mask."""
    mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    return int_to_ipv4(mask)


def netmask_to_cidr(netmask: str) -> int:
    """Convert subnet mask to CIDR notation."""
    binary = ipv4_to_binary(netmask)
    return binary.count('1')


def ip_in_cidr(ip: str, cidr_range: str) -> bool:
    """Check if IP is in CIDR range."""
    network, prefix = cidr_range.split('/')
    prefix = int(prefix)
    ip_network = get_network_address(ip, prefix)
    range_network = get_network_address(network, prefix)
    return ip_network == range_network


def get_host_count(cidr: int) -> int:
    """Get number of usable hosts in subnet."""
    if cidr >= 31:
        return 2 ** (32 - cidr)
    return 2 ** (32 - cidr) - 2


def get_first_host(ip: str, cidr: int) -> str:
    """Get first usable host address."""
    network = get_network_address(ip, cidr)
    return int_to_ipv4(ipv4_to_int(network) + 1)


def get_last_host(ip: str, cidr: int) -> str:
    """Get last usable host address."""
    broadcast = get_broadcast_address(ip, cidr)
    return int_to_ipv4(ipv4_to_int(broadcast) - 1)


def ip_range(start: str, end: str) -> list:
    """Generate list of IPs in range."""
    start_int = ipv4_to_int(start)
    end_int = ipv4_to_int(end)
    return [int_to_ipv4(i) for i in range(start_int, end_int + 1)]


def increment_ip(ip: str, amount: int) -> str:
    """Increment IP address by amount."""
    return int_to_ipv4(ipv4_to_int(ip) + amount)


def compare_ips(ip1: str, ip2: str) -> int:
    """Compare two IP addresses. Returns -1, 0, or 1."""
    int1 = ipv4_to_int(ip1)
    int2 = ipv4_to_int(ip2)
    if int1 < int2:
        return -1
    elif int1 > int2:
        return 1
    return 0


def expand_ipv6(ip: str) -> str:
    """Expand abbreviated IPv6 address."""
    if '::' not in ip:
        return ip.lower()
    left, right = ip.split('::')
    left_parts = left.split(':') if left else []
    right_parts = right.split(':') if right else []
    missing = 8 - len(left_parts) - len(right_parts)
    middle = ['0000'] * missing
    all_parts = left_parts + middle + right_parts
    return ':'.join(p.zfill(4) for p in all_parts).lower()


def compress_ipv6(ip: str) -> str:
    """Compress IPv6 address to shortest form."""
    expanded = expand_ipv6(ip)
    parts = [p.lstrip('0') or '0' for p in expanded.split(':')]
    best_start = -1
    best_len = 0
    current_start = -1
    current_len = 0
    for i, p in enumerate(parts):
        if p == '0':
            if current_start == -1:
                current_start = i
            current_len += 1
        else:
            if current_len > best_len:
                best_start = current_start
                best_len = current_len
            current_start = -1
            current_len = 0
    if current_len > best_len:
        best_start = current_start
        best_len = current_len
    if best_len > 1:
        before = ':'.join(parts[:best_start])
        after = ':'.join(parts[best_start + best_len:])
        return f"{before}::{after}"
    return ':'.join(parts)
