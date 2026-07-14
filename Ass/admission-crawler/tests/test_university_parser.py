"""
test_university_parser.py
"""

from admission_crawler.parsers.university_parser import parse_university_page

def test_parse_university_page():
    html = """
    <table>
        <tr>
            <th>STT</th>
            <th>Ngành</th>
            <th>Mã ngành</th>
            <th>Tổ hợp môn</th>
            <th>Điểm chuẩn</th>
            <th>Ghi chú</th>
        </tr>
        <tr>
            <td>1</td>
            <td>Công nghệ thông tin <a href="xem">Xem</a></td>
            <td>7480201</td>
            <td>A00, A01</td>
            <td>28.5</td>
            <td>Xét điểm THPT</td>
        </tr>
    </table>
    """
    cutoffs, err, meta = parse_university_page(html)
    assert not err
    assert len(cutoffs) == 1
    assert "Xem" not in cutoffs[0]["major_name_raw"]
    assert "Công nghệ thông tin" in cutoffs[0]["major_name_raw"]
    assert cutoffs[0]["cutoff_score_raw"] == "28.5"
    assert cutoffs[0]["subject_combination_raw"] == "A00, A01"
