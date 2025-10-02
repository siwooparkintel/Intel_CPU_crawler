#!/usr/bin/env python3
"""
Test database with specific Intel CPU specification page
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parser import IntelCpuParser
from database_manager import PowerSpecDatabaseManager
from utils import setup_logging
import requests
from bs4 import BeautifulSoup

def test_database_with_specific_cpu():
    """Test database with detailed Intel CPU specification page."""
    setup_logging('INFO')
    
    # Use the detailed CPU spec page we know has power data
    url = 'https://www.intel.com/content/www/us/en/products/sku/240961/intel-core-ultra-9-processor-288v-12m-cache-up-to-5-10-ghz/specifications.html'
    
    print(f"🧪 Testing database with detailed CPU spec page")
    print(f"URL: {url}")
    
    try:
        # Initialize components
        parser = IntelCpuParser()
        db_manager = PowerSpecDatabaseManager()
        
        # Fetch and parse the page
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        cpu_data = parser.parse_cpu_page(soup, url)
        
        if cpu_data:
            print(f"✅ Successfully parsed: {cpu_data['name']}")
            
            # Insert into database
            success = db_manager.insert_cpu_specs(cpu_data)
            if success:
                print(f"✅ Successfully stored in database")
                
                # Get statistics
                stats = db_manager.get_power_statistics()
                print(f"\n📊 POWER STATISTICS AFTER INSERT:")
                if 'power' in stats:
                    power_stats = stats['power']
                    print(f"  CPUs with power data: {power_stats['total_cpus_with_power_data']}")
                    if power_stats['avg_base_power_w']:
                        print(f"  Average base power: {power_stats['avg_base_power_w']} W")
                        print(f"  Base power range: {power_stats['min_base_power_w']} - {power_stats['max_base_power_w']} W")
                    if power_stats['avg_turbo_power_w']:
                        print(f"  Average turbo power: {power_stats['avg_turbo_power_w']} W")
                        print(f"  Turbo power range: {power_stats['min_turbo_power_w']} - {power_stats['max_turbo_power_w']} W")
                
                # Test export for modeling
                print(f"\n📤 Testing export for modeling...")
                export_success = db_manager.export_for_modeling('test_modeling_export.json')
                if export_success:
                    print(f"✅ Successfully exported modeling data")
                
            else:
                print(f"❌ Failed to store in database (might be duplicate)")
        else:
            print(f"❌ Failed to parse CPU data")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_database_with_specific_cpu()