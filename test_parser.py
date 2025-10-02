#!/usr/bin/env python3
"""
Test script for enhanced Intel CPU parser
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parser import IntelCpuParser
import requests
from bs4 import BeautifulSoup
import json

def test_enhanced_parser():
    """Test the enhanced parser with a real Intel CPU spec page."""
    url = 'https://www.intel.com/content/www/us/en/products/sku/240961/intel-core-ultra-9-processor-288v-12m-cache-up-to-5-10-ghz/specifications.html'
    parser = IntelCpuParser()

    try:
        print(f"Testing enhanced parser with URL: {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        cpu_data = parser.parse_cpu_page(soup, url)
        
        if cpu_data:
            print('✅ Successfully parsed CPU data!')
            print(f'CPU Name: {cpu_data.get("name", "Unknown")}')
            
            specs = cpu_data.get('specifications', {})
            print(f'Specification categories found: {list(specs.keys())}')
            
            # Show detailed breakdown
            for category, category_specs in specs.items():
                if isinstance(category_specs, dict) and category_specs:
                    print(f'\n📋 {category.upper().replace("_", " ")}:')
                    for key, value in list(category_specs.items())[:5]:  # Show first 5 items
                        print(f'  • {key}: {value}')
                    if len(category_specs) > 5:
                        print(f'  ... and {len(category_specs) - 5} more items')
            
            total_specs = sum(len(section) if isinstance(section, dict) else 1 for section in specs.values())
            print(f'\n📊 Total specifications extracted: {total_specs}')
            
            # Save detailed output to file
            with open('test_parser_output.json', 'w', encoding='utf-8') as f:
                json.dump(cpu_data, f, indent=2, ensure_ascii=False)
            print('💾 Detailed output saved to test_parser_output.json')
            
        else:
            print('❌ Failed to parse CPU data')
            
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_enhanced_parser()