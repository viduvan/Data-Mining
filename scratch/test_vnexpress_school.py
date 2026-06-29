import requests
from bs4 import BeautifulSoup

url = "https://diemthi.vnexpress.net/tra-cuu-dai-hoc/dai-hoc-bach-khoa-ha-noi-349"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")
print(f"Status: {response.status_code}")

# Tìm các table và xem nội dung
tables = soup.find_all("table")
print(f"Tìm thấy {len(tables)} bảng trên trang.")
for i, table in enumerate(tables):
    rows = table.find_all("tr")
    print(f"Bảng {i+1}: {len(rows)} dòng.")
    if len(rows) > 0:
        headers_cols = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
        print(f"  Headers: {headers_cols}")
        for r in rows[1:4]:
            cells = [td.get_text(strip=True) for td in r.find_all("td")]
            print(f"    Row: {cells}")
            
# Tìm xem có cấu trúc chọn năm không (tab hoặc select)
selects = soup.find_all("select")
print(f"Tìm thấy {len(selects)} thẻ select:")
for s in selects:
    print(f"  Select name: {s.get('name')}, id: {s.get('id')}")
    for opt in s.find_all("option"):
        print(f"    Option: {opt.get_text(strip=True)} -> Value: {opt.get('value')}")
