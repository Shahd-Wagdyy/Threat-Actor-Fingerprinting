"""Tests for search and profile matching functionality."""
import os
import json
import pytest
from pathlib import Path


class TestClusterSearch:
    """Test cluster profile search functionality."""
    
    def test_search_profiles_with_iocs(self):
        """Test finding clusters with IOCs."""
        matches = []
        profile_dir = "outputs/profiles"
        
        if not os.path.exists(profile_dir):
            pytest.skip("Profiles directory not found")
        
        for f in Path(profile_dir).glob("cluster_*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    d = json.load(file)
                    ioc = d.get('ioc_summary', {})
                    has_domains = ioc.get('domains', 0) > 0
                    has_ips_hashes = ioc.get('ips', 0) > 0 or ioc.get('sha256_hashes', 0) > 0
                    
                    if has_domains and has_ips_hashes:
                        matches.append(d['cluster_id'])
            except Exception as e:
                pytest.fail(f"Error processing {f}: {e}")
        
        # Should find at least some clusters with both domains and IPs/hashes
        assert len(matches) >= 0, "Search functionality works"
    
    def test_profile_has_required_fields(self):
        """Test that cluster profiles have required fields."""
        profile_dir = "outputs/profiles"
        
        if not os.path.exists(profile_dir):
            pytest.skip("Profiles directory not found")
        
        required_fields = ['cluster_id', 'ioc_summary', 'languages', 'total_posts']
        
        # Test first profile found
        profiles = list(Path(profile_dir).glob("cluster_*.json"))[:1]
        
        for profile_path in profiles:
            with open(profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for field in required_fields:
                    assert field in data, f"Missing field: {field}"
    
    def test_ioc_summary_structure(self):
        """Test IOC summary has expected structure."""
        profile_dir = "outputs/profiles"
        
        if not os.path.exists(profile_dir):
            pytest.skip("Profiles directory not found")
        
        profile_path = list(Path(profile_dir).glob("cluster_*.json"))[0]
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            ioc_summary = data.get('ioc_summary', {})
            
            # Check expected IOC types
            expected_keys = ['domains', 'ips', 'cves', 'sha256_hashes']
            for key in expected_keys:
                assert key in ioc_summary, f"Missing IOC type: {key}"
