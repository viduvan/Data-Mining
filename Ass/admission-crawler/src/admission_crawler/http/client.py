"""
client.py — HTTP client with rate limits, retries, circuit breaker, and cache.
"""

import logging
from typing import Optional, Dict, Any, Tuple

import httpx

from admission_crawler.config import settings
from admission_crawler.constants import DEFAULT_HEADERS
from admission_crawler.http.rate_limiter import RateLimiter
from admission_crawler.http.circuit_breaker import CircuitBreaker
from admission_crawler.http.robots import RobotsChecker
from admission_crawler.http.cache import HttpCache
from admission_crawler.http.retry_policy import create_retry_decorator, is_retryable_status

logger = logging.getLogger(__name__)


class CrawlerClient:
    def __init__(self, db_session):
        timeout = httpx.Timeout(
            connect=settings.http.connect_timeout_seconds,
            read=settings.http.read_timeout_seconds,
            timeout=settings.http.total_timeout_seconds,
        )
        self.client = httpx.Client(
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            follow_redirects=settings.http.follow_redirects,
            max_redirects=settings.http.max_redirects,
        )
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
        self.robots = RobotsChecker()
        self.cache = HttpCache(db_session)
        self.retry_decorator = create_retry_decorator()

    def close(self):
        self.client.close()

    @staticmethod
    def _is_html(content: Optional[str]) -> bool:
        return bool(content and content.lstrip().lower().startswith(("<!doctype html", "<html")))

    def fetch(self, url: str, year: int) -> Tuple[int, Optional[str], Optional[Dict[str, Any]]]:
        """Fetch a permitted URL, validating cached content before parsing."""
        if not url.startswith("https://vietnamnet.vn"):
            return 403, None, {"error": "Domain not allowed"}
        if not self.robots.can_fetch(url):
            return 403, None, {"error": "Blocked by robots.txt"}

        self.circuit_breaker.check()
        cache_meta = self.cache.get(url)
        headers = dict(DEFAULT_HEADERS)
        if cache_meta:
            if cache_meta.get("etag"):
                headers["If-None-Match"] = cache_meta["etag"]
            if cache_meta.get("last_modified"):
                headers["If-Modified-Since"] = cache_meta["last_modified"]

        @self.retry_decorator
        def make_request():
            self.rate_limiter.wait()
            self.rate_limiter.record_request()
            logger.info("Fetching %s", url)
            response = self.client.get(url, headers=headers)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                self.rate_limiter.handle_429(
                    int(retry_after) if retry_after and retry_after.isdigit() else None
                )
                response.raise_for_status()
            if response.status_code == 403:
                raise PermissionError("403 Forbidden received. Must halt.")
            if is_retryable_status(response):
                response.raise_for_status()
            return response

        try:
            response = make_request()
            self.circuit_breaker.record_success()
            if response.status_code == 304 and cache_meta:
                html_content = self.cache.read_html(cache_meta["html_path"])
                if self._is_html(html_content):
                    logger.info("304 Not Modified. Dùng cache cho %s", url)
                    return 304, html_content, None
                logger.warning("Cache không hợp lệ cho %s; tải lại không dùng conditional headers.", url)
                self.cache.invalidate(url)
                return self.fetch(url, year)
            if response.status_code == 200:
                html_content = response.text
                if not self._is_html(html_content):
                    return 502, None, {"error": "Response is not HTML"}
                self.cache.save(
                    url,
                    html_content,
                    year,
                    response.headers.get("ETag"),
                    response.headers.get("Last-Modified"),
                    200,
                )
                return 200, html_content, None
            return response.status_code, None, {"error": f"HTTP {response.status_code}"}
        except PermissionError:
            raise
        except Exception as error:
            self.circuit_breaker.record_failure()
            logger.error("Lỗi fetch %s: %s", url, error)
            return 500, None, {"error": str(error), "type": type(error).__name__}
