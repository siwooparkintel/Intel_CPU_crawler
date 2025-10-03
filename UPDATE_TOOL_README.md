# Intel CPU Database Updater

Automated tool for keeping your Intel CPU database up-to-date with the latest products.

## Overview

This tool checks Intel ARK for new processor products and automatically adds them to your database. It's designed to be run periodically (daily, weekly, etc.) to maintain an up-to-date CPU specification database.

## Features

- ✅ **Smart Detection**: Only processes new products not already in database
- ✅ **Duplicate Prevention**: Uses URL matching to avoid duplicate entries
- ✅ **Rate Limiting**: Configurable delays between requests (default: 2.5s)
- ✅ **Dry Run Mode**: Check for new products without modifying database
- ✅ **Comprehensive Logging**: Detailed logs for every update run
- ✅ **Safe Operation**: Automatically skips existing products

## Quick Start

### Option 1: Dry Run (Check Only)
Check for new products without updating the database:

```bash
# Windows
check_for_updates.bat

# Linux/Mac or Direct Python
python update_database.py --dry-run
```

### Option 2: Live Update
Update the database with any new products found:

```bash
# Windows
run_update.bat

# Linux/Mac or Direct Python
python update_database.py
```

## Command Line Usage

```bash
python update_database.py [OPTIONS]

Options:
  --verbose, -v      Show detailed logging
  --dry-run, -d      Check for new products without adding to database
  --delay SECONDS    Delay between requests (default: 2.5)
  -h, --help         Show help message
```

### Examples

```bash
# Check for updates with verbose logging
python update_database.py --verbose --dry-run

# Update database with 3 second delay
python update_database.py --delay 3.0

# Quick update with minimal output
python update_database.py
```

## Output and Logging

The updater provides detailed information:

```
================================================================================
Intel CPU Database Updater
================================================================================
Current database count: 927 CPUs
Found 927 existing URLs in database
Loaded 52 processor family URLs

Checking for new products...
[1/52] Checking: https://www.intel.com/...
  → Found 3 NEW products!
...

Discovery Summary: Found 5 new products across 2 families
================================================================================

Adding 5 new products to database...
  [1/5] Crawling: https://www.intel.com/...
    ✓ Added: Intel® Core™ Ultra 9 Processor 288V

Update Complete!
================================================================================
Duration: 45.2 seconds
New products found: 5
Products successfully added: 5
Database after: 932 CPUs
Net change: +5 CPUs
================================================================================
```

## Scheduling Updates

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., weekly on Monday at 9:00 AM)
4. Action: Start a program
5. Program: `D:\Users\siwoopar\code\Intel_cpu_crawler\run_update.bat`
6. Arguments: `scheduled` (prevents pause)

### Linux/Mac Cron Job

Add to crontab (`crontab -e`):

```bash
# Run every Monday at 9:00 AM
0 9 * * 1 cd /path/to/Intel_cpu_crawler && .venv/bin/python update_database.py

# Run daily at 6:00 AM
0 6 * * * cd /path/to/Intel_cpu_crawler && .venv/bin/python update_database.py
```

## How It Works

1. **Load Existing Data**: Reads all URLs currently in the database
2. **Check Families**: Scans each processor family page for product links
3. **Detect New Products**: Compares found URLs against existing database
4. **Parse New Products**: Extracts specifications from new product pages
5. **Update Database**: Adds new products with full specifications
6. **Report Results**: Provides summary of changes and statistics

## Configuration

The updater uses the same configuration as the main crawler:

- **config/config.yaml**: Request settings, timeouts, user agent
- **data/all_core_processor_urls.txt**: List of processor families to check

## Best Practices

### Update Frequency
- **Production**: Run weekly (Intel releases new products periodically)
- **Development**: Run monthly or as needed
- **Post-Launch**: Run daily for first month after major Intel launch

### Dry Run First
Always do a dry run before live updates to see what will be added:
```bash
python update_database.py --dry-run --verbose
```

### Monitor Logs
Check logs in `logs/` directory after each update:
```bash
# View latest log
ls -lt logs/update_*.log | head -1
cat $(ls -t logs/update_*.log | head -1)
```

### Backup Database
The tool doesn't modify existing records, but it's good practice to backup:
```bash
# Before running updates
cp data/intel_cpu_power_specs.db data/intel_cpu_power_specs_backup_$(date +%Y%m%d).db
```

## Exit Codes

The updater returns different exit codes for automation:

- **0**: Success (no updates needed or update completed successfully)
- **1**: Error (missing files, connection issues, etc.)
- **2**: Partial success (some products added, some failed)

## Troubleshooting

### No new products found
This is normal if Intel hasn't released new products since last update.

### Connection errors
- Check internet connection
- Verify Intel ARK website is accessible
- Increase delay between requests (`--delay 5.0`)

### Products not added
- Check logs for specific errors
- Verify database isn't locked by another process
- Ensure write permissions on database file

### Missing family URLs
Update `data/all_core_processor_urls.txt` with latest processor families from Intel ARK.

## Integration Examples

### PowerShell Script
```powershell
# Run update and email results
$output = & python update_database.py --verbose
if ($LASTEXITCODE -eq 0) {
    Send-MailMessage -To "admin@company.com" -Subject "CPU DB Updated" -Body $output
}
```

### Python Integration
```python
from update_database import DatabaseUpdater

updater = DatabaseUpdater()
results = updater.run_update(dry_run=False)

print(f"Added {results['products_added']} new CPUs")
print(f"Total in database: {results['final_count']}")
```

## Files Created

- **update_database.py**: Main updater script
- **run_update.bat**: Windows batch script for live updates
- **check_for_updates.bat**: Windows batch script for dry runs
- **logs/update_YYYYMMDD_HHMMSS.log**: Log files (created automatically)

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run with `--verbose` flag for detailed output
3. Test with `--dry-run` first
4. Verify database backup exists before major updates

## Version History

- **v1.0** (2025-10-02): Initial release
  - Smart new product detection
  - Dry run mode
  - Automated logging
  - Windows batch scripts
