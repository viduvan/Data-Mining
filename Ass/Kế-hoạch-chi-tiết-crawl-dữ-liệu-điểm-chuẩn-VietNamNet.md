# Kế hoạch chi tiết crawl dữ liệu điểm chuẩn VietNamNet

## 1. Scope chính thức

### 1.1. Phạm vi địa lý

Chỉ thu thập các trường mà VietNamNet gắn giá trị:

```text
Tỉnh thành = Hà Nội
```

Không xác định trường Hà Nội bằng tên trường hoặc tự suy luận từ địa chỉ. Trang danh sách của VietNamNet đã có riêng các cột **Trường – Mã trường – Tỉnh thành**, vì vậy nên dùng chính cột `Tỉnh thành` làm điều kiện lọc. ([VietNamNet News][1])

Quy tắc:

```text
province_raw sau chuẩn hóa Unicode và khoảng trắng == "Hà Nội"
```

Điều này có nghĩa:

* Trường có tên chứa “Hà Nội” nhưng VietNamNet ghi tỉnh khác → loại.
* Phân hiệu của trường đặt tại Hà Nội và VietNamNet ghi “Hà Nội” → lấy.
* Trường có cơ sở ở nhiều tỉnh → xử lý theo từng bản ghi trường/phân hiệu trên VietNamNet.
* Không dùng địa chỉ chi tiết để sửa tỉnh thành tự động.

### 1.2. Phạm vi thời gian

```text
2016–2025
```

VietNamNet hiện cung cấp bộ chọn liên tục từ năm 2016 đến 2025 trên hệ thống tra cứu. ([VietNamNet News][2])

### 1.3. Loại hình đào tạo

Giai đoạn đầu chỉ lấy:

```text
Hệ đại học
```

Loại khỏi dataset phân tích chính:

* Hệ cao đẳng.
* Điểm sàn hoặc ngưỡng nhận hồ sơ.
* Bản ghi không có điểm trúng tuyển.
* Bản ghi không xác định được là kết quả tuyển sinh.
* Các phương thức không sử dụng điểm thi THPT, nếu mục tiêu mô hình chỉ phân tích điểm chuẩn THPT.

Tuy nhiên, **không xóa dữ liệu ngay khi crawl**. Tất cả bản ghi vẫn được giữ trong bảng raw, sau đó gắn nhãn phương thức để lọc ở tầng normalized.

### 1.4. Đơn vị dữ liệu

Một dòng raw tương ứng với:

```text
1 năm
+ 1 bản ghi trường trên VietNamNet
+ 1 hàng ngành/chương trình trong bảng
+ 1 mức điểm
+ thông tin hệ/khối/ghi chú của chính hàng đó
```

Không được gộp các hàng chỉ vì chúng có cùng tên ngành. Một ngành có thể có:

* Nhiều chương trình.
* Nhiều phương thức.
* Nhiều tổ hợp.
* Nhiều cơ sở.
* Nhiều thang điểm.
* Nhiều điều kiện phụ.

---

# 2. Các đặc điểm của VietNamNet cần dựa vào

## 2.1. URL danh sách theo năm

Mẫu URL:

```text
https://vietnamnet.vn/giao-duc/diem-thi/
tra-cuu-diem-chuan-cd-dh-{year}
```

Ví dụ:

```text
.../tra-cuu-diem-chuan-cd-dh-2025
.../tra-cuu-diem-chuan-cd-dh-2024
.../tra-cuu-diem-chuan-cd-dh-2016
```

Trang danh sách hiện hiển thị 20 trường mỗi trang. Trang đầu 2025 có STT 1–20 và trang tiếp theo có STT 21–40. ([VietNamNet News][1])

## 2.2. Pagination của danh sách trường

URL phân trang có dạng:

```text
Trang giao diện 1:
.../tra-cuu-diem-chuan-cd-dh-2025

Trang giao diện 2:
.../tra-cuu-diem-chuan-cd-dh-2025-page1

Trang giao diện 3:
.../tra-cuu-diem-chuan-cd-dh-2025-page2
```

Như vậy số trong URL là **zero-based**, lệch một đơn vị so với số trang người dùng nhìn thấy.

Không nên tự sinh số trang vô hạn. Hãy parse các liên kết pagination có trong HTML. Ví dụ trang danh sách 2025 hiện có bốn trang, trong khi trang 2016 hiện có sáu trang. ([VietNamNet News][1])

## 2.3. URL chi tiết trường

Mẫu thực tế:

```text
https://vietnamnet.vn/giao-duc/diem-thi/
tra-cuu-diem-chuan-cd-dh-2025/
truong/dai-hoc-bach-khoa-ha-noi
?keyword=BKA
```

Không tự dựng slug từ tên trường. Luôn lấy trực tiếp `href` của liên kết “Xem” trong hàng trường, vì:

* Slug có thể khác tên hiện tại.
* Trường có thể đổi tên.
* Phân hiệu có thể dùng slug đặc biệt.
* Query `keyword` chứa mã trường và có thể cần thiết.

## 2.4. Pagination của ngành trong từng trường

Một trường có nhiều ngành sẽ có nhiều trang:

```text
Trang đầu:
.../truong/dai-hoc-bach-khoa-ha-noi?keyword=BKA

Trang tiếp:
.../truong/dai-hoc-bach-khoa-ha-noi-page1?keyword=BKA

Trang tiếp nữa:
.../truong/dai-hoc-bach-khoa-ha-noi-page2?keyword=BKA
```

Ví dụ Bách khoa Hà Nội năm 2025 có các trang ngành tiếp tục theo STT 1–20, 21–40, 41–60. ([VietNamNet News][3])

## 2.5. Các cột dữ liệu hiện có

Bảng chi tiết trường hiện có các cột:

```text
STT
Ngành
Điểm chuẩn
Hệ
khối thi
Ghi chú
```

Ngoài ra phần đầu trang có thể cung cấp:

```text
Tên trường
Mã trường
Địa chỉ
Điện thoại
Website
Năm
```

([VietNamNet News][3])

Cần parse theo **tên header đã chuẩn hóa**, không chỉ theo vị trí cột, vì cấu trúc có thể thay đổi giữa các năm.

---

# 3. Kiến trúc tổng thể

```text
VietNamNet
    │
    ▼
Robots/Policy Precheck
    │
    ▼
Year Index Discovery
    │
    ▼
University Discovery
    │
    ├── Lọc province = Hà Nội
    │
    ▼
University Detail Discovery
    │
    ▼
Major Table Parser
    │
    ▼
Raw Storage
    │
    ▼
Normalization & Classification
    │
    ▼
Validation & Review Queue
    │
    ▼
Normalized Database / CSV / Parquet
```

Tách crawler thành hai tầng độc lập:

### Tầng A — Discovery

Chỉ tìm:

* Năm.
* Trang danh sách.
* Trường Hà Nội.
* Mã trường.
* URL chi tiết trường.
* Pagination.

### Tầng B — Extraction

Đi vào từng trường để lấy:

* Thông tin trường.
* Các hàng ngành.
* Điểm chuẩn.
* Hệ.
* Khối.
* Ghi chú.

Cách chia này cho phép kiểm tra danh sách trường trước khi tạo nhiều request chi tiết.

---

# 4. Chiến lược crawl được đề xuất

## Bước 0 — Preflight trước mỗi lần chạy

Mỗi run phải thực hiện:

1. Tải `robots.txt`.
2. Kiểm tra đường dẫn mục tiêu có được phép hay không.
3. Kiểm tra domain chính xác là `vietnamnet.vn`.
4. Kiểm tra cấu hình năm.
5. Kiểm tra database và checkpoint.
6. Tạo `crawl_run_id`.
7. Ghi lại cấu hình rate limit.
8. Chạy một request thử.
9. Kiểm tra response có đúng tiêu đề và bảng dữ liệu.
10. Chỉ sau đó mới chạy toàn bộ.

`robots.txt` hiện cho phép phần lớn website và chặn một số đường dẫn tìm kiếm cùng `/sportapi`; đường dẫn tra cứu điểm chuẩn không nằm trong nhóm bị chặn. Tuy nhiên, đây chỉ là tín hiệu kỹ thuật, không phải quyền được phát hành lại dữ liệu. ([VietNamNet News][4])

## Bước 1 — Discovery danh sách trường

Với mỗi năm:

```python
for year in range(2016, 2026):
    fetch(base_index_url(year))
    discover_all_index_pages()
    parse_all_university_rows()
    retain_rows_where(province == "Hà Nội")
```

Mỗi hàng lưu:

```text
year
source_stt
university_name_raw
university_code_raw
province_raw
detail_url
index_page_url
discovered_at
```

### Không sử dụng nút lọc Hà Nội trên giao diện làm nguồn chính

Phương án ổn định hơn là:

* Crawl vài trang danh sách toàn quốc.
* Parse từng hàng.
* Lọc `province == "Hà Nội"` trong code.

Lý do:

* Không phụ thuộc JavaScript của nút lọc.
* Không phụ thuộc endpoint tìm kiếm ẩn.
* Dễ kiểm soát completeness.
* Số trang danh sách mỗi năm tương đối nhỏ.
* Không cần gọi đường dẫn tìm kiếm vốn đang bị `robots.txt` chặn.

## Bước 2 — Chuẩn hóa và khóa danh sách Hà Nội

Sau discovery, tạo file hoặc bảng kiểm tra:

```text
year | university_code | university_name | province | detail_url
```

Chạy các kiểm tra:

* `province_normalized == "Hà Nội"`.
* Có mã trường.
* Có URL chi tiết.
* Không trùng URL trong cùng năm.
* Không trùng mã trường bất thường trong cùng năm.
* URL vẫn thuộc `vietnamnet.vn`.
* URL có năm đúng với năm đang crawl.

Không crawl detail ngay trong cùng một vòng nếu chưa kiểm tra discovery. Tốt nhất tách thành hai lệnh:

```bash
python -m crawler discover --years 2016:2025 --province "Hà Nội"
python -m crawler crawl-details --status discovered
```

## Bước 3 — Crawl trang chi tiết từng trường

Với mỗi trường Hà Nội:

1. Request URL chi tiết đầu tiên.
2. Parse metadata trường.
3. Parse bảng ngành trang đầu.
4. Tìm các link pagination của chính bảng ngành.
5. Request từng trang chưa crawl.
6. Parse các hàng.
7. Lưu raw ngay sau từng trang.
8. Đánh dấu page hoàn thành.
9. Chạy validation.
10. Chuyển sang trường tiếp theo.

Không giữ toàn bộ dữ liệu trong RAM đến cuối run.

## Bước 4 — Không click “Xem” của từng ngành trong MVP

Mỗi hàng ngành có thể có liên kết “Xem”, nhưng việc mở từng ngành sẽ làm số request tăng rất mạnh.

### MVP nên lấy từ bảng trường

```text
major_name_raw
cutoff_score_raw
education_level_raw
subject_combination_raw
note_raw
```

### Chỉ mở trang từng ngành khi thực sự cần

Ví dụ để bổ sung:

* Mã ngành.
* Danh sách tổ hợp đầy đủ.
* Điều kiện phụ chi tiết.
* Phương thức tuyển sinh.
* Thông tin chuyên sâu khác.

Nên coi đây là **Phase 2 enrichment**, không phải crawler ban đầu.

---

# 5. Cơ chế chống gửi quá nhiều request

VietNamNet không công bố trên trang tra cứu một quota request cụ thể. Vì vậy cần đặt một quota nội bộ bảo thủ.

## 5.1. Cấu hình mặc định

```yaml
http:
  concurrency: 1
  connect_timeout_seconds: 10
  read_timeout_seconds: 30
  total_timeout_seconds: 45

rate_limit:
  min_delay_seconds: 5
  max_delay_seconds: 9
  requests_per_hour_cap: 300
  requests_per_day_cap: 1000

retry:
  max_attempts: 3
  retry_statuses: [408, 425, 500, 502, 503, 504]
  backoff_seconds: [30, 90, 300]

circuit_breaker:
  consecutive_failures: 5
  cooldown_minutes: 30
```

Các ngưỡng trên là **ngưỡng tự bảo vệ của dự án**, không phải quota do VietNamNet công bố.

## 5.2. Jitter

Không dùng delay cố định chính xác 5 giây. Dùng:

```python
sleep(random.uniform(5, 9))
```

Jitter giúp tránh tạo pattern request cứng và giảm khả năng đồng thời với các tác vụ khác.

Jitter không được dùng để “né” chống bot; mục tiêu chỉ là phân tán tải.

## 5.3. Không dùng concurrency lớn

Chốt:

```text
Concurrency = 1
```

Không cần async đa luồng cho dataset này. Tổng số trang không quá lớn, và ưu tiên chính là an toàn, khả năng resume và chất lượng dữ liệu.

## 5.4. Xử lý theo mã HTTP

|            Status | Xử lý                                                      |
| ----------------: | ---------------------------------------------------------- |
|             `200` | Parse và lưu                                               |
|         `301/302` | Theo redirect nếu vẫn trong domain/path được phép          |
|             `304` | Dùng dữ liệu cache                                         |
|             `400` | Ghi lỗi, không retry liên tục                              |
|             `403` | Dừng toàn bộ run, yêu cầu kiểm tra thủ công                |
|             `404` | Ghi URL missing; không retry nhiều lần                     |
|             `408` | Retry với backoff                                          |
|             `429` | Tôn trọng `Retry-After`; không có thì nghỉ ít nhất 30 phút |
| `500/502/503/504` | Retry tối đa 3 lần với backoff                             |
|              Khác | Ghi lỗi và đưa vào review                                  |

### Chính sách đặc biệt cho 429

```text
Lần đầu:
- đọc Retry-After
- nếu không có: nghỉ 30 phút
- giảm tốc độ còn một nửa

Lần thứ hai trong cùng run:
- dừng run
- không tự động tiếp tục

Lần thứ ba trong 24 giờ:
- khóa crawler trong 24 giờ
```

### Chính sách đặc biệt cho 403

Không:

* Đổi IP.
* Đổi proxy.
* Random User-Agent để vượt chặn.
* Dùng browser automation để né.
* Vượt CAPTCHA.
* Giả lập nhiều người dùng.

Phải dừng và kiểm tra.

## 5.5. User-Agent minh bạch

Dùng User-Agent riêng:

```text
UniversityCutoffResearchBot/1.0
(+contact: contact@example.com; educational research)
```

Không giả mạo Chrome nếu không cần thiết.

Có thể thêm:

```http
Accept: text/html,application/xhtml+xml
Accept-Language: vi-VN,vi;q=0.9
```

Không gửi cookies hoặc token nếu trang không yêu cầu.

---

# 6. Cơ chế không crawl lại dữ liệu đã có

## 6.1. URL canonicalization

Trước khi lưu URL:

* Chuyển sang HTTPS.
* Lowercase hostname.
* Loại fragment `#...`.
* Sắp xếp query parameters.
* Giữ `keyword`.
* Loại tracking parameters như `utm_*`.
* Chuẩn hóa `-page0` về URL base.

Ví dụ hai URL sau phải được coi là một:

```text
.../tra-cuu-diem-chuan-cd-dh-2025
.../tra-cuu-diem-chuan-cd-dh-2025-page0
```

## 6.2. Khóa URL

```python
url_hash = sha256(canonical_url.encode()).hexdigest()
```

Đặt unique constraint:

```text
UNIQUE(crawl_run_id, url_hash)
```

Hoặc với cache dùng:

```text
UNIQUE(url_hash, content_version)
```

## 6.3. TTL

Dữ liệu lịch sử gần như không thay đổi thường xuyên.

Đề xuất:

```yaml
cache_ttl:
  2016_2023_days: 365
  2024_days: 180
  2025_days: 30
```

Nếu chạy lại trước TTL:

* Không request lại.
* Dùng dữ liệu cache/database.
* Chỉ request lại khi có `--force-refresh`.

## 6.4. Conditional GET

Nếu response có:

```http
ETag
Last-Modified
```

thì lưu lại và gửi:

```http
If-None-Match
If-Modified-Since
```

Nếu trả `304 Not Modified`, không parse lại nội dung.

## 6.5. Content hash

Mỗi response thành công:

```python
content_sha256 = sha256(response_body).hexdigest()
```

Nếu cùng URL nhưng hash thay đổi:

* Tạo version mới.
* Không ghi đè bản cũ.
* Chạy parser lại.
* So sánh dữ liệu trước và sau.
* Gắn cờ `source_changed = true`.

---

# 7. Cơ chế checkpoint và resume

Crawler phải có khả năng dừng bất kỳ lúc nào mà không mất tiến trình.

## 7.1. Trạng thái URL

```text
DISCOVERED
QUEUED
FETCHING
FETCHED
PARSED
VALIDATED
COMPLETED
RETRY_PENDING
FAILED
BLOCKED
SKIPPED
```

## 7.2. Quy trình transaction

Với mỗi trang:

```text
1. Đánh dấu FETCHING
2. Request
3. Lưu response metadata
4. Đánh dấu FETCHED
5. Parse
6. Lưu records raw trong transaction
7. Đánh dấu PARSED
8. Validate
9. Đánh dấu COMPLETED hoặc FAILED
```

Nếu chương trình crash sau bước 4, lần chạy sau tiếp tục từ bước parse mà không cần request lại nếu response đã được cache.

## 7.3. Không ghi đè dữ liệu cũ

Mỗi lần chạy có:

```text
crawl_run_id
```

Dữ liệu raw nên append-only:

```text
record_id
crawl_run_id
source_page_id
...
```

Bảng normalized có thể dùng upsert, nhưng raw không được xóa tự động.

## 7.4. Lệnh resume

```bash
python -m crawler resume --run-id RUN_2025_001
```

Resume chỉ lấy các trạng thái:

```text
DISCOVERED
QUEUED
RETRY_PENDING
FETCHED nhưng chưa PARSED
PARSED nhưng chưa VALIDATED
```

---

# 8. Thiết kế database

## 8.1. Bảng `crawl_runs`

```sql
crawl_run_id
started_at
finished_at
status
years
province_filter
config_json
code_version
host
total_requested
total_success
total_failed
total_records
stop_reason
```

## 8.2. Bảng `source_pages`

```sql
source_page_id
crawl_run_id
canonical_url
url_hash
page_type
year
university_code
page_index
status
http_status
requested_at
response_time_ms
etag
last_modified
content_sha256
parser_version
error_type
error_message
retry_count
```

`page_type`:

```text
ROBOTS
YEAR_INDEX
UNIVERSITY_DETAIL
MAJOR_DETAIL
```

## 8.3. Bảng `universities_raw`

```sql
university_raw_id
crawl_run_id
year
source_stt
university_name_raw
university_code_raw
province_raw
detail_url
source_page_id
discovered_at
```

Unique tương đối:

```sql
UNIQUE(year, university_code_raw, detail_url)
```

Không dùng duy nhất `university_code_raw`, vì một số tình huống lịch sử có thể phức tạp.

## 8.4. Bảng `cutoffs_raw`

```sql
cutoff_raw_id
crawl_run_id
source_page_id

year
university_name_raw
university_code_raw
province_raw

source_row_stt
major_name_raw
cutoff_score_raw
education_level_raw
subject_combination_raw
note_raw

major_detail_url
row_html_hash
record_fingerprint
crawled_at
```

## 8.5. Bảng `cutoffs_normalized`

```sql
cutoff_id
cutoff_raw_id

year
university_id
university_code
university_name
province

major_name
major_name_normalized
major_code

cutoff_score
score_scale
score_unit

education_level
admission_method
admission_round
subject_combinations
program_type
campus

tie_break_condition
normalization_status
normalization_confidence
review_required

source_url
crawled_at
```

## 8.6. Bảng `universities`

```sql
university_id
canonical_name
current_code
province
active_from
active_to
```

## 8.7. Bảng `university_aliases`

```sql
alias_id
university_id
year_from
year_to
code_alias
name_alias
source
confidence
```

Không tự động kết luận hai trường là một chỉ vì tên gần giống.

---

# 9. Cơ chế deduplication

## 9.1. Exact fingerprint

```python
fingerprint_input = "|".join([
    str(year),
    normalize(university_code_raw),
    normalize(major_name_raw),
    normalize(cutoff_score_raw),
    normalize(education_level_raw),
    normalize(subject_combination_raw),
    normalize(note_raw),
])

record_fingerprint = sha256(fingerprint_input.encode()).hexdigest()
```

Unique:

```text
UNIQUE(year, university_code_raw, record_fingerprint)
```

## 9.2. Không deduplicate quá mạnh

Hai hàng cùng tên ngành nhưng khác:

* Điểm.
* Khối.
* Ghi chú.
* Chương trình.
* Phương thức.

phải được giữ riêng.

## 9.3. Trùng do pagination

Dùng kết hợp:

```text
source_page_id
source_row_stt
record_fingerprint
```

Nếu một hàng xuất hiện ở cuối trang trước và đầu trang sau:

* Ghi nhận duplicate.
* Chỉ giữ một bản normalized.
* Vẫn lưu dấu vết trong log.

---

# 10. Parsing dữ liệu

## 10.1. Không phụ thuộc tuyệt đối vào CSS selector

Parser nên có ba tầng:

### Tầng 1 — Selector cụ thể

Dùng selector từ DOM thực tế sau khi Gemini kiểm tra bằng DevTools.

### Tầng 2 — Table header matching

Tìm bảng có các header gần với:

```text
STT
Trường
Mã trường
Tỉnh thành
```

hoặc:

```text
STT
Ngành
Điểm chuẩn
Hệ
Khối thi
Ghi chú
```

### Tầng 3 — Semantic fallback

Nếu class CSS thay đổi nhưng bảng vẫn còn:

* Tìm tất cả `<table>`.
* Chuẩn hóa text header.
* Chấm điểm bảng.
* Chọn bảng có nhiều header khớp nhất.

Nếu không tìm thấy bảng đủ confidence:

```text
Không parse bằng regex toàn trang.
Đánh dấu PARSER_SCHEMA_CHANGED.
Dừng run sau ngưỡng lỗi.
```

## 10.2. Chuẩn hóa header

```python
HEADER_ALIASES = {
    "stt": {"stt", "số thứ tự"},
    "university": {"trường", "tên trường"},
    "university_code": {"mã trường"},
    "province": {"tỉnh thành", "tỉnh/thành"},
    "major": {"ngành", "tên ngành"},
    "score": {"điểm chuẩn", "điểm"},
    "level": {"hệ"},
    "subject_group": {"khối thi", "tổ hợp"},
    "note": {"ghi chú"},
}
```

## 10.3. Làm sạch text

```python
def clean_text(value):
    value = html.unescape(value)
    value = unicodedata.normalize("NFC", value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()
```

Không bỏ dấu tiếng Việt.

## 10.4. Loại chữ “Xem”

Tên ngành trên giao diện có thể hiển thị:

```text
Khoa học dữ liệu và Trí tuệ nhân tạo (CT tiên tiến) (Xem)
```

Nhưng “Xem” thường nằm trong anchor riêng. Parser cần lấy text của tên ngành mà không đưa từ “Xem” vào `major_name_raw`.

Không dùng `.get_text()` toàn cell rồi xóa mọi chuỗi `"Xem"` một cách mù quáng. Nên:

* Lấy anchor URL riêng.
* Xóa node link “Xem” khỏi bản sao DOM.
* Sau đó lấy tên ngành.

---

# 11. Xử lý điểm chuẩn

## 11.1. Luôn giữ raw

```text
cutoff_score_raw = chuỗi đúng như website
```

Thêm:

```text
cutoff_score = số Decimal nếu parse được
```

Không dùng `float` nếu cần bảo toàn giá trị. Dùng:

```python
Decimal("28.53")
```

## 11.2. Các dạng cần hỗ trợ

```text
28.53
28,53
34.85
500.00
-
Không tuyển
Đang cập nhật
```

Có thể xuất hiện thang điểm lớn hơn 30 trên hệ thống. Ví dụ Đại học Hà Nội năm 2025 có các điểm 34.85 và 33.89; trang xem theo ngành cũng có trường hợp điểm 500.00. Vì vậy không được áp dụng validation cứng `0 <= score <= 30`. ([VietNamNet News][5])

## 11.3. Score scale

```text
30
40
100
150
1200
1500
unknown
```

Quy tắc:

* Không suy ra thang điểm chỉ dựa vào `score > 30`.
* Có thể dùng rule để tạo `score_scale_candidate`.
* Nếu không có thông tin rõ ràng, để `unknown`.
* Không tự động quy đổi về thang 30 trong bảng raw.
* Nếu cần quy đổi, tạo cột riêng:

```text
normalized_score_30
normalization_method
normalization_assumption
```

## 11.4. Validation điểm

Chỉ kiểm tra cơ bản:

```text
score > 0
score <= 2000
```

Các ngưỡng chuyên biệt phụ thuộc `score_scale`.

---

# 12. Xác định phương thức tuyển sinh

Không mặc định mọi hàng đều là điểm thi THPT.

Ví dụ trang Bách khoa Hà Nội năm 2024 có ghi chú “Xét duyệt điểm thi THPT”, trong khi nhiều hàng năm 2025 có cột ghi chú trống. ([VietNamNet News][6])

## 12.1. Rule-based classifier

```python
METHOD_RULES = {
    "thpt_exam": [
        "điểm thi thpt",
        "thi tốt nghiệp thpt",
        "kết quả thi thpt",
        "xét duyệt điểm thi thpt",
    ],
    "transcript": [
        "học bạ",
        "kết quả học tập",
    ],
    "competency_test": [
        "đánh giá năng lực",
        "đgnl",
        "hsa",
    ],
    "thinking_assessment": [
        "đánh giá tư duy",
        "đgtd",
        "tsa",
    ],
    "direct_admission": [
        "tuyển thẳng",
        "xét tuyển thẳng",
    ],
}
```

Đầu vào classifier:

```text
major_name_raw + subject_combination_raw + note_raw
```

Đầu ra:

```text
admission_method
method_confidence
method_rule_matched
```

## 12.2. Nhãn cần có

```text
thpt_exam
transcript
competency_test
thinking_assessment
direct_admission
combined
other
unknown
```

`unknown` không được tự động loại khỏi raw.

Dataset phân tích MVP có thể lọc:

```sql
WHERE admission_method = 'thpt_exam'
   OR admission_method = 'unknown'
```

Nhóm `unknown` cần review trước khi dùng huấn luyện mô hình.

---

# 13. Chuẩn hóa ngành

## 13.1. Bảo toàn tên gốc

```text
major_name_raw
```

## 13.2. Tên làm sạch

```text
major_name_clean
```

Chỉ:

* Chuẩn hóa Unicode.
* Loại khoảng trắng thừa.
* Chuẩn hóa dấu gạch.
* Chuẩn hóa viết hoa/thường cho so sánh.

Không xóa các cụm:

```text
CT tiên tiến
Chất lượng cao
Dạy bằng tiếng Anh
Việt - Nhật
Việt - Pháp
```

Đây là thông tin phân biệt chương trình.

## 13.3. Tách chương trình

Ví dụ:

```text
Công nghệ thông tin (Việt - Nhật)
```

Tách thành:

```text
major_base_name = Công nghệ thông tin
program_type = international_cooperation
program_variant = Việt - Nhật
```

Nhưng vẫn giữ nguyên:

```text
major_name_raw = Công nghệ thông tin (Việt - Nhật)
```

## 13.4. Mapping ngành qua năm

Không tự động merge bằng fuzzy matching.

Pipeline:

```text
Exact normalized match
    ↓
Alias dictionary
    ↓
Fuzzy candidate generation
    ↓
Manual confirmation
```

Fuzzy matching chỉ tạo đề xuất:

```text
candidate_major_id
similarity_score
```

Không tự quyết định.

---

# 14. Tổ hợp xét tuyển

Dùng regex:

```python
r"\b[A-Z]\d{2}\b"
```

Ví dụ:

```text
A00
A01
D01
D07
C00
```

Lưu:

```text
subject_combination_raw
subject_combinations_json
```

Ví dụ:

```json
["A00", "A01", "D01"]
```

Nếu cột trống:

```text
[]
```

Không suy luận tổ hợp từ tên ngành.

---

# 15. Data quality và validation

## 15.1. Validation cấp trang danh sách

Mỗi trang index phải có:

* Tiêu đề chứa đúng năm.
* Bảng có header trường.
* Ít nhất một hàng trường, trừ trang cuối không hợp lệ.
* STT là số.
* Mỗi hàng có tên trường.
* URL detail thuộc VietNamNet.

## 15.2. Validation cấp trang trường

Phải có:

* Tên trường.
* Mã trường hoặc mã lấy từ discovery.
* Năm đúng.
* Bảng ngành.
* Header điểm chuẩn.
* Ít nhất một row hoặc trạng thái “không có dữ liệu”.

## 15.3. Validation cấp row

```text
year: 2016–2025
university_name_raw: không rỗng
major_name_raw: không rỗng
education_level_raw: có thể rỗng nhưng phải cảnh báo
cutoff_score_raw: có thể rỗng nhưng phải phân loại
```

## 15.4. Kiểm tra STT liên trang

Với một trường:

```text
Trang đầu: 1–20
Trang sau: 21–40
...
```

Nếu:

* STT bị lặp.
* Khoảng trống lớn.
* Trang giữa không đủ 20 hàng nhưng vẫn có trang sau.

thì đưa vào review.

Không bắt buộc STT luôn liên tục vì dữ liệu nguồn có thể có ngoại lệ, nhưng phải cảnh báo.

## 15.5. Kiểm tra completeness

Tạo báo cáo:

```text
year
index_pages_found
universities_total
hanoi_universities
hanoi_detail_pages
raw_cutoff_rows
parsed_rows
failed_pages
unknown_methods
missing_scores
duplicate_rows
```

## 15.6. Ngưỡng dừng tự động

```yaml
quality_gate:
  max_http_failure_rate: 0.02
  max_parse_failure_rate: 0.02
  max_empty_detail_rate: 0.05
  max_consecutive_schema_failures: 3
```

Nếu vượt:

* Dừng run.
* Không cố chạy tiếp.
* Xuất báo cáo lỗi.
* Giữ checkpoint.

---

# 16. Lưu raw HTML như thế nào

Do cần reproducibility và tránh request lại, có thể lưu response HTML **cục bộ**, nhưng:

* Không commit lên GitHub.
* Không phát hành công khai.
* Có retention.
* Nén gzip.
* Chỉ dùng nội bộ.

Cấu trúc:

```text
data/raw_html/
  2025/
    index/
    universities/
```

Tên file:

```text
{url_hash}.html.gz
```

Metadata ở database.

Đề xuất retention:

```text
HTML cache: 30–90 ngày
Structured raw records: giữ lâu dài
Hashes + metadata: giữ lâu dài
```

VietNamNet ghi rõ thông tin trên website chỉ được phát hành lại khi có sự đồng ý bằng văn bản. Vì vậy không nên đưa HTML hoặc toàn bộ dataset crawl lên repository công khai nếu chưa có phép. ([VietNamNet News][7])

---

# 17. Logging và monitoring

## 17.1. Structured logging JSON

Mỗi log:

```json
{
  "timestamp": "...",
  "run_id": "...",
  "event": "page_fetched",
  "url": "...",
  "page_type": "UNIVERSITY_DETAIL",
  "year": 2025,
  "university_code": "BKA",
  "status_code": 200,
  "elapsed_ms": 842,
  "retry": 0
}
```

## 17.2. Các event chính

```text
run_started
robots_checked
page_discovered
request_started
page_fetched
page_cached
page_not_modified
page_parsed
page_validated
record_inserted
duplicate_detected
retry_scheduled
rate_limit_hit
circuit_breaker_opened
schema_change_detected
run_completed
run_stopped
```

## 17.3. Không log toàn bộ HTML

Không đưa body HTML vào log.

Không log dữ liệu nhạy cảm hoặc cookies.

## 17.4. Báo cáo cuối run

```text
Run ID:
Thời gian:
Số request:
Cache hit:
HTTP 200:
HTTP 304:
HTTP 404:
HTTP 429:
Lỗi:
Trường Hà Nội:
Số hàng raw:
Số hàng normalized:
Số hàng cần review:
```

---

# 18. Stack Python đề xuất

```text
Python
httpx hoặc requests
BeautifulSoup4 + lxml hoặc selectolax
SQLAlchemy
Pydantic
Typer
Tenacity
PyYAML
pytest
```

Khuyến nghị:

* Dùng HTTP client thông thường trước.
* Không dùng Selenium/Playwright nếu HTML response đã chứa bảng.
* Chỉ thêm browser automation nếu kiểm chứng thực tế cho thấy một phần dữ liệu bắt buộc render bằng JavaScript.
* Browser automation không được dùng để vượt cơ chế chặn.

---

# 19. Cấu trúc source code

```text
src/
└── admission_crawler/
    ├── __init__.py
    ├── cli.py
    ├── config.py
    ├── constants.py
    │
    ├── http/
    │   ├── client.py
    │   ├── rate_limiter.py
    │   ├── retry_policy.py
    │   ├── cache.py
    │   ├── robots.py
    │   └── circuit_breaker.py
    │
    ├── discovery/
    │   ├── year_index.py
    │   ├── pagination.py
    │   └── university_discovery.py
    │
    ├── parsers/
    │   ├── common.py
    │   ├── index_parser.py
    │   ├── university_parser.py
    │   └── table_detector.py
    │
    ├── normalization/
    │   ├── text.py
    │   ├── score.py
    │   ├── university.py
    │   ├── major.py
    │   ├── admission_method.py
    │   └── subject_combination.py
    │
    ├── validation/
    │   ├── page_validator.py
    │   ├── record_validator.py
    │   ├── completeness.py
    │   └── anomaly_detector.py
    │
    ├── storage/
    │   ├── database.py
    │   ├── models.py
    │   ├── repositories.py
    │   ├── raw_html_store.py
    │   └── migrations/
    │
    ├── pipeline/
    │   ├── discover_pipeline.py
    │   ├── crawl_pipeline.py
    │   ├── normalize_pipeline.py
    │   └── export_pipeline.py
    │
    └── reporting/
        ├── run_report.py
        └── quality_report.py

configs/
├── default.yaml
├── development.yaml
└── production.yaml

tests/
├── fixtures/
│   ├── index_2016_page0.html
│   ├── index_2025_page0.html
│   ├── university_bka_2024_page0.html
│   └── university_bka_2025_page1.html
├── test_index_parser.py
├── test_university_parser.py
├── test_pagination.py
├── test_score_parser.py
├── test_method_classifier.py
└── test_deduplication.py

data/
├── raw_html/          # gitignored
├── exports/
├── reports/
└── sample/

scripts/
├── crawl_pilot.sh
├── crawl_full.sh
└── validate.sh
```

---

# 20. CLI đề xuất

```bash
# Kiểm tra robots và cấu trúc
admission-crawler preflight --year 2025

# Tìm danh sách trường Hà Nội
admission-crawler discover \
  --years 2016:2025 \
  --province "Hà Nội"

# Xem danh sách trước khi crawl detail
admission-crawler report universities \
  --province "Hà Nội"

# Pilot 2 năm và giới hạn 10 trường
admission-crawler crawl \
  --years 2024:2025 \
  --province "Hà Nội" \
  --limit-universities 10

# Crawl đầy đủ
admission-crawler crawl \
  --years 2016:2025 \
  --province "Hà Nội" \
  --resume

# Chuẩn hóa
admission-crawler normalize \
  --years 2016:2025

# Validate
admission-crawler validate \
  --years 2016:2025

# Xuất dữ liệu
admission-crawler export \
  --format parquet \
  --output data/exports/hanoi_cutoffs_2016_2025.parquet
```

---

# 21. Kế hoạch triển khai theo phase

## Phase 0 — Kiểm tra pháp lý và kỹ thuật

Đầu ra:

* Snapshot `robots.txt`.
* Ghi rõ chính sách sử dụng.
* Không public raw dataset.
* User-Agent có thông tin liên hệ.
* Xác nhận HTML chứa bảng.
* Xác nhận pagination.
* Xác nhận selector.

VietNamNet cung cấp email liên hệ tòa soạn `vietnamnet@vietnamnet.vn`; nếu dự án muốn công bố toàn bộ dataset, nên xin xác nhận bằng văn bản trước. ([VietNamNet News][7])

## Phase 1 — Parser pilot một trường

Dùng:

```text
Đại học Bách khoa Hà Nội
Năm 2024 và 2025
```

Lý do:

* Có nhiều trang.
* Có nhiều ngành.
* Có ghi chú phương thức ở 2024.
* Kiểm tra được pagination.

Acceptance:

* Parse đúng tất cả trang.
* STT liên tục.
* Không duplicate.
* Điểm parse đúng.
* Resume hoạt động.

## Phase 2 — Pilot 10 trường, hai năm

```text
2024–2025
10 trường Hà Nội
```

Ưu tiên gồm:

* Trường nhiều ngành.
* Trường ít ngành.
* Trường điểm thang 30.
* Trường có điểm trên 30.
* Học viện.
* Phân hiệu.
* Trường có nhiều chương trình đặc biệt.

Acceptance:

```text
HTTP success >= 98%
Parse success >= 98%
Không request trùng
Resume không mất dữ liệu
Không có 429/403
```

## Phase 3 — Discovery toàn bộ 2016–2025

Chỉ crawl index.

Đầu ra:

* Danh sách trường Hà Nội từng năm.
* Ma trận trường × năm.
* Các trường đổi mã/tên.
* Danh sách URL detail.
* Ước lượng chính xác số trang cần crawl.

## Phase 4 — Crawl detail toàn bộ

Chạy theo batch:

```text
Batch 1: 2024–2025
Batch 2: 2021–2023
Batch 3: 2018–2020
Batch 4: 2016–2017
```

Mỗi batch có run ID riêng.

Không chạy tất cả 10 năm trong một process duy nhất.

## Phase 5 — Normalize và review

* Phương thức tuyển sinh.
* Điểm/thang điểm.
* Tên trường.
* Tên ngành.
* Tổ hợp.
* Chương trình.
* Duplicate.
* Missing.

## Phase 6 — Verification

Mỗi năm:

* Chọn ít nhất 5 trường.
* Mỗi trường chọn 5–10 bản ghi.
* Đối chiếu website chính thức của trường hoặc một nguồn thứ hai.
* Lưu kết quả verification.

Schema:

```text
cutoff_id
verification_source_url
verification_status
verified_value
verified_at
difference
reviewer_note
```

## Phase 7 — Export

Tạo ba tập:

```text
raw_structured.parquet
normalized_all_methods.parquet
normalized_thpt_only.parquet
```

Không chỉ xuất CSV, vì CSV khó lưu list tổ hợp và schema.

---

# 22. Ước lượng request

Không nên hardcode một con số trước discovery.

Công thức:

```text
Total requests MVP
=
số trang index của 10 năm
+
tổng số trang ngành của tất cả trường Hà Nội
+
robots/preflight
+
một lượng nhỏ retry
```

Vì trang index và trang trường hiện hiển thị khoảng 20 hàng mỗi trang, có thể tính sau discovery:

```python
estimated_detail_pages = sum(
    max(1, ceil(university.expected_major_count / 20))
)
```

Nhưng tốt nhất là lấy pagination thật từ HTML.

Nếu click thêm trang chi tiết của từng ngành:

```text
Total enrichment requests
≈ Total MVP requests + tổng số ngành
```

Do đó Phase 1 không nên crawl từng ngành.

---

# 23. Những điều Gemini tuyệt đối không được làm

```text
Không dùng proxy rotation
Không đổi IP để vượt chặn
Không bypass CAPTCHA
Không random hàng trăm User-Agent
Không concurrency cao
Không gọi endpoint tìm kiếm bị robots chặn
Không đoán URL và quét vô hạn
Không retry 403 liên tục
Không retry 404 hàng chục lần
Không công khai raw HTML
Không ghi đè dữ liệu raw cũ
Không bỏ score > 30
Không mặc định mọi dòng là điểm thi THPT
Không gộp ngành chỉ dựa vào tên gần giống
Không dùng float cho điểm nếu cần bảo toàn
Không phụ thuộc duy nhất vào CSS class
```

---

# 24. Acceptance criteria cuối cùng

Crawler được coi là hoàn thành khi:

### Discovery

* Phát hiện toàn bộ pagination theo từng năm.
* Chỉ chọn trường có `province = Hà Nội`.
* Không trùng URL.
* Có report số trường theo năm.

### HTTP

* Concurrency bằng 1.
* Delay có jitter.
* Tôn trọng `Retry-After`.
* Dừng khi gặp 403.
* Circuit breaker hoạt động.
* Có cache và conditional request.

### Parsing

* Hỗ trợ index 2016 và 2025.
* Hỗ trợ detail nhiều trang.
* Parse theo header.
* Không đưa “Xem” vào tên trường/ngành.
* Giữ raw text.

### Storage

* Có checkpoint.
* Resume sau crash.
* Raw append-only.
* Có content hash.
* Không request lại URL đã cache.

### Quality

* Parse success từ 98% trở lên.
* Mọi lỗi đều có log.
* Có review queue.
* Có báo cáo completeness.
* Không lọc sai score trên 30.
* Không trộn các phương thức không tương đồng.

### Export

* Có file all methods.
* Có file THPT-only.
* Có source URL.
* Có thời gian crawl.
* Có version parser.
* Có trạng thái normalization.

---

Kế hoạch an toàn nhất là triển khai **discovery toàn bộ trước**, sau đó pilot Bách khoa Hà Nội 2024–2025, rồi mới mở rộng từng batch năm. Điều này giúp xác định chính xác khối lượng request và phát hiện thay đổi cấu trúc trước khi crawler tác động lên toàn bộ nguồn.

[1]: https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025 "Tra cứu điểm chuẩn tuyển sinh đại học 2025"
[2]: https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2016 "Tra cứu điểm chuẩn tuyển sinh đại học 2016"
[3]: https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025/truong/dai-hoc-bach-khoa-ha-noi?keyword=BKA "Tra cứu điểm chuẩn Đại học Bách khoa Hà Nội năm 2025"
[4]: https://vietnamnet.vn/robots.txt "vietnamnet.vn"
[5]: https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025/truong/dai-hoc-ha-noi?keyword=NHF "Tra cứu điểm chuẩn Đại học Hà Nội năm 2025"
[6]: https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2024/truong/dai-hoc-bach-khoa-ha-noi?keyword=BKA "Tra cứu điểm chuẩn Đại học Bách khoa Hà Nội năm 2024"
[7]: https://vietnamnet.vn/thong-tin-toa-soan "Thông tin tòa soạn"
