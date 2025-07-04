"""Simplified preference analysis without external dependencies"""
import sys
import os
from typing import Dict, List, Any
from collections import Counter
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy.orm import Session
from sqlalchemy import func
from data.models import User, Post, TargetUserLike, HashtagAnalysis, UserNetwork

class SimplifiedPreferenceAnalyzer:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def generate_comprehensive_report(self, target_user_id: str) -> Dict[str, Any]:
        """Generate comprehensive analysis report without external dependencies"""
        target_user = self.db.query(User).filter(User.user_id == target_user_id).first()
        if not target_user:
            return {'error': f'Target user {target_user_id} not found'}
        
        report = {
            'user_info': {
                'user_id': target_user.user_id,
                'username': target_user.username,
                'full_name': target_user.full_name,
                'follower_count': target_user.follower_count,
                'following_count': target_user.following_count
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'content_preferences': self._analyze_content_preferences(target_user_id),
            'engagement_patterns': self._analyze_engagement_patterns(target_user_id),
            'network_insights': self._analyze_network_insights(target_user_id),
            'hashtag_analysis': self._analyze_hashtag_preferences(target_user_id),
            'recommendations': self._generate_recommendations(target_user_id)
        }
        
        return report
    
    def _analyze_content_preferences(self, target_user_id: str) -> Dict[str, Any]:
        """Analyze content type preferences"""
        likes = self.db.query(TargetUserLike).filter(
            TargetUserLike.target_user_id == target_user_id
        ).all()
        
        if not likes:
            return {'error': 'No likes data available'}
        
        category_counts = Counter()
        post_type_counts = Counter()
        like_count_ranges = {'0-1K': 0, '1K-10K': 0, '10K-100K': 0, '100K+': 0}
        
        for like in likes:
            post = self.db.query(Post).filter(Post.post_id == like.post_id).first()
            if post:
                # Category analysis
                category = self._categorize_post(post)
                category_counts[category] += 1
                
                # Post type analysis
                if post.post_type:
                    post_type_counts[post.post_type] += 1
                
                # Like count ranges
                if post.like_count < 1000:
                    like_count_ranges['0-1K'] += 1
                elif post.like_count < 10000:
                    like_count_ranges['1K-10K'] += 1
                elif post.like_count < 100000:
                    like_count_ranges['10K-100K'] += 1
                else:
                    like_count_ranges['100K+'] += 1
        
        return {
            'category_preferences': dict(category_counts.most_common()),
            'post_type_preferences': dict(post_type_counts.most_common()),
            'engagement_level_preferences': like_count_ranges,
            'total_likes_analyzed': len(likes)
        }
    
    def _analyze_engagement_patterns(self, target_user_id: str) -> Dict[str, Any]:
        """Analyze when and how user engages"""
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
            'peak_hours': dict(hour_counts.most_common()),
            'active_days': dict(day_counts.most_common()),
            'network_depth_distribution': dict(depth_counts.most_common()),
            'total_likes': len(likes),
            'date_range': {
                'earliest': min(like.like_timestamp for like in likes if like.like_timestamp).isoformat(),
                'latest': max(like.like_timestamp for like in likes if like.like_timestamp).isoformat()
            }
        }
    
    def _analyze_network_insights(self, target_user_id: str) -> Dict[str, Any]:
        """Analyze network-based insights without NetworkX"""
        # Basic network metrics
        network_connections = self.db.query(UserNetwork).filter(
            UserNetwork.source_user_id == target_user_id
        ).all()
        
        # Depth distribution
        depth_distribution = Counter()
        for conn in network_connections:
            depth_distribution[conn.network_depth] += 1
        
        # Find influential users (by follower count)
        network_user_ids = [conn.target_user_id for conn in network_connections]
        influential_users = self.db.query(User).filter(
            User.user_id.in_(network_user_ids)
        ).order_by(User.follower_count.desc()).limit(10).all()
        
        # Network depth preference from likes
        likes = self.db.query(TargetUserLike).filter(
            TargetUserLike.target_user_id == target_user_id
        ).all()
        
        depth_likes = Counter()
        for like in likes:
            if like.network_depth:
                depth_likes[like.network_depth] += 1
        
        return {
            'network_metrics': {
                'total_connections': len(network_connections),
                'depth_distribution': dict(depth_distribution.most_common())
            },
            'influential_connections': [
                {
                    'user_id': user.user_id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'follower_count': user.follower_count
                }
                for user in influential_users
            ],
            'network_depth_preferences': dict(depth_likes.most_common())
        }
    
    def _analyze_hashtag_preferences(self, target_user_id: str) -> Dict[str, Any]:
        """Analyze hashtag preferences"""
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
                category = self._categorize_post(post)
                category_counter[category] += 1
        
        return {
            'top_hashtags': dict(hashtag_counter.most_common(20)),
            'category_preferences': dict(category_counter.most_common()),
            'total_likes_analyzed': total_likes
        }
    
    def _categorize_post(self, post: Post) -> str:
        """Categorize post based on hashtags"""
        if not post.hashtags:
            return 'uncategorized'
        
        hashtag_text = ' '.join(post.hashtags).lower()
        
        categories = {
            'food': ['food', 'foodie', 'restaurant', 'cooking', 'recipe', 'delicious'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'adventure', 'wanderlust'],
            'fitness': ['fitness', 'gym', 'workout', 'health', 'exercise', 'training'],
            'technology': ['tech', 'technology', 'coding', 'software', 'ai', 'programming'],
            'lifestyle': ['lifestyle', 'life', 'motivation', 'inspiration', 'goals'],
            'business': ['business', 'entrepreneur', 'startup', 'marketing', 'success'],
            'art': ['art', 'artist', 'creative', 'design', 'photography', 'aesthetic'],
            'music': ['music', 'song', 'artist', 'concert', 'album', 'musician'],
            'sports': ['sports', 'football', 'basketball', 'soccer', 'game', 'team'],
            'fashion': ['fashion', 'style', 'outfit', 'ootd', 'clothing', 'brand']
        }
        
        for category, keywords in categories.items():
            if any(keyword in hashtag_text for keyword in keywords):
                return category
        
        return 'general'
    
    def _generate_recommendations(self, target_user_id: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Get analysis data
        content_prefs = self._analyze_content_preferences(target_user_id)
        engagement_patterns = self._analyze_engagement_patterns(target_user_id)
        hashtag_prefs = self._analyze_hashtag_preferences(target_user_id)
        
        # Content recommendations
        if 'category_preferences' in content_prefs and content_prefs['category_preferences']:
            top_category = list(content_prefs['category_preferences'].items())[0][0]
            recommendations.append(f"Focus on {top_category} content - highest engagement category")
        
        # Timing recommendations
        if 'peak_hours' in engagement_patterns and engagement_patterns['peak_hours']:
            peak_hour = list(engagement_patterns['peak_hours'].items())[0][0]
            recommendations.append(f"Optimal posting time: {peak_hour:02d}:00 - peak engagement hour")
        
        # Hashtag recommendations
        if 'top_hashtags' in hashtag_prefs and hashtag_prefs['top_hashtags']:
            top_hashtags = list(hashtag_prefs['top_hashtags'].keys())[:5]
            recommendations.append(f"Use hashtags: {', '.join(top_hashtags)} - frequently liked")
        
        # Network recommendations
        if 'network_depth_distribution' in engagement_patterns:
            network_likes = engagement_patterns['network_depth_distribution']
            if network_likes:
                preferred_depth = list(network_likes.items())[0][0]
                if preferred_depth == 1:
                    recommendations.append("Engage more with direct connections - preferred network level")
                else:
                    recommendations.append("Explore extended network - likes content from deeper connections")
        
        return recommendations