import requests
from bs4 import BeautifulSoup

url = "https://diemthi.vnexpress.net/diem-chuan-dai-hoc"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

print(f"Status: {response.status_code}")
print(f"Độ dài HTML: {len(response.text)}")

# Tìm xem có các thẻ link nào chứa điểm chuẩn
links = [a["href"] for a in soup.find_all("a", href=True)]
print(f"Tổng số link: {len(links)}")
for l in links[:50]:
    if "diem-chuan" in l or "truong" in l:
        print(l)
