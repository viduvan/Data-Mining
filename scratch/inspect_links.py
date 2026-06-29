import requests
from bs4 import BeautifulSoup

url = "https://diemthi.tuyensinh247.com/diem-chuan.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

# Tìm các link dẫn tới điểm chuẩn của từng trường
links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "diem-chuan-" in href:
        links.append((a.get_text(strip=True), href))

print(f"Tìm thấy {len(links)} links điểm chuẩn.")
for name, href in links[:15]:
    print(f"  Trường: {name:<40} -> Link: {href}")
