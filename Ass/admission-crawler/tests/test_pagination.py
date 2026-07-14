"""
test_pagination.py
"""

from admission_crawler.discovery.pagination import canonicalize_url, extract_pagination_links

def test_canonicalize_url():
    base = "https://vietnamnet.vn"
    assert canonicalize_url("/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025-page0") == "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025"
    assert canonicalize_url("/giao-duc?utm_source=fb") == "https://vietnamnet.vn/giao-duc"
    
def test_extract_pagination_links():
    html = """
    <div class="pagination">
        <a href="/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025-page1">2</a>
        <a href="/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025-page2">3</a>
    </div>
    """
    links = extract_pagination_links(html, "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025")
    assert len(links) == 2
    assert "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025-page1" in links
