"""
Timeout handling utilities.

Usage:
    @with_timeout(timeout_seconds=30)
    async def long_running_operation():
        ...
"""

import asyncio
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec('P')
T = TypeVar('T')


def with_timeout(timeout_seconds: float):
    """Decorator to add timeout to async functions.

    Args:
        timeout_seconds: Maximum time to wait before raising TimeoutError

    Raises:
        TimeoutError: If function doesn't complete within timeout
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"{func.__name__} timed out after {timeout_seconds}s")
        return wrapper
    return decorator
