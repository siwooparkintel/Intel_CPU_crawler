"""
Utility functions for Intel CPU Crawler
Common helper functions and utilities.
"""

import logging
import colorlog
import requests
from typing import Dict, Any


def setup_logging(level: str = 'INFO') -> logging.Logger:
    """
    Set up colored logging for the application.
    
    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    from datetime import datetime
    log_filename = f"logs/crawler_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_headers(user_agent: str = None) -> Dict[str, str]:
    """
    Get HTTP headers for requests.
    
    Args:
        user_agent: Custom user agent string
        
    Returns:
        Dictionary of HTTP headers
    """
    if user_agent is None:
        user_agent = 'Intel CPU Crawler 1.0'
    
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    return headers


def handle_request_error(error: Exception, url: str, logger: logging.Logger):
    """
    Handle and log request errors appropriately.
    
    Args:
        error: The exception that occurred
        url: URL that caused the error
        logger: Logger instance
    """
    if isinstance(error, requests.exceptions.Timeout):
        logger.error(f"Request timeout for URL: {url}")
    elif isinstance(error, requests.exceptions.ConnectionError):
        logger.error(f"Connection error for URL: {url}")
    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = getattr(error.response, 'status_code', 'Unknown')
        logger.error(f"HTTP error {status_code} for URL: {url}")
    elif isinstance(error, requests.exceptions.RequestException):
        logger.error(f"Request error for URL {url}: {str(error)}")
    else:
        logger.error(f"Unexpected error for URL {url}: {str(error)}")


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    from urllib.parse import urlparse
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def clean_text(text: str) -> str:
    """
    Clean and normalize text extracted from HTML.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    import re
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-\.,;:()&+/]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def safe_extract_number(text: str, pattern: str) -> str:
    """
    Safely extract numeric values from text using regex.
    
    Args:
        text: Text to search in
        pattern: Regex pattern to match
        
    Returns:
        Extracted number as string, or empty string if not found
    """
    import re
    
    if not text:
        return ""
    
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else ""
    except Exception:
        return ""