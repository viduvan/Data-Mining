import requests
from bs4 import BeautifulSoup

url = "https://diemthi.tuyensinh247.com/diem-chuan.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

# In 100 links đầu tiên có chứa href
links = [a["href"] for a in soup.find_all("a", href=True)]
print(f"Tổng số links: {len(links)}")
for l in links[:50]:
    print(l)
