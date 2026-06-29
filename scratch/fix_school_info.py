"""Sửa schools_info.csv để khớp cột với export_powerbi.py"""
import pandas as pd

df = pd.read_csv("/home/vietpv/Desktop/Data-Mining/data/raw/schools_info.csv")

# Bỏ mã trường bị lẫn vào tên
df["school_name"] = df["school_name"].str.replace(r'^[A-Z0-9]+-', '', regex=True).str.strip()

# Rename cột
df = df.rename(columns={"type": "school_type", "location": "province"})

# Thêm cột region
def province_to_region(p):
    p = str(p).lower()
    bac = ["hà nội", "hải phòng", "hải dương", "bắc giang", "thái nguyên", 
           "quảng ninh", "nam định", "thái bình", "lào cai", "hà giang",
           "hưng yên", "vĩnh phúc", "phú thọ", "bắc ninh", "ninh bình"]
    nam = ["tp.hcm", "cần thơ", "bình dương", "đồng nai", "kiên giang",
           "an giang", "đắk lắk", "lâm đồng", "bình thuận", "tây ninh",
           "vũng tàu", "long an", "tiền giang"]
    for b in bac:
        if b in p:
            return "Miền Bắc"
    for n in nam:
        if n in p:
            return "Miền Nam"
    return "Miền Trung"

df["region"] = df["province"].apply(province_to_region)

df.to_csv("/home/vietpv/Desktop/Data-Mining/data/raw/schools_info.csv", index=False, encoding="utf-8-sig")
print(f"✅ Cập nhật schools_info.csv: {len(df)} trường")
print(f"   Columns: {list(df.columns)}")
print(f"   Region: {df['region'].value_counts().to_dict()}")
print(df.head(3).to_string())
