"""
Data Manager - File-based Data Storage and Export

Legacy file-based data management system for JSON and CSV exports.
Primarily used for backward compatibility and simple data exports.

Note: For production use, prefer the PowerSpecDatabaseManager for
structured storage and advanced analytics.

Features:
    - JSON export with proper encoding
    - CSV export with nested data flattening
    - Error handling and logging
    - Flexible output directory management

Usage:
    data_manager = DataManager(Path('data'))
    data_manager.save_json(cpu_data, 'cpu_specs.json')
    data_manager.save_csv(cpu_data, 'cpu_specs.csv')
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
    

    
