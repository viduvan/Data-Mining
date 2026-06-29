import requests
from bs4 import BeautifulSoup

url = "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-bach-khoa-ha-noi-BKA.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

for div in soup.find_all("div", class_="more-link"):
    a = div.find("a")
    if a:
        print(f"Text: {a.get_text(strip=True)}")
        print(f"Attributes: {a.attrs}")
        print(f"Parent Div Attributes: {div.attrs}")
