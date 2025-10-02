"""
Data Manager - Data storage and export functionality
Handles saving scraped data in various formats.
"""

import json
import csv
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict, Any
from datetime import datetime


class DataManager:
    """Manages data storage and export for scraped CPU data."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize data manager.
        
        Args:
            output_dir: Directory to save data files
        """
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, data: List[Dict[str, Any]], filename: str):
        """
        Save data as JSON file.
        
        Args:
            data: List of CPU data dictionaries
            filename: Output filename
        """
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(data)} records to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving JSON file {filepath}: {str(e)}")
            raise
    
    def save_csv(self, data: List[Dict[str, Any]], filename: str):
        """
        Save data as CSV file.
        
        Args:
            data: List of CPU data dictionaries
            filename: Output filename
        """
        if not data:
            self.logger.warning("No data to save to CSV")
            return
        
        filepath = self.output_dir / filename
        
        try:
            # Flatten nested dictionaries for CSV
            flattened_data = self._flatten_data(data)
            
            # Convert to DataFrame
            df = pd.DataFrame(flattened_data)
            
            # Save to CSV
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            self.logger.info(f"Saved {len(flattened_data)} records to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving CSV file {filepath}: {str(e)}")
            raise
    
    def _flatten_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Flatten nested dictionaries for CSV export.
        
        Args:
            data: List of nested dictionaries
            
        Returns:
            List of flattened dictionaries
        """
        flattened = []
        
        for item in data:
            flat_item = {}
            
            for key, value in item.items():
                if isinstance(value, dict):
                    # Flatten nested dictionary
                    for nested_key, nested_value in value.items():
                        flat_item[f"{key}_{nested_key}"] = nested_value
                else:
                    flat_item[key] = value
            
            flattened.append(flat_item)
        
        return flattened
    
    def save_summary_report(self, data: List[Dict[str, Any]], filename: str = None):
        """
        Save a summary report of the scraped data.
        
        Args:
            data: List of CPU data dictionaries
            filename: Output filename (optional)
        """
        if not data:
            self.logger.warning("No data to generate summary report")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.txt"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("Intel CPU Crawler - Summary Report\n")
                f.write("=" * 40 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total CPUs scraped: {len(data)}\n\n")
                
                # CPU names
                f.write("CPU Names:\n")
                f.write("-" * 20 + "\n")
                for i, cpu in enumerate(data, 1):
                    name = cpu.get('name', 'Unknown')
                    f.write(f"{i:3d}. {name}\n")
                
                f.write("\n")
                
                # Common specifications analysis
                spec_counts = {}
                for cpu in data:
                    specs = cpu.get('specifications', {})
                    for spec_key in specs.keys():
                        spec_counts[spec_key] = spec_counts.get(spec_key, 0) + 1
                
                if spec_counts:
                    f.write("Most Common Specifications:\n")
                    f.write("-" * 30 + "\n")
                    sorted_specs = sorted(spec_counts.items(), key=lambda x: x[1], reverse=True)
                    for spec, count in sorted_specs[:10]:  # Top 10
                        percentage = (count / len(data)) * 100
                        f.write(f"{spec}: {count} CPUs ({percentage:.1f}%)\n")
                
                f.write("\n")
                
                # URLs scraped
                f.write("URLs Scraped:\n")
                f.write("-" * 15 + "\n")
                for cpu in data:
                    url = cpu.get('url', 'Unknown URL')
                    f.write(f"{url}\n")
            
            self.logger.info(f"Summary report saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving summary report {filepath}: {str(e)}")
            raise
    
    def load_json(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load data from JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            List of CPU data dictionaries
        """
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded {len(data)} records from {filepath}")
            return data
            
        except FileNotFoundError:
            self.logger.error(f"File not found: {filepath}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON file {filepath}: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error loading JSON file {filepath}: {str(e)}")
            return []