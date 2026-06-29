"""
src/mining/clustering.py
Phân cụm trường/ngành học bằng K-Means Clustering

Mục tiêu:
- Phân nhóm trường theo đặc điểm điểm chuẩn
- Phân nhóm ngành theo mức độ cạnh tranh và xu hướng
- Xác định số cluster tối ưu (Elbow + Silhouette)

Cách dùng:
    from src.mining.clustering import ClusteringAnalyzer
    analyzer = ClusteringAnalyzer(df)
    school_clusters = analyzer.cluster_schools(n_clusters=4)
    major_clusters = analyzer.cluster_majors(n_clusters=5)
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # Backend không cần GUI
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score
from loguru import logger


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGES_DIR = PROJECT_ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


class ClusteringAnalyzer:
    """
    Phân cụm trường và ngành học bằng K-Means.

    Quy trình:
    1. Chuẩn bị features (aggregate theo trường/ngành)
    2. Chuẩn hóa features (StandardScaler)
    3. Xác định K tối ưu (Elbow + Silhouette)
    4. Fit K-Means
    5. Phân tích cluster profiles
    6. Visualization (Elbow, Silhouette, Scatter 2D)
    """

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame đã xử lý (từ ETL pipeline)
        """
        self.df = df
        self.scaler = StandardScaler()
        self.school_model = None
        self.major_model = None
        self.school_clusters_ = None
        self.major_clusters_ = None

    def plot_elbow(self, max_k: int = 8) -> None:
        """
        Vẽ biểu đồ Elbow + Silhouette để tìm K tối ưu (tương thích notebook).
        """
        school_features = self._prepare_school_features()
        if school_features.empty:
            logger.error("Không có features để vẽ Elbow")
            return
        feature_cols = ["avg_score", "max_score", "std_score", "num_majors", "avg_delta"]
        available_features = [c for c in feature_cols if c in school_features.columns]
        X = school_features[available_features].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        self._find_optimal_k(X_scaled, max_k=max_k, entity="schools")

    def plot_clusters_2d(self) -> None:
        """
        Vẽ lại biểu đồ phân cụm 2D PCA của trường (tương thích notebook).
        """
        if self.school_clusters_ is None:
            logger.info("Chưa phân cụm trường, tiến hành phân cụm tự động...")
            self.cluster_schools(auto_k=True)
            
        school_features = self.school_clusters_
        feature_cols = ["avg_score", "max_score", "std_score", "num_majors", "avg_delta"]
        available_features = [c for c in feature_cols if c in school_features.columns]
        X = school_features[available_features].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        
        self._plot_clusters_2d(
            X_scaled, 
            school_features["cluster"].values, 
            school_features["school_name"].values,
            title="Phân cụm Trường Đại học", 
            filename="school_clusters_2d.png"
        )
        # Đồng thời hiển thị biểu đồ nếu chạy trong môi trường Jupyter notebook
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            pca = PCA(n_components=2, random_state=42)
            X_2d = pca.fit_transform(X_scaled)
            labels = school_features["cluster"].values
            palette = sns.color_palette("husl", len(np.unique(labels)))
            for cluster_id in np.unique(labels):
                mask = labels == cluster_id
                ax.scatter(
                    X_2d[mask, 0], X_2d[mask, 1],
                    c=[palette[cluster_id]], label=f"Cluster {cluster_id}",
                    alpha=0.7, s=80, edgecolors="white", linewidths=0.5
                )
            ax.set_title("Phân cụm Trường Đại học (Jupyter View)", fontsize=14, fontweight="bold")
            ax.set_xlabel(f"PCA Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
            ax.set_ylabel(f"PCA Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
            ax.legend(loc="best")
            ax.grid(True, alpha=0.3)
            plt.show()
        except Exception:
            pass

    # ================================================================
    # Cluster Schools (Phân cụm trường)
    # ================================================================

    def cluster_schools(
        self,
        n_clusters: int = 4,
        max_k: int = 10,
        auto_k: bool = True,
        k: int = None,
    ) -> pd.DataFrame:
        """
        Phân cụm trường đại học.

        Features:
        - avg_score: Điểm chuẩn trung bình
        - max_score: Điểm chuẩn cao nhất
        - std_score: Độ biến động điểm
        - num_majors: Số ngành tuyển sinh
        - avg_delta: Thay đổi điểm trung bình hàng năm

        Args:
            n_clusters: Số cluster (nếu auto_k=False)
            max_k: K tối đa để thử khi auto_k=True
            auto_k: Tự động chọn K tối ưu
            k: Tham số alias cho n_clusters (tương thích notebook)

        Returns:
            DataFrame trường với cột 'cluster' và 'cluster_label'
        """
        if k is not None:
            n_clusters = k
            auto_k = False

        logger.info("Bắt đầu phân cụm trường...")

        # Tạo feature matrix
        school_features = self._prepare_school_features()
        if school_features.empty:
            logger.error("Không có features để cluster trường")
            return pd.DataFrame()

        # Scale features
        feature_cols = ["avg_score", "max_score", "std_score", "num_majors", "avg_delta"]
        available_features = [c for c in feature_cols if c in school_features.columns]
        X = school_features[available_features].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)

        # Xác định K tối ưu
        if auto_k:
            optimal_k = self._find_optimal_k(X_scaled, max_k=max_k, entity="schools")
            n_clusters = optimal_k
            logger.info(f"K tối ưu cho trường: {n_clusters}")

        # Fit K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        school_features["cluster"] = labels

        # Đánh giá
        sil_score = silhouette_score(X_scaled, labels)
        db_score = davies_bouldin_score(X_scaled, labels)
        logger.info(f"Silhouette Score (trường): {sil_score:.3f}")
        logger.info(f"Davies-Bouldin Score (trường): {db_score:.3f}")

        # Đặt tên cluster
        school_features = self._label_school_clusters(school_features)

        # Visualization
        self._plot_clusters_2d(X_scaled, labels, school_features["school_name"].values,
                               title="Phân cụm Trường Đại học", filename="school_clusters_2d.png")

        self.school_model = kmeans
        self.school_clusters_ = school_features
        logger.success(f"Phân cụm trường hoàn tất: {n_clusters} clusters")
        return school_features

    def cluster_majors(
        self,
        n_clusters: int = 5,
        max_k: int = 10,
        auto_k: bool = True,
    ) -> pd.DataFrame:
        """
        Phân cụm ngành học.

        Features:
        - avg_score: Điểm chuẩn trung bình
        - num_schools: Số trường có ngành này
        - avg_delta: Biến động điểm trung bình
        - score_variance: Phương sai điểm
        """
        logger.info("Bắt đầu phân cụm ngành...")

        major_features = self._prepare_major_features()
        if major_features.empty:
            return pd.DataFrame()

        feature_cols = ["avg_score", "num_schools", "avg_delta", "score_variance"]
        available_features = [c for c in feature_cols if c in major_features.columns]
        X = major_features[available_features].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)

        if auto_k:
            optimal_k = self._find_optimal_k(X_scaled, max_k=max_k, entity="majors")
            n_clusters = optimal_k

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        major_features["cluster"] = labels

        sil_score = silhouette_score(X_scaled, labels)
        logger.info(f"Silhouette Score (ngành): {sil_score:.3f}")

        major_features = self._label_major_clusters(major_features)

        self._plot_clusters_2d(X_scaled, labels, major_features["major_name"].values,
                               title="Phân cụm Ngành học", filename="major_clusters_2d.png")

        self.major_model = kmeans
        self.major_clusters_ = major_features
        logger.success(f"Phân cụm ngành hoàn tất: {n_clusters} clusters")
        return major_features

    # ================================================================
    # Feature Preparation
    # ================================================================

    def _prepare_school_features(self) -> pd.DataFrame:
        """Tổng hợp features theo trường."""
        features = (
            self.df.groupby("school_name")
            .agg(
                avg_score=("admission_score", "mean"),
                max_score=("admission_score", "max"),
                min_score=("admission_score", "min"),
                std_score=("admission_score", "std"),
                num_majors=("major_name", "nunique"),
                avg_delta=("delta_score", "mean"),
                total_quota=("quota", "sum"),
            )
            .round(2)
            .reset_index()
        )
        features["std_score"] = features["std_score"].fillna(0)
        return features

    def _prepare_major_features(self) -> pd.DataFrame:
        """Tổng hợp features theo ngành."""
        features = (
            self.df.groupby("major_name")
            .agg(
                avg_score=("admission_score", "mean"),
                num_schools=("school_name", "nunique"),
                avg_delta=("delta_score", "mean"),
                score_variance=("admission_score", "var"),
            )
            .round(2)
            .reset_index()
        )
        features["score_variance"] = features["score_variance"].fillna(0)
        return features

    # ================================================================
    # Optimal K Selection
    # ================================================================

    def _find_optimal_k(
        self, X_scaled: np.ndarray, max_k: int = 10, entity: str = "data"
    ) -> int:
        """
        Tìm K tối ưu bằng Elbow method + Silhouette score.

        Returns:
            K tối ưu (số cluster tốt nhất)
        """
        inertias = []
        sil_scores = []
        k_range = range(2, min(max_k + 1, len(X_scaled)))

        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(X_scaled)
            inertias.append(km.inertia_)
            sil_scores.append(silhouette_score(X_scaled, labels))

        # Plot Elbow + Silhouette
        self._plot_elbow_silhouette(
            list(k_range), inertias, sil_scores, entity=entity
        )

        # Chọn K tối ưu: K có Silhouette cao nhất
        best_k_idx = sil_scores.index(max(sil_scores))
        best_k = list(k_range)[best_k_idx]
        logger.info(f"K tối ưu ({entity}): {best_k} (Silhouette={max(sil_scores):.3f})")
        return best_k

    # ================================================================
    # Cluster Labeling
    # ================================================================

    def _label_school_clusters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Đặt nhãn cho cluster trường dựa trên đặc điểm."""
        cluster_profiles = df.groupby("cluster")["avg_score"].mean().sort_values(ascending=False)
        labels = {}

        level_names = ["Trường Top", "Trường Khá", "Trường Trung bình", "Trường Đại trà"]
        for i, (cluster_id, _) in enumerate(cluster_profiles.items()):
            label = level_names[i] if i < len(level_names) else f"Nhóm {i+1}"
            labels[cluster_id] = label

        df["cluster_label"] = df["cluster"].map(labels)
        return df

    def _label_major_clusters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Đặt nhãn cho cluster ngành."""
        cluster_profiles = df.groupby("cluster")["avg_score"].mean().sort_values(ascending=False)
        labels = {}
        level_names = [
            "Ngành Cạnh tranh Cao",
            "Ngành Cạnh tranh Khá",
            "Ngành Phổ thông",
            "Ngành Dễ xét tuyển",
            "Ngành Mới nổi",
        ]
        for i, (cluster_id, _) in enumerate(cluster_profiles.items()):
            label = level_names[i] if i < len(level_names) else f"Nhóm {i+1}"
            labels[cluster_id] = label

        df["cluster_label"] = df["cluster"].map(labels)
        return df

    # ================================================================
    # Visualization
    # ================================================================

    def _plot_elbow_silhouette(
        self, k_range, inertias, sil_scores, entity: str = "data"
    ) -> None:
        """Vẽ Elbow + Silhouette chart."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(f"Xác định K tối ưu — {entity}", fontsize=14, fontweight="bold")

        # Elbow
        ax1.plot(k_range, inertias, "bo-", linewidth=2, markersize=8)
        ax1.set_xlabel("Số clusters (K)")
        ax1.set_ylabel("Inertia (WCSS)")
        ax1.set_title("Elbow Method")
        ax1.grid(True, alpha=0.3)

        # Silhouette
        best_k = k_range[sil_scores.index(max(sil_scores))]
        colors = ["red" if k == best_k else "steelblue" for k in k_range]
        ax2.bar(k_range, sil_scores, color=colors, alpha=0.8)
        ax2.set_xlabel("Số clusters (K)")
        ax2.set_ylabel("Silhouette Score")
        ax2.set_title(f"Silhouette Score (Tốt nhất: K={best_k})")
        ax2.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        filepath = IMAGES_DIR / f"elbow_silhouette_{entity}.png"
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved: {filepath}")

    def _plot_clusters_2d(
        self, X_scaled, labels, names, title: str, filename: str
    ) -> None:
        """Vẽ scatter plot 2D sau khi giảm chiều bằng PCA."""
        pca = PCA(n_components=2, random_state=42)
        X_2d = pca.fit_transform(X_scaled)

        fig, ax = plt.subplots(figsize=(12, 8))
        palette = sns.color_palette("husl", len(np.unique(labels)))

        for cluster_id in np.unique(labels):
            mask = labels == cluster_id
            ax.scatter(
                X_2d[mask, 0], X_2d[mask, 1],
                c=[palette[cluster_id]], label=f"Cluster {cluster_id}",
                alpha=0.7, s=80, edgecolors="white", linewidths=0.5
            )

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(f"PCA Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
        ax.set_ylabel(f"PCA Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filepath = IMAGES_DIR / filename
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved: {filepath}")

    def get_cluster_summary(self, entity: str = "school") -> pd.DataFrame:
        """Trả về tổng hợp profile của từng cluster."""
        df = self.school_clusters_ if entity == "school" else self.major_clusters_
        if df is None:
            return pd.DataFrame()

        summary = (
            df.groupby(["cluster", "cluster_label"])
            .agg(count=("school_name" if entity == "school" else "major_name", "count"),
                 avg_score=("avg_score", "mean"))
            .round(2)
            .reset_index()
            .sort_values("avg_score", ascending=False)
        )
        return summary

    def save_model(self, filepath: Path = None) -> None:
        """Lưu mô hình cluster."""
        if filepath is None:
            filepath = PROJECT_ROOT / "data" / "processed" / "clustering_models.pkl"
        with open(filepath, "wb") as f:
            pickle.dump({
                "school_model": self.school_model,
                "major_model": self.major_model,
                "scaler": self.scaler,
            }, f)
        logger.info(f"Mô hình clustering đã lưu: {filepath}")


if __name__ == "__main__":
    # Điểm kích hoạt khi chạy script trực tiếp
    import argparse
    parser = argparse.ArgumentParser(description="Chạy phân cụm trường và ngành")
    parser.add_argument("--evaluate", action="store_true", help="Đánh giá mô hình")
    args = parser.parse_args()

    processed_file = PROJECT_ROOT / "data" / "processed" / "admission_processed.csv"
    if not processed_file.exists():
        logger.error(f"Không tìm thấy file: {processed_file}")
        import sys
        sys.exit(1)
        
    df = pd.read_csv(processed_file, encoding="utf-8-sig")
    analyzer = ClusteringAnalyzer(df)
    
    # Phân cụm trường
    logger.info("Chạy phân cụm trường...")
    schools_df = analyzer.cluster_schools(auto_k=True)
    if not schools_df.empty:
        # Lưu kết quả cluster label vào csv processed để lưu trữ
        schools_df[["school_name", "cluster", "cluster_label"]].to_csv(
            PROJECT_ROOT / "data" / "processed" / "school_clusters.csv", 
            index=False, 
            encoding="utf-8-sig"
        )
        logger.success("Đã lưu kết quả phân cụm trường vào school_clusters.csv")
        
    # Phân cụm ngành
    logger.info("Chạy phân cụm ngành...")
    majors_df = analyzer.cluster_majors(auto_k=True)
    if not majors_df.empty:
        majors_df[["major_name", "cluster", "cluster_label"]].to_csv(
            PROJECT_ROOT / "data" / "processed" / "major_clusters.csv", 
            index=False, 
            encoding="utf-8-sig"
        )
        logger.success("Đã lưu kết quả phân cụm ngành vào major_clusters.csv")
        
    # Lưu model pkl
    analyzer.save_model()

