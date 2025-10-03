# Intel CPU Crawler

A comprehensive Python-based web crawler for extracting Intel CPU specifications from official Intel specification pages, optimized for SoC power prediction modeling.

## 🚀 Features

### Advanced CPU Specification Extraction
- **Comprehensive Specification Parsing**: Extracts 29+ power-related specifications including TDP, turbo power, core counts, frequencies
- **Power Modeling Focus**: Optimized for SoC power prediction with detailed power characteristics
- **Enhanced Lithography Detection**: Accurate process technology extraction (Intel 3, Intel 7, 14nm, etc.)
- **Hybrid Architecture Support**: P-core/E-core breakdowns for modern Intel processors

### Smart Page Detection
- **Specification Page Targeting**: Focuses on actual CPU spec pages (`/sku/*/specifications.html`) instead of promotional content
- **US English Filtering**: Processes only US English pages to avoid international duplicates
- **False Positive Prevention**: Excludes marketing pages, documentation, and overview content

### Database & Export
- **SQLite Database**: Structured storage optimized for power modeling data
- **Multiple Export Formats**: JSON, CSV, and specialized modeling data exports
- **Duplicate Prevention**: Automatic detection and prevention of duplicate entries
- **Power Statistics**: Built-in analytics for power distribution and technology trends

### CLI Interface
- **Multiple Commands**: Crawl, search, export, database management
- **Configurable Parameters**: Max pages, delays, output formats, verbosity
- **Real-time Monitoring**: Comprehensive logging and progress tracking

## 📊 Current Capabilities

- **Process Technologies**: Intel 3, Intel 7, Intel 10, 14nm, and TSMC nodes
- **CPU Families**: Core Ultra, Core (14th gen), Xeon 6th gen, Atom
- **Power Data**: Base power, turbo power, minimum assured power
- **Architecture**: Hybrid P-core/E-core configurations
- **Memory Support**: DDR5/DDR4 specifications and channels
- **Graphics**: Integrated GPU specifications and frequencies

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/siwooparkintel/Intel_CPU_crawler.git
cd Intel_cpu_crawler
```

2. **Create virtual environment:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Basic Crawling
```bash
# Crawl with default settings
python main.py crawl

# Crawl with custom parameters
python main.py crawl --max-pages 20 --delay 1.5 --verbose
```

### Database Operations
```bash
# View comprehensive database statistics
python main.py db-stats

# Search for specific CPUs
python main.py search "Core Ultra"
python main.py search "Xeon"

# Clear database (with confirmation)
python main.py clear-db --yes
```

### Data Export
```bash
# Export data optimized for power modeling
python main.py export-modeling-data

# Standard JSON export is automatic after crawling
```

### Example Output
```
📊 DATABASE STATISTICS
==================================================
Total CPUs: 20

⚡ POWER STATISTICS:
  CPUs with power data: 7
  Average base power: 32.14 W
  Base power range: 15.0 - 45.0 W
  Average turbo power: 89.29 W
  Turbo power range: 55.0 - 115.0 W

🖥️  CORE COUNT DISTRIBUTION:
  10_cores: 4 CPUs
  14_cores: 3 CPUs
  24_cores: 2 CPUs

🔬 PROCESS TECHNOLOGY:
  Intel 3: 9 CPUs
  Intel 7: 7 CPUs
  14 nm: 1 CPUs
```

## ⚙️ Configuration

### Main Configuration (`config/config.yaml`)
```yaml
# Database settings
database:
  filename: "intel_cpu_power_specs.db"
  
# Crawler settings
crawler:
  max_pages: 10
  request_delay: 1.0
  
# URL filtering (only process US English Intel pages)
url_filtering:
  required_path: "/us/en/"
  required_domain: "intel.com"
```

### URL Configuration

**Main Settings** (`config/config.yaml`):
```yaml
# Base URLs for crawling (US English only)
base_urls:
  - "https://www.intel.com/content/www/us/en/products/details/processors/core.html"
  - "https://www.intel.com/content/www/us/en/products/details/processors/core-ultra.html"
```

**Processor Family URLs** (`data/all_core_processor_urls.txt`):
```
https://www.intel.com/content/www/us/en/ark/products/series/241071/...
https://www.intel.com/content/www/us/en/ark/products/series/230496/...
# One URL per line for each processor family (52 families)
```

## 📁 Project Structure

```
Intel_cpu_crawler/
├── 📁 src/                          # Core source code
│   ├── crawler.py                   # Main crawling orchestration
│   ├── parser.py                    # Enhanced specification extraction
│   ├── database_manager.py          # SQLite database operations
│   ├── data_manager.py              # File-based data management
│   └── utils.py                     # Utilities and logging
├── 📁 config/                       # Configuration files
│   └── config.yaml                  # Main settings (URLs, timeouts, etc.)
├── 📁 data/                         # Output data storage
│   ├── intel_cpu_power_specs.db     # SQLite database
│   ├── all_core_processor_urls.txt  # Processor family URLs
│   ├── intel_cpus.json              # JSON export
│   └── cpu_power_modeling_data.json # Power modeling data
├── 📁 logs/                         # Application logs
├── 📁 tests/                        # Unit tests
├── main.py                          # CLI entry point
└── requirements.txt                 # Dependencies
```

## 🎯 Use Cases

### SoC Power Prediction Modeling
- Extract comprehensive power specifications for machine learning models
- Analyze power trends across different process technologies
- Study hybrid architecture power characteristics
- Build datasets for Intel future product power estimation

### Competitive Analysis
- Compare power efficiency across CPU generations
- Analyze process technology adoption patterns
- Track specification evolution over time

### Research & Development
- Gather data for academic research on processor architectures
- Benchmark power characteristics for system design
- Validate power modeling assumptions with real specifications

## 🔧 Advanced Features

### Enhanced Lithography Detection
- Multiple pattern matching for process technology extraction
- Exclusion of false positives (instruction sets, non-process terms)
- Support for Intel naming conventions and TSMC nodes
- Validation against known process technology patterns

### Smart URL Filtering
- Priority-based URL discovery (specification pages first)
- Marketing content exclusion
- Duplicate URL prevention
- US English page restriction

### Power-Focused Parsing
- 29+ power-related specification patterns
- Hybrid architecture support (P-core/E-core)
- Multiple power states (base, turbo, minimum assured)
- Thermal and package specifications

## 📈 Data Quality

- **Specification Coverage**: 35% of crawled CPUs have complete power data
- **Process Technology Detection**: 95% accuracy with restricted patterns
- **Duplicate Prevention**: URL-based deduplication with 100% effectiveness
- **US English Filtering**: Eliminates international page duplicates

## � Testing

The project includes a comprehensive testing framework to ensure code quality and system health.

### Quick Test
```bash
# Run integration tests (recommended after any changes)
python run_tests.py --integration

# Run with verbose output
python run_tests.py --integration --verbose
```

### Complete Test Suite
```bash
# Run all tests (integration + unit)
python run_tests.py

# Run only unit tests
python run_tests.py --unit
```

### Test Coverage
- **Integration Tests**: Complete system workflow testing
- **Database Operations**: CRUD operations and data integrity
- **Configuration Loading**: YAML parsing and validation
- **Utility Functions**: All helper functions tested
- **CLI Interface**: Command structure verification

For detailed testing documentation, see [TESTING.md](TESTING.md).

## �🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. **Run tests**: `python run_tests.py --integration`
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Intel Corporation for providing comprehensive CPU specification data
- Built for SoC power prediction modeling research and development