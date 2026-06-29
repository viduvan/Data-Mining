"""
src/mining/forecasting.py
Dự báo điểm chuẩn tuyển sinh bằng Linear Regression và ARIMA

Mục tiêu:
- Dự báo điểm chuẩn cho các trường/ngành trong năm tới
- So sánh mô hình: Linear Regression vs ARIMA
- Đánh giá: MAE, RMSE, MAPE

Cách dùng:
    forecaster = ScoreForecaster(df)
    results = forecaster.forecast_all(forecast_year=2026)
    forecaster.plot_forecast("Đại học Bách khoa Hà Nội", "Công nghệ thông tin")
"""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from loguru import logger

try:
    from statsmodels.tsa.arima.model import ARIMA
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logger.warning("statsmodels không có sẵn. Chỉ dùng Linear Regression.")


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGES_DIR = PROJECT_ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


class ScoreForecaster:
    """
    Dự báo điểm chuẩn tuyển sinh.

    Hỗ trợ 2 mô hình:
    1. Linear Regression: Đơn giản, phù hợp với chuỗi dài
    2. ARIMA: Phù hợp với chuỗi thời gian có seasonality/autocorrelation

    Chiến lược:
    - Với chuỗi ngắn (< 4 điểm): dùng Linear Regression
    - Với chuỗi đủ dài (≥ 4 điểm): thử cả hai, chọn RMSE thấp hơn
    """

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame đã xử lý với columns: school_name, major_name,
                subject_group, year, admission_score
        """
        self.df = df
        self.forecasts_ = {}
        self.metrics_ = {}

    def forecast_school_major(self, school_name: str, major_name: str, forecast_year: int = 2026) -> dict:
        """Dự báo cho một trường và ngành cụ thể (tương thích notebook)."""
        # So khớp tương đối vì tên trường có mã prefix (ví dụ BKA-Đại học...)
        mask = self.df["school_name"].str.contains(school_name, case=False, na=False) & \
               self.df["major_name"].str.contains(major_name, case=False, na=False)
        sub_df = self.df[mask].sort_values("year")[["year", "admission_score"]].dropna()
        
        if sub_df.empty:
            mask = (self.df["school_name"] == school_name) & (self.df["major_name"] == major_name)
            sub_df = self.df[mask].sort_values("year")[["year", "admission_score"]].dropna()
            
        if sub_df.empty:
            logger.warning(f"Không tìm thấy dữ liệu cho {school_name} - {major_name}")
            return {"history": {}, "predicted_score": 0.0, "model_used": "N/A"}
            
        # Nhóm theo năm (lấy trung bình điểm chuẩn các tổ hợp)
        ts = sub_df.groupby("year")["admission_score"].mean().reset_index()
        years = ts["year"].values
        scores = ts["admission_score"].values
        
        pred, lower, upper, model = self._forecast_single(years, scores, forecast_year)
        history = dict(zip(years.astype(int), scores))
        
        return {
            "history": history,
            "predicted_score": round(float(pred), 2) if pred is not None else 0.0,
            "lower_bound": round(float(lower), 2) if lower is not None else None,
            "upper_bound": round(float(upper), 2) if upper is not None else None,
            "model_used": model
        }

    def evaluate_forecasting_models(self) -> dict:
        """Đánh giá mô hình dự báo tổng thể (tương thích notebook)."""
        metrics = self.evaluate_model()
        # Trả về các chỉ số MAE, RMSE, MAPE chính
        return {
            "MAE": metrics.get("MAE", 0.0),
            "RMSE": metrics.get("RMSE", 0.0),
            "MAPE": metrics.get("MAPE", 0.0)
        }

    def forecast_all(
        self,
        forecast_year: int = 2026,
        min_years: int = 3,
    ) -> pd.DataFrame:
        """
        Dự báo cho tất cả cặp (trường, ngành, tổ hợp) đủ dữ liệu.

        Args:
            forecast_year: Năm cần dự báo
            min_years: Số năm dữ liệu tối thiểu để dự báo

        Returns:
            DataFrame kết quả dự báo
        """
        logger.info(f"Dự báo điểm chuẩn năm {forecast_year}...")

        group_cols = ["school_name", "major_name", "subject_group"]
        results = []
        groups = self.df.groupby(group_cols)

        count = 0
        skipped = 0
        for group_key, group_df in groups:
            # Sort theo năm
            ts = group_df.sort_values("year")[["year", "admission_score"]].dropna()

            if len(ts) < min_years:
                skipped += 1
                continue

            school, major, subject_group = group_key
            years = ts["year"].values
            scores = ts["admission_score"].values

            # Dự báo
            pred, lower, upper, model_used = self._forecast_single(
                years, scores, forecast_year
            )

            if pred is not None:
                results.append({
                    "school_name": school,
                    "major_name": major,
                    "subject_group": subject_group,
                    "last_known_score": float(scores[-1]),
                    "last_known_year": int(years[-1]),
                    "forecast_year": forecast_year,
                    "predicted_score": round(float(pred), 2),
                    "lower_bound": round(float(lower), 2) if lower is not None else None,
                    "upper_bound": round(float(upper), 2) if upper is not None else None,
                    "model_used": model_used,
                    "trend": "Tăng" if pred > scores[-1] else "Giảm" if pred < scores[-1] else "Ổn định",
                    "delta_forecast": round(float(pred - scores[-1]), 2),
                    "n_years_data": len(ts),
                })
                count += 1

        logger.info(f"Dự báo thành công: {count} cặp (bỏ qua {skipped} cặp thiếu dữ liệu)")

        forecast_df = pd.DataFrame(results)
        if not forecast_df.empty:
            # Clip điểm dự báo về khoảng hợp lý
            forecast_df["predicted_score"] = forecast_df["predicted_score"].clip(0, 30)
            forecast_df = forecast_df.sort_values(
                "predicted_score", ascending=False
            ).reset_index(drop=True)

        self.forecasts_ = forecast_df
        return forecast_df

    def _forecast_single(
        self, years: np.ndarray, scores: np.ndarray, forecast_year: int
    ) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
        """
        Dự báo cho một chuỗi thời gian cụ thể.

        Returns:
            (predicted_score, lower_bound, upper_bound, model_name)
        """
        # Linear Regression luôn chạy được và cực kỳ nhanh, ổn định trên chuỗi thời gian ngắn
        lr_pred, lr_ci = self._linear_regression_forecast(years, scores, forecast_year)

        # Thử ARIMA nếu có đủ dữ liệu (tối thiểu 8 năm) để tránh solver không hội tụ gây chậm
        if STATSMODELS_AVAILABLE and len(scores) >= 8:
            try:
                arima_pred, arima_ci = self._arima_forecast(scores, steps=forecast_year - years[-1])
                return arima_pred, arima_ci[0], arima_ci[1], "ARIMA"
            except Exception:
                pass

        if lr_pred is not None:
            lower = lr_pred - lr_ci if lr_ci else None
            upper = lr_pred + lr_ci if lr_ci else None
            return lr_pred, lower, upper, "LinearRegression"

        return None, None, None, "N/A"

    def _linear_regression_forecast(
        self, years: np.ndarray, scores: np.ndarray, forecast_year: int
    ) -> Tuple[Optional[float], Optional[float]]:
        """Linear Regression trên chuỗi thời gian."""
        try:
            X = years.reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, scores)

            pred = model.predict([[forecast_year]])[0]

            # Ước tính CI từ residuals
            residuals = scores - model.predict(X)
            std_err = np.std(residuals)
            ci = 1.96 * std_err  # 95% CI

            return pred, ci
        except Exception as e:
            logger.debug(f"LinearRegression error: {e}")
            return None, None

    def _arima_forecast(
        self, scores: np.ndarray, steps: int = 1
    ) -> Tuple[float, Tuple[float, float]]:
        """ARIMA forecast."""
        model = ARIMA(scores, order=(1, 1, 1))
        fitted = model.fit()
        forecast = fitted.get_forecast(steps=steps)
        pred = forecast.predicted_mean.iloc[-1]
        ci = forecast.conf_int().iloc[-1]
        return pred, (ci.iloc[0], ci.iloc[1])

    def evaluate_model(self, test_split: float = 0.2) -> dict:
        """
        Đánh giá mô hình bằng cách giữ lại phần cuối để test.

        Args:
            test_split: Tỷ lệ dữ liệu dùng để test (default: 20%)

        Returns:
            Dict với MAE, RMSE, MAPE trung bình
        """
        group_cols = ["school_name", "major_name", "subject_group"]
        all_mae, all_rmse, all_mape = [], [], []

        # Lấy ngẫu nhiên tối đa 30 nhóm để đánh giá nhằm tối ưu hóa thời gian chạy trên tập dữ liệu lớn
        groups = list(self.df.groupby(group_cols))
        import random
        random.seed(42)
        random.shuffle(groups)

        evaluated_count = 0
        for _, group_df in groups:
            if evaluated_count >= 30:
                break
                
            ts = group_df.sort_values("year")[["year", "admission_score"]].dropna()
            if len(ts) < 4:
                continue

            split_idx = max(1, int(len(ts) * (1 - test_split)))
            train = ts.iloc[:split_idx]
            test = ts.iloc[split_idx:]

            pred, _, _, _ = self._forecast_single(
                train["year"].values,
                train["admission_score"].values,
                test["year"].values[-1]
            )
            if pred is None:
                continue

            actual = test["admission_score"].values[-1]
            all_mae.append(abs(pred - actual))
            all_rmse.append((pred - actual) ** 2)
            if actual != 0:
                all_mape.append(abs(pred - actual) / abs(actual) * 100)
                
            evaluated_count += 1

        metrics = {
            "MAE": round(np.mean(all_mae), 3) if all_mae else None,
            "RMSE": round(np.sqrt(np.mean(all_rmse)), 3) if all_rmse else None,
            "MAPE": round(np.mean(all_mape), 2) if all_mape else None,
            "n_evaluated": len(all_mae),
        }
        self.metrics_ = metrics
        logger.info(f"Evaluation: MAE={metrics['MAE']}, RMSE={metrics['RMSE']}, MAPE={metrics['MAPE']}%")
        return metrics

    def plot_forecast(
        self,
        school_name: str,
        major_name: str,
        subject_group: str = None,
        output_path: Path = None,
    ) -> None:
        """Vẽ biểu đồ actual vs forecast cho một cặp trường/ngành."""
        mask = (self.df["school_name"] == school_name) & (self.df["major_name"] == major_name)
        if subject_group:
            mask &= self.df["subject_group"] == subject_group

        ts = self.df[mask].sort_values("year")[["year", "admission_score"]].dropna()
        if ts.empty:
            logger.warning(f"Không có dữ liệu cho {school_name} - {major_name}")
            return

        years = ts["year"].values
        scores = ts["admission_score"].values
        forecast_year = int(years[-1]) + 1

        pred, lower, upper, model = self._forecast_single(years, scores, forecast_year)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(years, scores, "bo-", linewidth=2, markersize=8, label="Thực tế")

        if pred is not None:
            ax.plot(forecast_year, pred, "r*", markersize=15, label=f"Dự báo {forecast_year}: {pred:.2f}")
            if lower is not None and upper is not None:
                ax.fill_between([years[-1], forecast_year],
                                [scores[-1], lower],
                                [scores[-1], upper],
                                alpha=0.2, color="red", label="95% CI")
            ax.axvline(x=forecast_year - 0.5, color="gray", linestyle="--", alpha=0.5)

        ax.set_title(f"{school_name}\n{major_name} ({subject_group or 'All'})", fontsize=13)
        ax.set_xlabel("Năm")
        ax.set_ylabel("Điểm chuẩn")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        path = output_path or (IMAGES_DIR / f"forecast_{school_name[:20]}_{major_name[:20]}.png".replace(" ", "_"))
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved: {path}")

    def save_forecasts(self, output_dir: Path = None) -> Path:
        """Lưu kết quả dự báo ra CSV."""
        if self.forecasts_ is None or (isinstance(self.forecasts_, pd.DataFrame) and self.forecasts_.empty):
            logger.warning("Chưa có dự báo. Gọi forecast_all() trước.")
            return None
        output_dir = output_dir or (PROJECT_ROOT / "data" / "processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "score_forecasts.csv"
        self.forecasts_.to_csv(path, index=False, encoding="utf-8-sig")
        logger.info(f"Dự báo đã lưu: {path}")
        return path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Chạy dự báo điểm chuẩn")
    parser.add_argument("--evaluate", action="store_true", help="Đánh giá mô hình")
    args = parser.parse_args()

    processed_file = PROJECT_ROOT / "data" / "processed" / "admission_processed.csv"
    if not processed_file.exists():
        logger.error(f"Không tìm thấy file: {processed_file}")
        import sys
        sys.exit(1)
        
    df = pd.read_csv(processed_file, encoding="utf-8-sig")
    forecaster = ScoreForecaster(df)
    
    # Dự báo 2026
    logger.info("Chạy dự báo điểm chuẩn cho toàn bộ trường/ngành...")
    forecast_df = forecaster.forecast_all(forecast_year=2026)
    if not forecast_df.empty:
        forecaster.save_forecasts()
        
    # Đánh giá nếu có cờ --evaluate
    if args.evaluate:
        forecaster.evaluate_forecasting_models()
        
    # Vẽ biểu đồ mẫu cho Đại học Bách Khoa Hà Nội
    try:
        # Tìm trường bách khoa trong df
        bk_name = [name for name in df["school_name"].unique() if "Bách Khoa" in name]
        if bk_name:
            forecaster.plot_forecast(bk_name[0], "Khoa học máy tính (IT2)")
            logger.success(f"Đã vẽ biểu đồ dự báo mẫu cho {bk_name[0]}")
    except Exception as e:
        logger.warning(f"Không vẽ được biểu đồ mẫu: {e}")
        
    logger.success("Hoàn thành quy trình dự báo điểm chuẩn!")

