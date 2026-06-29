import requests
from bs4 import BeautifulSoup

url = "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-bach-khoa-ha-noi-BKA.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

for el in soup.find_all(True):
    text = el.get_text(strip=True)
    if "Xem thêm điểm chuẩn theo phương thức Điểm thi THPT năm 2024" == text:
        print(f"Tag: {el.name}, Class: {el.get('class')}")
        print(f"Raw HTML: {el}")
        # In các element cha con của nó
        print(f"Parent: {el.parent.name}, Class: {el.parent.get('class')}")
