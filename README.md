# Intel CPU Crawler

A Python web scraping project designed to crawl Intel CPU specifications and data from Intel's official website.

## Features

- **Power-Focused Data Extraction**: Enhanced parser specifically designed for SoC power prediction modeling
- **SQLite Database**: Lightweight database optimized for power-related CPU specifications
- **Duplicate Prevention**: Automatic deduplication based on CPU URLs
- **Multiple Export Formats**: JSON, CSV, and specialized modeling data export
- **Comprehensive CLI**: Command-line interface for crawling, database management, and data export
- **Power Statistics**: Built-in analytics for power consumption patterns
- **Configuration Management**: Flexible YAML-based configuration system
- **Robust Logging**: Detailed logging for debugging and monitoring

## Project Structure

```
Intel_cpu_crawler/
├── src/
│   ├── __init__.py
│   ├── crawler.py          # Main crawler logic
│   ├── parser.py           # Power-focused HTML parsing
│   ├── database_manager.py # SQLite database for power specs
│   ├── data_manager.py     # File-based data storage
│   └── utils.py            # Utility functions
├── config/
│   ├── config.yaml         # Configuration file with database settings
│   └── urls.yaml           # Target URLs
├── data/
│   ├── intel_cpu_power_specs.db    # SQLite database
│   ├── cpu_power_modeling_data.json # Exported modeling data
│   └── README.md
├── logs/                   # Log files
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
└── main.py                 # CLI entry point
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Intel_cpu_crawler
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Crawling
Run the crawler with default settings (includes database storage):
```bash
python main.py crawl
```

Run with specific options:
```bash
python main.py crawl --max-pages 50 --delay 2 --verbose
```

Disable database storage:
```bash
python main.py crawl --no-database --output-format csv
```

### Database Management
View database statistics:
```bash
python main.py db-stats
```

Search for specific CPUs:
```bash
python main.py search "Core i7"
python main.py search "Ultra"
```

Export data for power prediction modeling:
```bash
python main.py export-modeling-data --output modeling_data.json
```

### Power Prediction Modeling Data
The exported modeling data includes critical specifications for SoC power prediction:
- **Power Specifications**: Base power, turbo power, minimum assured power
- **Core Architecture**: Performance cores, efficiency cores, total cores
- **Frequency Data**: Base frequency, max turbo frequency per core type
- **Process Information**: Lithography, thermal specifications
- **System Configuration**: Memory channels, cache sizes, integrated graphics

## Configuration

Edit `config/config.yaml` to customize:
- Request delays and timeouts
- Database settings (path, backup options)
- Output formats and directories
- Logging levels and file rotation
- Target CPU specifications for extraction
- User agent strings

### Key Power Modeling Specifications Extracted:
- **Core Architecture**: Total cores, P-cores, E-cores, threads
- **Power Consumption**: Base power, turbo power, minimum assured power, TDP
- **Frequency Scaling**: Base frequency, max turbo frequency per core type  
- **Process Technology**: Lithography node, manufacturing process
- **Thermal Management**: Max operating temperature, TJunction
- **Memory Subsystem**: Memory types, channels, maximum capacity, speed
- **Integrated Graphics**: GPU frequency, execution units, Xe cores
- **AI Processing**: NPU specifications, TOPS performance
- **Package Information**: Socket type, package dimensions

## Development

- Follow PEP 8 style guidelines
- Add unit tests for new functionality
- Update documentation for significant changes
- Use proper error handling and logging

## License

This project is for educational purposes only. Please respect Intel's robots.txt and terms of service.