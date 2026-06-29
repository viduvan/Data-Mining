"""
tests/test_crawler.py
Unit tests cho crawler module
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.crawler.utils import (
    normalize_text,
    normalize_school_name,
    normalize_major_name,
    normalize_subject_group,
    parse_admission_score,
    parse_quota,
)


class TestNormalizeText:
    def test_strip_whitespace(self):
        assert normalize_text("  Hello  ") == "Hello"

    def test_collapse_spaces(self):
        assert normalize_text("Hello   World") == "Hello World"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_none_returns_empty(self):
        assert normalize_text(None) == ""


class TestNormalizeSchoolName:
    def test_abbreviation_dh(self):
        result = normalize_school_name("ĐH Bách khoa Hà Nội")
        assert "Đại học" in result

    def test_strip_whitespace(self):
        result = normalize_school_name("  Đại học Kinh tế  ")
        assert result == "Đại học Kinh tế"

    def test_empty_returns_empty(self):
        assert normalize_school_name("") == ""


class TestNormalizeSubjectGroup:
    def test_a00_standard(self):
        assert normalize_subject_group("A00") == "A00"

    def test_lowercase(self):
        assert normalize_subject_group("a00") == "A00"

    def test_with_spaces(self):
        assert normalize_subject_group("A 00") == "A00"

    def test_d01(self):
        assert normalize_subject_group("d01") == "D01"

    def test_invalid_returns_original(self):
        result = normalize_subject_group("XYZ")
        assert result == "XYZ"  # Không match format → trả về input upper


class TestParseAdmissionScore:
    def test_valid_float(self):
        assert parse_admission_score("25.5") == 25.5

    def test_comma_decimal(self):
        assert parse_admission_score("25,5") == 25.5

    def test_integer(self):
        assert parse_admission_score("25") == 25.0

    def test_na_returns_none(self):
        assert parse_admission_score("N/A") is None

    def test_empty_returns_none(self):
        assert parse_admission_score("") is None

    def test_out_of_range_returns_none(self):
        assert parse_admission_score("35.0") is None

    def test_negative_returns_none(self):
        assert parse_admission_score("-1") is None

    def test_max_valid_score(self):
        assert parse_admission_score("30.0") == 30.0


class TestParseQuota:
    def test_valid_integer(self):
        assert parse_quota("100") == 100

    def test_thousand_separator(self):
        assert parse_quota("1.200") == 1200

    def test_empty_returns_none(self):
        assert parse_quota("") is None

    def test_na_returns_none(self):
        assert parse_quota("N/A") is None

    def test_very_large_returns_none(self):
        assert parse_quota("999999") is None  # Vượt quá 100000


class TestNormalizeMajorName:
    def test_remove_major_code(self):
        result = normalize_major_name("7480201 - Công nghệ thông tin")
        assert result == "Công nghệ thông tin"

    def test_remove_major_code_dash_variants(self):
        result = normalize_major_name("7480101 – Khoa học máy tính")
        assert result == "Khoa học máy tính"

    def test_no_code(self):
        result = normalize_major_name("Y khoa")
        assert result == "Y khoa"

    def test_strip_whitespace(self):
        result = normalize_major_name("  Luật  ")
        assert result == "Luật"
