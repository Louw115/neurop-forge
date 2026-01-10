"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

Semantic Intent Schema - The missing layer that makes composition work.

This module defines:
1. Semantic domains (what area of functionality)
2. Semantic operations (what kind of action)
3. Semantic types (what concepts inputs/outputs represent)
4. Intent matching rules
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum


class SemanticDomain(Enum):
    """Semantic domain of functionality."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    FORMATTING = "formatting"
    PARSING = "parsing"
    SECURITY = "security"
    AUTHENTICATION = "authentication"
    CALCULATION = "calculation"
    COMPARISON = "comparison"
    FILTERING = "filtering"
    AGGREGATION = "aggregation"
    SEARCHING = "searching"
    SORTING = "sorting"
    ENCODING = "encoding"
    HASHING = "hashing"
    DATETIME = "datetime"
    STRING = "string"
    NUMERIC = "numeric"
    COLLECTION = "collection"
    IO = "io"
    NETWORK = "network"
    DATABASE = "database"
    UTILITY = "utility"


class SemanticOperation(Enum):
    """Type of operation the block performs."""
    CHECK = "check"
    VALIDATE = "validate"
    VERIFY = "verify"
    CONVERT = "convert"
    TRANSFORM = "transform"
    FORMAT = "format"
    PARSE = "parse"
    EXTRACT = "extract"
    ENCODE = "encode"
    DECODE = "decode"
    HASH = "hash"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    COMPARE = "compare"
    FILTER = "filter"
    MAP = "map"
    REDUCE = "reduce"
    SORT = "sort"
    SEARCH = "search"
    CALCULATE = "calculate"
    GENERATE = "generate"
    CREATE = "create"
    NORMALIZE = "normalize"
    SANITIZE = "sanitize"
    MERGE = "merge"
    SPLIT = "split"


class SemanticType(Enum):
    """Semantic type of data (what it represents, not just its structure)."""
    RAW_INPUT = "raw_input"
    VALIDATED_INPUT = "validated_input"
    USER_DATA = "user_data"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    PASSWORD = "password"
    USERNAME = "username"
    NAME = "name"
    ADDRESS = "address"
    NUMERIC_VALUE = "numeric_value"
    CURRENCY = "currency"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    DURATION = "duration"
    TEXT = "text"
    FORMATTED_TEXT = "formatted_text"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"
    HASH = "hash"
    TOKEN = "token"
    ID = "id"
    PATH = "path"
    COLOR = "color"
    COORDINATE = "coordinate"
    MEASUREMENT = "measurement"
    COLLECTION = "collection"
    BOOLEAN_RESULT = "boolean_result"
    ERROR = "error"
    GENERIC = "generic"


@dataclass(frozen=True)
class SemanticIntent:
    """
    Semantic intent declaration for a NeuropBlock.
    
    This is what makes composition WORK - it describes:
    - What domain this block operates in
    - What operation it performs
    - What semantic type it expects as input
    - What semantic type it produces as output
    - What preconditions must be true
    - What postconditions will be true
    """
    domain: SemanticDomain
    operation: SemanticOperation
    input_semantic_types: Tuple[SemanticType, ...]
    output_semantic_types: Tuple[SemanticType, ...]
    preconditions: Tuple[str, ...]
    postconditions: Tuple[str, ...]
    can_chain_from: Tuple[SemanticDomain, ...]
    can_chain_to: Tuple[SemanticDomain, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain.value,
            "operation": self.operation.value,
            "input_semantic_types": [t.value for t in self.input_semantic_types],
            "output_semantic_types": [t.value for t in self.output_semantic_types],
            "preconditions": list(self.preconditions),
            "postconditions": list(self.postconditions),
            "can_chain_from": [d.value for d in self.can_chain_from],
            "can_chain_to": [d.value for d in self.can_chain_to],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticIntent":
        return cls(
            domain=SemanticDomain(data["domain"]),
            operation=SemanticOperation(data["operation"]),
            input_semantic_types=tuple(SemanticType(t) for t in data["input_semantic_types"]),
            output_semantic_types=tuple(SemanticType(t) for t in data["output_semantic_types"]),
            preconditions=tuple(data["preconditions"]),
            postconditions=tuple(data["postconditions"]),
            can_chain_from=tuple(SemanticDomain(d) for d in data["can_chain_from"]),
            can_chain_to=tuple(SemanticDomain(d) for d in data["can_chain_to"]),
        )


DOMAIN_CHAIN_RULES = {
    SemanticDomain.PARSING: [SemanticDomain.VALIDATION, SemanticDomain.TRANSFORMATION],
    SemanticDomain.VALIDATION: [SemanticDomain.TRANSFORMATION, SemanticDomain.FORMATTING, SemanticDomain.SECURITY],
    SemanticDomain.TRANSFORMATION: [SemanticDomain.FORMATTING, SemanticDomain.VALIDATION, SemanticDomain.ENCODING],
    SemanticDomain.FORMATTING: [SemanticDomain.ENCODING, SemanticDomain.UTILITY],
    SemanticDomain.SECURITY: [SemanticDomain.VALIDATION, SemanticDomain.HASHING, SemanticDomain.ENCODING],
    SemanticDomain.ENCODING: [SemanticDomain.HASHING, SemanticDomain.UTILITY],
    SemanticDomain.HASHING: [SemanticDomain.COMPARISON, SemanticDomain.UTILITY],
    SemanticDomain.CALCULATION: [SemanticDomain.COMPARISON, SemanticDomain.FORMATTING],
    SemanticDomain.COMPARISON: [SemanticDomain.FILTERING, SemanticDomain.UTILITY],
    SemanticDomain.FILTERING: [SemanticDomain.AGGREGATION, SemanticDomain.TRANSFORMATION],
    SemanticDomain.AGGREGATION: [SemanticDomain.FORMATTING, SemanticDomain.UTILITY],
    SemanticDomain.SEARCHING: [SemanticDomain.FILTERING, SemanticDomain.TRANSFORMATION],
    SemanticDomain.SORTING: [SemanticDomain.FILTERING, SemanticDomain.UTILITY],
}


OPERATION_ORDER = {
    SemanticOperation.PARSE: 0,
    SemanticOperation.EXTRACT: 1,
    SemanticOperation.VALIDATE: 2,
    SemanticOperation.CHECK: 2,
    SemanticOperation.VERIFY: 2,
    SemanticOperation.SANITIZE: 3,
    SemanticOperation.NORMALIZE: 4,
    SemanticOperation.TRANSFORM: 5,
    SemanticOperation.CONVERT: 5,
    SemanticOperation.CALCULATE: 6,
    SemanticOperation.FILTER: 7,
    SemanticOperation.MAP: 7,
    SemanticOperation.SORT: 8,
    SemanticOperation.REDUCE: 9,
    SemanticOperation.MERGE: 9,
    SemanticOperation.FORMAT: 10,
    SemanticOperation.ENCODE: 11,
    SemanticOperation.HASH: 12,
    SemanticOperation.GENERATE: 13,
    SemanticOperation.CREATE: 13,
}


SEMANTIC_TYPE_COMPATIBILITY = {
    SemanticType.RAW_INPUT: [SemanticType.VALIDATED_INPUT, SemanticType.TEXT, SemanticType.GENERIC],
    SemanticType.TEXT: [SemanticType.FORMATTED_TEXT, SemanticType.EMAIL, SemanticType.URL, SemanticType.PHONE, SemanticType.NAME, SemanticType.GENERIC],
    SemanticType.VALIDATED_INPUT: [SemanticType.FORMATTED_TEXT, SemanticType.USER_DATA, SemanticType.GENERIC],
    SemanticType.EMAIL: [SemanticType.TEXT, SemanticType.FORMATTED_TEXT, SemanticType.HASH],
    SemanticType.URL: [SemanticType.TEXT, SemanticType.FORMATTED_TEXT, SemanticType.PATH],
    SemanticType.PASSWORD: [SemanticType.HASH, SemanticType.TOKEN],
    SemanticType.NUMERIC_VALUE: [SemanticType.FORMATTED_TEXT, SemanticType.CURRENCY, SemanticType.MEASUREMENT],
    SemanticType.DATE: [SemanticType.FORMATTED_TEXT, SemanticType.DATETIME],
    SemanticType.TIME: [SemanticType.FORMATTED_TEXT, SemanticType.DATETIME],
    SemanticType.JSON: [SemanticType.TEXT, SemanticType.GENERIC],
    SemanticType.COLLECTION: [SemanticType.GENERIC],
    SemanticType.GENERIC: [SemanticType.TEXT, SemanticType.FORMATTED_TEXT],
}


def can_chain(source_intent: SemanticIntent, target_intent: SemanticIntent) -> bool:
    """Check if source block output can chain to target block input."""
    if target_intent.domain in source_intent.can_chain_to:
        return True
    if source_intent.domain in target_intent.can_chain_from:
        return True
    if target_intent.domain in DOMAIN_CHAIN_RULES.get(source_intent.domain, []):
        return True
    return False


def are_semantic_types_compatible(source_types: Tuple[SemanticType, ...], target_types: Tuple[SemanticType, ...]) -> bool:
    """Check if source output semantic types are compatible with target input."""
    for source_type in source_types:
        for target_type in target_types:
            if source_type == target_type:
                return True
            if target_type in SEMANTIC_TYPE_COMPATIBILITY.get(source_type, []):
                return True
            if target_type == SemanticType.GENERIC:
                return True
    return False


def get_operation_order(operation: SemanticOperation) -> int:
    """Get the canonical order for an operation type."""
    return OPERATION_ORDER.get(operation, 99)
