#"""Data processing and analysis functions"""
import re
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from data.models import User, Post, TargetUserLike, HashtagAnalysis
from utils.logger import get_logger

logger = get_logger(__name__)

class DataProcessor:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
        
        hashtags = re.findall(r'#(\w+)', text.lower())
        return list(set(hashtags))  # Remove duplicates
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text"""
        if not text:
            return []
        
        mentions = re.findall(r'@(\w+)', text.lower())
        return list(set(mentions))  # Remove duplicates
    
    def categorize_post(self, post: Post) -> str:
        """Categorize post based on hashtags and content"""
        if not post.hashtags:
            return 'uncategorized'
        
        # Define category keywords
        categories = {
            'fashion': ['fashion', 'style', 'outfit', 'ootd', 'clothing', 'brand'],
            'food': ['food', 'foodie', 'restaurant', 'cooking', 'recipe', 'delicious'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'adventure', 'wanderlust'],
            'fitness': ['fitness', 'gym', 'workout', 'health', 'exercise', 'training'],
            'technology': ['tech', 'technology', 'coding', 'software', 'ai', 'programming'],
            'lifestyle': ['lifestyle', 'life', 'motivation', 'inspiration', 'goals'],
            'business': ['business', 'entrepreneur', 'startup', 'marketing', 'success'],
            'art': ['art', 'artist', 'creative', 'design', 'photography', 'aesthetic'],
            'music': ['music', 'song', 'artist', 'concert', 'album', 'musician'],
            'sports': ['sports', 'football', 'basketball', 'soccer', 'game', 'team']
        }
        
        hashtag_text = ' '.join(post.hashtags).lower()
        
        for category, keywords in categories.items():
            if any(keyword in hashtag_text for keyword in keywords):
                return category
        
        return 'general'
    
    def analyze_hashtag_preferences(self, target_user_id: str) -> Dict[str, Any]:
        """Analyze hashtag preferences for target user"""
        likes = self.db.query(TargetUserLike).filter(
            TargetUserLike.target_user_id == target_user_id
        ).all()
        
        hashtag_counter = Counter()
        category_counter = Counter()
        total_likes = len(likes)
        
        for like in likes:
            post = self.db.query(Post).filter(Post.post_id == like.post_id).first()
            if post and post.hashtags:
                hashtag_counter.update(post.hashtags)
                category = self.categorize_post(post)
                category_counter[category] += 1
        
        # Store hashtag analysis
        for hashtag, frequency in hashtag_counter.most_common(50):
            existing = self.db.query(HashtagAnalysis).filter(
                HashtagAnalysis.hashtag == hashtag,
                HashtagAnalysis.target_user_id == target_user_id
            ).first()
            
            if existing:
                existing.frequency = frequency
                existing.last_seen = datetime.utcnow()
            else:
                hashtag_analysis = HashtagAnalysis(
                    hashtag=hashtag,
                    target_user_id=target_user_id,
                    frequency=frequency,
                    last_seen=datetime.utcnow()
                )
                self.db.add(hashtag_analysis)
        
        self.db.commit()
        
        return {
            'top_hashtags': dict(hashtag_counter.most_common(20)),
            'category_preferences': dict(category_counter.most_common()),
            'total_likes_analyzed': total_likes
        }
    
    def calculate_engagement_patterns(self, target_user_id: str) -> Dict[str, Any]:
        """Calculate engagement patterns and timing"""
        likes = self.db.query(TargetUserLike).filter(
            TargetUserLike.target_user_id == target_user_id
        ).all()
        
        if not likes:
            return {'error': 'No likes found for analysis'}
        
        # Time-based analysis
        hour_counts = Counter()
        day_counts = Counter()
        
        for like in likes:
            if like.like_timestamp:
                hour_counts[like.like_timestamp.hour] += 1
                day_counts[like.like_timestamp.strftime('%A')] += 1
        
        # Network depth analysis
        depth_counts = Counter()
        for like in likes:
            if like.network_depth:
                depth_counts[like.network_depth] += 1
        
        return {
            'peak_hours': dict(hour_counts.most_common(5)),
            'active_days': dict(day_counts.most_common()),
            'network_depth_distribution': dict(depth_counts),
            'total_likes': len(likes),
            'date_range': {
                'earliest': min(like.like_timestamp for like in likes if like.like_timestamp),
                'latest': max(like.like_timestamp for like in likes if like.like_timestamp)
            }
        }