"""Script chạy tự động 9 notebooks bằng nbconvert."""
import subprocess
import sys
from pathlib import Path
from loguru import logger

NOTEBOOKS_DIR = Path("/home/vietpv/Desktop/Data-Mining/notebooks")

notebooks = [
    "01_data_overview.ipynb",
    "02_trend_analysis.ipynb",
    "03_school_analysis.ipynb",
    "04_major_analysis.ipynb",
    "05_subject_group_analysis.ipynb",
    "06_clustering.ipynb",
    "07_association_rules.ipynb",
    "08_forecasting.ipynb",
    "09_recommendation_demo.ipynb"
]

def run_notebook(nb_name):
    nb_path = NOTEBOOKS_DIR / nb_name
    logger.info(f"Đang thực thi: {nb_name}...")
    cmd = [
        "conda", "run", "-n", "testing",
        "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
        str(nb_path)
    ]
    # Thiết lập PYTHONPATH để python kernel trong Jupyter nhận diện được thư mục src
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = "/home/vietpv/Desktop/Data-Mining"
    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        logger.success(f"✅ Đã thực thi xong: {nb_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Lỗi khi chạy {nb_name}:")
        logger.error(e.stderr)
        return False

def main():
    logger.info("==================================================")
    logger.info("BẮT ĐẦU CHẠY TỰ ĐỘNG TẤT CẢ 9 NOTEBOOKS DỰ ÁN")
    logger.info("==================================================")
    
    success_count = 0
    for nb in notebooks:
        if run_notebook(nb):
            success_count += 1
        else:
            logger.warning("Dừng quá trình chạy do có lỗi ở notebook hiện tại.")
            sys.exit(1)
            
    logger.success(f"\n🎉 HOÀN THÀNH! Đã chạy thành công {success_count}/{len(notebooks)} notebooks.")

if __name__ == "__main__":
    main()
