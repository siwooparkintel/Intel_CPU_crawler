#!/usr/bin/env python3
"""
Intel CPU Crawler - Main Entry Point
Crawls Intel CPU specifications and data from Intel's official website.
"""

import click
import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from crawler import IntelCpuCrawler
from utils import setup_logging





@click.group()
def cli():
    """Intel CPU Crawler - Power Specification Database Tool"""
    pass

@cli.command()
@click.option('--output-format', '-f', 
              type=click.Choice(['json', 'csv', 'both']), 
              default='json',
              help='Output format for scraped data')
@click.option('--output-dir', '-o', 
              type=click.Path(), 
              default='data',
              help='Output directory for scraped data')
@click.option('--delay', '-d', 
              type=float, 
              default=1.0,
              help='Delay between requests in seconds')
@click.option('--max-pages', '-m', 
              type=int, 
              default=10,
              help='Maximum number of pages to crawl')
@click.option('--verbose', '-v', 
              is_flag=True,
              help='Enable verbose logging')
@click.option('--config', '-c', 
              type=click.Path(exists=True),
              default='config/config.yaml',
              help='Path to configuration file')
@click.option('--use-database/--no-database', 
              default=True,
              help='Enable/disable database storage')
def crawl(output_format, output_dir, delay, max_pages, verbose, config, use_database):
    """Crawl Intel CPU specifications and store in database."""
    # Setup logging
    log_level = 'DEBUG' if verbose else 'INFO'
    logger = setup_logging(log_level)
    
    logger.info("Starting Intel CPU Crawler")
    logger.info(f"Output format: {output_format}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Request delay: {delay}s")
    logger.info(f"Max pages: {max_pages}")
    logger.info(f"Database enabled: {use_database}")
    
    try:
        # Initialize crawler
        crawler = IntelCpuCrawler(
            config_path=config,
            output_dir=output_dir,
            delay=delay,
            max_pages=max_pages
        )
        
        # Override database setting if specified
        if not use_database and hasattr(crawler, 'db_manager'):
            crawler.db_manager = None
            crawler.use_database = False
            logger.info("Database storage disabled")
        
        # Run crawler
        results = crawler.crawl()
        
        # Save results to files
        if results:
            crawler.save_results(results, output_format)
            logger.info(f"Crawling completed successfully. Found {len(results)} CPU entries.")
        else:
            logger.warning("No results found")
        
    except KeyboardInterrupt:
        logger.info("Crawling interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Crawling failed: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--db-path', 
              default='data/intel_cpu_power_specs.db',
              help='Path to database file')
def db_stats(db_path):
    """Show database statistics."""
    try:
        from src.database_manager import PowerSpecDatabaseManager
        from src.utils import setup_logging
        
        setup_logging('INFO')
        logger = logging.getLogger(__name__)
        
        db_manager = PowerSpecDatabaseManager(db_path)
        
        # Get basic count
        count = db_manager.get_cpu_count()
        logger.info(f"Total CPUs in database: {count}")
        
        if count > 0:
            # Get power statistics
            stats = db_manager.get_power_statistics()
            
            print(f"\n📊 DATABASE STATISTICS")
            print(f"{'='*50}")
            print(f"Total CPUs: {count}")
            
            if 'power' in stats:
                power_stats = stats['power']
                print(f"\n⚡ POWER STATISTICS:")
                print(f"  CPUs with power data: {power_stats['total_cpus_with_power_data']}")
                if power_stats['avg_base_power_w']:
                    print(f"  Average base power: {power_stats['avg_base_power_w']} W")
                    print(f"  Base power range: {power_stats['min_base_power_w']} - {power_stats['max_base_power_w']} W")
                if power_stats['avg_turbo_power_w']:
                    print(f"  Average turbo power: {power_stats['avg_turbo_power_w']} W")
                    print(f"  Turbo power range: {power_stats['min_turbo_power_w']} - {power_stats['max_turbo_power_w']} W")
            
            if 'core_distribution' in stats:
                print(f"\n🖥️  CORE COUNT DISTRIBUTION:")
                for core_config, count in stats['core_distribution'].items():
                    print(f"  {core_config}: {count} CPUs")
            
            if 'process_technology' in stats:
                print(f"\n🔬 PROCESS TECHNOLOGY:")
                for tech, count in stats['process_technology'].items():
                    print(f"  {tech}: {count} CPUs")
        
    except Exception as e:
        click.echo(f"Error accessing database: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--db-path', 
              default='data/intel_cpu_power_specs.db',
              help='Path to database file')
@click.option('--output', '-o',
              default='data/cpu_power_modeling_data.json',
              help='Output file for modeling data')
def export_modeling_data(db_path, output):
    """Export CPU data for power prediction modeling."""
    try:
        from src.database_manager import PowerSpecDatabaseManager
        from src.utils import setup_logging
        
        setup_logging('INFO')
        logger = logging.getLogger(__name__)
        
        db_manager = PowerSpecDatabaseManager(db_path)
        
        success = db_manager.export_for_modeling(output)
        if success:
            logger.info(f"Successfully exported modeling data to {output}")
        else:
            logger.error("Failed to export modeling data")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error exporting data: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--db-path', 
              default='data/intel_cpu_power_specs.db',
              help='Path to database file')
@click.confirmation_option(prompt='Are you sure you want to clear all data from the database?')
def clear_db(db_path):
    """Clear all data from the database."""
    try:
        from src.database_manager import PowerSpecDatabaseManager
        from src.utils import setup_logging
        import os
        
        setup_logging('INFO')
        logger = logging.getLogger(__name__)
        
        # Remove the database file to start fresh
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Removed existing database: {db_path}")
        
        # Initialize new clean database
        db_manager = PowerSpecDatabaseManager(db_path)
        logger.info(f"Created new clean database: {db_path}")
        
        count = db_manager.get_cpu_count()
        logger.info(f"Database initialized with {count} CPUs")
        
    except Exception as e:
        click.echo(f"Error clearing database: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--db-path', 
              default='data/intel_cpu_power_specs.db',
              help='Path to database file')
@click.argument('name_pattern')
def search(db_path, name_pattern):
    """Search for CPUs by name pattern."""
    try:
        from src.database_manager import PowerSpecDatabaseManager
        from src.utils import setup_logging
        
        setup_logging('INFO')
        
        db_manager = PowerSpecDatabaseManager(db_path)
        results = db_manager.get_cpu_by_name(name_pattern)
        
        if results:
            print(f"\n🔍 Found {len(results)} CPUs matching '{name_pattern}':")
            print("="*60)
            
            for cpu in results:
                print(f"\n📦 {cpu['name']}")
                if cpu['processor_base_power']:
                    print(f"   Base Power: {cpu['processor_base_power']} W")
                if cpu['maximum_turbo_power']:
                    print(f"   Turbo Power: {cpu['maximum_turbo_power']} W")
                if cpu['total_cores']:
                    print(f"   Cores: {cpu['total_cores']} ({cpu['performance_cores']}P + {cpu['efficiency_cores']}E)")
                if cpu['max_turbo_frequency']:
                    print(f"   Max Frequency: {cpu['max_turbo_frequency']} GHz")
                if cpu['lithography']:
                    print(f"   Process: {cpu['lithography']}")
                if cpu['launch_date']:
                    print(f"   Launch: {cpu['launch_date']}")
        else:
            print(f"No CPUs found matching '{name_pattern}'")
            
    except Exception as e:
        click.echo(f"Error searching database: {str(e)}", err=True)
        sys.exit(1)



if __name__ == '__main__':
    cli()