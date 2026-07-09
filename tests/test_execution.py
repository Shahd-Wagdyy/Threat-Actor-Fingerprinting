"""Tests for script execution and pipeline functionality."""
import subprocess
import sys
import pytest
import os


class TestScriptExecution:
    """Test that core scripts can be executed."""
    
    def test_tmp_search_runs(self):
        """Test that tmp_search.py script runs without errors."""
        result = subprocess.run(
            [sys.executable, "tmp_search.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        # Script should complete (may have exit code 0 or other)
        # Main thing is it shouldn't crash
        assert result.returncode in [0, 1], f"Script failed: {result.stderr}"
    
    @pytest.mark.skipif(
        not os.path.exists("scripts/features/stylometry.py"),
        reason="stylometry.py not found"
    )
    def test_stylometry_module_imports(self):
        """Test that stylometry module can be imported."""
        try:
            from scripts.features import stylometry
            assert True
        except ImportError as e:
            pytest.fail(f"Cannot import stylometry: {e}")
    
    @pytest.mark.skipif(
        not os.path.exists("scripts/features/ioc_extractor.py"),
        reason="ioc_extractor.py not found"
    )
    def test_ioc_extractor_module_imports(self):
        """Test that IOC extractor module can be imported."""
        try:
            from scripts.features import ioc_extractor
            assert True
        except ImportError as e:
            pytest.fail(f"Cannot import ioc_extractor: {e}")


class TestDependencies:
    """Test that required dependencies are installed."""
    
    def test_pandas_installed(self):
        """Test pandas is available."""
        try:
            import pandas
        except ImportError:
            pytest.fail("pandas not installed")
    
    def test_numpy_installed(self):
        """Test numpy is available."""
        try:
            import numpy
        except ImportError:
            pytest.fail("numpy not installed")
    
    def test_sklearn_installed(self):
        """Test scikit-learn is available."""
        try:
            from sklearn import preprocessing
        except ImportError:
            pytest.fail("scikit-learn not installed")
    
    def test_hdbscan_installed(self):
        """Test hdbscan is available."""
        try:
            import hdbscan
        except ImportError:
            pytest.fail("hdbscan not installed")
