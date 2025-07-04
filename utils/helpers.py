"""General utility functions"""
import os  # This was missing!
import time
import random
import json
import csv
from typing import Any, Dict, List
from datetime import datetime

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_str(value: Any, default: str = '') -> str:
    """Safely convert value to string"""
    try:
        return str(value) if value is not None else default
    except:
        return default

def format_number(num: int) -> str:
    """Format large numbers with K, M suffixes"""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

def calculate_percentage(part: int, total: int) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def save_json_report(data: Dict[str, Any], filename: str) -> str:
    """Save report data as JSON file"""
    os.makedirs('reports', exist_ok=True)
    filepath = f"reports/{filename}"
    
    # Convert datetime objects to strings
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=json_serializer)
    
    return filepath

def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
    """Export data to CSV file"""
    if not data:
        return None
    
    os.makedirs('reports', exist_ok=True)
    filepath = f"reports/{filename}"
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    return filepath

def clean_instagram_username(username: str) -> str:
    """Clean and validate Instagram username"""
    # Remove @ symbol if present
    username = username.lstrip('@')
    
    # Remove any invalid characters
    import re
    username = re.sub(r'[^a-zA-Z0-9._]', '', username)
    
    return username.lower()

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
            time.sleep(delay)
    
    return None

def clean_instagram_username(username: str) -> str:
    """Clean and validate Instagram username"""
    # Remove @ symbol if present
    username = username.lstrip('@')
    
    # Remove any invalid characters
    import re
    username = re.sub(r'[^a-zA-Z0-9._]', '', username)
    
    return username.lower()

def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = [
        'INSTAGRAM_USERNAME',
        'INSTAGRAM_PASSWORD', 
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True