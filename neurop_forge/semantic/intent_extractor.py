"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

Semantic Intent Extractor - Automatically infers semantic intent from code.
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from neurop_forge.semantic.intent_schema import (
    SemanticDomain,
    SemanticOperation,
    SemanticType,
    SemanticIntent,
    DOMAIN_CHAIN_RULES,
)


DOMAIN_KEYWORDS = {
    SemanticDomain.VALIDATION: ["valid", "check", "verify", "is_", "has_", "ensure", "assert", "require"],
    SemanticDomain.TRANSFORMATION: ["transform", "convert", "map", "to_", "from_", "change", "modify"],
    SemanticDomain.FORMATTING: ["format_", "format", "display", "render", "pretty", "humanize", "stringify", "to_display", "as_string", "readable", "human_readable"],
    SemanticDomain.PARSING: ["parse", "extract", "split", "tokenize", "decode", "deserialize"],
    SemanticDomain.SECURITY: ["secure", "sanitize", "escape", "encrypt", "decrypt", "protect", "mask"],
    SemanticDomain.AUTHENTICATION: ["auth", "login", "logout", "session", "token", "password", "credential"],
    SemanticDomain.CALCULATION: ["calc", "compute", "sum", "avg", "mean", "median", "total", "count"],
    SemanticDomain.COMPARISON: ["compare", "diff", "equal", "match", "same", "greater", "less", "between"],
    SemanticDomain.FILTERING: ["filter", "select", "where", "find", "search", "query", "exclude", "include"],
    SemanticDomain.AGGREGATION: ["aggregate", "group", "collect", "combine", "merge", "reduce", "fold"],
    SemanticDomain.SEARCHING: ["search", "find", "lookup", "locate", "index", "query"],
    SemanticDomain.SORTING: ["sort", "order", "rank", "arrange", "organize"],
    SemanticDomain.ENCODING: ["encode", "base64", "hex", "url_encode", "serialize", "compress"],
    SemanticDomain.HASHING: ["hash", "md5", "sha", "digest", "checksum", "fingerprint"],
    SemanticDomain.DATETIME: ["date", "time", "timestamp", "duration", "period", "schedule", "calendar"],
    SemanticDomain.STRING: ["string", "text", "char", "word", "sentence", "trim", "pad", "case"],
    SemanticDomain.NUMERIC: ["number", "int", "float", "decimal", "round", "floor", "ceil", "abs"],
    SemanticDomain.COLLECTION: ["list", "array", "set", "dict", "map", "tuple", "collection", "sequence"],
    SemanticDomain.IO: ["read", "write", "file", "stream", "buffer", "io"],
    SemanticDomain.NETWORK: ["http", "url", "request", "response", "api", "endpoint", "socket"],
    SemanticDomain.DATABASE: ["db", "sql", "query", "insert", "update", "delete", "select", "table"],
}


OPERATION_KEYWORDS = {
    SemanticOperation.CHECK: ["is_", "has_", "can_", "should_", "check"],
    SemanticOperation.VALIDATE: ["valid", "validate", "verify"],
    SemanticOperation.VERIFY: ["verify", "confirm", "ensure"],
    SemanticOperation.CONVERT: ["convert", "to_", "from_", "as_"],
    SemanticOperation.TRANSFORM: ["transform", "modify", "change", "update"],
    SemanticOperation.FORMAT: ["format", "stringify", "display", "render"],
    SemanticOperation.PARSE: ["parse", "read", "decode", "deserialize"],
    SemanticOperation.EXTRACT: ["extract", "get_", "fetch", "retrieve"],
    SemanticOperation.ENCODE: ["encode", "serialize", "compress"],
    SemanticOperation.DECODE: ["decode", "deserialize", "decompress"],
    SemanticOperation.HASH: ["hash", "digest", "checksum"],
    SemanticOperation.ENCRYPT: ["encrypt", "cipher"],
    SemanticOperation.DECRYPT: ["decrypt", "decipher"],
    SemanticOperation.COMPARE: ["compare", "diff", "match", "equals"],
    SemanticOperation.FILTER: ["filter", "where", "select", "exclude"],
    SemanticOperation.MAP: ["map", "apply", "each", "for_each"],
    SemanticOperation.REDUCE: ["reduce", "fold", "aggregate", "combine"],
    SemanticOperation.SORT: ["sort", "order", "arrange", "rank"],
    SemanticOperation.SEARCH: ["search", "find", "locate", "lookup"],
    SemanticOperation.CALCULATE: ["calc", "compute", "sum", "count", "avg"],
    SemanticOperation.GENERATE: ["generate", "create", "make", "build", "new"],
    SemanticOperation.CREATE: ["create", "new", "init", "build"],
    SemanticOperation.NORMALIZE: ["normalize", "standard", "canonical"],
    SemanticOperation.SANITIZE: ["sanitize", "clean", "escape", "strip"],
    SemanticOperation.MERGE: ["merge", "combine", "join", "concat"],
    SemanticOperation.SPLIT: ["split", "separate", "divide", "chunk"],
}


SEMANTIC_TYPE_KEYWORDS = {
    SemanticType.EMAIL: ["email", "mail", "e_mail"],
    SemanticType.URL: ["url", "uri", "link", "href", "endpoint"],
    SemanticType.PHONE: ["phone", "tel", "mobile", "cell"],
    SemanticType.PASSWORD: ["password", "pass", "pwd", "secret", "credential"],
    SemanticType.USERNAME: ["username", "user_name", "login", "handle"],
    SemanticType.NAME: ["name", "first_name", "last_name", "full_name"],
    SemanticType.ADDRESS: ["address", "addr", "street", "city", "zip", "postal"],
    SemanticType.CURRENCY: ["currency", "money", "price", "cost", "amount", "dollar", "euro"],
    SemanticType.DATE: ["date", "day", "month", "year"],
    SemanticType.TIME: ["time", "hour", "minute", "second"],
    SemanticType.DATETIME: ["datetime", "timestamp", "when"],
    SemanticType.DURATION: ["duration", "period", "interval", "elapsed"],
    SemanticType.HTML: ["html", "markup", "dom"],
    SemanticType.JSON: ["json", "dict", "object", "data"],
    SemanticType.XML: ["xml", "element", "node"],
    SemanticType.HASH: ["hash", "digest", "checksum", "md5", "sha"],
    SemanticType.TOKEN: ["token", "jwt", "bearer", "session"],
    SemanticType.ID: ["id", "uuid", "guid", "identifier", "key"],
    SemanticType.PATH: ["path", "file", "directory", "folder"],
    SemanticType.COLOR: ["color", "colour", "rgb", "hex", "hsl"],
    SemanticType.COORDINATE: ["coord", "lat", "lon", "geo", "location"],
    SemanticType.MEASUREMENT: ["measure", "size", "length", "width", "height", "weight"],
    SemanticType.COLLECTION: ["list", "array", "set", "collection", "items"],
}


class SemanticIntentExtractor:
    """
    Extracts semantic intent from block metadata.
    
    This is the key component that makes composition work by
    understanding WHAT a block does, not just what it's called.
    """

    def extract(
        self,
        function_name: str,
        docstring: Optional[str],
        param_names: List[str],
        return_type_hint: Optional[str],
        category: str,
    ) -> SemanticIntent:
        """
        Extract semantic intent from function metadata.
        
        Args:
            function_name: Name of the function
            docstring: Function docstring
            param_names: Parameter names
            return_type_hint: Return type hint if available
            category: Block category
            
        Returns:
            SemanticIntent describing the block's semantic behavior
        """
        name_lower = function_name.lower()
        doc_lower = (docstring or "").lower()
        combined_text = f"{name_lower} {doc_lower} {' '.join(param_names)}"
        
        domain = self._infer_domain(combined_text, category)
        operation = self._infer_operation(name_lower, doc_lower)
        input_types = self._infer_semantic_types(param_names, doc_lower)
        output_types = self._infer_output_types(name_lower, return_type_hint, doc_lower)
        
        preconditions = self._extract_preconditions(doc_lower, input_types)
        postconditions = self._extract_postconditions(doc_lower, output_types, operation)
        
        can_chain_from = self._get_chain_from_domains(domain, operation)
        can_chain_to = self._get_chain_to_domains(domain, operation)
        
        return SemanticIntent(
            domain=domain,
            operation=operation,
            input_semantic_types=input_types,
            output_semantic_types=output_types,
            preconditions=preconditions,
            postconditions=postconditions,
            can_chain_from=can_chain_from,
            can_chain_to=can_chain_to,
        )

    def _infer_domain(self, text: str, category: str) -> SemanticDomain:
        """Infer semantic domain from text and category."""
        scores: Dict[SemanticDomain, int] = {}
        
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[domain] = score
        
        category_lower = category.lower()
        for domain in SemanticDomain:
            if domain.value in category_lower:
                scores[domain] = scores.get(domain, 0) + 3
        
        if scores:
            return max(scores, key=scores.get)
        
        return SemanticDomain.UTILITY

    def _infer_operation(self, name: str, docstring: str) -> SemanticOperation:
        """Infer operation type from function name and docstring."""
        combined = f"{name} {docstring}"
        
        scores: Dict[SemanticOperation, int] = {}
        
        for operation, keywords in OPERATION_KEYWORDS.items():
            for kw in keywords:
                if name.startswith(kw) or name.endswith(kw):
                    scores[operation] = scores.get(operation, 0) + 3
                elif kw in combined:
                    scores[operation] = scores.get(operation, 0) + 1
        
        if scores:
            return max(scores, key=scores.get)
        
        if name.startswith("is_") or name.startswith("has_"):
            return SemanticOperation.CHECK
        if name.startswith("get_"):
            return SemanticOperation.EXTRACT
        if name.startswith("set_") or name.startswith("create_"):
            return SemanticOperation.CREATE
        
        return SemanticOperation.TRANSFORM

    def _infer_semantic_types(self, param_names: List[str], docstring: str) -> Tuple[SemanticType, ...]:
        """Infer semantic types from parameter names."""
        types: Set[SemanticType] = set()
        combined = " ".join(param_names) + " " + docstring
        
        for sem_type, keywords in SEMANTIC_TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in combined.lower():
                    types.add(sem_type)
        
        if not types:
            types.add(SemanticType.GENERIC)
        
        return tuple(sorted(types, key=lambda t: t.value))

    def _infer_output_types(
        self,
        name: str,
        return_hint: Optional[str],
        docstring: str
    ) -> Tuple[SemanticType, ...]:
        """Infer output semantic types."""
        types: Set[SemanticType] = set()
        
        if name.startswith("is_") or name.startswith("has_") or name.startswith("can_"):
            types.add(SemanticType.BOOLEAN_RESULT)
        
        if name.startswith("format_") or "format" in docstring:
            types.add(SemanticType.FORMATTED_TEXT)
        
        if name.startswith("hash_") or "hash" in name:
            types.add(SemanticType.HASH)
        
        combined = f"{name} {return_hint or ''} {docstring}"
        for sem_type, keywords in SEMANTIC_TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in combined.lower() and sem_type not in types:
                    types.add(sem_type)
                    break
        
        if not types:
            types.add(SemanticType.GENERIC)
        
        return tuple(sorted(types, key=lambda t: t.value))

    def _extract_preconditions(
        self,
        docstring: str,
        input_types: Tuple[SemanticType, ...]
    ) -> Tuple[str, ...]:
        """Extract preconditions from docstring and types."""
        preconditions: List[str] = []
        
        for sem_type in input_types:
            if sem_type == SemanticType.EMAIL:
                preconditions.append("input is a string")
            elif sem_type == SemanticType.URL:
                preconditions.append("input is a string")
            elif sem_type == SemanticType.NUMERIC_VALUE:
                preconditions.append("input is numeric")
            elif sem_type == SemanticType.COLLECTION:
                preconditions.append("input is iterable")
        
        if "not none" in docstring or "not null" in docstring:
            preconditions.append("input is not null")
        
        if not preconditions:
            preconditions.append("input is defined")
        
        return tuple(preconditions)

    def _extract_postconditions(
        self,
        docstring: str,
        output_types: Tuple[SemanticType, ...],
        operation: SemanticOperation
    ) -> Tuple[str, ...]:
        """Extract postconditions from docstring and operation."""
        postconditions: List[str] = []
        
        if operation in [SemanticOperation.VALIDATE, SemanticOperation.CHECK, SemanticOperation.VERIFY]:
            postconditions.append("returns boolean indicating validity")
        
        if operation == SemanticOperation.FORMAT:
            postconditions.append("returns formatted string")
        
        if operation == SemanticOperation.SANITIZE:
            postconditions.append("returns sanitized value")
        
        for sem_type in output_types:
            if sem_type == SemanticType.HASH:
                postconditions.append("returns deterministic hash")
            elif sem_type == SemanticType.BOOLEAN_RESULT:
                postconditions.append("returns true or false")
        
        if not postconditions:
            postconditions.append("returns result")
        
        return tuple(postconditions)

    def _get_chain_from_domains(
        self,
        domain: SemanticDomain,
        operation: SemanticOperation
    ) -> Tuple[SemanticDomain, ...]:
        """Determine what domains this block can receive input from."""
        chain_from: Set[SemanticDomain] = set()
        
        for src_domain, valid_targets in DOMAIN_CHAIN_RULES.items():
            if domain in valid_targets:
                chain_from.add(src_domain)
        
        if operation in [SemanticOperation.VALIDATE, SemanticOperation.CHECK]:
            chain_from.add(SemanticDomain.PARSING)
            chain_from.add(SemanticDomain.TRANSFORMATION)
        
        if operation == SemanticOperation.FORMAT:
            chain_from.add(SemanticDomain.TRANSFORMATION)
            chain_from.add(SemanticDomain.CALCULATION)
            chain_from.add(SemanticDomain.VALIDATION)
        
        return tuple(sorted(chain_from, key=lambda d: d.value))

    def _get_chain_to_domains(
        self,
        domain: SemanticDomain,
        operation: SemanticOperation
    ) -> Tuple[SemanticDomain, ...]:
        """Determine what domains this block's output can feed into."""
        chain_to = DOMAIN_CHAIN_RULES.get(domain, [])
        return tuple(sorted(chain_to, key=lambda d: d.value))
