"""
Structured logging configuration for Foundry.
"""
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Set up structured logging for the Foundry application.
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional path to log file. If None, logs only to console.
    """
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Root logger
    root_logger = logging.getLogger("foundry")
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (e.g., "foundry.miner", "foundry.curator")
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"foundry.{name}")

