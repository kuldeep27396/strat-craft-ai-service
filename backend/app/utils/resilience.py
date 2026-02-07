"""
Resilience patterns: Retry with exponential backoff and circuit breaker.

Usage:
    @async_retry(max_attempts=3, base_delay=1.0)
    async def call_llm():
        ...

    breaker = CircuitBreaker()
    await breaker.call(some_function, arg1, arg2)
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec('P')
T = TypeVar('T')


def async_retry(max_attempts: int = 3, base_delay: float = 1.0):
    """Decorator for async retry with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles each retry)
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = auto()    # Normal operation
    OPEN = auto()      # Failing, reject requests
    HALF_OPEN = auto() # Testing if recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_attempts: int = 1


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures.

    Usage:
        breaker = CircuitBreaker(CircuitBreakerConfig())
        try:
            result = await breaker.call(some_function, arg1, arg2)
        except CircuitBreakerOpenError:
            # Handle open circuit
    """

    def __init__(self, config: CircuitBreakerConfig | None = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_attempts = 0

    def record_success(self):
        """Record a successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.half_open_attempts = 0

    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

    def can_attempt(self) -> bool:
        """Check if request should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if (datetime.utcnow() - self.last_failure_time).total_seconds() > self.config.timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.half_open_attempts = 0
                return True
            return False

        return self.half_open_attempts < self.config.half_open_attempts

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if not self.can_attempt():
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise
