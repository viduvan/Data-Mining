# 01_Problem_Statement.md

# Phân tích Bài toán Nghiệp vụ — Tuyển sinh Đại học Việt Nam

---

## 1. Phát biểu Bài toán

### 1.1 Bối cảnh

Hàng năm, hàng triệu học sinh THPT tại Việt Nam tham gia kỳ thi Tốt nghiệp THPT và đăng ký xét tuyển đại học. Dữ liệu điểm chuẩn tuyển sinh được Bộ Giáo dục và Đào tạo cùng các trường đại học công bố công khai sau mỗi mùa tuyển sinh. Tuy nhiên:

- Dữ liệu **phân tán** trên nhiều nguồn: website Bộ GD&ĐT, website từng trường, báo chí giáo dục
- Dữ liệu **thiếu đồng nhất**: khác nhau về định dạng, tên gọi, mã ngành giữa các năm
- Dữ liệu **chưa được khai thác** thành các insight có giá trị cho người dùng cuối
- Học sinh và phụ huynh thiếu công cụ **phân tích xu hướng** và **gợi ý lựa chọn** dựa trên dữ liệu

### 1.2 Bài toán chính

> **Xây dựng hệ thống phân tích và khai phá dữ liệu tuyển sinh đại học Việt Nam giai đoạn 2020–2025**, cung cấp cái nhìn toàn diện về xu hướng tuyển sinh và hỗ trợ ra quyết định cho các bên liên quan.

---

## 2. Câu hỏi Nghiên cứu

### 2.1 Câu hỏi mô tả (Descriptive)

| STT | Câu hỏi | Phương pháp |
|-----|---------|------------|
| Q1 | Điểm chuẩn tuyển sinh thay đổi như thế nào qua các năm 2020–2025? | EDA, Trend Analysis |
| Q2 | Nhóm ngành nào có điểm chuẩn cao nhất / thấp nhất? | EDA, Ranking |
| Q3 | Trường nào có điểm chuẩn ổn định / biến động nhiều nhất? | EDA, Variance Analysis |
| Q4 | Phân bố điểm chuẩn theo khu vực (Bắc/Trung/Nam) có khác nhau không? | EDA, Region Analysis |
| Q5 | Tổ hợp xét tuyển nào được sử dụng phổ biến nhất? | EDA, Frequency Analysis |

### 2.2 Câu hỏi khám phá (Exploratory)

| STT | Câu hỏi | Phương pháp |
|-----|---------|------------|
| Q6 | Có thể phân nhóm các trường/ngành theo đặc điểm tuyển sinh không? | K-Means Clustering |
| Q7 | Có mối liên hệ nào giữa chỉ tiêu tuyển sinh và điểm chuẩn không? | Correlation Analysis |
| Q8 | Những kết hợp nào (ngành, trường, tổ hợp) hay xuất hiện cùng nhau? | Association Rule Mining |

### 2.3 Câu hỏi dự đoán (Predictive)

| STT | Câu hỏi | Phương pháp |
|-----|---------|------------|
| Q9 | Điểm chuẩn của các trường/ngành năm tới sẽ là bao nhiêu? | ARIMA / Linear Regression |
| Q10 | Xu hướng tuyển sinh 5 năm tới sẽ như thế nào? | Forecasting |

### 2.4 Câu hỏi hỗ trợ quyết định (Decision Support)

| STT | Câu hỏi | Phương pháp |
|-----|---------|------------|
| Q11 | Với điểm thi X và tổ hợp Y, học sinh nên đăng ký trường nào? | Recommendation System |
| Q12 | Mức độ an toàn khi đăng ký vào trường Z là bao nhiêu? | Safety Score Calculation |

---

## 3. Phạm vi & Giới hạn

### 3.1 Phạm vi bao gồm

✅ Dữ liệu điểm chuẩn tuyển sinh từ năm **2020 đến 2025**

✅ Xét tuyển theo điểm thi THPT Quốc gia (phương thức chính)

✅ Các trường đại học có công bố dữ liệu công khai

✅ Phân tích theo: năm, trường, ngành, khu vực, tổ hợp xét tuyển

✅ Dashboard trực quan bằng Power BI

✅ Hệ thống gợi ý cơ bản dựa trên dữ liệu lịch sử

### 3.2 Phạm vi không bao gồm

❌ Dữ liệu điểm thi từng thí sinh (dữ liệu cá nhân)

❌ Xét tuyển học bạ, xét tuyển riêng của từng trường

❌ Hệ thống đăng ký xét tuyển trực tuyến

❌ Machine Learning Deep Learning (đề xuất hướng tương lai)

❌ Web Application / Mobile Application

❌ Dữ liệu sau năm 2025

---

## 4. Định nghĩa & Thuật ngữ

| Thuật ngữ | Định nghĩa |
|-----------|-----------|
| **Điểm chuẩn** | Điểm tối thiểu để trúng tuyển vào một ngành của một trường trong một năm |
| **Chỉ tiêu** | Số lượng sinh viên được tuyển vào một ngành |
| **Tổ hợp xét tuyển** | Nhóm 3 môn thi được dùng để xét tuyển (VD: A00 = Toán+Lý+Hóa) |
| **Khu vực ưu tiên** | Phân loại địa lý cho điểm cộng ưu tiên (KV1, KV2, KV2-NT, KV3) |
| **Delta Score (YoY)** | Chênh lệch điểm chuẩn so với năm trước đó |
| **Competition Level** | Mức độ cạnh tranh: Rất cao (≥27), Cao (23-27), TB (18-23), Thấp (<18) |
| **Safety Score** | Biên độ an toàn = (Điểm thí sinh - Điểm chuẩn) / Điểm chuẩn × 100% |

---

## 5. Đối tượng sử dụng & Nhu cầu

### 5.1 Học sinh THPT

- **Nhu cầu:** Biết mình với điểm X có khả năng đậu trường nào
- **Kết quả mong đợi:** Danh sách trường/ngành phù hợp với mức an toàn rõ ràng

### 5.2 Giáo viên & Tư vấn hướng nghiệp

- **Nhu cầu:** Dữ liệu tổng hợp xu hướng tuyển sinh để tư vấn học sinh
- **Kết quả mong đợi:** Dashboard tổng quan, báo cáo xu hướng theo năm

### 5.3 Nhà quản lý giáo dục

- **Nhu cầu:** Phân tích biến động tuyển sinh để điều chỉnh chính sách
- **Kết quả mong đợi:** KPI tuyển sinh, phân tích khu vực, dự báo xu hướng

### 5.4 Nhà nghiên cứu

- **Nhu cầu:** Dữ liệu và phân tích để nghiên cứu giáo dục đại học
- **Kết quả mong đợi:** Bộ dữ liệu chuẩn hóa, kết quả Mining, notebooks EDA

---

## 6. Tiêu chí Đánh giá Thành công

### 6.1 Tiêu chí dữ liệu

| KPI | Mục tiêu |
|-----|---------|
| Số năm dữ liệu | 2020–2025 (6 năm) |
| Số trường bao phủ | ≥ 100 trường đại học |
| Tỷ lệ missing values sau cleaning | < 5% |
| Độ chính xác tên trường/ngành chuẩn hóa | ≥ 95% |

### 6.2 Tiêu chí mô hình

| KPI | Mục tiêu |
|-----|---------|
| Silhouette Score (Clustering) | ≥ 0.4 |
| RMSE dự báo điểm chuẩn | ≤ 1.5 điểm |
| Độ chính xác recommendation | ≥ 80% (so sánh với kết quả thực tế) |

### 6.3 Tiêu chí sản phẩm

| Sản phẩm | Tiêu chí |
|---------|---------|
| Dashboard Power BI | ≥ 4 trang, interactive drill-down |
| Notebooks EDA | ≥ 5 notebooks với visualizations đầy đủ |
| Tài liệu | Đầy đủ 12 files theo lộ trình |
| Unit tests | Coverage ≥ 70% |

---

## 7. Thách thức & Rủi ro

| Thách thức | Mô tả | Biện pháp giảm thiểu |
|-----------|-------|---------------------|
| Dữ liệu không đồng nhất | Tên trường/ngành khác nhau giữa các năm | Xây dựng mapping dictionary chuẩn hóa |
| Website thay đổi cấu trúc | HTML structure thay đổi làm hỏng crawler | Viết crawler linh hoạt, có fallback |
| Missing data nhiều | Một số năm/trường thiếu dữ liệu | Chiến lược imputation + đánh dấu rõ ràng |
| Dữ liệu lịch sử khó tìm | Năm 2020-2022 có thể không còn online | Tìm nguồn backup (Kaggle, báo chí, archive.org) |
| Rate limiting khi crawl | Website chặn nếu crawl quá nhanh | Thêm delay, proxy rotation, user-agent rotation |
