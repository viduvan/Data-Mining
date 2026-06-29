"""Tạo file schools_info.csv từ dữ liệu thật đã crawl."""
import pandas as pd
from pathlib import Path

DATA_RAW = Path("/home/vietpv/Desktop/Data-Mining/data/raw")

df = pd.read_csv(DATA_RAW / "admission_2025.csv")

# Lấy danh sách unique trường
schools = df.drop_duplicates(subset=["school_code"])[["school_code", "school_name"]].copy()
schools = schools.rename(columns={"school_code": "school_code", "school_name": "school_name"})
schools["location"] = ""
schools["type"] = "Công lập"
schools["website"] = ""
schools["established_year"] = ""

# Gán location dựa trên tên trường
def guess_location(name):
    name = str(name).lower()
    if any(k in name for k in ["tphcm", "tp.hcm", "tp hcm", "hồ chí minh", "sài gòn"]):
        return "TP.HCM"
    elif any(k in name for k in ["hà nội", "hanoi", "thăng long"]):
        return "Hà Nội"  
    elif any(k in name for k in ["đà nẵng"]):
        return "Đà Nẵng"
    elif any(k in name for k in ["huế"]):
        return "Huế"
    elif any(k in name for k in ["cần thơ"]):
        return "Cần Thơ"
    elif any(k in name for k in ["thái nguyên"]):
        return "Thái Nguyên"
    elif any(k in name for k in ["vinh", "nghệ an"]):
        return "Nghệ An"
    elif any(k in name for k in ["quy nhơn", "bình định"]):
        return "Bình Định"
    elif any(k in name for k in ["nha trang", "khánh hòa"]):
        return "Khánh Hòa"
    elif any(k in name for k in ["đà lạt", "lâm đồng"]):
        return "Lâm Đồng"
    elif any(k in name for k in ["hải phòng"]):
        return "Hải Phòng"
    elif any(k in name for k in ["thanh hóa"]):
        return "Thanh Hóa"
    elif any(k in name for k in ["thái bình"]):
        return "Thái Bình"
    elif any(k in name for k in ["nam định"]):
        return "Nam Định"
    elif any(k in name for k in ["bắc giang"]):
        return "Bắc Giang"
    elif any(k in name for k in ["hải dương"]):
        return "Hải Dương"
    elif any(k in name for k in ["quảng nam"]):
        return "Quảng Nam"
    elif any(k in name for k in ["quảng ninh"]):
        return "Quảng Ninh"
    elif any(k in name for k in ["bình dương"]):
        return "Bình Dương"
    elif any(k in name for k in ["lào cai"]):
        return "Lào Cai"
    elif any(k in name for k in ["hà giang"]):
        return "Hà Giang"
    elif any(k in name for k in ["kiên giang"]):
        return "Kiên Giang"
    elif any(k in name for k in ["buôn ma thuột", "đắk lắk"]):
        return "Đắk Lắk"
    elif any(k in name for k in ["tây nguyên"]):
        return "Đắk Lắk"
    return "Hà Nội"  # Mặc định

def guess_type(name):
    name = str(name).lower()
    if any(k in name for k in ["dân lập", "tư thục", "fpt", "rmit", "quốc tế", "british", "anh quốc", "phenikaa", "vạn xuân", "hoa sen", "đông á", "văn lang", "công nghệ sài gòn"]):
        return "Tư thục"
    elif any(k in name for k in ["quân", "sĩ quan", "an ninh", "cảnh sát", "công an"]):
        return "Quân đội/Công an"
    return "Công lập"

schools["location"] = schools["school_name"].apply(guess_location)
schools["type"] = schools["school_name"].apply(guess_type)

schools.to_csv(DATA_RAW / "schools_info.csv", index=False, encoding="utf-8-sig")
print(f"✅ Đã tạo schools_info.csv: {len(schools)} trường")
print(f"   Phân bố loại: {schools['type'].value_counts().to_dict()}")
print(f"   Top 10 địa phương: {schools['location'].value_counts().head(10).to_dict()}")
