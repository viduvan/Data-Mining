"""
src/crawler/__init__.py
Crawler package cho Vietnam University Admission Data Mining
"""

from .base_crawler import BaseCrawler
from .admission_crawler import AdmissionCrawler
from .school_info_crawler import SchoolInfoCrawler

__all__ = ["BaseCrawler", "AdmissionCrawler", "SchoolInfoCrawler"]
