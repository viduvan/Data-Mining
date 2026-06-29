import requests
from bs4 import BeautifulSoup

url = "https://diemthi.vnexpress.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")
print(f"Status: {response.status_code}")
print(f"Title: {soup.title.get_text() if soup.title else 'None'}")

# In các link có trên trang
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if "điểm chuẩn" in text.lower() or "diem-chuan" in href or "tra-cuu" in href:
        print(f"Text: {text} -> Href: {href}")
