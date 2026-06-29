"""
tests/test_mining.py
Unit tests cho Data Mining module (Clustering, Association Rules, Forecasting)
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mining.clustering import ClusteringAnalyzer
from src.mining.association_rules import AssociationRuleMiner
from src.mining.forecasting import ScoreForecaster


@pytest.fixture
def sample_mining_df():
    """Tạo dữ liệu điểm chuẩn logic để test các mô hình mining."""
    records = []
    schools = ["Đại học Bách khoa Hà Nội", "Đại học Ngoại thương", "Đại học Y Hà Nội"]
    majors = ["Công nghệ thông tin", "Kinh tế", "Y khoa"]
    
    # Cố định seed
    np.random.seed(42)
    
    for year in [2020, 2021, 2022, 2023, 2024, 2025]:
        for school in schools:
            for major in majors:
                # Tạo điểm có trend tăng nhẹ
                base = 25.0 if school == "Đại học Y Hà Nội" else 23.0
                score = base + (year - 2020) * 0.4 + np.random.uniform(-0.5, 0.5)
                records.append({
                    "school_name": school,
                    "major_name": major,
                    "major_group": "Kỹ thuật" if "Công nghệ" in major else "Kinh tế",
                    "subject_group": "A00" if school == "Đại học Bách khoa Hà Nội" else "D01",
                    "admission_score": round(score, 2),
                    "quota": 100,
                    "delta_score": 0.4 if year > 2020 else 0.0,
                    "score_trend": "Tăng",
                    "competition_level": "Cao",
                    "year": year
                })
    return pd.DataFrame(records)


# ================================================================
# Test Clustering (Phân cụm K-Means)
# ================================================================

class TestClusteringAnalyzer:

    def test_init(self, sample_mining_df):
        analyzer = ClusteringAnalyzer(sample_mining_df)
        assert analyzer.df is not None

    def test_cluster_schools_returns_df(self, sample_mining_df):
        analyzer = ClusteringAnalyzer(sample_mining_df)
        clustered = analyzer.cluster_schools(n_clusters=2, auto_k=False)
        assert isinstance(clustered, pd.DataFrame)
        assert "cluster" in clustered.columns
        assert clustered["cluster"].nunique() <= 2


# ================================================================
# Test Association Rules (Luật kết hợp Apriori)
# ================================================================

class TestAssociationRuleMiner:

    def test_prepare_transactions(self, sample_mining_df):
        miner = AssociationRuleMiner(sample_mining_df)
        transactions = miner._prepare_transactions()
        assert isinstance(transactions, list)
        assert len(transactions) > 0

    def test_mine_rules(self, sample_mining_df):
        miner = AssociationRuleMiner(sample_mining_df)
        rules = miner.mine_rules(min_support=0.01, min_confidence=0.1, min_lift=1.0)
        assert isinstance(rules, pd.DataFrame)
        # Các cột luật kết hợp chuẩn sau format
        if not rules.empty:
            assert "rule" in rules.columns
            assert "antecedents" in rules.columns
            assert "consequents" in rules.columns
            assert "support" in rules.columns
            assert "lift" in rules.columns


# ================================================================
# Test Forecasting (Dự báo ARIMA / Hồi quy tuyến tính)
# ================================================================

class TestScoreForecaster:

    def test_forecast_all(self, sample_mining_df):
        forecaster = ScoreForecaster(sample_mining_df)
        res = forecaster.forecast_all(forecast_year=2026, min_years=3)
        assert isinstance(res, pd.DataFrame)
        if not res.empty:
            assert "predicted_score" in res.columns
            assert "model_used" in res.columns

    def test_forecast_insufficient_data(self, sample_mining_df):
        """Nếu không đủ data points -> không sinh ra bản ghi dự báo nào."""
        # Tạo df chỉ có 1 record
        tiny_df = sample_mining_df.head(1)
        forecaster = ScoreForecaster(tiny_df)
        res = forecaster.forecast_all(forecast_year=2026, min_years=3)
        assert res.empty

    def test_evaluate_model(self, sample_mining_df):
        forecaster = ScoreForecaster(sample_mining_df)
        metrics = forecaster.evaluate_model(test_split=0.2)
        assert isinstance(metrics, dict)
        assert "MAE" in metrics
        assert "RMSE" in metrics
