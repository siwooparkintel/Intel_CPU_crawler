# Data Directory

This directory contains scraped Intel CPU specifications and power modeling data.

## Files:
- `intel_cpu_power_specs.db` - Primary SQLite database with structured CPU specifications
- `cpu_power_modeling_data.json` - Exported data optimized for power prediction modeling
- `intel_cpus.json` - Legacy JSON export (for backward compatibility)

## Database Schema:
The SQLite database contains comprehensive CPU specifications including:
- Processor details (name, cores, threads, frequencies)
- Power specifications (base power, turbo power, minimum assured power)
- Cache information (L1, L2, L3 cache sizes)
- Memory and graphics support
- Manufacturing details (lithography, launch date)