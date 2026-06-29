# 00_Project_Overview.md

# Phân tích và Khai phá dữ liệu tuyển sinh Đại học Việt Nam giai đoạn 2020–2025 bằng Data Mining và Power BI

---

# Thông tin tài liệu

| Thuộc tính      | Nội dung                                                                                                   |
| --------------- | ---------------------------------------------------------------------------------------------------------- |
| Tên dự án       | Vietnam University Admission Data Mining                                                                   |
| Tên đề tài      | Phân tích và Khai phá dữ liệu tuyển sinh Đại học Việt Nam giai đoạn 2020–2025 bằng Data Mining và Power BI |
| Công nghệ       | Python, Power BI, SQL, Excel                                                                               |

---

# 1. Giới thiệu

## 1.1 Bối cảnh

Trong những năm gần đây, dữ liệu tuyển sinh đại học tại Việt Nam được công bố công khai bởi Bộ Giáo dục và Đào tạo cũng như các trường đại học. Tuy nhiên, các dữ liệu này thường được phân tán trên nhiều nguồn khác nhau, thiếu tính đồng nhất và chưa được khai thác hiệu quả nhằm hỗ trợ học sinh, phụ huynh và các đơn vị giáo dục trong việc phân tích xu hướng tuyển sinh.

Phần lớn học sinh hiện nay lựa chọn ngành học dựa trên cảm tính hoặc thông tin rời rạc, trong khi dữ liệu lịch sử nhiều năm có thể cung cấp các xu hướng giá trị như:

* Ngành học nào đang tăng hoặc giảm điểm chuẩn.
* Trường nào có mức điểm ổn định.
* Mối quan hệ giữa chỉ tiêu tuyển sinh và điểm chuẩn.
* Xu hướng phát triển của các nhóm ngành trong tương lai.

Đề tài này hướng tới việc xây dựng một hệ thống phân tích dữ liệu tuyển sinh đại học Việt Nam trong giai đoạn 2020–2025 bằng các kỹ thuật Data Mining kết hợp với Power BI nhằm trực quan hóa dữ liệu và hỗ trợ ra quyết định.

---

# 2. Mục tiêu dự án

## 2.1 Mục tiêu tổng quát

Xây dựng một hệ thống thu thập, xử lý, phân tích và khai phá dữ liệu tuyển sinh đại học Việt Nam nhằm:

* Chuẩn hóa dữ liệu tuyển sinh nhiều năm.
* Phân tích xu hướng tuyển sinh.
* Khai phá các quy luật tiềm ẩn trong dữ liệu.
* Hỗ trợ lựa chọn trường và ngành học.
* Xây dựng Dashboard trực quan bằng Power BI.

---

## 2.2 Mục tiêu cụ thể

### Thu thập dữ liệu

* Thu thập dữ liệu tuyển sinh từ năm 2020 đến năm 2025.
* Tổng hợp dữ liệu từ nhiều nguồn khác nhau.
* Chuẩn hóa thành một bộ dữ liệu thống nhất.

---

### Phân tích dữ liệu

Phân tích theo nhiều chiều:

* Theo năm
* Theo trường
* Theo ngành
* Theo khu vực
* Theo tổ hợp xét tuyển

---

### Khai phá dữ liệu

Áp dụng các thuật toán Data Mining:

* Clustering
* Association Rule Mining
* Forecasting
* Trend Analysis

---

### Trực quan hóa

Xây dựng Dashboard Power BI phục vụ:

* Nhà quản lý
* Học sinh
* Giáo viên
* Người nghiên cứu

---

### Hỗ trợ ra quyết định

Xây dựng chức năng gợi ý:

* Trường phù hợp
* Ngành phù hợp
* Khả năng trúng tuyển

dựa trên điểm thi và dữ liệu lịch sử.

---

# 3. Phạm vi dự án

## Bao gồm

✔ Thu thập dữ liệu tuyển sinh 2020–2025

✔ Làm sạch dữ liệu

✔ Chuẩn hóa dữ liệu

✔ Thiết kế Data Warehouse

✔ Thực hiện Exploratory Data Analysis (EDA)

✔ Áp dụng các thuật toán Data Mining

✔ Xây dựng Dashboard Power BI

✔ Hệ thống gợi ý trường/ngành

---

## Không bao gồm

* Phân tích điểm thi THPT từng thí sinh.
* Hệ thống đăng ký xét tuyển trực tuyến.
* Machine Learning Deep Learning.
* Web Application.
* Mobile Application.

Các nội dung trên được đề xuất như hướng phát triển trong tương lai.

---

# 4. Đối tượng sử dụng

## Học sinh THPT

* Theo dõi xu hướng điểm chuẩn.
* Tham khảo lựa chọn ngành.
* So sánh các trường.

---

## Giáo viên

* Phân tích dữ liệu tuyển sinh.
* Tư vấn định hướng nghề nghiệp.

---

## Nhà quản lý giáo dục

* Theo dõi xu hướng tuyển sinh.
* Đánh giá biến động điểm chuẩn.

---

## Nhà nghiên cứu

* Phân tích dữ liệu giáo dục.
* Khai phá tri thức từ dữ liệu.

---

# 5. Kiến trúc tổng thể

Hệ thống được thiết kế theo mô hình Pipeline Data Analytics.

```text
                 Data Sources
                       │
                       ▼
             Data Collection Layer
                       │
                       ▼
            Data Cleaning & ETL Layer
                       │
                       ▼
               Data Warehouse Layer
                       │
                       ▼
         Exploratory Data Analysis (EDA)
                       │
                       ▼
              Data Mining Algorithms
                       │
                       ▼
            Business Intelligence Layer
                  (Power BI Dashboard)
                       │
                       ▼
          Recommendation Decision Support
```

---

# 6. Kiến trúc chức năng

```text
                 Người dùng
                      │
                      ▼
             Dashboard Power BI
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
  Phân tích      Khai phá dữ liệu   Gợi ý trường
       │              │              │
       └──────────────┼──────────────┘
                      ▼
              Data Warehouse
                      ▼
              Clean Admission Data
                      ▼
                 Raw Dataset
```

---

# 7. Quy trình xử lý dữ liệu

Dự án được chia thành bảy giai đoạn chính.

## Giai đoạn 1

Data Collection

Thu thập dữ liệu từ:

* Website tuyển sinh
* Website các trường
* Các nguồn dữ liệu mở

Kết quả:

Raw Dataset

---

## Giai đoạn 2

Data Cleaning

Bao gồm:

* Chuẩn hóa tên trường
* Chuẩn hóa tên ngành
* Loại bỏ dữ liệu trùng
* Xử lý Missing Value
* Chuẩn hóa kiểu dữ liệu

Kết quả:

Clean Dataset

---

## Giai đoạn 3

Data Warehouse

Thiết kế:

* Fact Table
* Dimension Table

Áp dụng Star Schema.

---

## Giai đoạn 4

Exploratory Data Analysis

Phân tích:

* Xu hướng điểm chuẩn
* Xu hướng ngành học
* Xu hướng tuyển sinh
* Top trường
* Top ngành

---

## Giai đoạn 5

Data Mining

Bao gồm:

### Clustering

Phân nhóm ngành học.

### Association Rule Mining

Tìm quy luật trong dữ liệu.

### Forecasting

Dự báo điểm chuẩn.

---

## Giai đoạn 6

Business Intelligence

Thiết kế Dashboard:

* Executive Dashboard
* School Dashboard
* Major Dashboard
* Forecast Dashboard

---

## Giai đoạn 7

Recommendation System

Cho phép người dùng nhập:

* Điểm thi
* Tổ hợp
* Khu vực

Hệ thống trả về:

* Trường phù hợp
* Ngành phù hợp
* Mức độ an toàn

---

# 8. Công nghệ sử dụng

## Python

Mục đích

* Crawl dữ liệu
* ETL
* Cleaning
* Data Mining

Thư viện dự kiến

* pandas
* numpy
* BeautifulSoup
* requests
* scikit-learn
* mlxtend

---

## SQL

Mục đích

* Thiết kế Data Warehouse
* Truy vấn dữ liệu

---

## Excel

Mục đích

* Lưu dữ liệu trung gian
* Kiểm tra dữ liệu

---

## Power BI

Mục đích

* Dashboard
* KPI
* Forecast
* Drill Down
* Interactive Report

---

# 9. Cấu trúc thư mục dự án

```text
Vietnam-University-Admission-DataMining/
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   ├── processed/
│   └── warehouse/
│
├── notebooks/
│
├── src/
│   ├── crawler/
│   ├── preprocessing/
│   ├── mining/
│   └── recommendation/
│
├── powerbi/
│
├── sql/
│
├── docs/
│
├── images/
│
└── README.md
```

---

# 10. Kết quả mong đợi

Sau khi hoàn thành dự án, hệ thống sẽ đạt được các kết quả sau:

* Bộ dữ liệu tuyển sinh chuẩn hóa từ năm 2020–2025.
* Pipeline ETL hoàn chỉnh.
* Data Warehouse theo Star Schema.
* Báo cáo EDA với các insight có giá trị.
* Mô hình phân cụm các nhóm ngành học.
* Bộ luật kết hợp (Association Rules) phản ánh các mối quan hệ trong dữ liệu.
* Mô hình dự báo xu hướng điểm chuẩn.
* Dashboard Power BI trực quan, hỗ trợ phân tích đa chiều.
* Chức năng gợi ý trường/ngành theo điểm thi và tiêu chí của người dùng.

---

# 11. Giá trị của dự án

## Giá trị học thuật

* Minh họa đầy đủ quy trình Data Mining.
* Kết hợp Data Engineering, Data Analytics và Business Intelligence.
* Áp dụng nhiều kỹ thuật khai phá dữ liệu trong cùng một bài toán thực tế.

---

## Giá trị thực tiễn

* Hỗ trợ học sinh định hướng lựa chọn trường và ngành học.
* Hỗ trợ giáo viên trong công tác tư vấn tuyển sinh.
* Cung cấp góc nhìn trực quan về xu hướng tuyển sinh đại học tại Việt Nam.

---

## Giá trị kỹ thuật

Dự án không chỉ dừng ở việc xây dựng Dashboard Power BI mà còn triển khai đầy đủ quy trình:

Data Collection → ETL → Data Warehouse → EDA → Data Mining → BI Dashboard → Decision Support.

Điều này giúp dự án mang tính thực tiễn và có thể tiếp tục mở rộng thành hệ thống phân tích dữ liệu giáo dục hoặc nền tảng hỗ trợ tuyển sinh trong tương lai.

---

# 12. Lộ trình xây dựng tài liệu

Toàn bộ tài liệu dự án sẽ được chia thành các phần độc lập nhằm đảm bảo tính rõ ràng và dễ bảo trì.

| STT | File                      | Nội dung                                                       |
| --- | ------------------------- | -------------------------------------------------------------- |
| 00  | Project Overview          | Tổng quan dự án                                                |
| 01  | Problem Statement         | Phân tích bài toán nghiệp vụ                                   |
| 02  | System Architecture       | Kiến trúc hệ thống và Pipeline                                 |
| 03  | Data Collection           | Thiết kế thu thập dữ liệu và Web Crawling                      |
| 04  | Data Preprocessing        | ETL, Data Cleaning và Feature Engineering                      |
| 05  | Data Warehouse            | Thiết kế Star Schema, Fact và Dimension                        |
| 06  | Exploratory Data Analysis | Phân tích dữ liệu khám phá và KPI                              |
| 07  | Data Mining               | Clustering, Association Rules, Forecasting và đánh giá mô hình |
| 08  | Power BI Dashboard        | Thiết kế Dashboard, KPI, DAX và trải nghiệm người dùng         |
| 09  | Recommendation System     | Hệ thống hỗ trợ lựa chọn trường và ngành học                   |
| 10  | Project Implementation    | Cấu trúc mã nguồn, triển khai và hướng dẫn sử dụng             |
| 11  | Project Management        | Timeline, Milestone, quản lý tiến độ và rủi ro                 |
| 12  | Future Work               | Định hướng mở rộng dự án trong tương lai                       |

---

# 13. Kết luận

Dự án hướng tới việc xây dựng một hệ thống phân tích và khai phá dữ liệu tuyển sinh đại học Việt Nam có tính ứng dụng cao, kết hợp giữa Data Engineering, Data Mining và Business Intelligence. Thông qua việc thu thập, chuẩn hóa, phân tích và trực quan hóa dữ liệu, hệ thống không chỉ cung cấp các báo cáo và insight về xu hướng tuyển sinh mà còn hỗ trợ người dùng trong việc lựa chọn trường và ngành học phù hợp. Với kiến trúc mở và quy trình triển khai rõ ràng, dự án có thể được mở rộng trong tương lai thành một nền tảng phân tích dữ liệu giáo dục toàn diện.
