"""
Graph rules for block composition.

This module defines and enforces rules for how blocks can be connected
in a composition graph:
- Acyclic requirement
- Type flow consistency
- Trust propagation
- Error handling chains
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

from neurop_forge.core.block_schema import NeuropBlock
from neurop_forge.composition.compatibility import CompatibilityChecker, CompatibilityResult


class ValidationStatus(Enum):
    """Status of graph validation."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


class RuleViolation(Enum):
    """Types of rule violations."""
    CYCLE_DETECTED = "cycle_detected"
    TYPE_MISMATCH = "type_mismatch"
    TRUST_VIOLATION = "trust_violation"
    ORPHAN_NODE = "orphan_node"
    UNREACHABLE_NODE = "unreachable_node"
    ERROR_NOT_HANDLED = "error_not_handled"


@dataclass
class GraphViolation:
    """A violation of graph rules."""
    rule: RuleViolation
    severity: str
    nodes_involved: Tuple[str, ...]
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule.value,
            "severity": self.severity,
            "nodes_involved": list(self.nodes_involved),
            "message": self.message,
        }


@dataclass
class ValidationResult:
    """Result of graph validation."""
    status: ValidationStatus
    is_valid: bool
    violations: Tuple[GraphViolation, ...]
    warnings: Tuple[str, ...]
    node_count: int
    edge_count: int
    graph_trust_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "is_valid": self.is_valid,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": list(self.warnings),
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "graph_trust_score": self.graph_trust_score,
        }


@dataclass
class CompositionGraph:
    """A graph of composed blocks."""
    nodes: Dict[str, NeuropBlock]
    edges: List[Tuple[str, str]]
    entry_points: List[str]
    exit_points: List[str]

    def add_node(self, block: NeuropBlock) -> None:
        """Add a block to the graph."""
        identity = block.get_identity_hash()
        self.nodes[identity] = block

    def add_edge(self, source_id: str, target_id: str) -> None:
        """Add an edge between blocks."""
        self.edges.append((source_id, target_id))

    def get_block(self, identity: str) -> Optional[NeuropBlock]:
        """Get a block by identity."""
        return self.nodes.get(identity)

    def get_successors(self, identity: str) -> List[str]:
        """Get successor block identities."""
        return [target for source, target in self.edges if source == identity]

    def get_predecessors(self, identity: str) -> List[str]:
        """Get predecessor block identities."""
        return [source for source, target in self.edges if target == identity]


class GraphValidator:
    """
    Validator for block composition graphs.
    
    Enforces:
    - No cycles (DAG requirement)
    - Type consistency along edges
    - Trust score requirements
    - Error handling requirements
    """

    MINIMUM_GRAPH_TRUST = 0.2

    def __init__(self, compatibility_checker: Optional[CompatibilityChecker] = None):
        self._compatibility_checker = compatibility_checker or CompatibilityChecker()

    def validate(self, graph: CompositionGraph) -> ValidationResult:
        """
        Validate a composition graph.
        
        Args:
            graph: The graph to validate
            
        Returns:
            ValidationResult with validation details
        """
        violations: List[GraphViolation] = []
        warnings: List[str] = []

        cycle_violations = self._check_cycles(graph)
        violations.extend(cycle_violations)

        type_violations = self._check_type_consistency(graph)
        violations.extend(type_violations)

        trust_violations, trust_warnings = self._check_trust_requirements(graph)
        violations.extend(trust_violations)
        warnings.extend(trust_warnings)

        structure_violations = self._check_graph_structure(graph)
        violations.extend(structure_violations)

        error_violations = self._check_error_handling(graph)
        violations.extend(error_violations)

        graph_trust = self._calculate_graph_trust(graph)

        has_critical = any(v.severity == "critical" for v in violations)
        is_valid = not has_critical and len(violations) == 0

        if is_valid and warnings:
            status = ValidationStatus.WARNING
        elif is_valid:
            status = ValidationStatus.VALID
        else:
            status = ValidationStatus.INVALID

        return ValidationResult(
            status=status,
            is_valid=is_valid,
            violations=tuple(violations),
            warnings=tuple(warnings),
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            graph_trust_score=graph_trust,
        )

    def _check_cycles(self, graph: CompositionGraph) -> List[GraphViolation]:
        """Check for cycles in the graph (must be DAG)."""
        violations: List[GraphViolation] = []

        adjacency: Dict[str, List[str]] = defaultdict(list)
        for source, target in graph.edges:
            adjacency[source].append(target)

        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycle_nodes: List[str] = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        cycle_nodes.append(node)
                        return True
                elif neighbor in rec_stack:
                    cycle_nodes.append(node)
                    cycle_nodes.append(neighbor)
                    return True

            rec_stack.remove(node)
            return False

        for node_id in graph.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    violations.append(GraphViolation(
                        rule=RuleViolation.CYCLE_DETECTED,
                        severity="critical",
                        nodes_involved=tuple(set(cycle_nodes)),
                        message="Cycle detected in composition graph",
                    ))
                    break

        return violations

    def _check_type_consistency(
        self,
        graph: CompositionGraph,
    ) -> List[GraphViolation]:
        """Check type consistency along edges."""
        violations: List[GraphViolation] = []

        for source_id, target_id in graph.edges:
            source = graph.get_block(source_id)
            target = graph.get_block(target_id)

            if not source or not target:
                continue

            result = self._compatibility_checker.check_compatibility(source, target)

            if not result.is_compatible():
                violations.append(GraphViolation(
                    rule=RuleViolation.TYPE_MISMATCH,
                    severity="high",
                    nodes_involved=(source_id, target_id),
                    message=f"Type mismatch: {source.metadata.name} -> {target.metadata.name}",
                ))

        return violations

    def _check_trust_requirements(
        self,
        graph: CompositionGraph,
    ) -> Tuple[List[GraphViolation], List[str]]:
        """Check trust score requirements."""
        violations: List[GraphViolation] = []
        warnings: List[str] = []

        for identity, block in graph.nodes.items():
            trust = block.trust_score.overall_score

            if trust < self.MINIMUM_GRAPH_TRUST:
                violations.append(GraphViolation(
                    rule=RuleViolation.TRUST_VIOLATION,
                    severity="critical",
                    nodes_involved=(identity,),
                    message=f"Block {block.metadata.name} has trust score below minimum ({trust:.2f})",
                ))
            elif trust < 0.5:
                warnings.append(
                    f"Block {block.metadata.name} has low trust score ({trust:.2f})"
                )

        return violations, warnings

    def _check_graph_structure(
        self,
        graph: CompositionGraph,
    ) -> List[GraphViolation]:
        """Check graph structure for issues."""
        violations: List[GraphViolation] = []

        all_sources = set(source for source, _ in graph.edges)
        all_targets = set(target for _, target in graph.edges)
        all_nodes = set(graph.nodes.keys())

        orphans = all_nodes - all_sources - all_targets
        for orphan in orphans:
            if len(graph.nodes) > 1:
                violations.append(GraphViolation(
                    rule=RuleViolation.ORPHAN_NODE,
                    severity="medium",
                    nodes_involved=(orphan,),
                    message=f"Orphan node with no connections: {orphan[:16]}",
                ))

        if graph.entry_points:
            reachable = self._find_reachable(graph, graph.entry_points)
            unreachable = all_nodes - reachable
            for node in unreachable:
                violations.append(GraphViolation(
                    rule=RuleViolation.UNREACHABLE_NODE,
                    severity="medium",
                    nodes_involved=(node,),
                    message=f"Unreachable node: {node[:16]}",
                ))

        return violations

    def _find_reachable(
        self,
        graph: CompositionGraph,
        start_nodes: List[str],
    ) -> Set[str]:
        """Find all nodes reachable from start nodes."""
        reachable: Set[str] = set()
        stack = list(start_nodes)

        while stack:
            node = stack.pop()
            if node not in reachable:
                reachable.add(node)
                stack.extend(graph.get_successors(node))

        return reachable

    def _check_error_handling(
        self,
        graph: CompositionGraph,
    ) -> List[GraphViolation]:
        """Check that errors are properly handled in the graph."""
        violations: List[GraphViolation] = []

        for identity, block in graph.nodes.items():
            if block.failure_modes.can_fail:
                successors = graph.get_successors(identity)

                if successors:
                    for succ_id in successors:
                        succ = graph.get_block(succ_id)
                        if succ and not succ.failure_modes.can_fail:
                            violations.append(GraphViolation(
                                rule=RuleViolation.ERROR_NOT_HANDLED,
                                severity="medium",
                                nodes_involved=(identity, succ_id),
                                message=f"Block {block.metadata.name} can fail but successor doesn't handle errors",
                            ))

        return violations

    def _calculate_graph_trust(self, graph: CompositionGraph) -> float:
        """Calculate overall graph trust score."""
        if not graph.nodes:
            return 0.0

        total_trust = sum(
            block.trust_score.overall_score
            for block in graph.nodes.values()
        )

        return total_trust / len(graph.nodes)

    def create_graph(
        self,
        blocks: List[NeuropBlock],
        edges: Optional[List[Tuple[str, str]]] = None,
    ) -> CompositionGraph:
        """
        Create a composition graph from blocks.
        
        Args:
            blocks: List of blocks to include
            edges: Optional list of edges
            
        Returns:
            CompositionGraph
        """
        nodes = {block.get_identity_hash(): block for block in blocks}

        entry_points = []
        exit_points = []

        if edges:
            sources = set(e[0] for e in edges)
            targets = set(e[1] for e in edges)
            entry_points = [n for n in nodes if n not in targets]
            exit_points = [n for n in nodes if n not in sources]
        else:
            edges = []
            if blocks:
                entry_points = [blocks[0].get_identity_hash()]
                exit_points = [blocks[-1].get_identity_hash()]

        return CompositionGraph(
            nodes=nodes,
            edges=edges or [],
            entry_points=entry_points,
            exit_points=exit_points,
        )
