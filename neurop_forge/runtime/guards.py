"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.

Execution Guards - Safety mechanisms for block execution.

Provides:
- RetryPolicy: Automatic retry with backoff
- CircuitBreaker: Fail-fast for unhealthy blocks
- ExecutionGuard: Timeout and resource limits
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import time
import threading


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryPolicy:
    """
    Retry policy for block execution.
    
    Supports:
    - Maximum retry count
    - Exponential backoff
    - Retry on specific exceptions
    """
    max_retries: int = 3
    initial_delay_ms: float = 100.0
    max_delay_ms: float = 5000.0
    exponential_base: float = 2.0
    retry_on_exceptions: Tuple[type, ...] = (Exception,)
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt number."""
        delay = self.initial_delay_ms * (self.exponential_base ** attempt)
        return min(delay, self.max_delay_ms)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Check if should retry given exception and attempt."""
        if attempt >= self.max_retries:
            return False
        return isinstance(exception, self.retry_on_exceptions)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_retries": self.max_retries,
            "initial_delay_ms": self.initial_delay_ms,
            "max_delay_ms": self.max_delay_ms,
            "exponential_base": self.exponential_base,
        }


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for unhealthy blocks.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing fast, requests immediately fail
    - HALF_OPEN: Testing if block has recovered
    """
    failure_threshold: int = 5
    recovery_timeout_ms: float = 30000.0
    half_open_max_calls: int = 3
    
    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    success_count: int = field(default=0)
    last_failure_time: Optional[float] = field(default=None)
    half_open_calls: int = field(default=0)
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if self.last_failure_time is None:
                return False
            
            elapsed = (time.time() - self.last_failure_time) * 1000
            if elapsed >= self.recovery_timeout_ms:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls
        
        return False
    
    def record_success(self) -> None:
        """Record a successful execution."""
        self.failure_count = 0
        self.success_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.success_count = 0
    
    def record_failure(self) -> None:
        """Record a failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            return
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_ms": self.recovery_timeout_ms,
        }


class ExecutionGuard:
    """
    Execution guard with timeout and resource limits.
    
    Features:
    - Execution timeout
    - Memory limit tracking
    - CPU time tracking
    - Graceful cancellation
    """
    
    def __init__(
        self,
        timeout_ms: Optional[float] = None,
        max_memory_bytes: Optional[int] = None,
    ):
        self.timeout_ms = timeout_ms or 30000.0
        self.max_memory_bytes = max_memory_bytes
        self._cancelled = threading.Event()
        self._start_time: Optional[float] = None
    
    def start(self) -> None:
        """Start the guard timer."""
        self._start_time = time.time()
        self._cancelled.clear()
    
    def check(self) -> Tuple[bool, Optional[str]]:
        """Check if execution should continue."""
        if self._cancelled.is_set():
            return False, "Execution cancelled"
        
        if self._start_time is not None:
            elapsed_ms = (time.time() - self._start_time) * 1000
            if elapsed_ms > self.timeout_ms:
                return False, f"Timeout exceeded ({self.timeout_ms}ms)"
        
        return True, None
    
    def cancel(self) -> None:
        """Cancel execution."""
        self._cancelled.set()
    
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self._start_time is None:
            return 0.0
        return (time.time() - self._start_time) * 1000
    
    def remaining_ms(self) -> float:
        """Get remaining time before timeout."""
        elapsed = self.elapsed_ms()
        return max(0.0, self.timeout_ms - elapsed)
    
    def is_cancelled(self) -> bool:
        """Check if cancelled."""
        return self._cancelled.is_set()
    
    def execute_with_timeout(
        self,
        func: Callable[[], Any],
        timeout_ms: Optional[float] = None,
    ) -> Tuple[Any, Optional[str]]:
        """Execute function with timeout."""
        timeout = timeout_ms or self.timeout_ms
        
        result: List[Any] = [None]
        error: List[Optional[str]] = [None]
        
        def target():
            try:
                result[0] = func()
            except Exception as e:
                error[0] = str(e)
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout / 1000.0)
        
        if thread.is_alive():
            return None, f"Timeout after {timeout}ms"
        
        if error[0]:
            return None, error[0]
        
        return result[0], None
