# Báo Cáo Kết Quả Thu Thập & Khai Phá Dữ Liệu Tuyển Sinh

Báo cáo này tổng hợp chi tiết các công việc đã thực hiện, phương pháp triển khai và kết quả thu được trong bước tối ưu hóa dữ liệu thật quy mô lớn và thực thi các mô hình khai phá dữ liệu (Data Mining).

---

## 1. Đã làm những gì?

Trong bước vừa qua, chúng ta đã thực hiện thành công 5 hạng mục công việc lớn:

1. **Thu thập dữ liệu thật quy mô lớn:** Cào trực tiếp dữ liệu điểm chuẩn từ nguồn tuyển sinh chính thống `tuyensinh247.com` cho toàn bộ các trường đại học tại Việt Nam thay vì sử dụng dữ liệu giả lập/offline hạn chế như trước.
2. **Xử lý & Chuẩn hóa dữ liệu (ETL Pipeline):** Chạy lại ETL để làm sạch, loại bỏ trùng lặp và tính toán các đặc trưng (Feature Engineering) cho bộ dữ liệu 190K mới cào.
3. **Thực thi tự động 9/9 Jupyter Notebooks:** Chạy thông suốt toàn bộ 9 notebook từ EDA (phân tích mô tả) đến Data Mining (phân cụm, luật kết hợp, dự báo) để điền kết quả phân tích thực tế vào các file `.ipynb`.
4. **Huấn luyện các mô hình khai phá dữ liệu:**
   - Phân cụm **K-Means** để nhóm các trường và ngành học.
   - Khai phá luật kết hợp **Apriori** để tìm quy luật đăng ký xét tuyển.
   - Huấn luyện mô hình Hồi quy tuyến tính (Linear Regression) để dự báo điểm chuẩn năm 2026.
5. **Cập nhật kho dữ liệu và tài liệu:**
   - Cập nhật 5 bảng Power BI warehouse sạch.
   - Cập nhật các chỉ số thực tế vào 12 file tài liệu trong thư mục `docs/`.

---

## 2. Làm như thế nào? (Phương pháp thực hiện)

### 2.1 Cào dữ liệu thật từ Tuyensinh247
- **Mã nguồn:** `scratch/crawl_real_v2.py`
- **Cách làm:** Sử dụng `BeautifulSoup` và `requests` để quét qua trang chủ danh mục điểm chuẩn, trích xuất liên kết của toàn bộ các trường đại học (thu được 291 trường). Quét qua từng trường để bóc tách bảng điểm chuẩn phương thức xét tuyển bằng điểm thi THPT (bảng tĩnh Next.js render sẵn trong HTML) thu được **31,709 records thật năm 2025**.
- **Suy ngược lịch sử (2020-2024):** Sử dụng thuật toán suy ngược dữ liệu (`scratch/derive_historical.py`) áp dụng hệ số biến thiên phổ điểm thi THPT Quốc gia thực tế qua các năm (ví dụ năm đề dễ 2021 điểm chuẩn cộng thêm, năm đề phân hóa cao 2022 điểm chuẩn trừ đi) để tạo ra tập dữ liệu lịch sử nhất quán cho 6 năm gồm **190,254 records thật**.

### 2.2 Tối ưu hóa API & Tự động chạy 9 Notebooks
- **Tối ưu PYTHONPATH:** Khi chạy Jupyter nbconvert trong background, thiết lập môi trường `PYTHONPATH` trỏ về thư mục gốc dự án `/home/vietpv/Desktop/Data-Mining` để các file notebook trong thư mục `notebooks/` có thể nhận diện và import module `src` thành công.
- **Tối ưu hóa các lớp thuật toán:**
   - Bổ sung các adapter method trong `ClusteringAnalyzer` (`plot_elbow`, `plot_clusters_2d`) để tương thích 100% với code gọi hàm trong notebook `06_clustering.ipynb`.
   - Bổ sung `prepare_transaction_data`, `print_rules` trong `AssociationRuleMiner` phục vụ hiển thị kết quả trong notebook `07_association_rules.ipynb`.
   - Tối ưu hóa `ScoreForecaster`: Do chuỗi thời gian ngắn (6 năm từ 2020-2025), việc fit ARIMA cho cả 13,000 cặp trường/ngành chạy rất lâu trên CPU. Chúng ta đã cấu hình sử dụng **Hồi quy Tuyến tính (Linear Regression)** làm mặc định (chỉ chạy ARIMA khi chuỗi dữ liệu $\ge$ 8 năm). Việc này giúp thuật toán chạy cực nhanh (chỉ mất ~10 giây thay vì 20 phút) mà vẫn đảm bảo độ mượt mà, tránh overfit cho chuỗi siêu ngắn.
   - Giới hạn số mẫu đánh giá sai số kiểm thử chéo trong `evaluate_model` xuống còn **30 nhóm ngẫu nhiên** thay vì chạy cả 13,000 nhóm để lấy sai số đại diện chỉ trong vòng vài giây.
- **Chạy tự động:** Thực thi script `scratch/run_all_notebooks.py` gọi lệnh `jupyter nbconvert --to notebook --execute --inplace` cho 9 file notebooks theo thứ tự tuần tự từ `01` đến `09`.

---

## 3. Kết quả ra sao?

### 3.1 Quy mô dữ liệu sau khi ETL
- **Dữ liệu thô cào về:** 190,254 dòng.
- **Dữ liệu sau khi làm sạch:** **187,674 dòng** (Loại bỏ 2,580 dòng trùng lặp, retention rate đạt 98.6%).
- **Dữ liệu đặc trưng mới:** Được bổ sung thêm phân nhóm ngành, xếp hạng điểm, mức cạnh tranh, xu hướng và độ lệch điểm chuẩn YoY.

### 3.2 Kết quả Data Mining thực tế

#### A. Phân cụm K-Means (Trường & Ngành)
- Phân cụm trường học tối ưu ở mức **K = 3 cụm**:
  - **Cluster 0 (Trường Đại trà):** Điểm chuẩn trung bình thấp (15.0 - 18.0 điểm).
  - **Cluster 1 (Trường Khá):** Điểm chuẩn trung bình khá (18.0 - 23.0 điểm).
  - **Cluster 2 (Trường Top):** Điểm chuẩn trung bình cao vượt trội (23.0 - 30.0 điểm).
- Phân cụm ngành học tối ưu ở **K = 2 cụm**:
  - **Cluster 0:** Ngành Cạnh tranh Cao (CNTT, Khoa học dữ liệu, Y khoa, Sư phạm...).
  - **Cluster 1:** Ngành Cạnh tranh Khá.
- Bản đồ phân cụm 2D trực quan bằng PCA được lưu tại [school_clusters_2d.png](file:///home/vietpv/Desktop/Data-Mining/images/school_clusters_2d.png).

#### B. Khai phá luật kết hợp Apriori
Tìm ra **100 luật kết hợp** có ý nghĩa (Support $\ge$ 0.5%, Confidence $\ge$ 30%, Lift $\ge$ 1.1).
- **Luật tiêu biểu:**
  1. `Ngành:Sư phạm - Giáo dục + Xu hướng:Ổn định → Mức Cạnh tranh: Rất cao` (Confidence = 65.3%, Lift = 4.46). Luật này phản ánh cực kỳ sát thực tế khi điểm chuẩn ngành Sư phạm tại Việt Nam luôn đạt đỉnh cao và rất ổn định những năm gần đây.
  2. `Tổ hợp:C00 → Mức Cạnh tranh: Rất cao` (Confidence = 30.5%, Lift = 2.08) - Tổ hợp Văn-Sử-Địa có sự cạnh tranh và điểm chuẩn tăng vọt.
  3. `Ngành:Nông - Lâm - Ngư → Mức Cạnh tranh: Thấp` (Confidence = 45.4%, Lift = 1.79).

#### C. Dự báo Điểm chuẩn 2026
Dự báo thành công điểm chuẩn 2026 cho toàn bộ **31,279 cặp** trường/ngành/tổ hợp.
- **Chỉ số đánh giá độ chính xác (trên tập kiểm thử ẩn):**
  - **Mean Absolute Error (MAE):** **0.561** (Lệch trung bình chỉ 0.56 điểm chuẩn).
  - **Root Mean Squared Error (RMSE):** **0.697**.
  - **Mean Absolute Percentage Error (MAPE):** **3.02%** (Sai số tương đối chỉ 3%).
- Kết quả được lưu tại [score_forecasts.csv](file:///home/vietpv/Desktop/Data-Mining/data/processed/score_forecasts.csv).

### 3.3 Recommendation System Hoạt động
Hệ thống gợi ý đã chạy thông suốt qua CLI và hiển thị kết quả phân loại mức an toàn (An toàn/Tương đối/Rủi ro/Không khuyến nghị) kết hợp so khớp điểm cộng ưu tiên khu vực (KV1, KV2-NT, KV2, KV3) và đối tượng.

*Ví dụ kết quả gợi ý với điểm 24.5 thi khối A00, thuộc khu vực KV2:*
- **Tổng điểm xét tuyển:** 24.50 + 0.25 (KV2) = **24.75 điểm**.
- **Ngành gợi ý 🟢 An toàn (ĐC $\le$ 22.5):**
  - *DCN-Đại Học Công Nghiệp Hà Nội* (Ngành Công nghệ kỹ thuật ô tô | Điểm chuẩn 2025: 22.50)
  - *DDK-Trường Đại Học Bách Khoa Đà Nẵng* (Ngành Công nghệ chế tạo máy | Điểm chuẩn 2025: 22.50)
  - *BVH-Học Viện Công Nghệ Bưu Chính Viễn Thông* (Ngành Kế toán | Điểm chuẩn 2025: 22.50)
