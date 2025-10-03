#!/usr/bin/env python3
"""
Merge intel_Core_Ultra_power_specs.db into intel_cpu_power_specs.db
while preventing duplications based on URL.
"""

import sqlite3
import sys
from pathlib import Path

def get_table_info(db_path: str):
    """Get table information from database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n{db_path}:")
    print(f"  Tables: {tables}")
    
    if tables:
        table_name = tables[0][0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Row count in '{table_name}': {count}")
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        print(f"  Schema: {[col[1] for col in schema]}")
    
    conn.close()
    return tables[0][0] if tables else None

def merge_databases(source_db: str, target_db: str):
    """Merge source database into target database, preventing duplicates."""
    
    print("="*80)
    print("Database Merge Tool")
    print("="*80)
    
    # Check if files exist
    if not Path(source_db).exists():
        print(f"ERROR: Source database not found: {source_db}")
        return False
    
    if not Path(target_db).exists():
        print(f"ERROR: Target database not found: {target_db}")
        return False
    
    # Get table info
    source_table = get_table_info(source_db)
    target_table = get_table_info(target_db)
    
    if not source_table or not target_table:
        print("\nERROR: Could not find tables in databases")
        return False
    
    # Connect to both databases
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)
    
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()
    
    print(f"\n{'='*80}")
    print("Starting merge process...")
    print(f"{'='*80}")
    
    # Get all records from source
    source_cursor.execute(f"SELECT * FROM {source_table}")
    source_records = source_cursor.fetchall()
    
    # Get column names
    source_cursor.execute(f"PRAGMA table_info({source_table})")
    columns = [col[1] for col in source_cursor.fetchall()]
    
    print(f"\nColumns: {columns}")
    
    # Find the URL column index (for duplicate detection)
    url_column = None
    for idx, col in enumerate(columns):
        if 'url' in col.lower():
            url_column = idx
            print(f"Using column '{col}' (index {idx}) for duplicate detection")
            break
    
    if url_column is None:
        print("WARNING: No URL column found, will insert all records")
    
    # Get existing URLs from target database
    existing_urls = set()
    if url_column is not None:
        target_cursor.execute(f"SELECT {columns[url_column]} FROM {target_table}")
        existing_urls = {row[0] for row in target_cursor.fetchall()}
        print(f"Found {len(existing_urls)} existing URLs in target database")
    
    # Insert records
    inserted = 0
    skipped = 0
    errors = 0
    
    placeholders = ','.join(['?' for _ in columns])
    insert_sql = f"INSERT INTO {target_table} ({','.join(columns)}) VALUES ({placeholders})"
    
    for record in source_records:
        try:
            # Check for duplicate
            if url_column is not None and record[url_column] in existing_urls:
                skipped += 1
                continue
            
            # Insert record
            target_cursor.execute(insert_sql, record)
            inserted += 1
            
            # Add to existing URLs
            if url_column is not None:
                existing_urls.add(record[url_column])
                
        except Exception as e:
            errors += 1
            print(f"ERROR inserting record: {e}")
    
    # Commit changes
    target_conn.commit()
    
    # Get final counts
    target_cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
    final_count = target_cursor.fetchone()[0]
    
    # Close connections
    source_conn.close()
    target_conn.close()
    
    # Print summary
    print(f"\n{'='*80}")
    print("Merge Complete!")
    print(f"{'='*80}")
    print(f"Records in source database: {len(source_records)}")
    print(f"Records inserted: {inserted}")
    print(f"Records skipped (duplicates): {skipped}")
    print(f"Errors: {errors}")
    print(f"Final record count in target database: {final_count}")
    print(f"{'='*80}")
    
    return True

if __name__ == "__main__":
    source = "data/intel_Core_Ultra_power_specs.db"
    target = "data/intel_cpu_power_specs.db"
    
    print(f"\nMerging {source} → {target}\n")
    
    success = merge_databases(source, target)
    
    if success:
        print("\n✓ Merge completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Merge failed!")
        sys.exit(1)
