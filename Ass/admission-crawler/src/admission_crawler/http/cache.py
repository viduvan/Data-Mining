"""
cache.py — SQLite HTTP response cache.
"""

import hashlib
import gzip
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select

from admission_crawler.config import settings
from admission_crawler.constants import get_cache_ttl_days
from admission_crawler.storage.models import UrlCache

logger = logging.getLogger(__name__)

class HttpCache:
    def __init__(self, db_session: Session):
        self.session = db_session
        self.enabled = settings.cache.enabled
        self.html_dir = Path(settings.cache.html_dir)
        
        if self.enabled:
            self.html_dir.mkdir(parents=True, exist_ok=True)

    def _get_url_hash(self, url: str) -> str:
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def get(self, canonical_url: str) -> dict:
        """Retrieve cached response metadata if valid."""
        if not self.enabled:
            return None

        url_hash = self._get_url_hash(canonical_url)
        cache_entry = self.session.execute(
            select(UrlCache).where(UrlCache.url_hash == url_hash)
        ).scalar_one_or_none()

        if not cache_entry:
            return None

        # Check expiration
        if cache_entry.expires_at and datetime.utcnow() > cache_entry.expires_at:
            logger.debug(f"Cache expired for {canonical_url}")
            return None

        return {
            "etag": cache_entry.etag,
            "last_modified": cache_entry.last_modified,
            "html_path": cache_entry.html_path,
            "http_status": cache_entry.http_status
        }

    def invalidate(self, canonical_url: str) -> None:
        """Remove unusable cache metadata and its local body."""
        if not self.enabled:
            return
        url_hash = self._get_url_hash(canonical_url)
        cache_entry = self.session.get(UrlCache, url_hash)
        if not cache_entry:
            return
        html_path = cache_entry.html_path
        self.session.delete(cache_entry)
        self.session.commit()
        if html_path:
            Path(html_path).unlink(missing_ok=True)
    def read_html(self, html_path: str) -> str:
        """Read HTML content from disk."""
        if not html_path or not os.path.exists(html_path):
            return None
            
        try:
            if html_path.endswith('.gz'):
                with gzip.open(html_path, 'rt', encoding='utf-8') as f:
                    return f.read()
            else:
                with open(html_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error reading cache file {html_path}: {e}")
            return None

    def save(self, canonical_url: str, response_text: str, year: int, etag: str = None, last_modified: str = None, http_status: int = 200) -> str:
        """Save response to cache and disk."""
        if not self.enabled:
            return None

        url_hash = self._get_url_hash(canonical_url)
        
        # Save HTML to disk
        filename = f"{url_hash}.html.gz" if settings.cache.compress else f"{url_hash}.html"
        # Year based subfolder
        year_dir = self.html_dir / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        html_path = year_dir / filename
        
        if settings.cache.compress:
            with gzip.open(html_path, 'wt', encoding='utf-8') as f:
                f.write(response_text)
        else:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response_text)
                
        # Save metadata to DB
        ttl_days = get_cache_ttl_days(year)
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)
        
        cache_entry = self.session.execute(
            select(UrlCache).where(UrlCache.url_hash == url_hash)
        ).scalar_one_or_none()
        
        if cache_entry:
            cache_entry.fetched_at = datetime.utcnow()
            cache_entry.expires_at = expires_at
            cache_entry.etag = etag
            cache_entry.last_modified = last_modified
            cache_entry.http_status = http_status
            cache_entry.html_path = str(html_path)
        else:
            new_entry = UrlCache(
                url_hash=url_hash,
                canonical_url=canonical_url,
                fetched_at=datetime.utcnow(),
                expires_at=expires_at,
                etag=etag,
                last_modified=last_modified,
                http_status=http_status,
                html_path=str(html_path)
            )
            self.session.add(new_entry)
            
        self.session.commit()
        return str(html_path)
