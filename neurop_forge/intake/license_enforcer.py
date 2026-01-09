"""
License enforcer for source code provenance.

This module validates that source code has an acceptable open-source license.
Only MIT, BSD, and Apache 2.0 licenses are allowed. All other licenses
cause the source to be rejected.
"""

import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from neurop_forge.core.block_schema import LicenseType


class LicenseStatus(Enum):
    """Status of license validation."""
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"
    MISSING = "missing"


@dataclass
class LicenseValidationResult:
    """Result of license validation."""
    status: LicenseStatus
    license_type: Optional[LicenseType]
    confidence: float  # 0.0 to 1.0
    license_text: Optional[str]
    source_location: Optional[str]
    error_message: Optional[str]
    attribution_required: bool
    modifications_allowed: bool

    def is_valid(self) -> bool:
        return self.status == LicenseStatus.VALID

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "license_type": self.license_type.value if self.license_type else None,
            "confidence": self.confidence,
            "source_location": self.source_location,
            "error_message": self.error_message,
            "attribution_required": self.attribution_required,
            "modifications_allowed": self.modifications_allowed,
        }


class LicenseEnforcer:
    """
    Enforces license requirements for source code.
    
    Only allows:
    - MIT License
    - BSD 2-Clause License
    - BSD 3-Clause License
    - Apache 2.0 License
    - Unlicense
    - CC0 1.0
    - Public Domain
    
    All other licenses are rejected.
    """

    ALLOWED_LICENSES: Set[LicenseType] = {
        LicenseType.MIT,
        LicenseType.BSD_2_CLAUSE,
        LicenseType.BSD_3_CLAUSE,
        LicenseType.APACHE_2_0,
        LicenseType.UNLICENSE,
        LicenseType.CC0,
        LicenseType.PUBLIC_DOMAIN,
    }

    LICENSE_PATTERNS: Dict[LicenseType, List[re.Pattern]] = {
        LicenseType.MIT: [
            re.compile(r"MIT\s+License", re.IGNORECASE),
            re.compile(r"Permission\s+is\s+hereby\s+granted.*MIT", re.IGNORECASE | re.DOTALL),
            re.compile(r"SPDX-License-Identifier:\s*MIT", re.IGNORECASE),
        ],
        LicenseType.BSD_2_CLAUSE: [
            re.compile(r"BSD\s+2-Clause", re.IGNORECASE),
            re.compile(r"Simplified\s+BSD\s+License", re.IGNORECASE),
            re.compile(r"SPDX-License-Identifier:\s*BSD-2-Clause", re.IGNORECASE),
        ],
        LicenseType.BSD_3_CLAUSE: [
            re.compile(r"BSD\s+3-Clause", re.IGNORECASE),
            re.compile(r"New\s+BSD\s+License", re.IGNORECASE),
            re.compile(r"Modified\s+BSD\s+License", re.IGNORECASE),
            re.compile(r"SPDX-License-Identifier:\s*BSD-3-Clause", re.IGNORECASE),
        ],
        LicenseType.APACHE_2_0: [
            re.compile(r"Apache\s+License.*Version\s+2\.0", re.IGNORECASE | re.DOTALL),
            re.compile(r"Apache-2\.0", re.IGNORECASE),
            re.compile(r"SPDX-License-Identifier:\s*Apache-2\.0", re.IGNORECASE),
        ],
        LicenseType.UNLICENSE: [
            re.compile(r"This\s+is\s+free\s+and\s+unencumbered\s+software", re.IGNORECASE),
            re.compile(r"SPDX-License-Identifier:\s*Unlicense", re.IGNORECASE),
        ],
        LicenseType.CC0: [
            re.compile(r"CC0\s+1\.0", re.IGNORECASE),
            re.compile(r"Creative\s+Commons\s+Zero", re.IGNORECASE),
            re.compile(r"SPDX-License-Identifier:\s*CC0-1\.0", re.IGNORECASE),
        ],
        LicenseType.PUBLIC_DOMAIN: [
            re.compile(r"Public\s+Domain", re.IGNORECASE),
            re.compile(r"released\s+into\s+the\s+public\s+domain", re.IGNORECASE),
        ],
    }

    FORBIDDEN_PATTERNS: List[Tuple[re.Pattern, str]] = [
        (re.compile(r"GNU\s+General\s+Public\s+License", re.IGNORECASE), "GPL"),
        (re.compile(r"GPL-[23]\.0", re.IGNORECASE), "GPL"),
        (re.compile(r"LGPL", re.IGNORECASE), "LGPL"),
        (re.compile(r"AGPL", re.IGNORECASE), "AGPL"),
        (re.compile(r"Affero\s+General\s+Public", re.IGNORECASE), "AGPL"),
        (re.compile(r"All\s+rights\s+reserved", re.IGNORECASE), "Proprietary"),
        (re.compile(r"No\s+part.*may\s+be\s+reproduced", re.IGNORECASE), "Proprietary"),
        (re.compile(r"Commercial\s+use.*prohibited", re.IGNORECASE), "Commercial restriction"),
    ]

    LICENSE_ATTRIBUTION: Dict[LicenseType, bool] = {
        LicenseType.MIT: True,
        LicenseType.BSD_2_CLAUSE: True,
        LicenseType.BSD_3_CLAUSE: True,
        LicenseType.APACHE_2_0: True,
        LicenseType.UNLICENSE: False,
        LicenseType.CC0: False,
        LicenseType.PUBLIC_DOMAIN: False,
    }

    def __init__(self, strict_mode: bool = True):
        self._strict_mode = strict_mode

    def validate_license_text(self, license_text: str) -> LicenseValidationResult:
        """
        Validate license from license text content.
        
        Args:
            license_text: The full license text
            
        Returns:
            LicenseValidationResult: The validation result
        """
        if not license_text or not license_text.strip():
            return LicenseValidationResult(
                status=LicenseStatus.MISSING,
                license_type=None,
                confidence=0.0,
                license_text=None,
                source_location=None,
                error_message="No license text provided",
                attribution_required=True,
                modifications_allowed=False,
            )

        for pattern, restriction_type in self.FORBIDDEN_PATTERNS:
            if pattern.search(license_text):
                return LicenseValidationResult(
                    status=LicenseStatus.INVALID,
                    license_type=None,
                    confidence=0.9,
                    license_text=license_text[:500],
                    source_location=None,
                    error_message=f"Forbidden license type detected: {restriction_type}",
                    attribution_required=True,
                    modifications_allowed=False,
                )

        for license_type, patterns in self.LICENSE_PATTERNS.items():
            for pattern in patterns:
                if pattern.search(license_text):
                    return LicenseValidationResult(
                        status=LicenseStatus.VALID,
                        license_type=license_type,
                        confidence=0.95,
                        license_text=license_text[:1000],
                        source_location=None,
                        error_message=None,
                        attribution_required=self.LICENSE_ATTRIBUTION.get(license_type, True),
                        modifications_allowed=True,
                    )

        if self._strict_mode:
            return LicenseValidationResult(
                status=LicenseStatus.UNKNOWN,
                license_type=None,
                confidence=0.0,
                license_text=license_text[:500],
                source_location=None,
                error_message="Could not identify license type",
                attribution_required=True,
                modifications_allowed=False,
            )

        return LicenseValidationResult(
            status=LicenseStatus.UNKNOWN,
            license_type=None,
            confidence=0.0,
            license_text=license_text[:500],
            source_location=None,
            error_message="Unknown license - manual review required",
            attribution_required=True,
            modifications_allowed=False,
        )

    def validate_spdx_identifier(self, spdx_id: str) -> LicenseValidationResult:
        """
        Validate license from SPDX identifier.
        
        Args:
            spdx_id: The SPDX license identifier
            
        Returns:
            LicenseValidationResult: The validation result
        """
        spdx_mapping: Dict[str, LicenseType] = {
            "MIT": LicenseType.MIT,
            "BSD-2-Clause": LicenseType.BSD_2_CLAUSE,
            "BSD-3-Clause": LicenseType.BSD_3_CLAUSE,
            "Apache-2.0": LicenseType.APACHE_2_0,
            "Unlicense": LicenseType.UNLICENSE,
            "CC0-1.0": LicenseType.CC0,
        }

        normalized = spdx_id.strip()
        license_type = spdx_mapping.get(normalized)

        if license_type:
            return LicenseValidationResult(
                status=LicenseStatus.VALID,
                license_type=license_type,
                confidence=1.0,
                license_text=None,
                source_location=f"SPDX: {normalized}",
                error_message=None,
                attribution_required=self.LICENSE_ATTRIBUTION.get(license_type, True),
                modifications_allowed=True,
            )

        forbidden_spdx = ["GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "AGPL-3.0"]
        if normalized in forbidden_spdx:
            return LicenseValidationResult(
                status=LicenseStatus.INVALID,
                license_type=None,
                confidence=1.0,
                license_text=None,
                source_location=f"SPDX: {normalized}",
                error_message=f"Forbidden license: {normalized}",
                attribution_required=True,
                modifications_allowed=False,
            )

        return LicenseValidationResult(
            status=LicenseStatus.UNKNOWN,
            license_type=None,
            confidence=0.5,
            license_text=None,
            source_location=f"SPDX: {normalized}",
            error_message=f"Unknown SPDX identifier: {normalized}",
            attribution_required=True,
            modifications_allowed=False,
        )

    def extract_license_from_source(self, source_code: str) -> Optional[str]:
        """
        Extract license information from source code comments.
        
        Args:
            source_code: The source code content
            
        Returns:
            Optional[str]: Extracted license text if found
        """
        header_patterns = [
            re.compile(r'^(?:#|//|/\*|\'\'\').*?license.*?(?:\n|$)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'SPDX-License-Identifier:\s*(\S+)', re.IGNORECASE),
        ]

        lines = source_code.split('\n')
        header_lines = lines[:30]
        header_text = '\n'.join(header_lines)

        spdx_match = re.search(r'SPDX-License-Identifier:\s*(\S+)', header_text)
        if spdx_match:
            return f"SPDX-License-Identifier: {spdx_match.group(1)}"

        for pattern in [
            re.compile(r'MIT\s+License', re.IGNORECASE),
            re.compile(r'BSD.*License', re.IGNORECASE),
            re.compile(r'Apache.*License', re.IGNORECASE),
        ]:
            match = pattern.search(header_text)
            if match:
                start = max(0, match.start() - 100)
                end = min(len(header_text), match.end() + 200)
                return header_text[start:end]

        return None

    def validate_source_license(
        self,
        source_code: str,
        explicit_license: Optional[str] = None,
    ) -> LicenseValidationResult:
        """
        Validate the license for source code.
        
        Args:
            source_code: The source code content
            explicit_license: Optional explicit license text or SPDX identifier
            
        Returns:
            LicenseValidationResult: The validation result
        """
        if explicit_license:
            if re.match(r'^[A-Za-z0-9.-]+$', explicit_license.strip()):
                return self.validate_spdx_identifier(explicit_license)
            return self.validate_license_text(explicit_license)

        extracted = self.extract_license_from_source(source_code)
        if extracted:
            if "SPDX-License-Identifier:" in extracted:
                spdx_match = re.search(r'SPDX-License-Identifier:\s*(\S+)', extracted)
                if spdx_match:
                    return self.validate_spdx_identifier(spdx_match.group(1))
            return self.validate_license_text(extracted)

        return LicenseValidationResult(
            status=LicenseStatus.MISSING,
            license_type=None,
            confidence=0.0,
            license_text=None,
            source_location=None,
            error_message="No license information found in source",
            attribution_required=True,
            modifications_allowed=False,
        )

    def is_allowed(self, license_type: LicenseType) -> bool:
        """Check if a license type is allowed."""
        return license_type in self.ALLOWED_LICENSES
