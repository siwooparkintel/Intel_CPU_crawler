#!/usr/bin/env python3
"""
Debug script to analyze Intel CPU page structure
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import requests
from bs4 import BeautifulSoup

def analyze_page_structure():
    """Analyze the structure of Intel's CPU specification page."""
    url = 'https://www.intel.com/content/www/us/en/products/sku/240961/intel-core-ultra-9-processor-288v-12m-cache-up-to-5-10-ghz/specifications.html'
    
    try:
        print(f"Analyzing page structure: {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("\n🔍 ANALYZING PAGE STRUCTURE:")
        
        # Find all headers
        print("\n📋 Headers found:")
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for i, header in enumerate(headers[:10]):  # Show first 10
            print(f"  {header.name}: {header.get_text(strip=True)}")
        
        # Find tables
        print(f"\n📊 Tables found: {len(soup.find_all('table'))}")
        tables = soup.find_all('table')
        for i, table in enumerate(tables[:3]):  # Show first 3
            print(f"  Table {i+1}:")
            rows = table.find_all('tr')[:3]  # First 3 rows
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    print(f"    {key}: {value}")
        
        # Find definition lists
        print(f"\n📝 Definition lists found: {len(soup.find_all('dl'))}")
        dls = soup.find_all('dl')
        for i, dl in enumerate(dls[:2]):  # Show first 2
            print(f"  DL {i+1}:")
            dt_elements = dl.find_all('dt')[:3]  # First 3 items
            dd_elements = dl.find_all('dd')[:3]
            for j, dt in enumerate(dt_elements):
                if j < len(dd_elements):
                    key = dt.get_text(strip=True)
                    value = dd_elements[j].get_text(strip=True)
                    print(f"    {key}: {value}")
        
        # Look for specification-related elements
        print("\n🔧 Specification elements:")
        spec_elements = soup.find_all(text=lambda text: text and 'specifications' in text.lower())
        for i, elem in enumerate(spec_elements[:5]):
            parent = elem.parent
            print(f"  {parent.name if parent else 'None'}: {elem.strip()[:50]}...")
        
        # Look for common Intel specification patterns
        print("\n🎯 Looking for Intel-specific patterns:")
        
        # Look for elements containing specification data
        spec_containers = soup.find_all(['div', 'section'], 
                                      attrs={'class': lambda x: x and any(word in ' '.join(x).lower() 
                                                                         for word in ['spec', 'detail', 'info'])})
        print(f"  Spec containers found: {len(spec_containers)}")
        
        # Look for data attributes (fixed)
        data_elements = soup.find_all(attrs=lambda attrs: attrs and any(key.startswith('data-') for key in attrs.keys()))
        print(f"  Elements with data attributes: {len(data_elements)}")
        
        # Sample some text content to understand structure
        print("\n📄 Sample page content (first 500 chars):")
        page_text = soup.get_text()
        print(page_text[:500].replace('\n', ' ').replace('\t', ' '))
        
        # Look for specific specification keywords
        print("\n🔍 Specification keyword analysis:")
        keywords = ['Total Cores', 'Performance-cores', 'Cache', 'Memory Types', 'GPU Name', 'NPU Name']
        for keyword in keywords:
            count = page_text.lower().count(keyword.lower())
            if count > 0:
                print(f"  '{keyword}': found {count} times")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_page_structure()