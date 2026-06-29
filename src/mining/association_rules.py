"""
src/mining/association_rules.py
Khai phá luật kết hợp bằng Apriori algorithm (mlxtend)

Mục tiêu:
- Tìm mối quan hệ giữa: ngành học, tổ hợp xét tuyển, khu vực, mức cạnh tranh
- VD: {Tổ hợp A00} → {Kỹ thuật - Công nghệ} (support=0.3, confidence=0.8)
- VD: {Điểm Rất cao} → {Miền Bắc, Miền Nam} (support=0.2, confidence=0.7)

Cách dùng:
    miner = AssociationRuleMiner(df)
    rules = miner.mine_rules(min_support=0.05, min_confidence=0.5, min_lift=1.2)
    miner.save_rules(rules)
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from loguru import logger


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGES_DIR = PROJECT_ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


class AssociationRuleMiner:
    """
    Khai phá luật kết hợp từ dữ liệu tuyển sinh.

    Pipeline:
    1. Tạo transaction matrix (One-hot encoding)
    2. Tìm frequent itemsets bằng Apriori
    3. Sinh luật kết hợp từ frequent itemsets
    4. Lọc theo support, confidence, lift
    5. Visualization và export
    """

    # Cấu hình mặc định
    DEFAULT_MIN_SUPPORT = 0.005     # ≥0.5% transactions chứa itemset
    DEFAULT_MIN_CONFIDENCE = 0.3    # ≥30% confidence
    DEFAULT_MIN_LIFT = 1.1          # Lift ≥ 1.1 (có ý nghĩa thống kê)

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.rules_ = None
        self.frequent_itemsets_ = None

    def prepare_transaction_data(self) -> pd.DataFrame:
        """
        Chuyển đổi dữ liệu tuyển sinh thành dạng giao dịch phục vụ hiển thị (tương thích notebook).
        """
        transactions = self._prepare_transactions()
        return pd.DataFrame({"items": [", ".join(t) for t in transactions]})

    def print_rules(self, rules: pd.DataFrame = None, top_n: int = 20) -> None:
        """
        In ra các luật kết hợp (tương thích notebook).
        """
        if rules is None:
            rules = self.rules_
        if rules is not None and not rules.empty:
            top = rules.head(top_n)
            print(top.to_string(index=False))
        else:
            print("Không có luật kết hợp nào để hiển thị.")

    def mine_rules(
        self,
        min_support: float = None,
        min_confidence: float = None,
        min_lift: float = None,
        max_rules: int = 100,
    ) -> pd.DataFrame:
        """
        Thực hiện Association Rule Mining.

        Args:
            min_support: Ngưỡng support tối thiểu
            min_confidence: Ngưỡng confidence tối thiểu
            min_lift: Ngưỡng lift tối thiểu
            max_rules: Số luật tối đa trả về

        Returns:
            DataFrame chứa các luật kết hợp với metrics
        """
        min_support = min_support or self.DEFAULT_MIN_SUPPORT
        min_confidence = min_confidence or self.DEFAULT_MIN_CONFIDENCE
        min_lift = min_lift or self.DEFAULT_MIN_LIFT

        logger.info(f"Association Rule Mining: support≥{min_support}, confidence≥{min_confidence}, lift≥{min_lift}")

        # Bước 1: Chuẩn bị transactions
        transactions = self._prepare_transactions()
        if not transactions:
            logger.error("Không có transactions để mine")
            return pd.DataFrame()

        logger.info(f"Số transactions: {len(transactions):,}")

        # Bước 2: One-hot encoding
        te = TransactionEncoder()
        te_array = te.fit_transform(transactions)
        df_encoded = pd.DataFrame(te_array, columns=te.columns_)
        logger.info(f"Số items unique: {len(te.columns_)}")

        # Bước 3: Tìm frequent itemsets
        logger.info("Tìm frequent itemsets (Apriori)...")
        try:
            frequent_itemsets = apriori(
                df_encoded,
                min_support=min_support,
                use_colnames=True,
                max_len=4,  # Tối đa 4 items/itemset
            )
        except Exception as e:
            logger.error(f"Apriori thất bại: {e}")
            return pd.DataFrame()

        if frequent_itemsets.empty:
            logger.warning("Không tìm thấy frequent itemsets. Thử giảm min_support.")
            return pd.DataFrame()

        logger.info(f"Số frequent itemsets: {len(frequent_itemsets):,}")
        self.frequent_itemsets_ = frequent_itemsets

        # Bước 4: Sinh luật kết hợp
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=min_confidence,
        )

        if rules.empty:
            logger.warning("Không sinh được luật. Thử giảm min_confidence.")
            return pd.DataFrame()

        # Bước 5: Lọc theo lift
        rules = rules[rules["lift"] >= min_lift]
        rules = rules.sort_values("lift", ascending=False).head(max_rules)
        rules = rules.reset_index(drop=True)

        # Format kết quả
        rules = self._format_rules(rules)

        logger.success(f"Tìm được {len(rules)} luật kết hợp có ý nghĩa")
        self.rules_ = rules
        return rules

    def _prepare_transactions(self) -> list:
        """
        Chuyển dữ liệu tuyển sinh thành dạng transaction.

        Mỗi transaction = 1 record (trường+ngành+tổ hợp+năm)
        Items trong transaction = categorical features

        Ví dụ transaction:
        ["KT-Công nghệ", "A00", "Rất cao", "Bắc", "Hậu COVID"]
        """
        transactions = []

        for _, row in self.df.iterrows():
            items = []

            # Item 1: Nhóm ngành
            if pd.notna(row.get("major_group")) and row["major_group"] not in ("Khác", ""):
                items.append(f"Ngành:{row['major_group']}")

            # Item 2: Tổ hợp xét tuyển
            if pd.notna(row.get("subject_group")) and row["subject_group"] not in ("Không xác định", ""):
                items.append(f"TH:{row['subject_group']}")

            # Item 3: Mức cạnh tranh
            if pd.notna(row.get("competition_level")):
                items.append(f"Cạnh tranh:{row['competition_level']}")

            # Item 4: Xu hướng điểm
            if pd.notna(row.get("score_trend")) and row["score_trend"] != "Không xác định":
                items.append(f"Xu hướng:{row['score_trend']}")

            # Item 5: Loại trường (nếu có)
            if pd.notna(row.get("school_type")):
                items.append(f"Loại:{row['school_type']}")

            # Chỉ thêm transaction nếu có ít nhất 2 items
            if len(items) >= 2:
                transactions.append(items)

        return transactions

    def _format_rules(self, rules: pd.DataFrame) -> pd.DataFrame:
        """Format luật để dễ đọc hơn."""
        rules = rules.copy()

        # Chuyển frozenset → string
        rules["antecedents"] = rules["antecedents"].apply(
            lambda x: " + ".join(sorted(x))
        )
        rules["consequents"] = rules["consequents"].apply(
            lambda x: " + ".join(sorted(x))
        )
        rules["rule"] = rules["antecedents"] + " → " + rules["consequents"]

        # Round metrics
        for col in ["support", "confidence", "lift"]:
            if col in rules.columns:
                rules[col] = rules[col].round(4)

        return rules[["rule", "antecedents", "consequents", "support", "confidence", "lift"]]

    def get_top_rules(self, metric: str = "lift", n: int = 20) -> pd.DataFrame:
        """Lấy top N luật theo metric."""
        if self.rules_ is None:
            logger.warning("Chưa mine rules. Gọi mine_rules() trước.")
            return pd.DataFrame()
        return self.rules_.sort_values(metric, ascending=False).head(n)

    def plot_rules_scatter(self, output_path: Path = None) -> None:
        """Vẽ scatter plot: support vs confidence, size = lift."""
        if self.rules_ is None:
            return

        fig, ax = plt.subplots(figsize=(12, 8))

        scatter = ax.scatter(
            self.rules_["support"],
            self.rules_["confidence"],
            c=self.rules_["lift"],
            s=self.rules_["lift"] * 30,
            alpha=0.7,
            cmap="YlOrRd",
            edgecolors="gray",
            linewidths=0.5,
        )

        plt.colorbar(scatter, ax=ax, label="Lift")
        ax.set_xlabel("Support", fontsize=12)
        ax.set_ylabel("Confidence", fontsize=12)
        ax.set_title("Association Rules — Support vs Confidence (size = Lift)", fontsize=13)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        path = output_path or (IMAGES_DIR / "association_rules_scatter.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved: {path}")

    def save_rules(self, output_dir: Path = None, filename: str = "association_rules.csv") -> Path:
        """Lưu luật kết hợp ra CSV."""
        if self.rules_ is None:
            return None
        output_dir = output_dir or (PROJECT_ROOT / "data" / "processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / filename
        self.rules_.to_csv(path, index=False, encoding="utf-8-sig")
        logger.info(f"Luật kết hợp đã lưu: {path}")
        return path

    def print_top_rules(self, n: int = 10) -> None:
        """In top N luật có lift cao nhất."""
        top = self.get_top_rules(metric="lift", n=n)
        if top.empty:
            logger.warning("Không có rules để hiển thị")
            return
        print("\n" + "=" * 70)
        print(f"TOP {n} LUẬT KẾT HỢP (theo Lift)")
        print("=" * 70)
        for _, row in top.iterrows():
            print(f"  {row['rule']}")
            print(f"    Support={row['support']:.3f}  Confidence={row['confidence']:.3f}  Lift={row['lift']:.3f}")
            print()


if __name__ == "__main__":
    processed_file = PROJECT_ROOT / "data" / "processed" / "admission_processed.csv"
    if not processed_file.exists():
        logger.error(f"Không tìm thấy file: {processed_file}")
        import sys
        sys.exit(1)
        
    df = pd.read_csv(processed_file, encoding="utf-8-sig")
    miner = AssociationRuleMiner(df)
    
    # Khai phá luật kết hợp
    logger.info("Chạy khai phá luật kết hợp Apriori...")
    rules = miner.mine_rules()
    
    if not rules.empty:
        # Lưu kết quả
        miner.save_rules()
        # In các luật tiêu biểu
        miner.print_top_rules(n=10)
        # Vẽ biểu đồ
        miner.plot_rules_scatter()
        logger.success("Đã hoàn thành khai phá luật kết hợp thành công!")
    else:
        logger.warning("Không tìm thấy luật nào.")

