"""Logging configuration and utilities"""
import logging
import os
from datetime import datetime
from config.settings import settings

def setup_logger():
    """Setup application-wide logging"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('instagram_analytics')

def get_logger(name: str):
    """Get logger for specific module"""
    return logging.getLogger(name)