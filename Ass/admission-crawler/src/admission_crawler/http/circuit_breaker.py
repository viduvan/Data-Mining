"""
circuit_breaker.py — Stops execution if too many consecutive errors occur.
"""

import time
import logging
from datetime import datetime, timedelta
from admission_crawler.config import settings

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self):
        self.consecutive_failures = 0
        self.threshold = settings.circuit_breaker.consecutive_failures
        self.cooldown_minutes = settings.circuit_breaker.cooldown_minutes
        self.last_failure_time = None
        self.is_open = False

    def record_success(self) -> None:
        """Reset the failure counter on a successful request."""
        self.consecutive_failures = 0
        if self.is_open:
            logger.info("Circuit breaker CLOSED (recovered).")
        self.is_open = False

    def record_failure(self) -> None:
        """Increment the failure counter."""
        self.consecutive_failures += 1
        self.last_failure_time = datetime.utcnow()
        if self.consecutive_failures >= self.threshold:
            self.is_open = True
            logger.error(f"Circuit breaker OPENED! Quá nhiều lỗi liên tiếp ({self.consecutive_failures}).")

    def check(self) -> None:
        """Check if the circuit is open. If so, raise an exception or wait."""
        if self.is_open:
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds() / 60.0
                if elapsed >= self.cooldown_minutes:
                    logger.info("Thời gian cooldown đã hết, thử gửi lại request (HALF-OPEN).")
                    return
                else:
                    remaining = self.cooldown_minutes - elapsed
                    logger.warning(f"Circuit breaker đang MỞ. Phải đợi thêm {remaining:.1f} phút.")
                    time.sleep(remaining * 60)
            else:
                logger.error("Circuit breaker đang MỞ nhưng không có last_failure_time!")
                raise RuntimeError("Circuit breaker is OPEN.")
