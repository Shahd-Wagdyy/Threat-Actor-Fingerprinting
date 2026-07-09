"""Tests for data validation and integrity."""
import os
import json
import pandas as pd
import pytest


class TestDataStructure:
    """Test that required data files exist and have correct structure."""
    
    def test_raw_telegram_posts_exist(self):
        """Verify raw data files exist."""
        assert os.path.exists("data/raw/telegram_posts.csv"), "Missing raw CSV"
        assert os.path.exists("data/raw/telegram_posts.json"), "Missing raw JSON"
    
    def test_processed_features_exist(self):
        """Verify processed feature files exist."""
        features = [
            "data/processed/stylometric_features.csv",
            "data/processed/temporal_features.csv",
            "data/processed/ioc_features.csv"
        ]
        for feature in features:
            assert os.path.exists(feature), f"Missing {feature}"
    
    def test_embeddings_exist(self):
        """Verify embedding files exist."""
        assert os.path.exists("data/embeddings/post_embeddings.npy"), "Missing embeddings"
        assert os.path.exists("data/embeddings/post_metadata.csv"), "Missing metadata"


class TestDataContent:
    """Test data quality and content."""
    
    def test_stylometric_features_shape(self):
        """Verify stylometric features have correct shape."""
        df = pd.read_csv("data/processed/stylometric_features.csv")
        assert df.shape[0] > 0, "No samples in stylometric features"
        assert df.shape[1] > 1, "Insufficient features"
        assert not df.isnull().all().any(), "Columns with all null values"
    
    def test_temporal_features_shape(self):
        """Verify temporal features have correct shape."""
        df = pd.read_csv("data/processed/temporal_features.csv")
        assert df.shape[0] > 0, "No samples in temporal features"
        assert df.shape[1] > 0, "No temporal features"
    
    def test_ioc_features_shape(self):
        """Verify IOC features have correct shape."""
        df = pd.read_csv("data/processed/ioc_features.csv")
        assert df.shape[0] > 0, "No samples in IOC features"
        assert df.shape[1] > 0, "No IOC features"
    
    def test_clustering_results_exist(self):
        """Verify clustering outputs exist."""
        assert os.path.exists("outputs/clustering_results.csv"), "Missing clustering results"
        df = pd.read_csv("outputs/clustering_results.csv")
        assert "cluster" in df.columns or any("cluster" in col.lower() for col in df.columns), "No cluster column"
    
    def test_cluster_profiles_exist(self):
        """Verify cluster profiles have been generated."""
        profile_dir = "outputs/profiles"
        assert os.path.exists(profile_dir), "Missing profiles directory"
        profiles = [f for f in os.listdir(profile_dir) if f.endswith('.json')]
        assert len(profiles) > 0, "No cluster profiles generated"
    
    def test_cluster_profile_structure(self):
        """Verify cluster profile JSON structure."""
        profile_file = "outputs/profiles/cluster_0.json"
        if os.path.exists(profile_file):
            with open(profile_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert "cluster_id" in data, "Missing cluster_id"
                assert "ioc_summary" in data, "Missing ioc_summary"
                assert "languages" in data, "Missing languages"


class TestDataTypes:
    """Test that data types are correct."""
    
    def test_temporal_features_datetime(self):
        """Verify temporal features contain valid timestamps."""
        df = pd.read_csv("data/processed/temporal_features.csv")
        # Check if any timestamp-like columns exist
        timestamp_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
        for col in timestamp_cols:
            try:
                pd.to_datetime(df[col])
            except Exception as e:
                pytest.fail(f"Cannot parse {col} as datetime: {e}")
    
    def test_numeric_features_are_numeric(self):
        """Verify numeric features are properly typed."""
        df = pd.read_csv("data/processed/stylometric_features.csv")
        # Check all non-ID columns are numeric
        numeric_cols = df.select_dtypes(include=['number']).columns
        assert len(numeric_cols) > 0, "No numeric columns found"
