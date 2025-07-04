"""Database setup and initialization script - FIXED VERSION with proper indexes"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
import logging

# Setup basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Now import our modules
try:
    from data.models import Base
    from config.settings import settings
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.info("Make sure you have __init__.py files in all directories and your .env file is configured")
    sys.exit(1)

def create_database():
    """Create the main database if it doesn't exist"""
    # Parse database URL to get connection params
    db_url = settings.DATABASE_URL
    # Extract database name from URL
    db_name = db_url.split('/')[-1]
    base_url = db_url.rsplit('/', 1)[0]
    
    try:
        # Connect to postgres database to create our target database
        postgres_url = base_url + '/postgres'
        conn = psycopg2.connect(postgres_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"Created database: {db_name}")
        else:
            logger.info(f"Database {db_name} already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def create_tables():
    """Create all tables from models"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(engine)
        logger.info("All tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def create_indexes():
    """Create additional indexes for performance"""
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_user_network_source ON user_network(source_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_network_target ON user_network(target_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_network_depth ON user_network(network_depth)",
        "CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_posts_like_count ON posts(like_count)",
        "CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(post_date)",
        "CREATE INDEX IF NOT EXISTS idx_likes_target_user ON target_user_likes(target_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_likes_post ON target_user_likes(post_id)",
        "CREATE INDEX IF NOT EXISTS idx_likes_timestamp ON target_user_likes(like_timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_hashtags_user ON hashtag_analysis(target_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_hashtags_tag ON hashtag_analysis(hashtag)"
    ]
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            for sql in indexes_sql:
                try:
                    # Use text() wrapper for raw SQL
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"Created index: {sql.split()[5]}")  # Extract index name
                except Exception as e:
                    logger.warning(f"Could not create index: {sql[:50]}... Error: {e}")
        logger.info("All indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting database setup...")
        
        # Test if we can import settings
        logger.info(f"Database URL: {settings.DATABASE_URL[:30]}...")
        
        create_database()
        create_tables()
        create_indexes()
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your .env file has correct DATABASE_URL")
        print("3. Verify all __init__.py files exist")
        print("4. Make sure your virtual environment is activated")
        sys.exit(1)