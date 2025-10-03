#!/usr/bin/env python3
"""
Update code_name field in database from additional_specs.

This script:
1. Extracts code_name from additional_specs -> general -> code_name
2. Removes "Products formerly" prefix
3. Updates all existing CPU records
"""

import sqlite3
import json
import re
from pathlib import Path


def clean_code_name(code_name_raw: str) -> str:
    """Clean code name by removing 'Products formerly' prefix.
    
    Args:
        code_name_raw: Raw code name from Intel (e.g., "Products formerly Lunar Lake")
        
    Returns:
        Cleaned code name (e.g., "Lunar Lake")
    """
    if not code_name_raw:
        return None
    
    # Remove "Products formerly" prefix (case insensitive)
    cleaned = re.sub(r'^products\s+formerly\s+', '', code_name_raw, flags=re.IGNORECASE)
    
    # Remove any leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Remove trailing colon if present
    cleaned = cleaned.rstrip(':')
    
    return cleaned if cleaned else None


def update_code_names(db_path: str = 'data/intel_cpu_power_specs.db'):
    """Update code_name field for all CPUs in database.
    
    Args:
        db_path: Path to SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*80)
    print("Updating code_name field from additional_specs")
    print("="*80)
    
    # Get all CPUs with their additional_specs
    cursor.execute("SELECT id, name, additional_specs, code_name FROM cpu_power_specs")
    rows = cursor.fetchall()
    
    print(f"\nFound {len(rows)} CPUs in database")
    
    updated_count = 0
    skipped_count = 0
    not_found_count = 0
    
    for cpu_id, name, specs_json, current_code_name in rows:
        try:
            # Parse additional_specs JSON
            if not specs_json:
                skipped_count += 1
                continue
                
            specs = json.loads(specs_json)
            
            # Extract code_name from multiple possible locations
            code_name_raw = None
            
            # Try general section first (most common)
            if 'general' in specs and isinstance(specs['general'], dict):
                code_name_raw = specs['general'].get('code_name')
            
            # Try essentials section as fallback
            if not code_name_raw and 'essentials' in specs and isinstance(specs['essentials'], dict):
                code_name_raw = specs['essentials'].get('code_name')
            
            # Try cpu_specifications as another fallback
            if not code_name_raw and 'cpu_specifications' in specs and isinstance(specs['cpu_specifications'], dict):
                code_name_raw = specs['cpu_specifications'].get('code_name')
            
            if code_name_raw:
                # Clean the code name
                code_name_cleaned = clean_code_name(code_name_raw)
                
                if code_name_cleaned and code_name_cleaned != ':':
                    # Update database
                    cursor.execute(
                        "UPDATE cpu_power_specs SET code_name = ? WHERE id = ?",
                        (code_name_cleaned, cpu_id)
                    )
                    updated_count += 1
                    
                    # Show some examples
                    if updated_count <= 5:
                        print(f"\n{name}")
                        print(f"  Raw: '{code_name_raw}'")
                        print(f"  Cleaned: '{code_name_cleaned}'")
                        print(f"  Previous: '{current_code_name}'")
                else:
                    skipped_count += 1
            else:
                not_found_count += 1
                
        except Exception as e:
            print(f"Error processing CPU {name}: {e}")
            skipped_count += 1
    
    # Commit changes
    conn.commit()
    
    # Print summary
    print("\n" + "="*80)
    print("Update Summary")
    print("="*80)
    print(f"Total CPUs: {len(rows)}")
    print(f"Updated: {updated_count}")
    print(f"Code name not found: {not_found_count}")
    print(f"Skipped: {skipped_count}")
    print("="*80)
    
    # Show some examples of updated records
    print("\nSample of updated code names:")
    cursor.execute("""
        SELECT name, code_name 
        FROM cpu_power_specs 
        WHERE code_name IS NOT NULL AND code_name != ''
        ORDER BY RANDOM()
        LIMIT 10
    """)
    
    for name, code_name in cursor.fetchall():
        print(f"  {name[:60]:<60} → {code_name}")
    
    # Show statistics by code name
    print("\nCode name distribution:")
    cursor.execute("""
        SELECT code_name, COUNT(*) as count
        FROM cpu_power_specs
        WHERE code_name IS NOT NULL AND code_name != ''
        GROUP BY code_name
        ORDER BY count DESC
        LIMIT 15
    """)
    
    for code_name, count in cursor.fetchall():
        print(f"  {code_name:<30} {count:>3} CPUs")
    
    conn.close()
    print("\n✓ Update complete!")


if __name__ == "__main__":
    update_code_names()
