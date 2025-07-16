"""
Error Handling Service
Provides robust error handling and retry mechanisms for API calls and operations
"""

import asyncio
import logging
import time
from typing import Any, Callable, Optional, TypeVar, Union
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')

class APIError(Exception):
    """Custom exception for API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: tuple = (Exception,)

class ErrorHandler:
    def __init__(self):
        self.retry_config = RetryConfig()
        self.error_counts = {}
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60  # seconds

    async def call_api_with_retry(
        self,
        api_call: Callable,
        *args,
        retry_config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Any:
        """Call API with retry mechanism"""
        config = retry_config or self.retry_config
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                # Check circuit breaker
                if self._is_circuit_open(api_call.__name__):
                    raise APIError("Circuit breaker is open")
                
                # Make API call
                if asyncio.iscoroutinefunction(api_call):
                    result = await api_call(*args, **kwargs)
                else:
                    result = api_call(*args, **kwargs)
                
                # Reset error count on success
                self._reset_error_count(api_call.__name__)
                return result
                
            except config.retry_on_exceptions as e:
                last_exception = e
                self._increment_error_count(api_call.__name__)
                
                if attempt < config.max_retries:
                    delay = self._calculate_delay(attempt, config)
                    logger.warning(f"API call failed (attempt {attempt + 1}/{config.max_retries + 1}): {e}")
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"API call failed after {config.max_retries + 1} attempts: {e}")
                    break
        
        # If we get here, all retries failed
        if isinstance(last_exception, APIError):
            raise last_exception
        else:
            raise APIError(f"API call failed after {config.max_retries + 1} attempts: {last_exception}")

    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for exponential backoff with jitter"""
        delay = min(
            config.base_delay * (config.exponential_base ** attempt),
            config.max_delay
        )
        
        if config.jitter:
            # Add jitter to prevent thundering herd
            jitter = delay * 0.1 * (time.time() % 1)
            delay += jitter
        
        return delay

    def _increment_error_count(self, operation_name: str):
        """Increment error count for circuit breaker"""
        if operation_name not in self.error_counts:
            self.error_counts[operation_name] = {"count": 0, "last_error": None}
        
        self.error_counts[operation_name]["count"] += 1
        self.error_counts[operation_name]["last_error"] = datetime.now()

    def _reset_error_count(self, operation_name: str):
        """Reset error count on successful operation"""
        if operation_name in self.error_counts:
            self.error_counts[operation_name]["count"] = 0
            self.error_counts[operation_name]["last_error"] = None

    def _is_circuit_open(self, operation_name: str) -> bool:
        """Check if circuit breaker is open"""
        if operation_name not in self.error_counts:
            return False
        
        error_info = self.error_counts[operation_name]
        
        # Check if error count exceeds threshold
        if error_info["count"] >= self.circuit_breaker_threshold:
            # Check if timeout has passed
            if error_info["last_error"]:
                time_since_last_error = datetime.now() - error_info["last_error"]
                if time_since_last_error.total_seconds() < self.circuit_breaker_timeout:
                    return True
                else:
                    # Reset after timeout
                    self._reset_error_count(operation_name)
        
        return False

    def with_error_handling(self, retry_config: Optional[RetryConfig] = None):
        """Decorator for adding error handling to functions"""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                return await self.call_api_with_retry(func, *args, retry_config=retry_config, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                return self.call_api_with_retry(func, *args, retry_config=retry_config, **kwargs)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator

    def handle_async_operation(
        self,
        operation: Callable,
        *args,
        retry_config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Any:
        """Handle async operations with error handling"""
        return self.call_api_with_retry(operation, *args, retry_config=retry_config, **kwargs)

    def create_custom_retry_config(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on_exceptions: tuple = (Exception,)
    ) -> RetryConfig:
        """Create a custom retry configuration"""
        return RetryConfig(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retry_on_exceptions=retry_on_exceptions
        )

    def get_error_stats(self) -> dict:
        """Get error statistics for monitoring"""
        return {
            "error_counts": self.error_counts,
            "circuit_breaker_threshold": self.circuit_breaker_threshold,
            "circuit_breaker_timeout": self.circuit_breaker_timeout
        }

    def reset_error_stats(self):
        """Reset all error statistics"""
        self.error_counts = {}

# Global instances
error_handler = ErrorHandler()

# Convenience functions
async def call_api_with_retry(
    api_call: Callable,
    *args,
    retry_config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """Call API with retry mechanism"""
    return await error_handler.call_api_with_retry(api_call, *args, retry_config=retry_config, **kwargs)

def with_error_handling(retry_config: Optional[RetryConfig] = None):
    """Decorator for adding error handling to functions"""
    return error_handler.with_error_handling(retry_config)