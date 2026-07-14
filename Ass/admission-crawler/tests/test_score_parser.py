"""
test_score_parser.py
"""

from admission_crawler.normalization.score import parse_score

def test_parse_score():
    val, scale = parse_score("28.5")
    assert val == "28.5"
    assert scale == "30"
    
    val, scale = parse_score("28,5")
    assert val == "28.5"
    assert scale == "30"
    
    val, scale = parse_score("85.5")
    assert val == "85.5"
    assert scale == "100"
    
    val, scale = parse_score("950")
    assert val == "950"
    assert scale == "1200"
    
    val, scale = parse_score("Đang cập nhật")
    assert val is None
    assert scale == "unknown"
