"""
src/crawler/base_crawler.py
Abstract base class cho tất cả crawler — retry, rate limiting, logging
"""

import time
import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)
import logging

from .config import (
    DEFAULT_HEADERS,
    CRAWL_DELAY_SECONDS,
    CRAWL_MAX_RETRIES,
    CRAWL_TIMEOUT_SECONDS,
    CRAWL_BACKOFF_FACTOR,
    DATA_RAW_DIR,
)
from .utils import get_random_user_agent, random_delay, get_timestamp


class BaseCrawler(ABC):
    """
    Abstract base class cho tất cả crawler.

    Cung cấp:
    - HTTP session management
    - Retry logic với exponential backoff
    - Rate limiting
    - User-Agent rotation
    - Logging chuẩn
    """

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or DATA_RAW_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = self._make_session()
        self._request_count = 0
        logger.info(f"{self.__class__.__name__} khởi tạo. Output: {self.output_dir}")

    def _make_session(self) -> requests.Session:
        """Tạo HTTP session với headers mặc định."""
        session = requests.Session()
        headers = DEFAULT_HEADERS.copy()
        headers["User-Agent"] = get_random_user_agent()
        session.headers.update(headers)
        return session

    def _rotate_user_agent(self) -> None:
        """Thay đổi User-Agent định kỳ."""
        new_ua = get_random_user_agent()
        self.session.headers.update({"User-Agent": new_ua})
        logger.debug(f"User-Agent rotated: {new_ua[:50]}...")

    def fetch_page(
        self,
        url: str,
        params: dict = None,
        timeout: int = None,
    ) -> Optional[str]:
        """
        Tải nội dung HTML từ URL với retry tự động.

        Args:
            url: URL cần tải
            params: Query parameters
            timeout: Timeout (seconds)

        Returns:
            HTML content string hoặc None nếu thất bại
        """
        timeout = timeout or CRAWL_TIMEOUT_SECONDS

        # Rotate User-Agent mỗi 10 requests
        self._request_count += 1
        if self._request_count % 10 == 0:
            self._rotate_user_agent()

        try:
            html = self._fetch_with_retry(url, params, timeout)
            random_delay(CRAWL_DELAY_SECONDS)
            return html
        except RetryError as e:
            logger.error(f"Thất bại sau {CRAWL_MAX_RETRIES} lần retry: {url} — {e}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không mong đợi khi tải {url}: {e}")
            return None

    @retry(
        stop=stop_after_attempt(CRAWL_MAX_RETRIES),
        wait=wait_exponential(multiplier=CRAWL_BACKOFF_FACTOR, min=2, max=30),
        retry=retry_if_exception_type(
            (requests.exceptions.ConnectionError,
             requests.exceptions.Timeout,
             requests.exceptions.ChunkedEncodingError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _fetch_with_retry(
        self, url: str, params: dict, timeout: int
    ) -> Optional[str]:
        """Internal method với retry decorator."""
        response = self.session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"
        logger.debug(f"GET {url} → {response.status_code} ({len(response.text)} chars)")
        return response.text

    def parse_html(self, html: str, parser: str = "lxml") -> Optional[BeautifulSoup]:
        """
        Parse HTML string thành BeautifulSoup object.

        Args:
            html: HTML string
            parser: Parser backend ('lxml', 'html.parser')

        Returns:
            BeautifulSoup object hoặc None
        """
        if not html:
            return None
        try:
            soup = BeautifulSoup(html, parser)
            return soup
        except Exception as e:
            logger.error(f"Lỗi parse HTML: {e}")
            return None

    def close(self) -> None:
        """Đóng HTTP session."""
        self.session.close()
        logger.info(f"{self.__class__.__name__} session đóng.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ================================================================
    # Abstract methods — subclasses phải implement
    # ================================================================

    @abstractmethod
    def crawl(self, *args, **kwargs):
        """
        Phương thức crawl chính. Subclass phải implement.
        Trả về list of dict records.
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, data: list, filename: str) -> Path:
        """
        Lưu dữ liệu đã crawl. Subclass phải implement.
        Trả về Path của file đã lưu.
        """
        raise NotImplementedError
