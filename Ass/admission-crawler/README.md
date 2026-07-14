# Admission Crawler

Python crawler thu thập điểm chuẩn đại học Hà Nội từ VietNamNet (2016–2025).

## Mục đích

Dự án nghiên cứu học thuật — phân tích xu hướng điểm chuẩn đại học tại Hà Nội.
Dữ liệu chỉ dùng nội bộ, không phát hành lại raw HTML hoặc toàn bộ dataset.

## Cài đặt

```bash
cd admission-crawler
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Sử dụng nhanh

```bash
# Kiểm tra robots.txt và cấu trúc trang
admission-crawler preflight --year 2025

# Discovery danh sách trường Hà Nội
admission-crawler discover --years 2025:2025 --province "Hà Nội"

# Pilot 2 trường trước khi crawl toàn bộ
admission-crawler crawl --years 2025:2025 --province "Hà Nội" --limit-universities 2

# Crawl đầy đủ (chạy sau khi pilot OK)
admission-crawler crawl --years 2016:2025 --province "Hà Nội"

# Resume sau crash
admission-crawler resume --run-id <RUN_ID>

# Chuẩn hóa và validate
admission-crawler normalize
admission-crawler validate

# Export
admission-crawler export --format parquet --output data/exports/
```

## Cấu hình rate limit (default)

- Concurrency: 1 (sequential)
- Delay: 5–9 giây random giữa mỗi request
- Tối đa 300 request/giờ, 1000 request/ngày
- 403 → dừng run ngay
- 429 → nghỉ ≥30 phút, giảm tốc 50%

## Lưu ý pháp lý

Dữ liệu thuộc VietNamNet. Raw HTML và dataset đầy đủ **không được** commit lên
repository hoặc phát hành công khai nếu chưa có sự đồng ý bằng văn bản.
Xem: https://vietnamnet.vn/thong-tin-toa-soan

## Cấu trúc output

```
data/
├── crawler.db          ← SQLite — nguồn sự thật (gitignored)
├── raw_html/           ← HTML cache cục bộ (gitignored)
├── exports/            ← Parquet/CSV output (gitignored)
└── reports/            ← JSON reports
```
