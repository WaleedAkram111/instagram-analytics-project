from instagrapi import Client
import os
import time
import random
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

class InstagramClient:
    def __init__(self):
        self.client = Client()
        self.login()
    
    def login(self):
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            raise ValueError("Instagram credentials not found in environment variables")
        
        try:
            self.client.login(username, password)
            logger.info("Successfully logged in to Instagram")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise
    
    def get_user_info(self, username):
        """Get user information by username"""
        try:
            user_id = self.client.user_id_from_username(username)
            user_info = self.client.user_info(user_id)
            return user_info
        except Exception as e:
            logger.error(f"Error getting user info for {username}: {e}")
            return None
    
    def get_user_following(self, user_id, amount=100):
        """Get users that user_id is following"""
        try:
            following = self.client.user_following(user_id, amount=amount)
            return following
        except Exception as e:
            logger.error(f"Error getting following for {user_id}: {e}")
            return {}
    
    def get_user_medias(self, user_id, amount=20):
        """Get recent posts from user"""
        try:
            medias = self.client.user_medias(user_id, amount=amount)
            return medias
        except Exception as e:
            logger.error(f"Error getting medias for {user_id}: {e}")
            return []
    
    def get_media_likers(self, media_id, amount=100):
        """Get users who liked a post"""
        try:
            likers = self.client.media_likers(media_id, amount=amount)
            return likers
        except Exception as e:
            logger.error(f"Error getting likers for {media_id}: {e}")
            return []
    
    def rate_limit_wait(self):
        """Wait with random delay for rate limiting"""
        min_delay = int(os.getenv('RATE_LIMIT_MIN', 2))
        max_delay = int(os.getenv('RATE_LIMIT_MAX', 5))
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)