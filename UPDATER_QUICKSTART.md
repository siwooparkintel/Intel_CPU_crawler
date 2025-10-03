# Database Update Tool - Quick Reference

## What You've Built

A complete automated system for keeping your Intel CPU database up-to-date with new products.

## Files Created

1. **update_database.py** - Main Python script
   - Checks Intel ARK for new products
   - Compares against existing database
   - Adds only new products (prevents duplicates)
   - Full logging and error handling

2. **run_update.bat** - Windows quick launcher
   - One-click database update
   - Creates timestamped log files
   - Shows success/failure status

3. **check_for_updates.bat** - Dry-run checker
   - Check for new products without updating
   - Safe to run anytime
   - Shows what would be added

4. **UPDATE_TOOL_README.md** - Complete documentation
   - Usage instructions
   - Scheduling guide
   - Troubleshooting tips

## How to Use

### Check for New Products (Safe)
```bash
# Double-click this file or run:
check_for_updates.bat
```
This shows what new products are available WITHOUT changing your database.

### Update Database (Live)
```bash
# Double-click this file or run:
run_update.bat
```
This actually adds new products to your database.

### Command Line (Advanced)
```bash
# Python directly with options
python update_database.py --verbose --dry-run
python update_database.py --delay 3.0
```

## What It Does

1. ✅ Loads all 927 existing URLs from your database
2. ✅ Checks all 52 processor families from Intel ARK
3. ✅ Finds new products not in database
4. ✅ Parses specifications for new products
5. ✅ Adds them to database (avoiding duplicates)
6. ✅ Reports results with statistics

## Current Status

- **Database**: 927 CPUs (as of Oct 2, 2025)
- **Families Monitored**: 52 processor families
- **Last Full Crawl**: Successfully completed
- **Backup Created**: `intel_cpu_power_specs_backup_20251002_175309.db`

## Recommended Usage

### For Regular Updates
Run **weekly** or **bi-weekly**:
```bash
check_for_updates.bat    # See what's new
run_update.bat           # If you want to add them
```

### For Monitoring Intel Launches
Run **daily** during major Intel launch periods (like new Core Ultra releases)

### For Production Systems
Set up Windows Task Scheduler to run `run_update.bat` automatically

## Example Output

```
================================================================================
Intel CPU Database Updater
================================================================================
Current database count: 927 CPUs
Checking for new products...

[1/52] Checking: Intel Core Ultra Series 2
  → No new products (checked 44 CPUs)
[2/52] Checking: Intel Core Ultra Series 1
  → No new products (checked 20 CPUs)
...
[52/52] Checking: 4th Gen Intel Core i5
  → Found 3 NEW products!

Discovery Summary: Found 3 new products across 1 families

Adding 3 new products to database...
  [1/3] Crawling: Intel® Core™ i5-4590T
    ✓ Added: Intel® Core™ i5-4590T Processor
  [2/3] Crawling: Intel® Core™ i5-4460S
    ✓ Added: Intel® Core™ i5-4460S Processor
  [3/3] Crawling: Intel® Core™ i5-4440S
    ✓ Added: Intel® Core™ i5-4440S Processor

Update Complete!
================================================================================
Products successfully added: 3
Database after: 930 CPUs
Net change: +3 CPUs
================================================================================
```

## Safety Features

✅ **Duplicate Prevention**: Uses URL matching - never adds same CPU twice
✅ **Dry Run Mode**: Test before making changes
✅ **Database Backup**: Keep backups before major updates
✅ **Rate Limiting**: 2.5s delay between requests (customizable)
✅ **Error Handling**: Continues on errors, logs everything

## Logs Location

All update logs are saved in: `logs/update_YYYYMMDD_HHMMSS.log`

View latest log:
```powershell
Get-Content (Get-ChildItem logs\update_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

## Quick Troubleshooting

**No new products found?**
- Normal! Intel doesn't release new CPUs every day
- Try again after Intel announcements

**Connection errors?**
- Check internet connection
- Intel ARK might be temporarily down
- Increase delay: `python update_database.py --delay 5.0`

**Want to test?**
- Always use dry-run first: `check_for_updates.bat`
- Review logs before running live update

## Next Steps

1. ✅ **Test it**: Run `check_for_updates.bat` now
2. ⏰ **Schedule it**: Set up weekly task scheduler
3. 📧 **Monitor it**: Check logs after each run
4. 💾 **Backup**: Keep regular database backups

## Integration Options

### Task Scheduler (Recommended)
- Frequency: Weekly on Mondays at 9 AM
- Program: `D:\Users\siwoopar\code\Intel_cpu_crawler\run_update.bat`
- Arguments: `scheduled`

### Email Notifications
Add to your batch file:
```batch
if %ERRORLEVEL% EQU 0 (
    powershell -Command "Send-MailMessage -To 'you@email.com' -From 'crawler@company.com' -Subject 'CPU DB Updated' -Body 'Database updated successfully' -SmtpServer 'smtp.company.com'"
)
```

### Python Script Integration
```python
from update_database import DatabaseUpdater

updater = DatabaseUpdater()
results = updater.run_update(dry_run=False)

if results['products_added'] > 0:
    print(f"Added {results['products_added']} new CPUs!")
    # Send notification, trigger downstream processes, etc.
```

## Contact & Support

- Check logs in `logs/` directory
- See UPDATE_TOOL_README.md for detailed docs
- Test with --dry-run before live updates
