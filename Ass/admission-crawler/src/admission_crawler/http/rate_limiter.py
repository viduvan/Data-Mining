"""
rate_limiter.py — Delay and quota management.
"""

import time
import random
import logging
from datetime import datetime
from admission_crawler.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.min_delay = settings.rate_limit.min_delay_seconds
        self.max_delay = settings.rate_limit.max_delay_seconds
        self.requests_per_hour = settings.rate_limit.requests_per_hour_cap
        self.requests_per_day = settings.rate_limit.requests_per_day_cap
        
        self.last_request_time = 0.0
        self.requests_this_hour = 0
        self.requests_today = 0
        self.current_hour = datetime.utcnow().hour
        self.current_day = datetime.utcnow().day
        
        self.reduced_speed_multiplier = 1.0

    def wait(self) -> None:
        """Wait before the next request to respect rate limits."""
        now = datetime.utcnow()
        
        # Reset counters if hour/day changed
        if now.hour != self.current_hour:
            self.requests_this_hour = 0
            self.current_hour = now.hour
            
        if now.day != self.current_day:
            self.requests_today = 0
            self.current_day = now.day

        # Check quotas
        if self.requests_today >= self.requests_per_day:
            logger.error("Đã đạt giới hạn request theo ngày. Dừng crawl.")
            raise PermissionError("Daily request quota exceeded.")
            
        if self.requests_this_hour >= self.requests_per_hour:
            logger.warning("Đã đạt giới hạn request theo giờ. Tạm nghỉ...")
            # Calculate time until next hour
            sleep_time = 3600 - (now.minute * 60 + now.second)
            time.sleep(sleep_time)
            self.requests_this_hour = 0

        # Calculate jitter delay
        elapsed = time.time() - self.last_request_time
        target_delay = random.uniform(self.min_delay, self.max_delay) * self.reduced_speed_multiplier
        
        if elapsed < target_delay:
            time.sleep(target_delay - elapsed)

    def record_request(self) -> None:
        """Record that a request was made."""
        self.last_request_time = time.time()
        self.requests_this_hour += 1
        self.requests_today += 1

    def handle_429(self, retry_after: int = None) -> None:
        """Handle HTTP 429 Too Many Requests."""
        self.reduced_speed_multiplier *= 2.0  # Reduce speed by half
        sleep_minutes = retry_after / 60 if retry_after else settings.rate_limit_429.first_hit_sleep_minutes
        logger.warning(f"Gặp 429 Too Many Requests. Nghỉ {sleep_minutes} phút. Giảm tốc độ còn 1/2.")
        time.sleep(sleep_minutes * 60)
