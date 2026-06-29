import requests
from loguru import logger

url = "https://diemthi.tuyensinh247.com/diem-chuan.html"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    logger.info(f"Đang thử kết nối đến {url}...")
    response = requests.get(url, headers=headers, timeout=10)
    logger.success(f"Kết nối thành công! Status code: {response.status_code}")
    logger.info(f"Độ dài HTML: {len(response.text)} ký tự")
    if "Bách khoa" in response.text or "Kinh tế" in response.text or "tuyensinh" in response.text:
        logger.info("Tìm thấy từ khóa hợp lệ trong HTML.")
except Exception as e:
    logger.error(f"Kết nối thất bại: {e}")
