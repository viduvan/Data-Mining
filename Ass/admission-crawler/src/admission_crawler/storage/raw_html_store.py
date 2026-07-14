"""
raw_html_store.py — Raw HTML filesystem storage (distinct from cache).
"""

import os
import gzip
from pathlib import Path
from admission_crawler.config import settings

def save_raw_html(year: int, url_hash: str, content: str) -> str:
    """
    Save raw HTML permanently for data provenance.
    Returns the file path.
    """
    base_dir = Path(settings.cache.html_dir) / str(year)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = base_dir / f"{url_hash}.html.gz"
    
    # Only save if not exists to save disk I/O, unless we need to overwrite.
    # Usually content hash implies content is same.
    if not file_path.exists():
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            f.write(content)
            
    return str(file_path)
