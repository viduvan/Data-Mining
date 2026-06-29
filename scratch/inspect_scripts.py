import requests
from bs4 import BeautifulSoup

url = "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-bach-khoa-ha-noi-BKA.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

scripts = soup.find_all("script")
print(f"Tìm thấy {len(scripts)} thẻ script.")
for i, script in enumerate(scripts):
    content = script.get_text()
    if "more-link" in content or "click" in content or "load" in content or "diem-chuan" in content:
        print(f"Script {i+1} (length {len(content)}):")
        print(content[:500])
        print("-" * 50)
