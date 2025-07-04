import psycopg2
from config.database import get_db
from config.instagram_client import InstagramClient
from utils.logger import get_logger
from datetime import datetime
import json

logger = get_logger(__name__)

class UserDataCollector:
    def __init__(self):
        self.ig_client = InstagramClient()
        self.db = next(get_db())
    
    def store_user(self, user_data):
        """Store user information in database"""
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO users (user_id, username, full_name, follower_count, 
                                 following_count, is_private, profile_pic_url, bio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    follower_count = EXCLUDED.follower_count,
                    following_count = EXCLUDED.following_count,
                    last_updated = CURRENT_TIMESTAMP;
            """
            
            cursor.execute(query, (
                user_data['user_id'],
                user_data['username'],
                user_data.get('full_name', ''),
                user_data.get('follower_count', 0),
                user_data.get('following_count', 0),
                user_data.get('is_private', False),
                user_data.get('profile_pic_url', ''),
                user_data.get('bio', '')
            ))
            
            self.db.commit()
            logger.info(f"Stored user: {user_data['username']}")
            
        except Exception as e:
            logger.error(f"Error storing user {user_data.get('username', 'unknown')}: {e}")
            self.db.rollback()
    
    def store_network_relationship(self, source_user_id, target_user_id, depth):
        """Store relationship between users"""
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO user_network (source_user_id, target_user_id, 
                                        relationship_type, network_depth)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (source_user_id, target_user_id, relationship_type) DO NOTHING;
            """
            
            cursor.execute(query, (source_user_id, target_user_id, 'following', depth))
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing network relationship: {e}")
            self.db.rollback()
    
    def store_post(self, post_data):
        """Store post information"""
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO posts (post_id, author_user_id, post_url, caption, 
                                 like_count, comment_count, post_type, hashtags, 
                                 mentions, location, post_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (post_id) DO UPDATE SET
                    like_count = EXCLUDED.like_count,
                    comment_count = EXCLUDED.comment_count,
                    last_updated = CURRENT_TIMESTAMP;
            """
            
            cursor.execute(query, (
                post_data['post_id'],
                post_data['author_user_id'],
                post_data['post_url'],
                post_data.get('caption', ''),
                post_data.get('like_count', 0),
                post_data.get('comment_count', 0),
                post_data.get('post_type', 'photo'),
                post_data.get('hashtags', []),
                post_data.get('mentions', []),
                post_data.get('location', ''),
                post_data.get('post_date', datetime.now())
            ))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing post {post_data.get('post_id', 'unknown')}: {e}")
            self.db.rollback()
    
    def store_user_like(self, like_data):
        """Store target user like"""
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO target_user_likes (target_user_id, post_id, 
                                             like_timestamp, network_depth, 
                                             post_category, discovery_method)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (target_user_id, post_id) DO NOTHING;
            """
            
            cursor.execute(query, (
                like_data['target_user_id'],
                like_data['post_id'],
                like_data.get('like_timestamp', datetime.now()),
                like_data.get('network_depth', 1),
                like_data.get('post_category', 'general'),
                like_data.get('discovery_method', 'network_traversal')
            ))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing user like: {e}")
            self.db.rollback()
    
    def build_social_network(self, target_user_id, max_depth=2, max_users_per_level=50):
        """Build social network using BFS"""
        logger.info(f"Building social network for user {target_user_id}")
        
        queue = [(target_user_id, 0)]
        visited = set()
        network_users = []
        
        while queue and len(network_users) < 1000:  # Safety limit
            current_user_id, depth = queue.pop(0)
            
            if current_user_id in visited or depth >= max_depth:
                continue
            
            visited.add(current_user_id)
            
            # Get following list
            following = self.ig_client.get_user_following(current_user_id, amount=max_users_per_level)
            
            for user_id, user_info in list(following.items())[:max_users_per_level]:
                # Store user info
                user_data = {
                    'user_id': str(user_id),
                    'username': user_info.username,
                    'full_name': user_info.full_name,
                    'follower_count': user_info.follower_count,
                    'following_count': user_info.following_count,
                    'is_private': user_info.is_private
                }
                
                self.store_user(user_data)
                self.store_network_relationship(current_user_id, str(user_id), depth + 1)
                
                network_users.append(str(user_id))
                
                # Add to queue for next level
                if depth + 1 < max_depth:
                    queue.append((str(user_id), depth + 1))
            
            # Rate limiting
            self.ig_client.rate_limit_wait()
        
        logger.info(f"Built network with {len(network_users)} users")
        return network_users
    
    def collect_high_engagement_posts(self, network_users, min_likes=10000):
        """Collect posts with high engagement"""
        logger.info(f"Collecting high engagement posts from {len(network_users)} users")
        
        high_engagement_posts = []
        
        for user_id in network_users[:100]:  # Limit for safety
            try:
                posts = self.ig_client.get_user_medias(user_id, amount=10)
                
                for post in posts:
                    if post.like_count >= min_likes:
                        post_data = {
                            'post_id': str(post.pk),
                            'author_user_id': user_id,
                            'post_url': f"https://instagram.com/p/{post.code}",
                            'caption': post.caption_text if post.caption_text else "",
                            'like_count': post.like_count,
                            'comment_count': post.comment_count,
                            'post_type': 'photo',  # Simplified
                            'hashtags': self.extract_hashtags(post.caption_text),
                            'post_date': post.taken_at
                        }
                        
                        self.store_post(post_data)
                        high_engagement_posts.append(str(post.pk))
                
                # Rate limiting
                self.ig_client.rate_limit_wait()
                
            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                continue
        
        logger.info(f"Collected {len(high_engagement_posts)} high engagement posts")
        return high_engagement_posts
    
    def check_target_user_likes(self, target_user_id, post_list):
        """Check if target user liked specific posts"""
        logger.info(f"Checking {len(post_list)} posts for target user likes")
        
        found_likes = []
        
        for post_id in post_list:
            try:
                likers = self.ig_client.get_media_likers(post_id, amount=1000)
                
                # Check if target user is in likers
                target_liked = any(str(liker.pk) == target_user_id for liker in likers)
                
                if target_liked:
                    like_data = {
                        'target_user_id': target_user_id,
                        'post_id': post_id,
                        'like_timestamp': datetime.now(),
                        'network_depth': self.get_network_depth(post_id),
                        'discovery_method': 'network_traversal'
                    }
                    
                    self.store_user_like(like_data)
                    found_likes.append(like_data)
                
                # Rate limiting
                self.ig_client.rate_limit_wait()
                
            except Exception as e:
                logger.error(f"Error checking post {post_id}: {e}")
                continue
        
        logger.info(f"Found {len(found_likes)} likes by target user")
        return found_likes
    
    def extract_hashtags(self, text):
        """Extract hashtags from text"""
        if not text:
            return []