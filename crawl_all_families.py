#!/usr/bin/env python3
"""
Crawl all processor families from all_core_processor_urls.txt
with a configurable delay between requests.
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crawler import IntelCpuCrawler
from database_manager import PowerSpecDatabaseManager
from utils import setup_logging

def extract_urls_from_file(filepath: str) -> list:
    """Extract all URLs from the processor families file."""
    urls = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('https://'):
                urls.append(line)
    return urls

def main():
    """Main execution function."""
    # Setup logger
    logger = setup_logging('INFO')
    
    # Configuration
    urls_file = "data/all_core_processor_urls.txt"
    delay_seconds = 2.5
    
    logger.info("="*80)
    logger.info("Intel CPU Crawler - Mass Collection Mode")
    logger.info("="*80)
    
    # Extract URLs
    logger.info(f"Reading URLs from: {urls_file}")
    urls = extract_urls_from_file(urls_file)
    logger.info(f"Found {len(urls)} processor family URLs")
    
    if not urls:
        logger.error("No URLs found in file!")
        return
    
    # Initialize components
    logger.info("Initializing crawler and database...")
    crawler = IntelCpuCrawler()
    db_manager = PowerSpecDatabaseManager()
    
    # Get initial stats
    initial_count = db_manager.get_cpu_count()
    logger.info(f"Database currently contains {initial_count} CPUs")
    
    # Process each family URL
    success_count = 0
    fail_count = 0
    total_cpus_found = 0
    
    logger.info("="*80)
    logger.info(f"Starting crawl with {delay_seconds}s delay between family pages")
    logger.info("="*80)
    
    for idx, family_url in enumerate(urls, 1):
        try:
            logger.info(f"\n[{idx}/{len(urls)}] Processing family: {family_url}")
            
            # Get CPU URLs from the family page
            cpu_urls = crawler._get_cpu_urls(family_url)
            
            if cpu_urls:
                logger.info(f"  → Found {len(cpu_urls)} CPUs in this family")
                total_cpus_found += len(cpu_urls)
                
                # Crawl each CPU with delay
                for cpu_idx, cpu_url in enumerate(cpu_urls, 1):
                    try:
                        logger.info(f"    [{cpu_idx}/{len(cpu_urls)}] Crawling: {cpu_url}")
                        
                        # Parse the CPU page
                        cpu_data = crawler._scrape_cpu_page(cpu_url)
                        
                        if cpu_data:
                            # Save to database
                            db_manager.insert_cpu_specs(cpu_data)
                            logger.info(f"    ✓ Saved: {cpu_data.get('processor_name', 'Unknown')}")
                        else:
                            logger.warning(f"    ✗ No data extracted from {cpu_url}")
                            
                        # Delay between CPU pages (within same family)
                        if cpu_idx < len(cpu_urls):
                            time.sleep(delay_seconds)
                            
                    except Exception as e:
                        logger.error(f"    ✗ Error crawling CPU {cpu_url}: {e}")
                        fail_count += 1
                
                success_count += 1
            else:
                logger.warning(f"  → No CPUs found in family")
                fail_count += 1
            
            # Delay between family pages
            if idx < len(urls):
                logger.info(f"  Waiting {delay_seconds}s before next family...")
                time.sleep(delay_seconds)
                
        except Exception as e:
            logger.error(f"  ✗ Error processing family {family_url}: {e}")
            fail_count += 1
            
            # Still wait before next family
            if idx < len(urls):
                time.sleep(delay_seconds)
    
    # Final statistics
    final_count = db_manager.get_cpu_count()
    new_cpus = final_count - initial_count
    
    logger.info("="*80)
    logger.info("Crawl Complete!")
    logger.info("="*80)
    logger.info(f"Families processed: {success_count}/{len(urls)}")
    logger.info(f"Total CPUs discovered: {total_cpus_found}")
    logger.info(f"New CPUs added to database: {new_cpus}")
    logger.info(f"Database total: {final_count} CPUs")
    logger.info(f"Failed families: {fail_count}")
    logger.info("="*80)

if __name__ == "__main__":
    main()
