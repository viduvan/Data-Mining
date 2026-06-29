import requests
from bs4 import BeautifulSoup

url = "https://diemthi.vnexpress.net/tra-cuu-dai-hoc"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")
print(f"Status: {response.status_code}")
print(f"Title: {soup.title.get_text() if soup.title else 'None'}")

# In 50 link đầu tiên
for a in soup.find_all("a", href=True)[:50]:
    print(f"Text: {a.get_text(strip=True)[:40]:<40} -> Href: {a['href']}")
