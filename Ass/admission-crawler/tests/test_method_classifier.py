"""
test_method_classifier.py
"""

from admission_crawler.normalization.admission_method import classify_admission_method

def test_classify_admission_method():
    # Test THPT exam
    method, conf, rule = classify_admission_method("Kỹ thuật phần mềm", "A00, A01", "Xét điểm thi THPT quốc gia")
    assert method == "thpt_exam"
    assert conf == 1.0
    
    # Test High school transcript
    method, conf, rule = classify_admission_method("Kinh tế", "", "Xét tuyển học bạ")
    assert method == "transcript"
    assert conf == 1.0
    
    # Test DGNL
    method, conf, rule = classify_admission_method("Khoa học máy tính", "", "Kết quả thi ĐGNL ĐHQGHN")
    assert method == "dgnl_dhqg"
    
    # Test unknown
    method, conf, rule = classify_admission_method("Y đa khoa", "", "")
    assert method == "unknown"
