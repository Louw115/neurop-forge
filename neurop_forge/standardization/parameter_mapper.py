"""
Parameter Mapper for Neurop Block Forge V2.

Maps non-standard parameter names to their canonical equivalents,
enabling consistent block interfaces across the library.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

from neurop_forge.standardization.canonical_names import (
    get_canonical_name,
    is_canonical,
    get_all_valid_names,
    CANONICAL_BY_TYPE,
)


class MappingConfidence(Enum):
    """Confidence level for parameter mappings."""
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class ParameterMapping:
    """Represents a mapping from original to canonical parameter name."""
    original_name: str
    canonical_name: str
    data_type: str
    confidence: MappingConfidence
    reason: str = ""


@dataclass
class BlockMappingResult:
    """Result of mapping parameters for a block."""
    block_id: str
    block_name: str
    mappings: List[ParameterMapping] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)
    unmapped: List[str] = field(default_factory=list)
    
    @property
    def has_changes(self) -> bool:
        return len(self.mappings) > 0
    
    @property
    def all_mapped(self) -> bool:
        return len(self.unmapped) == 0


class ParameterMapper:
    """Maps parameter names to canonical equivalents."""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self._custom_mappings: Dict[str, str] = {}
    
    def add_custom_mapping(self, original: str, canonical: str) -> None:
        """Add a custom parameter name mapping."""
        self._custom_mappings[original.lower()] = canonical
    
    def map_parameter(
        self,
        param_name: str,
        data_type: str = "any",
    ) -> ParameterMapping:
        """
        Map a single parameter name to its canonical form.
        
        Args:
            param_name: The parameter name to map
            data_type: The data type of the parameter
            
        Returns:
            ParameterMapping with the result
        """
        lower_name = param_name.lower()
        
        if lower_name in self._custom_mappings:
            return ParameterMapping(
                original_name=param_name,
                canonical_name=self._custom_mappings[lower_name],
                data_type=data_type,
                confidence=MappingConfidence.EXACT,
                reason="custom mapping",
            )
        
        if is_canonical(param_name):
            return ParameterMapping(
                original_name=param_name,
                canonical_name=param_name,
                data_type=data_type,
                confidence=MappingConfidence.EXACT,
                reason="already canonical",
            )
        
        canonical = get_canonical_name(param_name, data_type)
        if canonical:
            return ParameterMapping(
                original_name=param_name,
                canonical_name=canonical,
                data_type=data_type,
                confidence=MappingConfidence.HIGH,
                reason=f"alias for '{canonical}'",
            )
        
        inferred = self._infer_canonical(param_name, data_type)
        if inferred:
            return inferred
        
        return ParameterMapping(
            original_name=param_name,
            canonical_name=param_name,
            data_type=data_type,
            confidence=MappingConfidence.NONE,
            reason="no mapping found",
        )
    
    def _infer_canonical(
        self,
        param_name: str,
        data_type: str,
    ) -> Optional[ParameterMapping]:
        """Try to infer a canonical name from common patterns."""
        lower = param_name.lower()
        
        text_patterns = ["_text", "_string", "_str", "_input", "_content"]
        for pattern in text_patterns:
            if lower.endswith(pattern) or lower.startswith(pattern[1:] + "_"):
                return ParameterMapping(
                    original_name=param_name,
                    canonical_name="text",
                    data_type="string",
                    confidence=MappingConfidence.MEDIUM,
                    reason=f"inferred from pattern '{pattern}'",
                )
        
        int_patterns = ["_count", "_num", "_number", "_idx", "_index"]
        for pattern in int_patterns:
            if lower.endswith(pattern):
                base = pattern[1:]
                canonical = "n" if "count" in base or "num" in base else "index"
                return ParameterMapping(
                    original_name=param_name,
                    canonical_name=canonical,
                    data_type="integer",
                    confidence=MappingConfidence.MEDIUM,
                    reason=f"inferred from pattern '{pattern}'",
                )
        
        list_patterns = ["_list", "_items", "_array", "_values"]
        for pattern in list_patterns:
            if lower.endswith(pattern):
                return ParameterMapping(
                    original_name=param_name,
                    canonical_name="items",
                    data_type="list",
                    confidence=MappingConfidence.MEDIUM,
                    reason=f"inferred from pattern '{pattern}'",
                )
        
        return None
    
    def map_block_interface(
        self,
        block_id: str,
        block_name: str,
        inputs: List[Dict],
    ) -> BlockMappingResult:
        """
        Map all parameters in a block interface.
        
        Args:
            block_id: Block identity hash
            block_name: Block name
            inputs: List of input parameter dicts with 'name' and 'data_type'
            
        Returns:
            BlockMappingResult with all mappings
        """
        result = BlockMappingResult(block_id=block_id, block_name=block_name)
        
        for inp in inputs:
            param_name = inp.get("name", "")
            data_type = inp.get("data_type", "any")
            
            mapping = self.map_parameter(param_name, data_type)
            
            if mapping.confidence == MappingConfidence.NONE:
                result.unmapped.append(param_name)
            elif mapping.original_name == mapping.canonical_name:
                result.unchanged.append(param_name)
            else:
                result.mappings.append(mapping)
        
        return result
    
    def get_statistics(
        self,
        results: List[BlockMappingResult],
    ) -> Dict:
        """Get statistics about parameter mappings."""
        total_params = 0
        mapped = 0
        unchanged = 0
        unmapped = 0
        
        confidence_counts = {c.value: 0 for c in MappingConfidence}
        
        for result in results:
            total_params += len(result.mappings) + len(result.unchanged) + len(result.unmapped)
            mapped += len(result.mappings)
            unchanged += len(result.unchanged)
            unmapped += len(result.unmapped)
            
            for m in result.mappings:
                confidence_counts[m.confidence.value] += 1
        
        return {
            "total_parameters": total_params,
            "mapped": mapped,
            "unchanged": unchanged,
            "unmapped": unmapped,
            "confidence_breakdown": confidence_counts,
            "mapping_rate": round(mapped / total_params * 100, 1) if total_params > 0 else 0,
        }
