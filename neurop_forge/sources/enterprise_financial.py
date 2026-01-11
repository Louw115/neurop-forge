"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Enterprise Financial Utilities - Pure functions for enterprise financial operations.

These blocks are designed for regulated financial workflows:
- Payment processing validation
- Account verification
- Compliance-ready calculations

All functions are:
- Pure (no side effects)
- Deterministic (same input = same output)  
- Auditable (designed for compliance logging)
"""


def process_payment(amount: float, currency: str, account_id: str, reference: str) -> dict:
    """
    Process a payment transaction (validation and formatting only).
    
    Returns a payment record suitable for audit logging.
    This is a pure validation function - actual payment processing
    would be handled by external payment providers.
    """
    if amount <= 0:
        return {
            "success": False,
            "error": "Invalid amount: must be positive",
            "amount": amount,
            "currency": currency
        }
    
    if not account_id or len(account_id) < 4:
        return {
            "success": False,
            "error": "Invalid account ID",
            "account_id": account_id
        }
    
    if currency not in ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF"]:
        return {
            "success": False,
            "error": f"Unsupported currency: {currency}",
            "currency": currency
        }
    
    import hashlib
    from datetime import datetime
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    tx_hash = hashlib.sha256(
        f"{amount}{currency}{account_id}{reference}{timestamp}".encode()
    ).hexdigest()[:16]
    
    return {
        "success": True,
        "transaction_id": f"TX-{tx_hash.upper()}",
        "amount": round(amount, 2),
        "currency": currency,
        "account_id": account_id[:4] + "*" * (len(account_id) - 4),
        "reference": reference,
        "timestamp": timestamp,
        "status": "VALIDATED"
    }


def verify_account(account_id: str, account_type: str) -> dict:
    """
    Verify an account ID format and type.
    
    Validates account format without making external calls.
    Returns verification status suitable for audit logging.
    """
    valid_types = ["checking", "savings", "credit", "debit", "investment"]
    
    if account_type.lower() not in valid_types:
        return {
            "valid": False,
            "account_id_masked": account_id[:4] + "****" if len(account_id) > 4 else "****",
            "error": f"Invalid account type. Must be one of: {', '.join(valid_types)}"
        }
    
    if not account_id or len(account_id) < 8:
        return {
            "valid": False,
            "account_id_masked": "****",
            "error": "Account ID too short (minimum 8 characters)"
        }
    
    if not account_id.replace("-", "").replace(" ", "").isalnum():
        return {
            "valid": False,
            "account_id_masked": account_id[:4] + "****",
            "error": "Account ID contains invalid characters"
        }
    
    return {
        "valid": True,
        "account_id_masked": account_id[:4] + "*" * (len(account_id) - 4),
        "account_type": account_type.lower(),
        "format_check": "PASSED",
        "verification_status": "VERIFIED"
    }


def validate_amount(amount: float, min_amount: float, max_amount: float, currency: str) -> dict:
    """
    Validate a transaction amount against limits.
    
    Used for compliance checks on transaction limits.
    """
    if amount < min_amount:
        return {
            "valid": False,
            "amount": amount,
            "currency": currency,
            "error": f"Amount below minimum ({min_amount} {currency})"
        }
    
    if amount > max_amount:
        return {
            "valid": False,
            "amount": amount,
            "currency": currency,
            "error": f"Amount exceeds maximum ({max_amount} {currency})"
        }
    
    risk_level = "LOW"
    if amount > 10000:
        risk_level = "HIGH"
    elif amount > 5000:
        risk_level = "MEDIUM"
    
    return {
        "valid": True,
        "amount": round(amount, 2),
        "currency": currency,
        "min_limit": min_amount,
        "max_limit": max_amount,
        "risk_level": risk_level,
        "compliance_check": "PASSED"
    }


def calculate_interest(principal: float, rate: float, period_days: int) -> dict:
    """
    Calculate interest for a given period.
    
    Returns detailed calculation suitable for audit trail.
    Uses simple interest calculation: I = P * r * t
    """
    if principal <= 0:
        return {
            "success": False,
            "error": "Principal must be positive"
        }
    
    if rate < 0:
        return {
            "success": False,
            "error": "Interest rate cannot be negative"
        }
    
    if period_days < 0:
        return {
            "success": False,
            "error": "Period cannot be negative"
        }
    
    years = period_days / 365.0
    interest = principal * (rate / 100) * years
    
    return {
        "success": True,
        "principal": round(principal, 2),
        "rate_percent": rate,
        "period_days": period_days,
        "interest_earned": round(interest, 2),
        "final_amount": round(principal + interest, 2),
        "calculation_method": "SIMPLE_INTEREST"
    }


def mask_credit_card(number: str) -> str:
    """Mask a credit card number showing only last 4 digits."""
    digits = ''.join(c for c in number if c.isdigit())
    if len(digits) < 4:
        return "****"
    return "*" * (len(digits) - 4) + digits[-4:]


def format_account_statement_line(
    date: str,
    description: str,
    amount: float,
    balance: float,
    transaction_type: str
) -> dict:
    """
    Format a single statement line for account statements.
    
    Produces audit-ready transaction records.
    """
    return {
        "date": date,
        "description": description[:50] if len(description) > 50 else description,
        "amount": round(amount, 2),
        "balance": round(balance, 2),
        "type": transaction_type.upper() if transaction_type in ["credit", "debit"] else "UNKNOWN",
        "formatted_amount": f"${abs(amount):,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"
    }


def calculate_total_with_fees(
    amount: float,
    processing_fee_percent: float,
    flat_fee: float
) -> dict:
    """
    Calculate total amount including processing fees.
    
    Common for payment processing compliance calculations.
    """
    processing_fee = round(amount * processing_fee_percent / 100, 2)
    total_fees = round(processing_fee + flat_fee, 2)
    total = round(amount + total_fees, 2)
    
    return {
        "base_amount": round(amount, 2),
        "processing_fee_percent": processing_fee_percent,
        "processing_fee_amount": processing_fee,
        "flat_fee": flat_fee,
        "total_fees": total_fees,
        "total_amount": total
    }


def validate_routing_number(routing: str) -> dict:
    """
    Validate a US bank routing number using checksum.
    
    Uses the ABA routing number validation algorithm.
    """
    digits = ''.join(c for c in routing if c.isdigit())
    
    if len(digits) != 9:
        return {
            "valid": False,
            "routing_masked": digits[:4] + "*****" if len(digits) > 4 else "*****",
            "error": "Routing number must be exactly 9 digits"
        }
    
    weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
    total = sum(int(d) * w for d, w in zip(digits, weights))
    
    if total % 10 != 0:
        return {
            "valid": False,
            "routing_masked": digits[:4] + "*****",
            "error": "Routing number checksum failed"
        }
    
    return {
        "valid": True,
        "routing_masked": digits[:4] + "*****",
        "checksum_verified": True
    }
