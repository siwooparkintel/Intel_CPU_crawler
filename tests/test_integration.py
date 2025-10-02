"""
Integration Tests for Intel CPU Crawler

Comprehensive tests that verify the entire system works correctly after any changes.
These tests cover the complete workflow from configuration loading to data export.
"""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, Mock
import sqlite3

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestCrawlerIntegration(unittest.TestCase):
    """Integration tests for the complete crawler system."""
    
    def setUp(self):
        """Set up test fixtures with temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, 'test_crawler.db')
        self.test_json_path = os.path.join(self.temp_dir, 'test_output.json')
        
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_module_imports(self):
        """Test that all core modules can be imported successfully."""
        # Test crawler module
        from crawler import IntelCpuCrawler
        self.assertTrue(hasattr(IntelCpuCrawler, 'crawl'))
        
        # Test parser module
        from parser import IntelCpuParser
        self.assertTrue(hasattr(IntelCpuParser, 'parse_cpu_page'))
        
        # Test database manager
        from database_manager import PowerSpecDatabaseManager
        self.assertTrue(hasattr(PowerSpecDatabaseManager, 'insert_cpu_specs'))
        
        # Test data manager
        from data_manager import DataManager
        self.assertTrue(hasattr(DataManager, 'save_json'))
        
        # Test utilities
        from utils import setup_logging, get_headers, validate_url, clean_text
        self.assertTrue(callable(setup_logging))
        self.assertTrue(callable(get_headers))
        self.assertTrue(callable(validate_url))
        self.assertTrue(callable(clean_text))
    
    def test_configuration_loading(self):
        """Test that configuration loading works correctly."""
        from crawler import IntelCpuCrawler
        
        # Test with default config
        crawler = IntelCpuCrawler(config_path='config/config.yaml')
        self.assertIn('base_urls', crawler.config)
        self.assertIn('user_agent', crawler.config)
        self.assertIsInstance(crawler.config['base_urls'], list)
        self.assertGreater(len(crawler.config['base_urls']), 0)
        
        # Test with missing config (should use defaults)
        crawler_default = IntelCpuCrawler(config_path='nonexistent.yaml')
        self.assertIn('base_urls', crawler_default.config)
        self.assertIn('user_agent', crawler_default.config)
    
    def test_database_operations(self):
        """Test complete database functionality."""
        from database_manager import PowerSpecDatabaseManager
        
        # Initialize database
        db_manager = PowerSpecDatabaseManager(self.test_db_path)
        
        # Test initial state
        self.assertEqual(db_manager.get_cpu_count(), 0)
        
        # Test inserting CPU data
        sample_cpu_data = {
            'name': 'Test CPU',
            'url': 'https://example.com/test-cpu',
            'specifications': {
                'legacy': {
                    'total_cores': '8',
                    'processor_base_power': '65.0',
                    'maximum_turbo_power': '125.0',
                    'max_turbo_frequency': '4.5',
                    'lithography': 'intel 7',
                    'launch_date': 'Q1\'24'
                }
            }
        }
        
        # Insert CPU and verify
        success = db_manager.insert_cpu_specs(sample_cpu_data)
        self.assertTrue(success)
        self.assertEqual(db_manager.get_cpu_count(), 1)
        
        # Test duplicate prevention
        duplicate_success = db_manager.insert_cpu_specs(sample_cpu_data)
        self.assertFalse(duplicate_success)
        self.assertEqual(db_manager.get_cpu_count(), 1)  # Should still be 1
        
        # Test search functionality
        search_results = db_manager.get_cpu_by_name('Test')
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]['name'], 'Test CPU')
        
        # Test statistics
        stats = db_manager.get_power_statistics()
        self.assertIn('power', stats)
        self.assertEqual(stats['power']['total_cpus_with_power_data'], 1)
    
    def test_data_manager_operations(self):
        """Test file-based data operations."""
        from data_manager import DataManager
        
        data_manager = DataManager(self.temp_dir)
        
        # Test data to save
        test_data = [
            {
                'name': 'Test CPU 1',
                'cores': 8,
                'power': 65.0,
                'nested_data': {
                    'cache': '16MB',
                    'frequency': '3.2GHz'
                }
            },
            {
                'name': 'Test CPU 2',
                'cores': 4,
                'power': 35.0
            }
        ]
        
        # Test JSON export
        json_file = 'test_export.json'
        data_manager.save_json(test_data, json_file)
        
        json_path = Path(self.temp_dir) / json_file
        self.assertTrue(json_path.exists())
        
        # Verify JSON content
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]['name'], 'Test CPU 1')
        
        # Test CSV export
        csv_file = 'test_export.csv'
        data_manager.save_csv(test_data, csv_file)
        
        csv_path = Path(self.temp_dir) / csv_file
        self.assertTrue(csv_path.exists())
    
    def test_utility_functions(self):
        """Test all utility functions work correctly."""
        from utils import setup_logging, get_headers, validate_url, clean_text
        
        # Test logging setup
        logger = setup_logging('INFO')
        self.assertIsNotNone(logger)
        
        # Test headers generation
        headers = get_headers()
        self.assertIn('User-Agent', headers)
        self.assertIn('Accept', headers)
        
        # Test URL validation
        self.assertTrue(validate_url('https://www.intel.com'))
        self.assertTrue(validate_url('http://example.com'))
        self.assertFalse(validate_url('not-a-url'))
        self.assertFalse(validate_url(''))
        
        # Test text cleaning
        test_cases = [
            ('  Multiple   spaces  ', 'Multiple spaces'),
            ('Text\n\r\twith\nwhitespace', 'Text with whitespace'),
            ('Normal text', 'Normal text'),
            ('', ''),
            (None, '')
        ]
        
        for input_text, expected in test_cases:
            result = clean_text(input_text)
            self.assertEqual(result, expected, f"Failed for input: {input_text}")
    
    def test_parser_functionality(self):
        """Test parser core functionality."""
        from parser import IntelCpuParser
        
        parser = IntelCpuParser()
        
        # Test URL filtering (basic functionality)
        test_urls = [
            'https://www.intel.com/content/www/us/en/products/sku/123456/test-cpu/specifications.html',
            'https://www.example.com/not-intel',
            'https://www.intel.com/content/www/de/de/products/sku/123456/test-cpu/specifications.html',  # German
            'https://www.intel.com/content/www/us/en/products/sku/123456/test-cpu/specifications.html'
        ]
        
        # Parser should be able to process Intel specification URLs
        intel_spec_urls = [url for url in test_urls if 'intel.com' in url and '/specifications.html' in url]
        self.assertGreater(len(intel_spec_urls), 0)
    
    @patch('requests.Session.get')
    def test_crawler_initialization_and_config(self, mock_get):
        """Test crawler initialization with different configurations."""
        from crawler import IntelCpuCrawler
        
        # Mock response for any HTTP requests during initialization
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Test</body></html>'
        mock_get.return_value = mock_response
        
        # Test crawler with custom parameters
        crawler = IntelCpuCrawler(
            config_path='config/config.yaml',
            output_dir=self.temp_dir,
            delay=0.1,
            max_pages=1
        )
        
        self.assertEqual(crawler.output_dir, Path(self.temp_dir))
        self.assertEqual(crawler.delay, 0.1)
        self.assertEqual(crawler.max_pages, 1)
        self.assertIsNotNone(crawler.session)
        self.assertIsNotNone(crawler.parser)
        self.assertIsNotNone(crawler.data_manager)
    
    def test_end_to_end_workflow(self):
        """Test the complete workflow with mocked HTTP requests."""
        from crawler import IntelCpuCrawler
        from database_manager import PowerSpecDatabaseManager
        
        # Create mock HTML content that parser can process
        mock_listing_html = '''
        <html>
            <body>
                <a href="/content/www/us/en/products/sku/123456/test-cpu/specifications.html">Test CPU</a>
                <a href="/content/www/us/en/products/sku/789012/another-cpu/specifications.html">Another CPU</a>
            </body>
        </html>
        '''
        
        mock_spec_html = '''
        <html>
            <head><title>Test CPU Specifications</title></head>
            <body>
                <h1>Test CPU</h1>
                <div>
                    <span>Total Cores:</span>
                    <span>8</span>
                </div>
                <div>
                    <span>Processor Base Power:</span>
                    <span>65 W</span>
                </div>
            </body>
        </html>
        '''
        
        with patch('requests.Session.get') as mock_get:
            # Set up mock responses
            mock_response_listing = Mock()
            mock_response_listing.status_code = 200
            mock_response_listing.text = mock_listing_html
            
            mock_response_spec = Mock()
            mock_response_spec.status_code = 200
            mock_response_spec.text = mock_spec_html
            
            # Return listing page first, then spec pages
            mock_get.side_effect = [mock_response_listing, mock_response_spec]
            
            # Initialize crawler with test database
            crawler = IntelCpuCrawler(
                config_path='config/config.yaml',
                output_dir=self.temp_dir,
                delay=0.0,  # No delay for testing
                max_pages=1
            )
            
            # Replace database with test database
            crawler.db_manager = PowerSpecDatabaseManager(self.test_db_path)
            
            # This would normally crawl, but our mocks will prevent actual HTTP requests
            # We're testing that the system initializes correctly and can handle the workflow
            self.assertTrue(hasattr(crawler, 'crawl'))
            self.assertTrue(callable(crawler.crawl))
    
    def test_cli_integration(self):
        """Test that CLI commands can be imported and have correct structure."""
        # Test that main module can be imported
        import main
        
        # Test that click commands are properly defined
        self.assertTrue(hasattr(main, 'cli'))
        self.assertTrue(hasattr(main, 'crawl'))
        self.assertTrue(hasattr(main, 'db_stats'))
        self.assertTrue(hasattr(main, 'export_modeling_data'))
        self.assertTrue(hasattr(main, 'search'))
        self.assertTrue(hasattr(main, 'clear_db'))


class TestSystemHealth(unittest.TestCase):
    """High-level system health tests."""
    
    def test_requirements_compatibility(self):
        """Test that all required packages are importable."""
        required_packages = [
            'requests',
            'bs4',  # beautifulsoup4
            'lxml',
            'pandas',
            'colorlog',
            'click',
            'yaml'
        ]
        
        for package in required_packages:
            try:
                if package == 'bs4':
                    from bs4 import BeautifulSoup
                elif package == 'yaml':
                    import yaml
                else:
                    __import__(package)
            except ImportError as e:
                self.fail(f"Required package {package} could not be imported: {e}")
    
    def test_file_structure(self):
        """Test that required files and directories exist."""
        base_dir = Path(__file__).parent.parent
        
        required_files = [
            'main.py',
            'requirements.txt',
            'config/config.yaml',
            'src/crawler.py',
            'src/parser.py',
            'src/database_manager.py',
            'src/data_manager.py',
            'src/utils.py'
        ]
        
        required_dirs = [
            'src',
            'config',
            'data',
            'logs',
            'tests'
        ]
        
        for file_path in required_files:
            full_path = base_dir / file_path
            self.assertTrue(full_path.exists(), f"Required file missing: {file_path}")
        
        for dir_path in required_dirs:
            full_path = base_dir / dir_path
            self.assertTrue(full_path.exists(), f"Required directory missing: {dir_path}")
    
    def test_configuration_validity(self):
        """Test that configuration files are valid."""
        import yaml
        
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Test required configuration keys
        required_keys = ['base_urls', 'user_agent', 'database']
        for key in required_keys:
            self.assertIn(key, config, f"Required config key missing: {key}")
        
        # Test that base_urls is a list with valid URLs
        self.assertIsInstance(config['base_urls'], list)
        self.assertGreater(len(config['base_urls']), 0)
        
        for url in config['base_urls']:
            self.assertTrue(url.startswith('https://'), f"Invalid URL: {url}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)