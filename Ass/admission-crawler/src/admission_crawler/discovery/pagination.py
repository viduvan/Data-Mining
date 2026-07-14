"""
pagination.py — Extract pagination links from HTML.
"""

import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import List, Set
from bs4 import BeautifulSoup
from admission_crawler.config import settings

def canonicalize_url(url: str, base_url: str = settings.targets.base_url) -> str:
    """
    Standardize a URL:
    - Make absolute
    - Lowercase hostname
    - Remove fragment
    - Sort query parameters
    - Remove tracking params (utm_*)
    - Treat -page0 as base
    """
    if not url:
        return ""
        
    if url.startswith('/'):
        url = base_url.rstrip('/') + url
        
    parsed = urlparse(url)
    if not parsed.netloc:
        return url # Not a valid absolute URL after base_url joining?
        
    # Lowercase netloc
    netloc = parsed.netloc.lower()
    
    # Process path (remove -page0)
    path = parsed.path
    if path.endswith('-page0'):
        path = path[:-6]
        
    # Process query
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    # Filter out utm_ and sort
    filtered_params = sorted([(k, v) for k, v in query_params if not k.startswith('utm_')])
    new_query = urlencode(filtered_params)
    
    # Rebuild
    canonical = urlunparse((
        'https', # Always use https
        netloc,
        path,
        parsed.params,
        new_query,
        '' # Remove fragment
    ))
    
    return canonical

def extract_pagination_links(html: str, current_url: str) -> List[str]:
    """
    Find pagination links like -page1, -page2 within the pagination container.
    Returns a list of canonicalized absolute URLs.
    """
    soup = BeautifulSoup(html, 'lxml')
    links = set()
    
    # We look for links containing '-page'
    # Or typically, Vietnamnet pagination has specific classes, but looking at hrefs is safer
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if '-page' in href:
            canon_url = canonicalize_url(href)
            # Only keep links that share the same base path logic as the current URL
            # Simple check: same domain and similar path prefix
            if settings.targets.allowed_domain in canon_url:
                links.add(canon_url)
                
    return sorted(list(links))
