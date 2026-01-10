"""
Interface Normalizer for Neurop Block Forge V2.

Updates block interfaces with standardized parameter names while
maintaining backward compatibility through alias metadata.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from neurop_forge.standardization.parameter_mapper import (
    ParameterMapper,
    BlockMappingResult,
    MappingConfidence,
)


@dataclass
class NormalizationResult:
    """Result of normalizing block interfaces."""
    blocks_processed: int = 0
    blocks_modified: int = 0
    parameters_normalized: int = 0
    parameters_unchanged: int = 0
    parameters_unmapped: int = 0
    errors: List[str] = field(default_factory=list)
    modified_blocks: List[str] = field(default_factory=list)


class InterfaceNormalizer:
    """Normalizes block interfaces with standard parameter names."""
    
    def __init__(
        self,
        library_path: str = ".neurop_expanded_library",
        output_path: Optional[str] = None,
        min_confidence: MappingConfidence = MappingConfidence.MEDIUM,
    ):
        self.library_path = Path(library_path)
        self.output_path = Path(output_path) if output_path else self.library_path
        self.min_confidence = min_confidence
        self._mapper = ParameterMapper()
        self._result = NormalizationResult()
    
    def add_custom_mapping(self, original: str, canonical: str) -> None:
        """Add a custom parameter name mapping."""
        self._mapper.add_custom_mapping(original, canonical)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze all blocks without modifying them.
        
        Returns:
            Analysis results with mapping statistics
        """
        if not self.library_path.exists():
            return {"error": f"Library not found: {self.library_path}"}
        
        mapping_results: List[BlockMappingResult] = []
        blocks_with_changes = 0
        
        for block_file in self.library_path.glob("*.json"):
            try:
                with open(block_file) as f:
                    block_data = json.load(f)
                
                block_id = block_data.get("identity", {}).get("hash_value", "")
                block_name = block_data.get("metadata", {}).get("name", "")
                inputs = block_data.get("interface", {}).get("inputs", [])
                
                result = self._mapper.map_block_interface(block_id, block_name, inputs)
                mapping_results.append(result)
                
                if result.has_changes:
                    blocks_with_changes += 1
                    
            except Exception as e:
                continue
        
        stats = self._mapper.get_statistics(mapping_results)
        stats["blocks_analyzed"] = len(mapping_results)
        stats["blocks_with_changes"] = blocks_with_changes
        
        top_mappings: Dict[str, int] = {}
        for result in mapping_results:
            for m in result.mappings:
                key = f"{m.original_name} -> {m.canonical_name}"
                top_mappings[key] = top_mappings.get(key, 0) + 1
        
        stats["top_mappings"] = sorted(
            top_mappings.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:20]
        
        return stats
    
    def normalize(
        self,
        execute: bool = False,
        preserve_aliases: bool = True,
    ) -> NormalizationResult:
        """
        Normalize all block interfaces.
        
        Args:
            execute: If True, write changes; False for dry-run
            preserve_aliases: If True, store original names as aliases
            
        Returns:
            NormalizationResult with statistics
        """
        self._result = NormalizationResult()
        
        if not self.library_path.exists():
            self._result.errors.append(f"Library not found: {self.library_path}")
            return self._result
        
        if execute and self.output_path != self.library_path:
            self.output_path.mkdir(parents=True, exist_ok=True)
        
        for block_file in self.library_path.glob("*.json"):
            try:
                self._process_block(block_file, execute, preserve_aliases)
            except Exception as e:
                self._result.errors.append(f"{block_file.name}: {str(e)}")
        
        return self._result
    
    def _process_block(
        self,
        block_file: Path,
        execute: bool,
        preserve_aliases: bool,
    ) -> None:
        """Process a single block file."""
        with open(block_file) as f:
            block_data = json.load(f)
        
        self._result.blocks_processed += 1
        
        block_id = block_data.get("identity", {}).get("hash_value", "")
        block_name = block_data.get("metadata", {}).get("name", "")
        inputs = block_data.get("interface", {}).get("inputs", [])
        
        mapping_result = self._mapper.map_block_interface(block_id, block_name, inputs)
        
        self._result.parameters_unchanged += len(mapping_result.unchanged)
        self._result.parameters_unmapped += len(mapping_result.unmapped)
        
        if not mapping_result.has_changes:
            if execute and self.output_path != self.library_path:
                output_file = self.output_path / block_file.name
                with open(output_file, "w") as f:
                    json.dump(block_data, f, indent=2)
            return
        
        high_confidence_mappings = [
            m for m in mapping_result.mappings
            if self._meets_confidence(m.confidence)
        ]
        
        if not high_confidence_mappings:
            if execute and self.output_path != self.library_path:
                output_file = self.output_path / block_file.name
                with open(output_file, "w") as f:
                    json.dump(block_data, f, indent=2)
            return
        
        self._result.blocks_modified += 1
        self._result.modified_blocks.append(block_name)
        self._result.parameters_normalized += len(high_confidence_mappings)
        
        mapping_dict = {m.original_name: m for m in high_confidence_mappings}
        
        for inp in block_data.get("interface", {}).get("inputs", []):
            param_name = inp.get("name", "")
            if param_name in mapping_dict:
                mapping = mapping_dict[param_name]
                
                if preserve_aliases:
                    aliases = inp.get("aliases", [])
                    if param_name not in aliases:
                        aliases.append(param_name)
                    inp["aliases"] = aliases
                
                inp["name"] = mapping.canonical_name
                inp["original_name"] = param_name
        
        if execute:
            output_file = self.output_path / block_file.name
            with open(output_file, "w") as f:
                json.dump(block_data, f, indent=2)
    
    def _meets_confidence(self, confidence: MappingConfidence) -> bool:
        """Check if confidence meets minimum threshold."""
        confidence_order = [
            MappingConfidence.NONE,
            MappingConfidence.LOW,
            MappingConfidence.MEDIUM,
            MappingConfidence.HIGH,
            MappingConfidence.EXACT,
        ]
        return confidence_order.index(confidence) >= confidence_order.index(self.min_confidence)
    
    def get_result(self) -> NormalizationResult:
        """Get the current normalization result."""
        return self._result
