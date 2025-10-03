#!/usr/bin/env python3
"""
Intel CPU Database Updater - Periodic Update Tool

This script checks Intel ARK for new processor products and automatically
adds them to the database if they don't already exist.

Usage:
    python update_database.py [--verbose] [--dry-run]
    
Options:
    --verbose    Show detailed logging
    --dry-run    Check for new products without adding to database
"""

import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crawler import IntelCpuCrawler
from database_manager import PowerSpecDatabaseManager
from utils import setup_logging


class DatabaseUpdater:
    """Manages periodic database updates with new Intel products."""
    
    def __init__(self, config_path: str = 'config/config.yaml', delay_seconds: float = 2.5):
        """Initialize the updater.
        
        Args:
            config_path: Path to configuration file
            delay_seconds: Delay between requests to avoid rate limiting
        """
        self.logger = logging.getLogger(__name__)
        self.crawler = IntelCpuCrawler(config_path=config_path)
        self.db_manager = PowerSpecDatabaseManager()
        self.delay_seconds = delay_seconds
        
    def get_existing_urls(self) -> Set[str]:
        """Get set of all URLs already in the database.
        
        Returns:
            Set of URLs
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT url FROM cpu_power_specs")
        urls = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        
        self.logger.info(f"Found {len(urls)} existing URLs in database")
        return urls
    
    def extract_family_urls_from_file(self, filepath: str = "data/all_core_processor_urls.txt") -> List[str]:
        """Extract processor family URLs from file.
        
        Args:
            filepath: Path to file containing URLs
            
        Returns:
            List of family URLs
        """
        urls = []
        
        if not Path(filepath).exists():
            self.logger.warning(f"URL file not found: {filepath}")
            return urls
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('https://'):
                    urls.append(line)
        
        self.logger.info(f"Loaded {len(urls)} processor family URLs from {filepath}")
        return urls
    
    def check_for_new_products(self, family_urls: List[str], existing_urls: Set[str]) -> Dict[str, List[str]]:
        """Check each family for new products not in database.
        
        Args:
            family_urls: List of processor family URLs to check
            existing_urls: Set of URLs already in database
            
        Returns:
            Dictionary mapping family URL to list of new product URLs
        """
        new_products = {}
        
        self.logger.info("="*80)
        self.logger.info("Checking for new products...")
        self.logger.info("="*80)
        
        for idx, family_url in enumerate(family_urls, 1):
            try:
                self.logger.info(f"[{idx}/{len(family_urls)}] Checking: {family_url}")
                
                # Get all CPU URLs from this family
                cpu_urls = self.crawler._get_cpu_urls(family_url)
                
                if cpu_urls:
                    # Find new URLs not in database
                    new_urls = [url for url in cpu_urls if url not in existing_urls]
                    
                    if new_urls:
                        new_products[family_url] = new_urls
                        self.logger.info(f"  → Found {len(new_urls)} NEW products!")
                    else:
                        self.logger.info(f"  → No new products (checked {len(cpu_urls)} CPUs)")
                else:
                    self.logger.warning(f"  → No CPUs found in family")
                
                # Delay between family checks
                if idx < len(family_urls):
                    time.sleep(self.delay_seconds)
                    
            except Exception as e:
                self.logger.error(f"  ✗ Error checking family: {e}")
                continue
        
        return new_products
    
    def add_new_products(self, new_products: Dict[str, List[str]]) -> Dict[str, Any]:
        """Add new products to the database.
        
        Args:
            new_products: Dictionary mapping family URL to list of new product URLs
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_new': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Count total new products
        for urls in new_products.values():
            stats['total_new'] += len(urls)
        
        if stats['total_new'] == 0:
            self.logger.info("No new products to add")
            return stats
        
        self.logger.info("="*80)
        self.logger.info(f"Adding {stats['total_new']} new products to database...")
        self.logger.info("="*80)
        
        overall_idx = 0
        for family_url, cpu_urls in new_products.items():
            self.logger.info(f"\nProcessing family: {family_url}")
            self.logger.info(f"  New products: {len(cpu_urls)}")
            
            for cpu_url in cpu_urls:
                overall_idx += 1
                try:
                    self.logger.info(f"  [{overall_idx}/{stats['total_new']}] Crawling: {cpu_url}")
                    
                    # Parse the CPU page
                    cpu_data = self.crawler._scrape_cpu_page(cpu_url)
                    
                    if cpu_data:
                        # Save to database
                        success = self.db_manager.insert_cpu_specs(cpu_data)
                        
                        if success:
                            stats['successful'] += 1
                            self.logger.info(f"    ✓ Added: {cpu_data.get('name', 'Unknown')}")
                        else:
                            stats['skipped'] += 1
                            self.logger.warning(f"    ⊘ Skipped (already exists)")
                    else:
                        stats['failed'] += 1
                        self.logger.warning(f"    ✗ Failed to extract data")
                    
                    # Delay between requests
                    if overall_idx < stats['total_new']:
                        time.sleep(self.delay_seconds)
                        
                except Exception as e:
                    stats['failed'] += 1
                    self.logger.error(f"    ✗ Error: {e}")
        
        return stats
    
    def run_update(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run the update process.
        
        Args:
            dry_run: If True, only check for new products without adding
            
        Returns:
            Dictionary with update statistics
        """
        start_time = datetime.now()
        
        self.logger.info("="*80)
        self.logger.info("Intel CPU Database Updater")
        self.logger.info("="*80)
        self.logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Mode: {'DRY RUN (check only)' if dry_run else 'LIVE UPDATE'}")
        self.logger.info("="*80)
        
        # Get initial database count
        initial_count = self.db_manager.get_cpu_count()
        self.logger.info(f"Current database count: {initial_count} CPUs")
        
        # Get existing URLs
        existing_urls = self.get_existing_urls()
        
        # Load family URLs
        family_urls = self.extract_family_urls_from_file()
        
        if not family_urls:
            self.logger.error("No family URLs found. Please ensure data/all_core_processor_urls.txt exists.")
            return {'error': 'No family URLs found'}
        
        # Check for new products
        new_products = self.check_for_new_products(family_urls, existing_urls)
        
        # Count total new products
        total_new = sum(len(urls) for urls in new_products.values())
        
        self.logger.info("="*80)
        self.logger.info(f"Discovery Summary: Found {total_new} new products across {len(new_products)} families")
        self.logger.info("="*80)
        
        if total_new == 0:
            self.logger.info("✓ Database is up to date! No new products found.")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'initial_count': initial_count,
                'final_count': initial_count,
                'families_checked': len(family_urls),
                'new_products_found': 0,
                'products_added': 0,
                'duration_seconds': duration,
                'dry_run': dry_run
            }
        
        # Show new products by family
        for family_url, cpu_urls in new_products.items():
            family_name = family_url.split('/')[-1].replace('.html', '').replace('-', ' ').title()
            self.logger.info(f"\n{family_name}: {len(cpu_urls)} new products")
            for url in cpu_urls[:3]:  # Show first 3
                product_name = url.split('/')[-2]
                self.logger.info(f"  - {product_name}")
            if len(cpu_urls) > 3:
                self.logger.info(f"  ... and {len(cpu_urls) - 3} more")
        
        # Add new products (unless dry run)
        stats = {'successful': 0, 'failed': 0, 'skipped': 0}
        
        if not dry_run:
            stats = self.add_new_products(new_products)
        else:
            self.logger.info("\n" + "="*80)
            self.logger.info("DRY RUN MODE - Products not added to database")
            self.logger.info("="*80)
        
        # Get final database count
        final_count = self.db_manager.get_cpu_count()
        
        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print final summary
        self.logger.info("\n" + "="*80)
        self.logger.info("Update Complete!")
        self.logger.info("="*80)
        self.logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        self.logger.info(f"Families checked: {len(family_urls)}")
        self.logger.info(f"New products found: {total_new}")
        
        if not dry_run:
            self.logger.info(f"Products successfully added: {stats['successful']}")
            self.logger.info(f"Products failed: {stats['failed']}")
            self.logger.info(f"Products skipped: {stats['skipped']}")
            self.logger.info(f"Database before: {initial_count} CPUs")
            self.logger.info(f"Database after: {final_count} CPUs")
            self.logger.info(f"Net change: +{final_count - initial_count} CPUs")
        
        self.logger.info("="*80)
        
        return {
            'initial_count': initial_count,
            'final_count': final_count,
            'families_checked': len(family_urls),
            'new_products_found': total_new,
            'products_added': stats['successful'],
            'products_failed': stats['failed'],
            'products_skipped': stats['skipped'],
            'duration_seconds': duration,
            'dry_run': dry_run
        }


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Intel CPU Database Updater - Check for and add new products'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Check for new products without adding to database'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=2.5,
        help='Delay in seconds between requests (default: 2.5)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logging(log_level)
    
    # Run updater
    updater = DatabaseUpdater(delay_seconds=args.delay)
    results = updater.run_update(dry_run=args.dry_run)
    
    # Exit with appropriate code
    if 'error' in results:
        sys.exit(1)
    elif results.get('new_products_found', 0) > 0 and not args.dry_run:
        if results.get('products_failed', 0) > 0:
            sys.exit(2)  # Some failures
        else:
            sys.exit(0)  # Success
    else:
        sys.exit(0)  # No updates needed or dry run


if __name__ == "__main__":
    main()
