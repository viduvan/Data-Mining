"""
test_deduplication.py
"""

import hashlib

def test_fingerprint_generation():
    # Fingerprint = MD5(year + major_name_raw + subject + score)
    year = 2025
    major = "7480201 - Công nghệ thông tin"
    subject = "A00, A01"
    score = "28.5"
    
    fp_str1 = f"{year}|{major}|{subject}|{score}"
    fingerprint1 = hashlib.md5(fp_str1.encode('utf-8')).hexdigest()
    
    fp_str2 = f"{year}|{major}|{subject}|{score}"
    fingerprint2 = hashlib.md5(fp_str2.encode('utf-8')).hexdigest()
    
    assert fingerprint1 == fingerprint2
    
    # Slight change
    fp_str3 = f"{year}|{major}|{subject}|28.0"
    fingerprint3 = hashlib.md5(fp_str3.encode('utf-8')).hexdigest()
    
    assert fingerprint1 != fingerprint3
