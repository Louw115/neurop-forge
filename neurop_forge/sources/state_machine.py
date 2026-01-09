"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
State Machine Utilities - Pure functions for state machine patterns.
All functions are pure, deterministic, and atomic.
"""

def build_state_machine(initial_state: str, states: list, transitions: dict) -> dict:
    """Build a state machine definition."""
    return {
        "initial_state": initial_state,
        "states": states,
        "transitions": transitions,
        "current_state": initial_state
    }


def get_current_state(machine: dict) -> str:
    """Get current state of state machine."""
    return machine.get("current_state", machine.get("initial_state", ""))


def is_valid_state(machine: dict, state: str) -> bool:
    """Check if a state is valid in the machine."""
    return state in machine.get("states", [])


def get_allowed_transitions(machine: dict, from_state: str) -> list:
    """Get allowed transitions from a state."""
    transitions = machine.get("transitions", {})
    return transitions.get(from_state, [])


def can_transition(machine: dict, from_state: str, to_state: str) -> bool:
    """Check if transition is allowed."""
    allowed = get_allowed_transitions(machine, from_state)
    return to_state in allowed


def apply_transition(machine: dict, to_state: str) -> dict:
    """Apply a state transition (returns new machine state)."""
    current = get_current_state(machine)
    if not can_transition(machine, current, to_state):
        return machine
    result = dict(machine)
    result["current_state"] = to_state
    result["previous_state"] = current
    return result


def is_final_state(machine: dict, state: str) -> bool:
    """Check if a state is a final/terminal state."""
    return len(get_allowed_transitions(machine, state)) == 0


def is_in_final_state(machine: dict) -> bool:
    """Check if machine is in a final state."""
    current = get_current_state(machine)
    return is_final_state(machine, current)


def get_state_path(transitions_history: list) -> list:
    """Extract state path from transition history."""
    if not transitions_history:
        return []
    path = [transitions_history[0].get("from_state")]
    for t in transitions_history:
        path.append(t.get("to_state"))
    return path


def build_transition_record(from_state: str, to_state: str, trigger: str, timestamp: str, metadata: dict) -> dict:
    """Build a transition record for history."""
    return {
        "from_state": from_state,
        "to_state": to_state,
        "trigger": trigger,
        "timestamp": timestamp,
        "metadata": metadata
    }


def validate_state_machine(machine: dict) -> dict:
    """Validate state machine definition."""
    errors = []
    states = set(machine.get("states", []))
    initial = machine.get("initial_state", "")
    if not initial:
        errors.append("Missing initial state")
    elif initial not in states:
        errors.append(f"Initial state '{initial}' not in states list")
    transitions = machine.get("transitions", {})
    for from_state, to_states in transitions.items():
        if from_state not in states:
            errors.append(f"Transition from unknown state: {from_state}")
        for to_state in to_states:
            if to_state not in states:
                errors.append(f"Transition to unknown state: {to_state}")
    return {"valid": len(errors) == 0, "errors": errors}


def find_path(machine: dict, from_state: str, to_state: str) -> list:
    """Find a path between two states (BFS)."""
    if from_state == to_state:
        return [from_state]
    transitions = machine.get("transitions", {})
    visited = {from_state}
    queue = [[from_state]]
    while queue:
        path = queue.pop(0)
        current = path[-1]
        for next_state in transitions.get(current, []):
            if next_state == to_state:
                return path + [next_state]
            if next_state not in visited:
                visited.add(next_state)
                queue.append(path + [next_state])
    return []


def is_reachable(machine: dict, from_state: str, to_state: str) -> bool:
    """Check if a state is reachable from another."""
    return len(find_path(machine, from_state, to_state)) > 0


def get_reachable_states(machine: dict, from_state: str) -> list:
    """Get all states reachable from a state."""
    transitions = machine.get("transitions", {})
    reachable = set()
    queue = [from_state]
    while queue:
        current = queue.pop(0)
        for next_state in transitions.get(current, []):
            if next_state not in reachable:
                reachable.add(next_state)
                queue.append(next_state)
    return list(reachable)


def build_order_state_machine() -> dict:
    """Build a typical order processing state machine."""
    return build_state_machine(
        initial_state="pending",
        states=["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"],
        transitions={
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["processing", "cancelled"],
            "processing": ["shipped", "cancelled"],
            "shipped": ["delivered"],
            "delivered": ["refunded"],
            "cancelled": [],
            "refunded": []
        }
    )


def build_payment_state_machine() -> dict:
    """Build a typical payment processing state machine."""
    return build_state_machine(
        initial_state="pending",
        states=["pending", "authorized", "captured", "refunded", "failed", "cancelled"],
        transitions={
            "pending": ["authorized", "failed", "cancelled"],
            "authorized": ["captured", "cancelled"],
            "captured": ["refunded"],
            "refunded": [],
            "failed": ["pending"],
            "cancelled": []
        }
    )


def build_user_lifecycle_machine() -> dict:
    """Build a user account lifecycle state machine."""
    return build_state_machine(
        initial_state="pending_verification",
        states=["pending_verification", "active", "suspended", "deactivated", "deleted"],
        transitions={
            "pending_verification": ["active", "deleted"],
            "active": ["suspended", "deactivated"],
            "suspended": ["active", "deactivated"],
            "deactivated": ["active", "deleted"],
            "deleted": []
        }
    )


def get_state_metadata(machine: dict, state: str) -> dict:
    """Get metadata for a state."""
    state_metadata = machine.get("state_metadata", {})
    return state_metadata.get(state, {})


def add_state_metadata(machine: dict, state: str, metadata: dict) -> dict:
    """Add metadata to a state."""
    result = dict(machine)
    if "state_metadata" not in result:
        result["state_metadata"] = {}
    result["state_metadata"][state] = metadata
    return result


def get_transition_duration(from_state: str, to_state: str, durations: dict) -> int:
    """Get expected duration for a transition."""
    key = f"{from_state}->{to_state}"
    return durations.get(key, 0)


def calculate_total_time_in_state(transitions_history: list, state: str) -> int:
    """Calculate total time spent in a state from history."""
    total = 0
    for i, t in enumerate(transitions_history):
        if t.get("from_state") == state:
            if i + 1 < len(transitions_history):
                from datetime import datetime
                start = t.get("timestamp", "")
                end = transitions_history[i + 1].get("timestamp", "")
                if start and end:
                    try:
                        s = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        e = datetime.fromisoformat(end.replace('Z', '+00:00'))
                        total += int((e - s).total_seconds())
                    except:
                        pass
    return total


def format_state_diagram(machine: dict) -> str:
    """Format state machine as a simple text diagram."""
    lines = ["State Machine:", f"  Initial: {machine.get('initial_state', '')}"]
    lines.append("  Transitions:")
    for from_state, to_states in machine.get("transitions", {}).items():
        for to_state in to_states:
            lines.append(f"    {from_state} -> {to_state}")
    return "\n".join(lines)


def build_saga_step(name: str, action: str, compensation: str, state: str) -> dict:
    """Build a saga step definition."""
    return {
        "name": name,
        "action": action,
        "compensation": compensation,
        "state": state
    }


def get_compensation_actions(saga_steps: list, failed_step_index: int) -> list:
    """Get compensation actions for saga rollback."""
    compensations = []
    for i in range(failed_step_index - 1, -1, -1):
        step = saga_steps[i]
        if step.get("state") == "completed":
            compensations.append({
                "step_name": step.get("name"),
                "compensation": step.get("compensation")
            })
    return compensations


def is_saga_complete(saga_steps: list) -> bool:
    """Check if all saga steps are complete."""
    return all(step.get("state") == "completed" for step in saga_steps)


def is_saga_failed(saga_steps: list) -> bool:
    """Check if any saga step has failed."""
    return any(step.get("state") == "failed" for step in saga_steps)


def get_next_saga_step(saga_steps: list) -> int:
    """Get index of next saga step to execute."""
    for i, step in enumerate(saga_steps):
        if step.get("state") == "pending":
            return i
    return -1
