import requests
from bs4 import BeautifulSoup
import re

url = "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-bach-khoa-ha-noi-BKA.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

print("Duyệt các thẻ tiêu đề:")
for tag in ["h2", "h3", "h4", "div", "p"]:
    for el in soup.find_all(tag):
        text = el.get_text(strip=True)
        if "điểm chuẩn" in text.lower() and "202" in text:
            print(f"[{tag.upper()}] Text: {text[:80]}")
