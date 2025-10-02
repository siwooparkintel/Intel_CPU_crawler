"""
Intel CPU Crawler - Web Scraping Module

This module orchestrates the web scraping process for Intel CPU specifications.
It coordinates between URL discovery, page parsing, and data storage while
ensuring proper rate limiting and error handling.

Key Components:
    - IntelCpuCrawler: Main crawler class with database integration
    - URL filtering for US English specification pages only
    - Duplicate detection and prevention
    - Comprehensive logging and error handling
    - Rate limiting to avoid being blocked

Example:
    crawler = IntelCpuCrawler(config_path='config/config.yaml')
    results = crawler.crawl(max_pages=10)
"""

import requests
from bs4 import BeautifulSoup
import time
import yaml
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional

from parser import IntelCpuParser
from data_manager import DataManager
from database_manager import PowerSpecDatabaseManager
from utils import get_headers, handle_request_error


class IntelCpuCrawler:
    """Main crawler class for Intel CPU specifications."""
    
    def __init__(self, config_path: str = 'config/config.yaml', 
                 output_dir: str = 'data', delay: float = 1.0, 
                 max_pages: int = 10):
        """
        Initialize the Intel CPU crawler.
        
        Args:
            config_path: Path to configuration file
            output_dir: Directory to save scraped data
            delay: Delay between requests in seconds
            max_pages: Maximum number of pages to crawl
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.max_pages = max_pages
        
        # Initialize components
        self.session = self._create_session()
        self.parser = IntelCpuParser()
        self.data_manager = DataManager(self.output_dir)
        
        # Initialize database if enabled
        self.use_database = self.config.get('database', {}).get('enabled', True)
        if self.use_database:
            db_path = self.config.get('database', {}).get('path', 'data/intel_cpu_power_specs.db')
            self.db_manager = PowerSpecDatabaseManager(db_path)
            self.logger.info("Database manager initialized")
        else:
            self.db_manager = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'base_urls': [
                'https://www.intel.com/content/www/us/en/products/details/processors.html'
            ],
            'request_timeout': 30,
            'max_retries': 3,
            'user_agent': 'Intel CPU Crawler 1.0'
        }
    
    def _create_session(self) -> requests.Session:
        """Create requests session with proper configuration."""
        session = requests.Session()
        session.headers.update(get_headers(self.config.get('user_agent', 'Intel CPU Crawler 1.0')))
        return session
    
    def crawl(self) -> List[Dict[str, Any]]:
        """
        Main crawling method.
        
        Returns:
            List of CPU specification dictionaries
        """
        self.logger.info("Starting Intel CPU crawling process")
        all_cpus = []
        
        base_urls = self.config.get('base_urls', [])
        if not base_urls:
            self.logger.error("No base URLs configured")
            return []
        
        for base_url in base_urls:
            self.logger.info(f"Crawling base URL: {base_url}")
            
            try:
                # Get CPU listing pages
                cpu_urls = self._get_cpu_urls(base_url)
                self.logger.info(f"Found {len(cpu_urls)} CPU URLs to process")
                
                # Limit number of pages if specified
                if self.max_pages > 0:
                    cpu_urls = cpu_urls[:self.max_pages]
                    self.logger.info(f"Limited to {len(cpu_urls)} URLs due to max_pages setting")
                
                # Process each CPU URL
                for i, cpu_url in enumerate(cpu_urls, 1):
                    self.logger.info(f"Processing CPU {i}/{len(cpu_urls)}: {cpu_url}")
                    
                    try:
                        cpu_data = self._scrape_cpu_page(cpu_url)
                        if cpu_data:
                            all_cpus.append(cpu_data)
                            self.logger.debug(f"Successfully scraped: {cpu_data.get('name', 'Unknown CPU')}")
                            
                            # Store in database if enabled
                            if self.db_manager:
                                success = self.db_manager.insert_cpu_specs(cpu_data)
                                if success:
                                    self.logger.debug(f"Stored in database: {cpu_data.get('name')}")
                                else:
                                    self.logger.debug(f"Skipped duplicate in database: {cpu_data.get('name')}")
                        
                        # Rate limiting
                        if i < len(cpu_urls):  # Don't delay after last request
                            time.sleep(self.delay)
                            
                    except Exception as e:
                        self.logger.error(f"Error processing CPU URL {cpu_url}: {str(e)}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"Error processing base URL {base_url}: {str(e)}")
                continue
        
        self.logger.info(f"Crawling completed. Total CPUs found: {len(all_cpus)}")
        
        # Log database statistics if enabled
        if self.db_manager:
            total_in_db = self.db_manager.get_cpu_count()
            self.logger.info(f"Total CPUs in database: {total_in_db}")
        
        return all_cpus
    
    def _get_cpu_urls(self, base_url: str) -> List[str]:
        """
        Extract CPU detail page URLs from the base URL.
        
        Args:
            base_url: Base URL to scrape for CPU links
            
        Returns:
            List of CPU detail page URLs
        """
        try:
            response = self._make_request(base_url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self.parser.extract_cpu_urls(soup, base_url)
            
        except Exception as e:
            self.logger.error(f"Error getting CPU URLs from {base_url}: {str(e)}")
            return []
    
    def _scrape_cpu_page(self, cpu_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape individual CPU specification page.
        
        Args:
            cpu_url: URL of CPU specification page
            
        Returns:
            Dictionary containing CPU specifications or None if failed
        """
        try:
            response = self._make_request(cpu_url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cpu_data = self.parser.parse_cpu_page(soup, cpu_url)
            
            return cpu_data
            
        except Exception as e:
            self.logger.error(f"Error scraping CPU page {cpu_url}: {str(e)}")
            return None
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make HTTP request with error handling and retries.
        
        Args:
            url: URL to request
            
        Returns:
            Response object or None if failed
        """
        max_retries = self.config.get('max_retries', 3)
        timeout = self.config.get('request_timeout', 30)
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    handle_request_error(e, url, self.logger)
                    return None
                else:
                    self.logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def save_results(self, results: List[Dict[str, Any]], format_type: str = 'json'):
        """
        Save crawling results to file.
        
        Args:
            results: List of CPU data dictionaries
            format_type: Output format ('json', 'csv', or 'both')
        """
        if not results:
            self.logger.warning("No results to save")
            return
        
        try:
            if format_type in ['json', 'both']:
                self.data_manager.save_json(results, 'intel_cpus.json')
                self.logger.info(f"Results saved to {self.output_dir / 'intel_cpus.json'}")
            
            if format_type in ['csv', 'both']:
                self.data_manager.save_csv(results, 'intel_cpus.csv')
                self.logger.info(f"Results saved to {self.output_dir / 'intel_cpus.csv'}")
                
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            raise