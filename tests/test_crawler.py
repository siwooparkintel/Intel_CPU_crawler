"""
Test utilities for Intel CPU Crawler
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestIntelCpuParser(unittest.TestCase):
    """Test cases for IntelCpuParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from parser import IntelCpuParser
        self.parser = IntelCpuParser()
    
    def test_is_cpu_url(self):
        """Test CPU URL detection."""
        # Test CPU URLs
        cpu_urls = [
            "https://intel.com/processors/core-i7",
            "https://intel.com/cpu/xeon-platinum",
            "https://intel.com/products/pentium-gold"
        ]
        
        for url in cpu_urls:
            with self.subTest(url=url):
                self.assertTrue(self.parser._is_cpu_url(url))
        
        # Test non-CPU URLs
        non_cpu_urls = [
            "https://intel.com/graphics/arc",
            "https://intel.com/support/downloads",
            "https://intel.com/about-us"
        ]
        
        for url in non_cpu_urls:
            with self.subTest(url=url):
                self.assertFalse(self.parser._is_cpu_url(url))


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from data_manager import DataManager
        import tempfile
        
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_manager = DataManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_flatten_data(self):
        """Test data flattening for CSV export."""
        test_data = [
            {
                'name': 'Intel Core i7',
                'specifications': {
                    'cores': '8',
                    'threads': '16'
                },
                'price': '$400'
            }
        ]
        
        flattened = self.data_manager._flatten_data(test_data)
        
        expected = [
            {
                'name': 'Intel Core i7',
                'specifications_cores': '8',
                'specifications_threads': '16',
                'price': '$400'
            }
        ]
        
        self.assertEqual(flattened, expected)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_validate_url(self):
        """Test URL validation."""
        from utils import validate_url
        
        # Valid URLs
        valid_urls = [
            "https://www.intel.com",
            "http://intel.com/processors",
            "https://ark.intel.com/content/www/us/en/ark.html"
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(validate_url(url))
        
        # Invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://invalid",
            "",
            None
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(validate_url(url))
    
    def test_clean_text(self):
        """Test text cleaning function."""
        from utils import clean_text
        
        test_cases = [
            ("  Multiple   spaces  ", "Multiple spaces"),
            ("Text\nwith\nnewlines", "Text with newlines"),
            ("Special@#$chars!!", "Specialchars"),
            ("", ""),
            (None, "")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = clean_text(input_text)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()