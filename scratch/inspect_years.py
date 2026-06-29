import requests
from bs4 import BeautifulSoup

url = "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-bach-khoa-ha-noi-BKA.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

# Tìm các thẻ h2, h3 và xem các thẻ table tương ứng sau chúng
for el in soup.find_all(["h2", "h3", "h4", "div"]):
    text = el.get_text(strip=True)
    if "Điểm chuẩn" in text and "202" in text:
        print(f"Tiêu đề: {text} (Tag: {el.name}, Class: {el.get('class')})")
        # Tìm table kế tiếp của thẻ này
        sibling = el.find_next_sibling()
        while sibling and sibling.name != "table" and sibling.name not in ["h2", "h3"]:
            sibling = sibling.find_next_sibling()
        if sibling and sibling.name == "table":
            print(f"  -> Có table đi kèm: {len(sibling.find_all('tr'))} dòng.")
