"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Email Utilities - Pure functions for email validation and parsing.

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)
- Atomic (one intent per function)

License: MIT
"""

import re


def is_valid_email(email: str) -> bool:
    """Check if a string is a valid email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_email_strict(email: str) -> bool:
    """Strictly validate email format (no consecutive dots, no leading/trailing dots)."""
    if '..' in email:
        return False
    local, _, domain = email.partition('@')
    if not local or not domain:
        return False
    if local.startswith('.') or local.endswith('.'):
        return False
    if domain.startswith('.') or domain.endswith('.'):
        return False
    return is_valid_email(email)


def extract_local_part(email: str) -> str:
    """Extract the local part (before @) of an email."""
    parts = email.split('@')
    return parts[0] if len(parts) == 2 else ""


def extract_domain(email: str) -> str:
    """Extract the domain (after @) of an email."""
    parts = email.split('@')
    return parts[1].lower() if len(parts) == 2 else ""


def extract_tld(email: str) -> str:
    """Extract the top-level domain from an email."""
    domain = extract_domain(email)
    if not domain:
        return ""
    parts = domain.split('.')
    return parts[-1] if parts else ""


def normalize_email(email: str) -> str:
    """Normalize an email to lowercase."""
    return email.lower().strip()


def normalize_gmail(email: str) -> str:
    """Normalize Gmail address (remove dots and plus addressing)."""
    if not is_valid_email(email):
        return email
    local, domain = email.split('@')
    if domain.lower() in ['gmail.com', 'googlemail.com']:
        local = local.split('+')[0]
        local = local.replace('.', '')
        domain = 'gmail.com'
    return f"{local}@{domain}".lower()


def has_plus_addressing(email: str) -> bool:
    """Check if email uses plus addressing (user+tag@domain)."""
    local = extract_local_part(email)
    return '+' in local


def extract_plus_tag(email: str) -> str:
    """Extract the plus tag from an email."""
    local = extract_local_part(email)
    if '+' in local:
        return local.split('+')[1]
    return ""


def remove_plus_addressing(email: str) -> str:
    """Remove plus addressing from email."""
    if not is_valid_email(email):
        return email
    local, domain = email.split('@')
    local = local.split('+')[0]
    return f"{local}@{domain}"


def is_disposable_domain(domain: str, disposable_domains: list) -> bool:
    """Check if a domain is in a list of disposable email domains."""
    return domain.lower() in [d.lower() for d in disposable_domains]


def is_free_email_provider(domain: str) -> bool:
    """Check if a domain is a free email provider."""
    free_providers = [
        'gmail.com', 'googlemail.com', 'yahoo.com', 'yahoo.co.uk',
        'hotmail.com', 'hotmail.co.uk', 'outlook.com', 'live.com',
        'aol.com', 'mail.com', 'protonmail.com', 'icloud.com',
        'zoho.com', 'yandex.com', 'gmx.com', 'fastmail.com'
    ]
    return domain.lower() in free_providers


def is_business_email(email: str) -> bool:
    """Check if an email appears to be a business email (not free provider)."""
    domain = extract_domain(email)
    return not is_free_email_provider(domain) and is_valid_email(email)


def mask_email(email: str) -> str:
    """Mask an email address for privacy."""
    if not is_valid_email(email):
        return email
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_email_domain(email: str) -> str:
    """Mask both local and domain parts."""
    if not is_valid_email(email):
        return email
    local, domain = email.split('@')
    domain_parts = domain.split('.')
    masked_local = local[0] + '***' if local else '***'
    masked_domain = domain_parts[0][0] + '***.' + domain_parts[-1] if domain_parts else '***'
    return f"{masked_local}@{masked_domain}"


def generate_email_hash(email: str) -> str:
    """Generate a hash of the normalized email for comparison."""
    import hashlib
    normalized = normalize_email(email)
    return hashlib.sha256(normalized.encode()).hexdigest()


def emails_match(email1: str, email2: str) -> bool:
    """Check if two emails match (case-insensitive)."""
    return normalize_email(email1) == normalize_email(email2)


def format_display_email(name: str, email: str) -> str:
    """Format email with display name."""
    if not name:
        return email
    if any(c in name for c in '",<>'):
        name = f'"{name}"'
    return f"{name} <{email}>"


def parse_display_email(formatted: str) -> dict:
    """Parse a formatted email (Name <email>) into parts."""
    match = re.match(r'^(?:"?([^"]*)"?\s+)?<?([^<>]+@[^<>]+)>?$', formatted.strip())
    if match:
        return {'name': match.group(1) or '', 'email': match.group(2)}
    return {'name': '', 'email': formatted}


def extract_emails_from_text(text: str) -> list:
    """Extract all email addresses from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def count_emails_in_text(text: str) -> int:
    """Count email addresses in text."""
    return len(extract_emails_from_text(text))


def is_valid_subdomain_email(email: str) -> bool:
    """Check if email has valid subdomain structure."""
    domain = extract_domain(email)
    parts = domain.split('.')
    return len(parts) >= 2 and all(len(p) > 0 for p in parts)


def get_email_provider_name(email: str) -> str:
    """Get a human-readable provider name."""
    domain = extract_domain(email).lower()
    providers = {
        'gmail.com': 'Gmail',
        'googlemail.com': 'Gmail',
        'yahoo.com': 'Yahoo',
        'hotmail.com': 'Hotmail',
        'outlook.com': 'Outlook',
        'live.com': 'Microsoft Live',
        'icloud.com': 'iCloud',
        'protonmail.com': 'ProtonMail',
        'aol.com': 'AOL'
    }
    return providers.get(domain, domain.split('.')[0].capitalize())


def split_email_list(email_string: str, delimiter: str) -> list:
    """Split a delimited string of emails into a list."""
    emails = email_string.split(delimiter)
    return [e.strip() for e in emails if e.strip()]


def join_email_list(emails: list, delimiter: str) -> str:
    """Join a list of emails into a delimited string."""
    return delimiter.join(emails)


def validate_email_list(emails: list) -> dict:
    """Validate a list of emails and return results."""
    valid = [e for e in emails if is_valid_email(e)]
    invalid = [e for e in emails if not is_valid_email(e)]
    return {'valid': valid, 'invalid': invalid, 'valid_count': len(valid), 'invalid_count': len(invalid)}


def deduplicate_emails(emails: list) -> list:
    """Remove duplicate emails (case-insensitive)."""
    seen = set()
    result = []
    for email in emails:
        normalized = normalize_email(email)
        if normalized not in seen:
            seen.add(normalized)
            result.append(email)
    return result


def sort_emails_by_domain(emails: list) -> list:
    """Sort emails by domain, then by local part."""
    return sorted(emails, key=lambda e: (extract_domain(e), extract_local_part(e).lower()))


def group_emails_by_domain(emails: list) -> dict:
    """Group emails by their domain."""
    groups = {}
    for email in emails:
        domain = extract_domain(email)
        if domain not in groups:
            groups[domain] = []
        groups[domain].append(email)
    return groups


def is_role_based_email(email: str) -> bool:
    """Check if email is a role-based address (info@, support@, etc.)."""
    role_prefixes = [
        'info', 'support', 'sales', 'admin', 'contact', 'help',
        'webmaster', 'postmaster', 'hostmaster', 'abuse', 'noreply',
        'no-reply', 'marketing', 'team', 'hello', 'office', 'hr'
    ]
    local = extract_local_part(email).lower()
    return local in role_prefixes


def generate_reply_to(original_email: str, reply_domain: str) -> str:
    """Generate a reply-to address."""
    local = extract_local_part(original_email)
    return f"reply+{local}@{reply_domain}"


def parse_email_header_list(header: str) -> list:
    """Parse a comma-separated email header into list of addresses."""
    emails = []
    for part in header.split(','):
        parsed = parse_display_email(part)
        if parsed['email']:
            emails.append(parsed)
    return emails


def format_email_header_list(addresses: list) -> str:
    """Format a list of addresses for email header."""
    formatted = []
    for addr in addresses:
        if isinstance(addr, dict):
            formatted.append(format_display_email(addr.get('name', ''), addr.get('email', '')))
        else:
            formatted.append(str(addr))
    return ', '.join(formatted)


def is_valid_mx_domain_format(domain: str) -> bool:
    """Check if domain format could have MX records (basic validation)."""
    if not domain or '.' not in domain:
        return False
    parts = domain.split('.')
    return all(re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', p) for p in parts)


def sanitize_email_for_display(email: str) -> str:
    """Sanitize email for safe display (escape HTML entities)."""
    return email.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_mailto_link(email: str, subject: str, body: str) -> str:
    """Build a mailto: link."""
    from urllib.parse import quote
    link = f"mailto:{email}"
    params = []
    if subject:
        params.append(f"subject={quote(subject)}")
    if body:
        params.append(f"body={quote(body)}")
    if params:
        link += '?' + '&'.join(params)
    return link


def parse_mailto_link(link: str) -> dict:
    """Parse a mailto: link into components."""
    from urllib.parse import unquote, urlparse, parse_qs
    if not link.startswith('mailto:'):
        return {}
    parsed = urlparse(link)
    email = parsed.path
    query = parse_qs(parsed.query)
    return {
        'email': email,
        'subject': unquote(query.get('subject', [''])[0]),
        'body': unquote(query.get('body', [''])[0]),
        'cc': query.get('cc', []),
        'bcc': query.get('bcc', [])
    }
