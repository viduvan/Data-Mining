import requests
from bs4 import BeautifulSoup

url = "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-bach-khoa-ha-noi-BKA.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

# Tìm các bảng hoặc thông tin điểm chuẩn
tables = soup.find_all("table")
print(f"Tìm thấy {len(tables)} bảng trên trang.")

for i, table in enumerate(tables):
    rows = table.find_all("tr")
    print(f"Bảng {i+1}: {len(rows)} dòng.")
    if len(rows) > 0:
        headers_cols = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
        print(f"  Headers: {headers_cols}")
        # In thử 3 dòng đầu
        for row in rows[1:4]:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            print(f"    Row: {cells}")
