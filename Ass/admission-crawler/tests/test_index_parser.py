"""
test_index_parser.py
"""

from admission_crawler.parsers.index_parser import parse_index_page

def test_parse_index_page():
    html = """
    <table>
        <tr>
            <th>STT</th>
            <th>Mã trường</th>
            <th>Tên trường</th>
            <th>Tỉnh thành</th>
        </tr>
        <tr>
            <td>1</td>
            <td>BKA</td>
            <td><a href="/giao-duc/diem-thi/bka">Đại học Bách Khoa Hà Nội</a></td>
            <td>Hà Nội</td>
        </tr>
    </table>
    """
    unis, err = parse_index_page(html)
    assert not err
    assert len(unis) == 1
    assert unis[0]["university_code_raw"] == "BKA"
    assert "Đại học Bách Khoa Hà Nội" in unis[0]["university_name_raw"]
    assert unis[0]["province_raw"] == "Hà Nội"
    assert unis[0]["detail_url"] == "/giao-duc/diem-thi/bka"

def test_parse_index_page_error():
    html = "<div>Không có bảng</div>"
    unis, err = parse_index_page(html)
    assert err
    assert len(unis) == 0
