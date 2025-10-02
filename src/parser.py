"""
Intel CPU Parser - HTML parsing utilities
Handles parsing of Intel CPU specification pages.
"""

from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from utils import normalize_unicode_text


class IntelCpuParser:
    """Parser for Intel CPU specification pages."""
    
    def __init__(self):
        """Initialize the parser."""
        self.logger = logging.getLogger(__name__)
    
    def extract_cpu_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract CPU detail page URLs from product listing page.
        
        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of CPU detail page URLs
        """
        cpu_urls = []
        
        try:
            # Priority 1: Look for CPU SKU specification pages (most detailed)
            sku_links = soup.find_all('a', href=re.compile(r'/sku/\d+/.*specifications\.html'))
            cpu_links = sku_links
            
            # Priority 2: Look for general CPU specification links
            spec_links = soup.find_all('a', href=re.compile(r'specifications\.html'))
            cpu_links.extend(spec_links)
            
            # Priority 3: Look for product SKU pages
            product_sku_links = soup.find_all('a', href=re.compile(r'/products/sku/'))
            cpu_links.extend(product_sku_links)
            
            # Priority 4: Traditional CPU product links (as fallback)
            traditional_cpu_links = soup.find_all('a', href=re.compile(r'/processors/|/cpu/'))
            cpu_links.extend(traditional_cpu_links)
            
            # Priority 5: Links with CPU-related text (but filter heavily)
            cpu_text_links = soup.find_all('a', string=re.compile(r'Intel.*(?:Core|Xeon|Pentium|Celeron)', re.I))
            cpu_links.extend(cpu_text_links)
            
            # Look for "View Specifications" or "View Details" type links
            spec_button_links = soup.find_all('a', string=re.compile(r'(?:view|see)\s+(?:specifications|specs|details)', re.I))
            cpu_links.extend(spec_button_links)
            
            # Look for links in specification tables or product cards
            spec_table_links = soup.select('table a[href*="specifications"], .product-card a[href*="sku"], .cpu-list a[href*="specifications"]')
            cpu_links.extend(spec_table_links)
            
            for link in cpu_links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    
                    # Filter for CPU-related URLs (now includes US English check)
                    if self._is_cpu_url(full_url):
                        cpu_urls.append(full_url)
            
            # Remove duplicates while preserving order
            cpu_urls = list(dict.fromkeys(cpu_urls))
            
            # Try to find more specification URLs from the page content
            additional_urls = self._find_specification_urls(soup, base_url)
            cpu_urls.extend(additional_urls)
            
            # Final deduplication
            cpu_urls = list(dict.fromkeys(cpu_urls))
            
            # Prioritize specification pages over promotional pages
            spec_urls = [url for url in cpu_urls if 'specifications.html' in url or '/sku/' in url]
            other_urls = [url for url in cpu_urls if 'specifications.html' not in url and '/sku/' not in url]
            
            # Return specification URLs first, then others
            final_urls = spec_urls + other_urls
            
            # Log filtering results
            self.logger.debug(f"Found {len(spec_urls)} specification URLs and {len(other_urls)} other CPU URLs")
            self.logger.debug(f"Found {len(final_urls)} total US English CPU URLs out of {len(cpu_links)} total links")
            
            return final_urls
            
        except Exception as e:
            self.logger.error(f"Error extracting CPU URLs: {str(e)}")
            return []
    
    def _is_cpu_url(self, url: str) -> bool:
        """
        Check if URL appears to be a CPU specification page and is US English.
        Focus on actual CPU spec pages, not promotional content.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be a US English CPU specification page
        """
        # First check if it's a US English page
        if not self._is_us_english_url(url):
            return False
        
        url_lower = url.lower()
        
        # Priority 1: Actual CPU specification pages (SKU pages)
        if '/sku/' in url_lower and 'specifications.html' in url_lower:
            return True
        
        # Priority 2: Product detail pages with specifications
        if '/products/sku/' in url_lower:
            return True
        
        # Priority 3: Direct specification pages
        if 'specifications.html' in url_lower and any(cpu in url_lower for cpu in ['core', 'xeon', 'pentium', 'celeron', 'atom']):
            return True
        
        # Exclude promotional/marketing pages
        marketing_excludes = [
            '/products/details/processors.html',  # General processor pages
            '/products/details/processors/core.html',  # Core family page
            '/products/details/processors/xeon.html',  # Xeon family page
            '/products/details/processors/atom.html',  # Atom family page
            '/products/overview.html',  # Overview pages
            '/processors/processor-numbers.html',  # General info pages
            '/products/docs/',  # Documentation pages
            'where-to-buy',  # Purchase pages
            'ai-pc',  # AI PC promotional pages
            '/edge.html',  # Edge computing pages
            '14th-gen.html'  # Generation overview pages
        ]
        
        # Exclude known promotional/marketing pages
        for exclude in marketing_excludes:
            if exclude in url_lower:
                return False
        
        # Only allow specific CPU specification patterns
        cpu_spec_patterns = [
            r'/sku/\d+/',  # SKU-based URLs
            r'specifications\.html',  # Direct spec pages
            r'/products/sku/'  # Product SKU pages
        ]
        
        # Check if URL matches any specification pattern
        for pattern in cpu_spec_patterns:
            if re.search(pattern, url_lower):
                # Additional validation for CPU-related content
                cpu_indicators = ['core', 'xeon', 'pentium', 'celeron', 'atom', 'processor']
                if any(indicator in url_lower for indicator in cpu_indicators):
                    return True
        
        # Reject everything else (promotional pages, family pages, etc.)
        return False
    
    def _is_us_english_url(self, url: str) -> bool:
        """
        Check if URL is a US English Intel page.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL contains /us/en/ path
        """
        return '/us/en/' in url.lower() and 'intel.com' in url.lower()
    
    def _find_specification_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find CPU specification URLs from page content using various methods.
        
        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of CPU specification URLs
        """
        spec_urls = []
        
        try:
            # Method 1: Look for JavaScript-generated URLs in script tags
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Look for URLs in JavaScript
                    url_matches = re.findall(r'["\']([^"\']*(?:sku|specifications)[^"\']*)["\']', script.string)
                    for match in url_matches:
                        if '/us/en/' in match and ('sku' in match or 'specifications' in match):
                            full_url = urljoin(base_url, match)
                            spec_urls.append(full_url)
            
            # Method 2: Look in data attributes
            data_links = soup.find_all(attrs={'data-url': re.compile(r'.*(?:sku|specifications).*')})
            for element in data_links:
                data_url = element.get('data-url')
                if data_url:
                    full_url = urljoin(base_url, data_url)
                    if self._is_us_english_url(full_url):
                        spec_urls.append(full_url)
            
            # Method 3: Look for hidden form inputs with URLs
            hidden_inputs = soup.find_all('input', type='hidden')
            for inp in hidden_inputs:
                value = inp.get('value', '')
                if 'specifications' in value or 'sku' in value:
                    if value.startswith('http') and self._is_us_english_url(value):
                        spec_urls.append(value)
                    elif value.startswith('/'):
                        full_url = urljoin(base_url, value)
                        if self._is_us_english_url(full_url):
                            spec_urls.append(full_url)
            
            # Method 4: Look in JSON-LD structured data
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                if script.string:
                    try:
                        import json
                        data = json.loads(script.string)
                        # Recursively search for URLs in the JSON data
                        urls = self._extract_urls_from_json(data)
                        for url in urls:
                            if ('sku' in url or 'specifications' in url) and self._is_us_english_url(url):
                                spec_urls.append(url)
                    except (json.JSONDecodeError, Exception):
                        pass
        
        except Exception as e:
            self.logger.debug(f"Error finding specification URLs: {str(e)}")
        
        return list(set(spec_urls))  # Remove duplicates
    
    def _extract_urls_from_json(self, data) -> List[str]:
        """Recursively extract URLs from JSON data."""
        urls = []
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, str) and ('http' in value or value.startswith('/')):
                    if 'sku' in value or 'specifications' in value:
                        urls.append(value)
                else:
                    urls.extend(self._extract_urls_from_json(value))
        elif isinstance(data, list):
            for item in data:
                urls.extend(self._extract_urls_from_json(item))
        return urls
    
    def parse_cpu_page(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """
        Parse individual CPU specification page.
        
        Args:
            soup: BeautifulSoup object of the CPU page
            url: URL of the page
            
        Returns:
            Dictionary containing CPU specifications
        """
        try:
            # Extract CPU name with URL context
            cpu_name = self._extract_cpu_name_with_url(soup, url)
            # Normalize Unicode characters in CPU name
            cpu_name = normalize_unicode_text(cpu_name)
            
            cpu_data = {
                'url': url,
                'name': cpu_name,
                'specifications': self._extract_specifications(soup),
                'price': self._extract_price(soup),
                'availability': self._extract_availability(soup),
                'description': self._extract_description(soup)
            }
            
            # Add timestamp
            from datetime import datetime
            cpu_data['scraped_at'] = datetime.now().isoformat()
            
            return cpu_data
            
        except Exception as e:
            self.logger.error(f"Error parsing CPU page {url}: {str(e)}")
            return None
    
    def _extract_cpu_name_with_url(self, soup: BeautifulSoup, url: str) -> str:
        """Extract CPU name with URL context for better accuracy."""
        
        # First try the existing strategies
        name = self._extract_cpu_name(soup)
        if name != "Unknown CPU":
            return name
        
        # Fallback: extract from URL
        try:
            from urllib.parse import unquote
            
            # Intel URLs often contain the CPU name
            # Example: /intel-core-ultra-9-processor-288v-12m-cache-up-to-5-10-ghz/
            url_parts = unquote(url).split('/')
            
            for part in url_parts:
                if 'intel' in part.lower() and ('core' in part.lower() or 'xeon' in part.lower()):
                    # Convert URL slug to readable name
                    name_from_url = part.replace('-', ' ')
                    # Capitalize appropriately
                    words = name_from_url.split()
                    formatted_words = []
                    
                    for word in words:
                        if word.lower() in ['intel', 'core', 'xeon', 'processor']:
                            formatted_words.append(word.capitalize())
                        elif word.lower().startswith('i') and word[1:].isdigit():
                            formatted_words.append(f"i{word[1:]}")  # i7, i9, etc.
                        elif word.isdigit() or (word.endswith('v') and word[:-1].isdigit()):
                            formatted_words.append(word.upper())  # 288V, etc.
                        else:
                            formatted_words.append(word.capitalize())
                    
                    formatted_name = ' '.join(formatted_words)
                    if len(formatted_name) > 10:
                        return formatted_name
        
        except Exception as e:
            self.logger.debug(f"Error extracting name from URL: {str(e)}")
        
        return "Unknown CPU"
    
    def _extract_cpu_name(self, soup: BeautifulSoup) -> str:
        """Extract CPU name from Intel's specification pages."""
        
        # Try multiple strategies to find the CPU name
        strategies = [
            self._extract_name_from_title,
            self._extract_name_from_headers,
            self._extract_name_from_meta,
            self._extract_name_from_breadcrumbs,
            self._extract_name_from_url
        ]
        
        for strategy in strategies:
            try:
                name = strategy(soup)
                if name and len(name) > 5 and 'intel' in name.lower():
                    return name
            except Exception as e:
                self.logger.debug(f"Name extraction strategy failed: {str(e)}")
                continue
        
        return "Unknown CPU"
    
    def _extract_name_from_title(self, soup: BeautifulSoup) -> str:
        """Extract name from page title."""
        title = soup.find('title')
        if title:
            title_text = title.get_text(strip=True)
            # Intel pages often have the CPU name at the start of title
            if 'intel' in title_text.lower():
                # Extract the CPU name part (before specifications)
                name_part = title_text.split('|')[0].strip()
                # Don't split on hyphen for processor names (i5-110, i7-1234U, etc.)
                # Only remove specification-related suffixes
                name_part = re.sub(r'\s*-\s*specifications.*$', '', name_part, flags=re.IGNORECASE)
                name_part = re.sub(r'\s*specs.*$', '', name_part, flags=re.IGNORECASE)
                if len(name_part) > 10:  # Reasonable length check
                    return name_part
        return None
    
    def _extract_name_from_headers(self, soup: BeautifulSoup) -> str:
        """Extract name from page headers."""
        header_selectors = [
            'h1.pdp-product-name',
            'h1[data-testid="product-name"]',
            '.product-title h1',
            'h1.page-title',
            '.product-header h1',
            '.specification-header h1',
            'h1',
            'h2'
        ]
        
        for selector in header_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and 'intel' in text.lower() and ('core' in text.lower() or 'xeon' in text.lower() or 'processor' in text.lower()):
                    # Clean up common suffixes
                    text = re.sub(r'\s*-\s*specifications.*$', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'\s*specs.*$', '', text, flags=re.IGNORECASE)
                    return text
        
        return None
    
    def _extract_name_from_meta(self, soup: BeautifulSoup) -> str:
        """Extract name from meta tags."""
        meta_selectors = [
            'meta[property="og:title"]',
            'meta[name="title"]',
            'meta[name="description"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                content = meta.get('content')
                if 'intel' in content.lower() and ('core' in content.lower() or 'xeon' in content.lower()):
                    # Extract the processor name part
                    match = re.match(r'(Intel.*?(?:Core|Xeon).*?)(?:\s*[-|]|$)', content, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
        
        return None
    
    def _extract_name_from_breadcrumbs(self, soup: BeautifulSoup) -> str:
        """Extract name from breadcrumb navigation."""
        breadcrumb_selectors = [
            '.breadcrumbs',
            '.breadcrumb',
            'nav[aria-label="breadcrumb"]',
            '[role="navigation"]'
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumb = soup.select_one(selector)
            if breadcrumb:
                links = breadcrumb.find_all('a')
                for link in reversed(links):  # Check from end (most specific)
                    text = link.get_text(strip=True)
                    if text and 'intel' in text.lower() and len(text) > 10:
                        return text
        
        return None
    
    def _extract_name_from_url(self, soup: BeautifulSoup) -> str:
        """Extract name from URL structure (fallback)."""
        try:
            # This would need the URL to be passed, which we have in parse_cpu_page
            # For now, return None as this is a fallback method
            return None
        except Exception:
            return None
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract comprehensive CPU specifications from Intel's detailed spec pages."""
        specs = {
            'essentials': {},
            'cpu_specifications': {},
            'memory_specifications': {},
            'gpu_specifications': {},
            'npu_specifications': {},
            'expansion_options': {},
            'package_specifications': {},
            'advanced_technologies': {},
            'security_reliability': {},
            'supplemental_information': {}
        }
        
        try:
            # Extract specifications from structured sections
            specs.update(self._extract_section_specifications(soup))
            
            # Extract from modern tech-section-row structure (newer Intel pages)
            tech_row_specs = self._extract_tech_section_row_specifications(soup)
            
            # Merge tech-row specs into appropriate categories
            for key, value in tech_row_specs.items():
                category = self._categorize_specification(key)
                if category not in specs:
                    specs[category] = {}
                specs[category][key] = value
            
            # Extract from tables and key-value pairs (fallback method)
            table_specs = self._extract_table_specifications(soup)
            
            # Merge table specs into appropriate categories
            for key, value in table_specs.items():
                # Try to categorize unknown specs
                category = self._categorize_specification(key)
                if category not in specs:
                    specs[category] = {}
                specs[category][key] = value
            
            # Extract legacy format for backward compatibility
            legacy_specs = self._extract_legacy_specifications(soup)
            if legacy_specs:
                # Categorize legacy specs into proper sections instead of keeping in legacy
                categorized_legacy = self._categorize_legacy_specifications(legacy_specs)
                for category, category_specs in categorized_legacy.items():
                    if category not in specs:
                        specs[category] = {}
                    specs[category].update(category_specs)
                
                # Keep only uncategorized specs in legacy
                uncategorized = {k: v for k, v in legacy_specs.items() 
                               if not any(k in cat_specs for cat_specs in categorized_legacy.values())}
                if uncategorized:
                    specs['legacy'] = uncategorized
            
        except Exception as e:
            self.logger.error(f"Error extracting specifications: {str(e)}")
        
        # Normalize Unicode in all specification values
        specs = self._normalize_specification_unicode(specs)
        
        return specs
    
    def _extract_tech_section_row_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from modern Intel pages using tech-section-row structure."""
        specs = {}
        
        try:
            # Find all rows with tech-section-row class (modern Intel page structure)
            rows = soup.find_all('div', class_='tech-section-row')
            
            for row in rows:
                # Find label and data divs
                label_div = row.find('div', class_='tech-label')
                data_div = row.find('div', class_='tech-data')
                
                if label_div and data_div:
                    key = label_div.get_text(strip=True)
                    value = data_div.get_text(strip=True)
                    
                    if key and value:
                        # Clean the key (remove footnote markers like ‡, †, etc.)
                        clean_key = self._clean_specification_key(key)
                        specs[clean_key] = value
                        self.logger.debug(f"Extracted from tech-section-row: {clean_key} = {value}")
        
        except Exception as e:
            self.logger.error(f"Error extracting tech-section-row specifications: {str(e)}")
        
        return specs
    
    def _extract_section_specifications(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """Extract specifications from Intel's structured sections."""
        sections = {}
        
        # Define section mappings
        section_mappings = {
            'essentials': ['essentials', 'essential'],
            'cpu_specifications': ['cpu specifications', 'processor specifications'],
            'memory_specifications': ['memory specifications', 'memory specs'],
            'gpu_specifications': ['gpu specifications', 'graphics specifications'],
            'npu_specifications': ['npu specifications', 'ai specifications'],
            'expansion_options': ['expansion options', 'connectivity'],
            'package_specifications': ['package specifications', 'package specs'],
            'advanced_technologies': ['advanced technologies', 'features'],
            'security_reliability': ['security & reliability', 'security'],
            'supplemental_information': ['supplemental information', 'additional info']
        }
        
        try:
            # Look for section headers and extract following content
            for section_key, section_names in section_mappings.items():
                section_data = {}
                
                for section_name in section_names:
                    # Find section headers
                    headers = soup.find_all(['h2', 'h3', 'h4'], string=re.compile(section_name, re.IGNORECASE))
                    
                    for header in headers:
                        section_data.update(self._extract_section_content(header))
                
                if section_data:
                    sections[section_key] = section_data
            
            # Extract from definition lists and structured elements
            dl_elements = soup.find_all('dl')
            for dl in dl_elements:
                dt_dd_pairs = self._extract_dt_dd_pairs(dl)
                if dt_dd_pairs:
                    # Try to determine which section this belongs to
                    parent_section = self._find_parent_section(dl)
                    if parent_section in sections:
                        sections[parent_section].update(dt_dd_pairs)
                    else:
                        sections.setdefault('general', {}).update(dt_dd_pairs)
        
        except Exception as e:
            self.logger.error(f"Error extracting section specifications: {str(e)}")
        
        return sections
    
    def _extract_section_content(self, header) -> Dict[str, str]:
        """Extract content following a section header."""
        content = {}
        
        try:
            # Find the next sibling elements that contain specifications
            current = header.find_next_sibling()
            
            while current and current.name not in ['h1', 'h2', 'h3', 'h4']:
                # Extract from tables
                if current.name == 'table':
                    table_specs = self._extract_table_content(current)
                    content.update(table_specs)
                
                # Extract from definition lists
                elif current.name == 'dl':
                    dl_specs = self._extract_dt_dd_pairs(current)
                    content.update(dl_specs)
                
                # Extract from structured divs
                elif current.name == 'div':
                    div_specs = self._extract_div_specifications(current)
                    content.update(div_specs)
                
                current = current.find_next_sibling()
                
                # Prevent infinite loops
                if not current:
                    break
        
        except Exception as e:
            self.logger.error(f"Error extracting section content: {str(e)}")
        
        return content
    
    def _extract_table_content(self, table) -> Dict[str, str]:
        """Extract specifications from a table."""
        specs = {}
        
        try:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value and key != value:  # Avoid header rows
                        # Clean and normalize the key
                        clean_key = self._clean_specification_key(key)
                        specs[clean_key] = value
        
        except Exception as e:
            self.logger.error(f"Error extracting table content: {str(e)}")
        
        return specs
    
    def _extract_dt_dd_pairs(self, dl_element) -> Dict[str, str]:
        """Extract key-value pairs from definition lists."""
        pairs = {}
        
        try:
            dt_elements = dl_element.find_all('dt')
            dd_elements = dl_element.find_all('dd')
            
            # Match dt and dd elements
            for i, dt in enumerate(dt_elements):
                if i < len(dd_elements):
                    key = dt.get_text(strip=True)
                    value = dd_elements[i].get_text(strip=True)
                    if key and value:
                        clean_key = self._clean_specification_key(key)
                        pairs[clean_key] = value
        
        except Exception as e:
            self.logger.error(f"Error extracting dt/dd pairs: {str(e)}")
        
        return pairs
    
    def _extract_div_specifications(self, div_element) -> Dict[str, str]:
        """Extract specifications from structured div elements."""
        specs = {}
        
        try:
            # Look for specification patterns in divs
            spec_patterns = [
                (r'class.*spec', 'specification items'),
                (r'data-.*spec', 'data specification attributes'),
                (r'class.*detail', 'detail sections')
            ]
            
            for pattern, description in spec_patterns:
                matching_divs = div_element.find_all('div', class_=re.compile(pattern, re.IGNORECASE))
                
                for spec_div in matching_divs:
                    # Extract key-value pairs from the div
                    key_elem = spec_div.find(class_=re.compile(r'key|label|name', re.IGNORECASE))
                    value_elem = spec_div.find(class_=re.compile(r'value|detail|data', re.IGNORECASE))
                    
                    if key_elem and value_elem:
                        key = key_elem.get_text(strip=True)
                        value = value_elem.get_text(strip=True)
                        if key and value:
                            clean_key = self._clean_specification_key(key)
                            specs[clean_key] = value
        
        except Exception as e:
            self.logger.error(f"Error extracting div specifications: {str(e)}")
        
        return specs
    
    def _extract_table_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from all tables (fallback method)."""
        specs = {}
        
        try:
            # Find all tables that might contain specifications
            tables = soup.find_all('table')
            
            for table in tables:
                table_specs = self._extract_table_content(table)
                specs.update(table_specs)
        
        except Exception as e:
            self.logger.error(f"Error extracting table specifications: {str(e)}")
        
        return specs
    
    def _extract_legacy_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications using regex patterns (legacy method)."""
        specs = {}
        
        try:
            page_text = soup.get_text().lower()
            
            # Power-focused specification patterns for SoC power prediction modeling
            spec_patterns = {
                # Core specifications (critical for power modeling)
                'total_cores': r'total cores\s*(\d+)',
                'performance_cores': r'(?:# of )?performance[- ]cores?\s*(\d+)',
                'efficiency_cores': r'(?:# of )?(?:low power )?efficient?[- ]cores?\s*(\d+)',
                'total_threads': r'total threads\s*(\d+)',
                
                # Frequencies (critical for power prediction)
                'max_turbo_frequency': r'max turbo frequency\s*(\d+(?:\.\d+)?)\s*ghz',
                'base_frequency': r'(?:processor )?base frequency\s*(\d+(?:\.\d+)?)\s*ghz',
                'performance_core_max_frequency': r'performance[- ]core max turbo frequency\s*(\d+(?:\.\d+)?)\s*ghz',
                'efficiency_core_max_frequency': r'(?:low power )?efficient?[- ]core max turbo frequency\s*(\d+(?:\.\d+)?)\s*ghz',
                'performance_core_base_frequency': r'performance[- ]core base frequency\s*(\d+(?:\.\d+)?)\s*ghz',
                'efficiency_core_base_frequency': r'(?:low power )?efficient?[- ]core base frequency\s*(\d+(?:\.\d+)?)\s*ghz',
                'turbo_boost_max_frequency': r'intel.*?turbo boost max.*?frequency.*?(\d+(?:\.\d+)?)\s*ghz',
                
                # Power specifications (most critical for power modeling)
                'processor_base_power': r'processor base power\s*(\d+(?:\.\d+)?)\s*w',
                'maximum_turbo_power': r'maximum turbo power\s*(\d+(?:\.\d+)?)\s*w',
                'minimum_assured_power': r'minimum assured power\s*(\d+(?:\.\d+)?)\s*w',
                'tdp': r'tdp\s*(\d+(?:\.\d+)?)\s*w',
                'configurable_tdp_up': r'configurable tdp[- ]up\s*(\d+(?:\.\d+)?)\s*w',
                'configurable_tdp_down': r'configurable tdp[- ]down\s*(\d+(?:\.\d+)?)\s*w',
                
                # Cache (affects power consumption)
                'cache_size': r'cache\s*(\d+(?:\.\d+)?)\s*mb',
                'smart_cache': r'(?:intel )?smart cache\s*(\d+(?:\.\d+)?)\s*mb',
                'l1_cache': r'l1 cache\s*(\d+(?:\.\d+)?)\s*(?:mb|kb)',
                'l2_cache': r'l2 cache\s*(\d+(?:\.\d+)?)\s*(?:mb|kb)',
                'l3_cache': r'l3 cache\s*(\d+(?:\.\d+)?)\s*mb',
                
                # Process technology (critical for power characteristics)
                # Simplified: just look for "Lithography" or "CPU Lithography" label and parse paired value
                'lithography': r'(?:cpu\s+)?lithography\s*[:\s]+([^\n\r<>]+?)(?=\s*(?:\n|\r|<|$))',
                
                # Memory (affects system power)
                'max_memory_size': r'max memory.*?(\d+)\s*gb',
                'memory_channels': r'max.*?memory channels\s*(\d+)',
                'memory_types': r'memory types\s*([^\n\r]+(?:ddr|lpddr)[^\n\r]*)',
                'memory_speed': r'(?:up to )?(\d+)\s*mt/s',
                
                # Graphics power specifications
                'gpu_name': r'gpu name.*?([^\n\r]+(?:arc|uhd|iris|graphics)[^\n\r]*)',
                'graphics_max_frequency': r'graphics.*?max.*?frequency\s*(\d+(?:\.\d+)?)\s*ghz',
                'graphics_base_frequency': r'graphics.*?base.*?frequency\s*(\d+(?:\.\d+)?)\s*ghz',
                'xe_cores': r'xe[- ]cores\s*(\d+)',
                'execution_units': r'execution units\s*(\d+)',
                
                # AI/NPU power specifications
                'npu_name': r'npu name.*?([^\n\r]+ai boost[^\n\r]*)',
                'npu_tops': r'npu.*?peak tops.*?(\d+)',
                'overall_tops': r'overall peak tops.*?(\d+)',
                'ai_boost': r'intel.*?ai boost.*?(\d+)',
                
                # Package and thermal (important for power modeling)
                'socket': r'sockets? supported\s*([a-z0-9]+)',
                'max_operating_temperature': r'max operating temperature\s*(\d+)\s*°?c',
                'package_size': r'package size\s*([0-9.x]+mm)',
                'tjunction': r't.*?junction\s*(\d+)\s*°?c',
                
                # Other relevant specs
                'instruction_set': r'instruction set\s*([0-9]+-bit)',
                'launch_date': r'launch date\s*([q\d\'\/\-\s]+)',
                'code_name': r'code name.*?([^\n\r]+)',
                'product_collection': r'product collection\s*([^\n\r]+)',
                'vertical_segment': r'vertical segment\s*([^\n\r]+)',
                
                # Advanced power features (boolean patterns - return yes/no)
                'speed_shift': r'(intel.*?speed shift)',
                'turbo_boost': r'(intel.*?turbo boost)',
                'enhanced_speedstep': r'(enhanced intel speedstep)',
                'thermal_monitoring': r'(thermal monitoring)',
                'configurable_tdp': r'(configurable tdp)',
            }
            
            for spec_name, pattern in spec_patterns.items():
                match = re.search(pattern, page_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if value:
                        specs[spec_name] = value
            
            # Enhanced lithography detection
            lithography_value = self._extract_lithography_enhanced(soup, soup.get_text())
            if lithography_value:
                specs['lithography'] = lithography_value
                self.logger.debug(f"Enhanced lithography detection found: {lithography_value}")
        
        except Exception as e:
            self.logger.error(f"Error extracting legacy specifications: {str(e)}")
        
        return specs
    
    def _clean_specification_key(self, key: str) -> str:
        """Clean and normalize specification keys."""
        if not key:
            return ""
        
        # Remove special characters and normalize spacing
        clean_key = re.sub(r'[^\w\s\-]', '', key)
        clean_key = re.sub(r'\s+', ' ', clean_key).strip()
        
        # Convert to lowercase and replace spaces with underscores
        clean_key = clean_key.lower().replace(' ', '_').replace('-', '_')
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ['intel_', 'processor_', 'cpu_']
        suffixes_to_remove = ['_support', '_technology']
        
        for prefix in prefixes_to_remove:
            if clean_key.startswith(prefix):
                clean_key = clean_key[len(prefix):]
        
        for suffix in suffixes_to_remove:
            if clean_key.endswith(suffix):
                clean_key = clean_key[:-len(suffix)]
        
        return clean_key
    
    def _normalize_specification_unicode(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Unicode characters in all specification values."""
        try:
            def normalize_dict(d):
                if isinstance(d, dict):
                    return {k: normalize_dict(v) for k, v in d.items()}
                elif isinstance(d, str):
                    return normalize_unicode_text(d)
                else:
                    return d
            
            return normalize_dict(specs)
        except Exception as e:
            self.logger.error(f"Error normalizing Unicode in specifications: {str(e)}")
            return specs
    
    def _categorize_specification(self, key: str) -> str:
        """Categorize a specification into appropriate section."""
        key_lower = key.lower()
        
        # CPU related
        if any(word in key_lower for word in ['core', 'thread', 'frequency', 'turbo', 'cache']):
            return 'cpu_specifications'
        
        # Memory related
        if any(word in key_lower for word in ['memory', 'ddr', 'lpddr', 'channel']):
            return 'memory_specifications'
        
        # Graphics related
        if any(word in key_lower for word in ['gpu', 'graphics', 'display', 'resolution', 'xe']):
            return 'gpu_specifications'
        
        # AI/NPU related
        if any(word in key_lower for word in ['npu', 'ai', 'tops', 'neural']):
            return 'npu_specifications'
        
        # Power related
        if any(word in key_lower for word in ['power', 'tdp', 'watt', 'temperature']):
            return 'package_specifications'
        
        # Connectivity
        if any(word in key_lower for word in ['pci', 'thunderbolt', 'usb', 'expansion']):
            return 'expansion_options'
        
        # Security
        if any(word in key_lower for word in ['security', 'encryption', 'trust', 'guard']):
            return 'security_reliability'
        
        # Default category
        return 'general'
    
    def _categorize_legacy_specifications(self, legacy_specs: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Categorize legacy specifications into proper sections."""
        categorized = {
            'essentials': {},
            'cpu_specifications': {},
            'memory_specifications': {},
            'gpu_specifications': {},
            'npu_specifications': {},
            'expansion_options': {},
            'package_specifications': {},
            'advanced_technologies': {},
            'security_reliability': {},
            'supplemental_information': {}
        }
        
        # Define categorization mappings
        category_mappings = {
            'essentials': [
                'product_collection', 'vertical_segment', 'launch_date', 'code_name', 'instruction_set'
            ],
            'cpu_specifications': [
                'total_cores', 'performance_cores', 'efficiency_cores', 'total_threads',
                'max_turbo_frequency', 'base_frequency', 'performance_core_max_frequency',
                'efficiency_core_max_frequency', 'performance_core_base_frequency',
                'efficiency_core_base_frequency', 'turbo_boost_max_frequency',
                'cache_size', 'smart_cache', 'l1_cache', 'l2_cache', 'l3_cache', 'lithography'
            ],
            'memory_specifications': [
                'max_memory_size', 'memory_channels', 'memory_types', 'memory_speed'
            ],
            'gpu_specifications': [
                'gpu_name', 'graphics_max_frequency', 'graphics_base_frequency',
                'xe_cores', 'execution_units'
            ],
            'npu_specifications': [
                'npu_name', 'npu_tops', 'overall_tops', 'ai_boost'
            ],
            'expansion_options': [
                'socket'
            ],
            'package_specifications': [
                'processor_base_power', 'maximum_turbo_power', 'minimum_assured_power',
                'tdp', 'configurable_tdp_up', 'configurable_tdp_down',
                'max_operating_temperature', 'package_size', 'tjunction'
            ],
            'advanced_technologies': [
                'speed_shift', 'turbo_boost', 'enhanced_speedstep', 'thermal_monitoring',
                'configurable_tdp'
            ]
        }
        
        # Categorize each specification
        for spec_key, spec_value in legacy_specs.items():
            categorized_spec = False
            for category, spec_list in category_mappings.items():
                if spec_key in spec_list:
                    categorized[category][spec_key] = spec_value
                    categorized_spec = True
                    break
            
            # If not categorized, put in supplemental_information
            if not categorized_spec:
                categorized['supplemental_information'][spec_key] = spec_value
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def _find_parent_section(self, element) -> str:
        """Find which section an element belongs to based on nearby headers."""
        try:
            # Look for the closest preceding header
            current = element.find_previous(['h1', 'h2', 'h3', 'h4'])
            
            if current:
                header_text = current.get_text().lower()
                
                if 'cpu' in header_text or 'processor' in header_text:
                    return 'cpu_specifications'
                elif 'memory' in header_text:
                    return 'memory_specifications'
                elif 'gpu' in header_text or 'graphics' in header_text:
                    return 'gpu_specifications'
                elif 'npu' in header_text or 'ai' in header_text:
                    return 'npu_specifications'
                elif 'expansion' in header_text or 'connectivity' in header_text:
                    return 'expansion_options'
                elif 'package' in header_text:
                    return 'package_specifications'
                elif 'security' in header_text:
                    return 'security_reliability'
                elif 'essential' in header_text:
                    return 'essentials'
        
        except Exception:
            pass
        
        return 'general'
    
    def _extract_lithography_enhanced(self, soup: BeautifulSoup, text: str) -> Optional[str]:
        """Simplified lithography detection - look for 'Lithography' or 'CPU Lithography' label and parse paired value."""
        try:
            # Simple pattern: find "Lithography" or "CPU Lithography" label followed by the value
            # This matches the actual structure on Intel spec pages
            lithography_patterns = [
                r'(?:cpu\s+)?lithography\s*[:\s]+([^\n\r<>]+?)(?=\s*(?:\n|\r|<|$))',
            ]
            
            # Search through patterns
            for pattern in lithography_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    extracted = match.group(1).strip()
                    
                    # Clean and validate the extracted value
                    cleaned = self._clean_lithography_value(extracted)
                    if cleaned:
                        self.logger.debug(f"Found lithography: {cleaned}")
                        return cleaned
            
            # Fallback: Look for standalone technology values in structured data
            fallback_result = self._extract_lithography_fallback(soup)
            if fallback_result:
                return fallback_result
                
        except Exception as e:
            self.logger.error(f"Error in enhanced lithography extraction: {str(e)}")
        
        return None
    
    def _clean_lithography_value(self, value: str) -> Optional[str]:
        """Clean and validate lithography value."""
        if not value or len(value) < 2:
            return None
        
        # Remove common prefixes/suffixes and clean
        value = re.sub(r'^(?:using|with|on|at|by)\s+', '', value, flags=re.IGNORECASE)
        value = re.sub(r'\s+(?:process|technology|node|class|generation|finfet|gaafet)$', '', value, flags=re.IGNORECASE)
        value = value.strip()
        
        # Additional cleaning for better readability
        value = re.sub(r'\s+', ' ', value)  # Normalize spaces
        value = re.sub(r'[\(\)\[\]]', '', value)  # Remove brackets
        
        # Exclude known non-process Intel technologies
        non_process_intel_terms = [
            'intel 64',     # 64-bit instruction set
            'intel 32',     # 32-bit instruction set
            'intel x86',    # x86 architecture
            'intel x64',    # x64 architecture
            'intel sse',    # SIMD instruction sets
            'intel avx',    # Advanced Vector Extensions
            'intel ht',     # Hyper-Threading
            'intel vt',     # Virtualization Technology
        ]
        
        for term in non_process_intel_terms:
            if value.lower() == term:
                return None
        
        # Validate that it contains meaningful lithography information
        # More permissive validation since we're now getting values directly paired with "Lithography" label
        valid_patterns = [
            r'\d+\s*nm',                    # 14 nm, 10nm, etc.
            r'intel\s+(?:[3-9]|1[0-9])\b', # Intel 3, Intel 7, Intel 10, etc. (not 32/64)
            r'n\d+[a-z]?\b',                # N5, N3, N3B (TSMC naming)
            r'\d+\s*nanometer',            # 7 nanometer
            r'\d+\s*nm\s*\+',              # 14nm+, enhanced processes
            r'intel\s+(?:[3-9]|1[0-9])\s*\+', # Intel 7+
            r'\d+\s*nm\s+(?:finfet|gaafet)', # Advanced transistor types
            r'tsmc\s+n\d+',                # TSMC N5, N3, etc.
            r'samsung\s+\d+\s*nm',         # Samsung processes
            r'globalfoundries\s+\d+\s*nm', # GF processes
        ]
        
        for pattern in valid_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return value
        
        return None
    
    def _extract_lithography_fallback(self, soup: BeautifulSoup) -> Optional[str]:
        """Fallback method to find lithography in structured elements."""
        try:
            # Look in specification tables specifically
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Check if key indicates lithography
                        lithography_keywords = [
                            'lithography', 'process', 'technology', 'node', 
                            'fabrication', 'manufacturing', 'silicon'
                        ]
                        
                        if any(keyword in key for keyword in lithography_keywords):
                            cleaned = self._clean_lithography_value(value)
                            if cleaned:
                                return cleaned
            
            # Look in definition lists
            dls = soup.find_all('dl')
            for dl in dls:
                dt_elements = dl.find_all('dt')
                dd_elements = dl.find_all('dd')
                
                for i, dt in enumerate(dt_elements):
                    if i < len(dd_elements):
                        key = dt.get_text(strip=True).lower()
                        value = dd_elements[i].get_text(strip=True)
                        
                        lithography_keywords = [
                            'lithography', 'process', 'technology', 'node', 
                            'fabrication', 'manufacturing'
                        ]
                        
                        if any(keyword in key for keyword in lithography_keywords):
                            cleaned = self._clean_lithography_value(value)
                            if cleaned:
                                return cleaned
                                
        except Exception as e:
            self.logger.debug(f"Error in lithography fallback extraction: {str(e)}")
        
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract CPU price from the page."""
        price_selectors = [
            '.price',
            '.product-price',
            '[data-testid="price"]',
            '.pdp-price'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Look for price pattern
                price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', price_text)
                if price_match:
                    return price_match.group()
        
        return None
    
    def _extract_availability(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract availability information."""
        availability_selectors = [
            '.availability',
            '.stock-status',
            '[data-testid="availability"]'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description."""
        desc_selectors = [
            '.product-description',
            '.pdp-description',
            '[data-testid="description"]',
            '.product-overview'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                if len(description) > 10:  # Basic validation
                    return description[:500]  # Limit length
        
        return None