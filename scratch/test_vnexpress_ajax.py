import requests
from bs4 import BeautifulSoup

url = "https://diemthi.vnexpress.net/tra-cuu-dai-hoc/dai-hoc-bach-khoa-ha-noi-349"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

# In 10 dòng đầu có chứa text liên quan đến ngành hoặc điểm chuẩn
lines = response.text.split("\n")
matched = 0
for idx, l in enumerate(lines):
    if "Công nghệ" in l or "IT1" in l or "29." in l or "28." in l:
        print(f"Line {idx}: {l.strip()[:150]}")
        matched += 1
        if matched > 20:
            break
            
if matched == 0:
    print("Không tìm thấy từ khóa nào trong HTML raw. Có vẻ dữ liệu được load bằng AJAX.")
