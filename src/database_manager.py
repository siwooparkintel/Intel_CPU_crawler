"""
Database Manager for Intel CPU Power Specifications
Simple SQLite database optimized for power prediction modeling.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class PowerSpecDatabaseManager:
    """Simple database manager for Intel CPU power specifications."""
    
    def __init__(self, db_path: str = 'data/intel_cpu_power_specs.db'):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database with power-focused schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create main table for CPU power specifications
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cpu_power_specs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    
                    -- Core specifications (critical for power modeling)
                    total_cores INTEGER,
                    performance_cores INTEGER,
                    efficiency_cores INTEGER,
                    total_threads INTEGER,
                    
                    -- Frequency specifications (GHz) - critical for power prediction
                    max_turbo_frequency REAL,
                    base_frequency REAL,
                    performance_core_max_frequency REAL,
                    efficiency_core_max_frequency REAL,
                    performance_core_base_frequency REAL,
                    efficiency_core_base_frequency REAL,
                    turbo_boost_max_frequency REAL,
                    
                    -- Power specifications (Watts) - most critical
                    processor_base_power REAL,
                    maximum_turbo_power REAL,
                    minimum_assured_power REAL,
                    tdp REAL,
                    configurable_tdp_up REAL,
                    configurable_tdp_down REAL,
                    
                    -- Process technology (critical for power characteristics)
                    lithography TEXT,
                    process_node TEXT,
                    
                    -- Cache specifications (MB) - affects power
                    cache_size REAL,
                    smart_cache REAL,
                    l1_cache TEXT,
                    l2_cache TEXT,
                    l3_cache REAL,
                    
                    -- Memory specifications (affects system power)
                    max_memory_size INTEGER,
                    memory_channels INTEGER,
                    memory_types TEXT,
                    memory_speed INTEGER,
                    
                    -- Graphics power specifications
                    gpu_name TEXT,
                    graphics_max_frequency REAL,
                    graphics_base_frequency REAL,
                    xe_cores INTEGER,
                    execution_units INTEGER,
                    
                    -- AI/NPU specifications
                    npu_name TEXT,
                    npu_tops INTEGER,
                    overall_tops INTEGER,
                    
                    -- Package and thermal specifications
                    socket TEXT,
                    max_operating_temperature INTEGER,
                    package_size TEXT,
                    tjunction INTEGER,
                    
                    -- Product information
                    code_name TEXT,
                    product_collection TEXT,
                    vertical_segment TEXT,
                    launch_date TEXT,
                    instruction_set TEXT,
                    
                    -- Additional specifications as JSON (flexible)
                    additional_specs JSON,
                    
                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scraper_version TEXT DEFAULT '1.0'
                )
            ''')
            
            # Create indexes for common queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON cpu_power_specs(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON cpu_power_specs(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_power ON cpu_power_specs(processor_base_power)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cores ON cpu_power_specs(total_cores)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_lithography ON cpu_power_specs(lithography)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_collection ON cpu_power_specs(product_collection)')
            
            conn.commit()
            self.logger.info(f"Database initialized at {self.db_path}")
    
    def insert_cpu_specs(self, cpu_data: Dict[str, Any]) -> bool:
        """
        Insert CPU specifications into database.
        
        Args:
            cpu_data: Dictionary containing CPU data from parser
            
        Returns:
            True if inserted, False if duplicate or error
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for duplicates
                if self._cpu_exists(cursor, cpu_data['url']):
                    self.logger.info(f"CPU already exists in database: {cpu_data['url']}")
                    return False
                
                # Extract power specifications from the categorized structure
                specs = cpu_data.get('specifications', {})
                
                # Merge specifications from all categories for database insertion
                all_specs = {}
                for category in ['essentials', 'cpu_specifications', 'memory_specifications', 
                               'gpu_specifications', 'npu_specifications', 'expansion_options',
                               'package_specifications', 'advanced_technologies', 'legacy']:
                    category_specs = specs.get(category, {})
                    if isinstance(category_specs, dict):
                        all_specs.update(category_specs)
                
                # Handle core specifications with fallback for older architectures
                total_cores = self._safe_int(all_specs.get('total_cores'))
                performance_cores = self._safe_int(all_specs.get('performance_cores'))
                efficiency_cores = self._safe_int(all_specs.get('efficiency_cores'))
                
                # For older Intel processors without P/E core distinction,
                # assume all cores are performance cores (traditional architecture)
                is_legacy_architecture = False
                if total_cores and not performance_cores and not efficiency_cores:
                    performance_cores = total_cores
                    efficiency_cores = 0
                    is_legacy_architecture = True
                    self.logger.debug(f"Applied legacy core logic: {total_cores} total cores -> {performance_cores}P + {efficiency_cores}E")
                
                # Handle frequency specifications with fallback for older architectures
                max_turbo_freq = self._safe_float(all_specs.get('max_turbo_frequency'))
                base_freq = self._safe_float(all_specs.get('base_frequency'))
                p_core_max_freq = self._safe_float(all_specs.get('performance_core_max_frequency'))
                e_core_max_freq = self._safe_float(all_specs.get('efficiency_core_max_frequency'))
                p_core_base_freq = self._safe_float(all_specs.get('performance_core_base_frequency'))
                e_core_base_freq = self._safe_float(all_specs.get('efficiency_core_base_frequency'))
                
                # For older processors, map general frequencies to P-core frequencies
                if is_legacy_architecture:
                    if max_turbo_freq and not p_core_max_freq:
                        p_core_max_freq = max_turbo_freq
                        self.logger.debug(f"Mapped max_turbo_frequency ({max_turbo_freq}) to performance_core_max_frequency")
                    if base_freq and not p_core_base_freq:
                        p_core_base_freq = base_freq
                        self.logger.debug(f"Mapped base_frequency ({base_freq}) to performance_core_base_frequency")
                
                # Prepare data for insertion
                insert_data = {
                    'url': cpu_data['url'],
                    'name': cpu_data['name'],
                    
                    # Core specifications
                    'total_cores': total_cores,
                    'performance_cores': performance_cores,
                    'efficiency_cores': efficiency_cores,
                    'total_threads': self._safe_int(all_specs.get('total_threads')),
                    
                    # Frequency specifications
                    'max_turbo_frequency': max_turbo_freq,
                    'base_frequency': base_freq,
                    'performance_core_max_frequency': p_core_max_freq,
                    'efficiency_core_max_frequency': e_core_max_freq,
                    'performance_core_base_frequency': p_core_base_freq,
                    'efficiency_core_base_frequency': e_core_base_freq,
                    'turbo_boost_max_frequency': self._safe_float(all_specs.get('turbo_boost_max_frequency')),
                    
                    # Power specifications
                    'processor_base_power': self._safe_float(all_specs.get('processor_base_power')),
                    'maximum_turbo_power': self._safe_float(all_specs.get('maximum_turbo_power')),
                    'minimum_assured_power': self._safe_float(all_specs.get('minimum_assured_power')),
                    'tdp': self._safe_float(all_specs.get('tdp')),
                    'configurable_tdp_up': self._safe_float(all_specs.get('configurable_tdp_up')),
                    'configurable_tdp_down': self._safe_float(all_specs.get('configurable_tdp_down')),
                    
                    # Process technology
                    'lithography': all_specs.get('lithography'),
                    'process_node': all_specs.get('process_node'),
                    
                    # Cache specifications
                    'cache_size': self._safe_float(all_specs.get('cache_size')),
                    'smart_cache': self._safe_float(all_specs.get('smart_cache')),
                    'l1_cache': all_specs.get('l1_cache'),
                    'l2_cache': all_specs.get('l2_cache'),
                    'l3_cache': self._safe_float(all_specs.get('l3_cache')),
                    
                    # Memory specifications
                    'max_memory_size': self._safe_int(all_specs.get('max_memory_size')),
                    'memory_channels': self._safe_int(all_specs.get('memory_channels')),
                    'memory_types': all_specs.get('memory_types'),
                    'memory_speed': self._safe_int(all_specs.get('memory_speed')),
                    
                    # Graphics specifications
                    'gpu_name': all_specs.get('gpu_name'),
                    'graphics_max_frequency': self._safe_float(all_specs.get('graphics_max_frequency')),
                    'graphics_base_frequency': self._safe_float(all_specs.get('graphics_base_frequency')),
                    'xe_cores': self._safe_int(all_specs.get('xe_cores')),
                    'execution_units': self._safe_int(all_specs.get('execution_units')),
                    
                    # AI/NPU specifications
                    'npu_name': all_specs.get('npu_name'),
                    'npu_tops': self._safe_int(all_specs.get('npu_tops')),
                    'overall_tops': self._safe_int(all_specs.get('overall_tops')),
                    
                    # Package specifications
                    'socket': all_specs.get('socket'),
                    'max_operating_temperature': self._safe_int(all_specs.get('max_operating_temperature')),
                    'package_size': all_specs.get('package_size'),
                    'tjunction': self._safe_int(all_specs.get('tjunction')),
                    
                    # Product information
                    'code_name': self._clean_code_name(all_specs.get('code_name')),
                    'product_collection': all_specs.get('product_collection'),
                    'vertical_segment': all_specs.get('vertical_segment'),
                    'launch_date': all_specs.get('launch_date'),
                    'instruction_set': all_specs.get('instruction_set'),
                    
                    # Store additional specs as JSON
                    'additional_specs': json.dumps({
                        k: v for k, v in specs.items() 
                        if k != 'legacy' and v  # Store non-legacy, non-empty sections
                    }),
                    
                    # Metadata
                    'scraper_version': '1.0'
                }
                
                # Build INSERT query
                columns = ', '.join(insert_data.keys())
                placeholders = ', '.join(['?' for _ in insert_data])
                
                query = f'''
                    INSERT INTO cpu_power_specs ({columns})
                    VALUES ({placeholders})
                '''
                
                cursor.execute(query, list(insert_data.values()))
                conn.commit()
                
                self.logger.info(f"Successfully inserted CPU: {cpu_data['name']}")
                return True
                
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"Duplicate CPU not inserted: {cpu_data['url']} - {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error inserting CPU data: {str(e)}")
            return False
    
    def _cpu_exists(self, cursor: sqlite3.Cursor, url: str) -> bool:
        """Check if CPU with given URL already exists."""
        cursor.execute('SELECT id FROM cpu_power_specs WHERE url = ?', (url,))
        return cursor.fetchone() is not None
    
    def _clean_code_name(self, code_name: Any) -> Optional[str]:
        """Clean code name by removing 'Products formerly' prefix.
        
        Args:
            code_name: Raw code name from Intel (e.g., "Products formerly Lunar Lake")
            
        Returns:
            Cleaned code name (e.g., "Lunar Lake") or None
        """
        if not code_name or not isinstance(code_name, str):
            return None
        
        # Remove "Products formerly" prefix (case insensitive)
        import re
        cleaned = re.sub(r'^products\s+formerly\s+', '', code_name, flags=re.IGNORECASE)
        
        # Remove any leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Remove trailing colon if present (some Intel pages have ":")
        cleaned = cleaned.rstrip(':')
        
        return cleaned if cleaned and cleaned != ':' else None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to integer."""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                # Extract numeric part
                import re
                match = re.search(r'(\d+)', value)
                if match:
                    return int(match.group(1))
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                # Extract numeric part
                import re
                match = re.search(r'(\d+(?:\.\d+)?)', value)
                if match:
                    return float(match.group(1))
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def get_cpu_count(self) -> int:
        """Get total number of CPUs in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM cpu_power_specs')
            return cursor.fetchone()[0]
    
    def get_power_statistics(self) -> Dict[str, Any]:
        """Get power-related statistics from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Power statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_cpus,
                    AVG(processor_base_power) as avg_base_power,
                    MIN(processor_base_power) as min_base_power,
                    MAX(processor_base_power) as max_base_power,
                    AVG(maximum_turbo_power) as avg_turbo_power,
                    MIN(maximum_turbo_power) as min_turbo_power, 
                    MAX(maximum_turbo_power) as max_turbo_power
                FROM cpu_power_specs 
                WHERE processor_base_power IS NOT NULL
            ''')
            
            row = cursor.fetchone()
            if row:
                stats['power'] = {
                    'total_cpus_with_power_data': row[0],
                    'avg_base_power_w': round(row[1], 2) if row[1] else None,
                    'min_base_power_w': row[2],
                    'max_base_power_w': row[3],
                    'avg_turbo_power_w': round(row[4], 2) if row[4] else None,
                    'min_turbo_power_w': row[5],
                    'max_turbo_power_w': row[6]
                }
            
            # Core count distribution
            cursor.execute('''
                SELECT total_cores, COUNT(*) as count
                FROM cpu_power_specs 
                WHERE total_cores IS NOT NULL
                GROUP BY total_cores
                ORDER BY total_cores
            ''')
            
            stats['core_distribution'] = {
                f'{row[0]}_cores': row[1] for row in cursor.fetchall()
            }
            
            # Process technology distribution
            cursor.execute('''
                SELECT lithography, COUNT(*) as count
                FROM cpu_power_specs 
                WHERE lithography IS NOT NULL
                GROUP BY lithography
                ORDER BY count DESC
            ''')
            
            stats['process_technology'] = {
                row[0]: row[1] for row in cursor.fetchall()
            }
            
            return stats
    
    def export_for_modeling(self, output_path: str = 'data/cpu_power_modeling_data.json') -> bool:
        """
        Export CPU data in format suitable for power prediction modeling.
        
        Args:
            output_path: Path to save the modeling data
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Select key fields for power modeling
                cursor.execute('''
                    SELECT 
                        name,
                        total_cores,
                        performance_cores,
                        efficiency_cores,
                        max_turbo_frequency,
                        base_frequency,
                        performance_core_max_frequency,
                        efficiency_core_max_frequency,
                        processor_base_power,
                        maximum_turbo_power,
                        minimum_assured_power,
                        lithography,
                        cache_size,
                        memory_channels,
                        memory_speed,
                        graphics_max_frequency,
                        xe_cores,
                        npu_tops,
                        overall_tops,
                        max_operating_temperature,
                        vertical_segment,
                        launch_date
                    FROM cpu_power_specs
                    ORDER BY name
                ''')
                
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                modeling_data = []
                for row in rows:
                    cpu_data = dict(zip(columns, row))
                    # Only include CPUs with essential power data
                    if cpu_data['processor_base_power'] and cpu_data['total_cores']:
                        modeling_data.append(cpu_data)
                
                # Save to JSON file
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'metadata': {
                            'exported_at': datetime.now().isoformat(),
                            'total_cpus': len(modeling_data),
                            'description': 'Intel CPU power specifications for SoC power prediction modeling'
                        },
                        'data': modeling_data
                    }, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Exported {len(modeling_data)} CPUs for modeling to {output_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error exporting modeling data: {str(e)}")
            return False
    
    def get_cpu_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Get CPUs matching name pattern."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM cpu_power_specs 
                WHERE name LIKE ? 
                ORDER BY name
            ''', (f'%{name_pattern}%',))
            
            return [dict(row) for row in cursor.fetchall()]