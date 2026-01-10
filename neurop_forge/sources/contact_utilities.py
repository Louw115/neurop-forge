"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Contact Utilities - Pure functions for contact information.
All functions are pure, deterministic, and atomic.
"""

import re


def create_contact(name: str, email: str, phone: str) -> dict:
    """Create contact record."""
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "active": True
    }


def format_full_name(first: str, last: str) -> str:
    """Format full name."""
    return f"{first} {last}".strip()


def parse_full_name(name: str) -> dict:
    """Parse full name into parts."""
    parts = name.strip().split()
    if len(parts) == 0:
        return {"first": "", "last": ""}
    if len(parts) == 1:
        return {"first": parts[0], "last": ""}
    return {"first": parts[0], "last": " ".join(parts[1:])}


def format_name_last_first(first: str, last: str) -> str:
    """Format name as Last, First."""
    if last and first:
        return f"{last}, {first}"
    return last or first


def get_initials_from_name(name: str) -> str:
    """Get initials from full name."""
    words = name.split()
    return "".join(w[0].upper() for w in words if w)[:2]


def normalize_contact_name(name: str) -> str:
    """Normalize contact name."""
    return " ".join(w.capitalize() for w in name.split())


def format_vcard_name(first: str, last: str) -> str:
    """Format name for vCard."""
    return f"{last};{first};;;"


def validate_contact(contact: dict) -> dict:
    """Validate contact record."""
    errors = []
    if not contact.get("name"):
        errors.append("Name is required")
    if not contact.get("email") and not contact.get("phone"):
        errors.append("Email or phone required")
    return {"valid": len(errors) == 0, "errors": errors}


def merge_contacts(primary: dict, secondary: dict) -> dict:
    """Merge two contacts preferring primary."""
    return {
        "name": primary.get("name") or secondary.get("name"),
        "email": primary.get("email") or secondary.get("email"),
        "phone": primary.get("phone") or secondary.get("phone"),
        "active": primary.get("active", secondary.get("active", True))
    }


def mask_contact_email(contact: dict) -> dict:
    """Mask email in contact."""
    email = contact.get("email", "")
    if "@" in email:
        local, domain = email.rsplit("@", 1)
        masked = local[0] + "***" + "@" + domain
    else:
        masked = email
    return {**contact, "email": masked}


def mask_contact_phone(contact: dict) -> dict:
    """Mask phone in contact."""
    phone = contact.get("phone", "")
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 4:
        masked = "***-***-" + digits[-4:]
    else:
        masked = "***"
    return {**contact, "phone": masked}


def format_mailto_link(email: str, subject: str) -> str:
    """Format mailto link with subject."""
    from urllib.parse import quote
    return f"mailto:{email}?subject={quote(subject)}"


def format_tel_link(phone: str) -> str:
    """Format tel link."""
    digits = re.sub(r'\D', '', phone)
    return f"tel:+{digits}"


def compare_contacts(c1: dict, c2: dict) -> bool:
    """Compare if contacts are same person."""
    if c1.get("email") and c2.get("email"):
        return c1["email"].lower() == c2["email"].lower()
    if c1.get("phone") and c2.get("phone"):
        return re.sub(r'\D', '', c1["phone"]) == re.sub(r'\D', '', c2["phone"])
    return c1.get("name", "").lower() == c2.get("name", "").lower()


def dedupe_contacts(contacts: list) -> list:
    """Remove duplicate contacts."""
    seen_emails = set()
    result = []
    for contact in contacts:
        email = contact.get("email", "").lower()
        if email and email in seen_emails:
            continue
        if email:
            seen_emails.add(email)
        result.append(contact)
    return result


def search_contacts(contacts: list, query: str) -> list:
    """Search contacts by name/email/phone."""
    query_lower = query.lower()
    return [c for c in contacts if 
            query_lower in c.get("name", "").lower() or
            query_lower in c.get("email", "").lower() or
            query in c.get("phone", "")]


def sort_contacts_by_name(contacts: list, ascending: bool) -> list:
    """Sort contacts by name."""
    return sorted(contacts, key=lambda c: c.get("name", "").lower(), reverse=not ascending)


def group_contacts_by_letter(contacts: list) -> dict:
    """Group contacts by first letter."""
    groups = {}
    for contact in contacts:
        name = contact.get("name", "")
        letter = name[0].upper() if name else "#"
        if letter not in groups:
            groups[letter] = []
        groups[letter].append(contact)
    return groups


def export_contacts_csv_row(contact: dict) -> str:
    """Export contact as CSV row."""
    name = contact.get("name", "").replace('"', '""')
    email = contact.get("email", "").replace('"', '""')
    phone = contact.get("phone", "").replace('"', '""')
    return f'"{name}","{email}","{phone}"'


def import_contact_from_csv(row: list) -> dict:
    """Import contact from CSV row."""
    return {
        "name": row[0] if len(row) > 0 else "",
        "email": row[1] if len(row) > 1 else "",
        "phone": row[2] if len(row) > 2 else "",
        "active": True
    }
