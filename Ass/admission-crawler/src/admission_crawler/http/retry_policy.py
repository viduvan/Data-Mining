"""
retry_policy.py — Tenacity configuration for HTTP requests.
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
    retry_if_result,
    before_sleep_log
)
import httpx
import logging
from admission_crawler.config import settings

logger = logging.getLogger(__name__)

def is_retryable_status(response: httpx.Response) -> bool:
    """Return True if the response status code is in the retry list."""
    if response is None:
        return True # Retry on connection errors where response is None
    return response.status_code in settings.retry.retry_statuses

def create_retry_decorator():
    """Create a configured Tenacity retry decorator."""
    
    # Custom wait strategy that follows the configured backoff list
    # Tenacity's wait_chain or wait_fixed can be used. 
    # Since we have specific list [30, 90, 300], we can implement a custom wait.
    
    backoff_list = settings.retry.backoff_seconds
    
    def custom_wait(retry_state):
        attempt = retry_state.attempt_number - 1
        if attempt < len(backoff_list):
            return backoff_list[attempt]
        return backoff_list[-1]

    return retry(
        stop=stop_after_attempt(settings.retry.max_attempts),
        wait=custom_wait,
        retry=(
            retry_if_exception_type(httpx.RequestError) |
            retry_if_exception_type(httpx.TimeoutException)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )

# Note: In `client.py`, we will likely wrap the actual request call in this decorator, 
# or apply it programmatically.
