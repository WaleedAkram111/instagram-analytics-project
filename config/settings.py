#"""Global application settings and configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://analyst_user:secure_password_123@localhost:5432/instagram_analytics')
    
    # Instagram API Configuration
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
    INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
    
    # Rate Limiting
    RATE_LIMIT_MIN = int(os.getenv('RATE_LIMIT_MIN', 2))
    RATE_LIMIT_MAX = int(os.getenv('RATE_LIMIT_MAX', 5))
    
    # Analysis Parameters
    DEFAULT_MAX_DEPTH = 2
    DEFAULT_MIN_LIKES = 10000
    DEFAULT_MAX_USERS_PER_LEVEL = 50
    DEFAULT_MAX_POSTS_PER_USER = 10
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/instagram_analytics.log'
    
    # Safety Limits
    MAX_NETWORK_SIZE = 1000
    MAX_POSTS_TO_CHECK = 500
    MAX_API_CALLS_PER_HOUR = 200

settings = Settings()

# ==============================================================================
# DATA MODULE - Database Models and Data Processing
# ==============================================================================
