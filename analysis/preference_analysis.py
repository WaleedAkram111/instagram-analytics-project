"""User preference analysis and insights generation"""
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from data.models import User, Post, TargetUserLike, HashtagAnalysis
from data.processors import DataProcessor
from analysis.network_analysis import NetworkAnalyzer
from utils.logger import get_logger

logger = get_logger(__name__)

class PreferenceAnalyzer:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.processor = DataProcessor(db_session)
        self.network_analyzer = NetworkAnalyzer(db_session)
    
    def generate_comprehensive_report(self, target_user_id: str) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        logger.info(f"Generating comprehensive report for user {target_user_id}")
        
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
            'analysis_timestamp': func.now(),
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
        
        # Category analysis
        category_counts = {}
        post_type_counts = {}
        like_count_ranges = {'0-1K': 0, '1K-10K': 0, '10K-100K': 0, '100K+': 0}
        
        for like in likes:
            post = self.db.query(Post).filter(Post.post_id == like.post_id).first()
            if post:
                # Category analysis
                category = self.processor.categorize_post(post)
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Post type analysis
                post_type_counts[post.post_type] = post_type_counts.get(post.post_type, 0) + 1
                
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
            'category_preferences': category_counts,
            'post_type_preferences': post_type_counts,
            'engagement_level_preferences': like_count_ranges,
            'total_likes_analyzed': len(likes)
        }
    
    def _analyze_engagement_patterns(self, target_user_id: str) -> Dict[str, Any]:
        """Analyze when and how user engages"""
        return self.processor.calculate_engagement_patterns(target_user_id)
    
    def _analyze_network_insights(self, target_user_id: str) -> Dict[str, Any]:
        """Analyze network-based insights"""
        network_metrics = self.network_analyzer.calculate_network_metrics(target_user_id)
        influential_users = self.network_analyzer.find_influential_users(target_user_id)
        
        # Network depth preference analysis
        likes = self.db.query(TargetUserLike).filter(
            TargetUserLike.target_user_id == target_user_id
        ).all()
        
        depth_likes = {}
        for like in likes:
            depth = like.network_depth or 1
            depth_likes[depth] = depth_likes.get(depth, 0) + 1
        
        return {
            'network_metrics': network_metrics,
            'influential_connections': influential_users[:10],
            'network_depth_preferences': depth_likes
        }
    
    def _analyze_hashtag_preferences(self, target_user_id: str) -> Dict[str, Any]:
        """Analyze hashtag preferences"""
        return self.processor.analyze_hashtag_preferences(target_user_id)
    
    def _generate_recommendations(self, target_user_id: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Get analysis data
        content_prefs = self._analyze_content_preferences(target_user_id)
        engagement_patterns = self._analyze_engagement_patterns(target_user_id)
        hashtag_prefs = self._analyze_hashtag_preferences(target_user_id)
        
        # Content recommendations
        if 'category_preferences' in content_prefs:
            top_category = max(content_prefs['category_preferences'].items(), 
                             key=lambda x: x[1])[0]
            recommendations.append(f"Focus on {top_category} content - highest engagement category")
        
        # Timing recommendations
        if 'peak_hours' in engagement_patterns:
            peak_hour = max(engagement_patterns['peak_hours'].items(), 
                          key=lambda x: x[1])[0]
            recommendations.append(f"Optimal posting time: {peak_hour}:00 - peak engagement hour")
        
        # Hashtag recommendations
        if 'top_hashtags' in hashtag_prefs:
            top_hashtags = list(hashtag_prefs['top_hashtags'].keys())[:5]
            recommendations.append(f"Use hashtags: {', '.join(top_hashtags)} - frequently liked")
        
        # Network recommendations
        network_likes = engagement_patterns.get('network_depth_distribution', {})
        if network_likes:
            preferred_depth = max(network_likes.items(), key=lambda x: x[1])[0]
            if preferred_depth == 1:
                recommendations.append("Engage more with direct connections - preferred network level")
            else:
                recommendations.append("Explore extended network - likes content from deeper connections")
        
        return recommendations
