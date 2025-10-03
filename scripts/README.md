# Utility Scripts

This directory contains utility scripts for managing the Intel CPU database.

## Scripts Overview

### `update_database.py`
**Purpose**: Automated periodic checker for new Intel products  
**Usage**: 
```bash
# Dry run - check for new products without updating
python scripts/update_database.py --dry-run --verbose

# Live update - add new products to database
python scripts/update_database.py --verbose
```
**Features**:
- Compares Intel ARK URLs against existing database
- Finds and adds new products automatically
- Rate limiting with configurable delay (default 2.5s)
- Duplicate prevention
- Comprehensive logging

**Related Files**:
- `check_for_updates.bat` - Quick dry run from project root
- `run_update.bat` - Full update with logging

---

### `crawl_all_families.py`
**Purpose**: Mass collection script for all Intel processor families  
**Usage**:
```bash
python scripts/crawl_all_families.py
```
**Features**:
- Reads URLs from `data/all_core_processor_urls.txt`
- Processes all 52 processor families
- Progress tracking
- 2.5s delay between requests to respect rate limits

**When to Use**:
- Initial database population
- Rebuilding database from scratch
- Adding multiple new processor families

---

### `update_code_names.py`
**Purpose**: Migration script to populate code_name field from additional_specs  
**Usage**:
```bash
python scripts/update_code_names.py
```
**Features**:
- Extracts code_name from additional_specs JSON field
- Removes "Products formerly" prefix automatically
- Shows statistics by code name distribution
- One-time migration (already completed for current database)

**When to Use**:
- After database restore from backup
- If code names need to be regenerated

---

### `merge_databases.py`
**Purpose**: Merge two SQLite databases while preventing duplications  
**Usage**:
```bash
python scripts/merge_databases.py
```
**Features**:
- URL-based deduplication
- Preserves all data from both databases
- Shows statistics of merged vs skipped records

**When to Use**:
- Combining databases from different sources
- Consolidating separate crawling efforts
- Database migration

---

## Quick Reference

| Task | Command |
|------|---------|
| Check for new products | `check_for_updates.bat` or `python scripts/update_database.py --dry-run` |
| Update database | `run_update.bat` or `python scripts/update_database.py` |
| Mass crawl all families | `python scripts/crawl_all_families.py` |
| Update code names | `python scripts/update_code_names.py` |
| Merge databases | `python scripts/merge_databases.py` |

## Best Practices

1. **Always run dry-run first** before live updates to verify what will be added
2. **Use rate limiting** (2.5s delay) to respect Intel's servers
3. **Check logs** in `logs/` directory after each run
4. **Backup database** before major operations using database backup tool

## Documentation

For detailed information, see:
- `UPDATE_TOOL_README.md` - Comprehensive update tool documentation
- `UPDATER_QUICKSTART.md` - Quick start guide
- `TERMINOLOGY_GUIDE.md` - Technical terminology reference
