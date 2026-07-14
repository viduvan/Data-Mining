"""
robots.py — robots.txt checker.
"""

from urllib.robotparser import RobotFileParser
import httpx
import logging
from admission_crawler.config import settings
from admission_crawler.constants import DEFAULT_HEADERS

logger = logging.getLogger(__name__)

class RobotsChecker:
    def __init__(self):
        self.parser = RobotFileParser()
        self.url = settings.targets.robots_url
        self.is_fetched = False

    def fetch(self) -> None:
        """Fetch and parse robots.txt."""
        try:
            logger.info(f"Đang kiểm tra {self.url}")
            with httpx.Client(timeout=10.0, headers=DEFAULT_HEADERS) as client:
                response = client.get(self.url)
                response.raise_for_status()
                lines = response.text.splitlines()
                self.parser.parse(lines)
                self.is_fetched = True
                logger.info("Đã parse xong robots.txt")
        except Exception as e:
            logger.error(f"Lỗi khi lấy robots.txt: {e}")
            # If robots.txt fails, assume we can crawl but log error
            self.is_fetched = False

    def can_fetch(self, url: str) -> bool:
        """Check if the given URL is allowed to be fetched."""
        if not self.is_fetched:
            self.fetch()
            
        if not self.is_fetched:
            logger.warning("Không thể đọc robots.txt, mặc định cho phép.")
            return True
            
        is_allowed = self.parser.can_fetch(settings.http.user_agent, url)
        if not is_allowed:
            logger.warning(f"robots.txt CHẶN đường dẫn này: {url}")
        return is_allowed
