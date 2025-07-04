"""Export analysis results in various formats"""
import argparse
import json
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config.settings import settings
from data.models import User, TargetUserLike, Post, HashtagAnalysis
from utils.helpers import export_to_csv, save_json_report
from utils.logger import setup_logger

logger = setup_logger()

def export_user_likes(db_session, target_user_id: str, output_format: str = 'csv'):
    """Export user likes data"""
    likes_query = db_session.query(
        TargetUserLike.like_timestamp,
        TargetUserLike.network_depth,
        TargetUserLike.post_category,
        Post.like_count,
        Post.comment_count,
        Post.post_type,
        Post.hashtags,
        Post.caption
    ).join(Post, TargetUserLike.post_id == Post.post_id).filter(
        TargetUserLike.target_user_id == target_user_id
    )
    
    likes_data = []
    for like in likes_query.all():
        likes_data.append({
            'like_timestamp': like.like_timestamp.isoformat() if like.like_timestamp else '',
            'network_depth': like.network_depth,
            'post_category': like.post_category,
            'post_like_count': like.like_count,
            'post_comment_count': like.comment_count,
            'post_type': like.post_type,
            'hashtags': ', '.join(like.hashtags) if like.hashtags else '',
            'caption_preview': like.caption[:100] + '...' if like.caption and len(like.caption) > 100 else like.caption or ''
        })
    
    if output_format == 'csv':
        return export_to_csv(likes_data, f"user_likes_{target_user_id}.csv")
    else:
        return save_json_report(likes_data, f"user_likes_{target_user_id}.json")

def export_hashtag_analysis(db_session, target_user_id: str, output_format: str = 'csv'):
    """Export hashtag analysis data"""
    hashtags_query = db_session.query(HashtagAnalysis).filter(
        HashtagAnalysis.target_user_id == target_user_id
    ).order_by(HashtagAnalysis.frequency.desc())
    
    hashtag_data = []
    for hashtag in hashtags_query.all():
        hashtag_data.append({
            'hashtag': hashtag.hashtag,
            'frequency': hashtag.frequency,
            'avg_like_count': float(hashtag.avg_like_count) if hashtag.avg_like_count else 0,
            'last_seen': hashtag.last_seen.isoformat() if hashtag.last_seen else ''
        })
    
    if output_format == 'csv':
        return export_to_csv(hashtag_data, f"hashtag_analysis_{target_user_id}.csv")
    else:
        return save_json_report(hashtag_data, f"hashtag_analysis_{target_user_id}.json")

def export_network_summary(db_session, target_user_id: str, output_format: str = 'csv'):
    """Export network summary data"""
    from data.models import UserNetwork
    
    network_query = db_session.query(
        UserNetwork.target_user_id,
        UserNetwork.network_depth,
        User.username,
        User.full_name,
        User.follower_count,
        User.following_count
    ).join(User, UserNetwork.target_user_id == User.user_id).filter(
        UserNetwork.source_user_id == target_user_id
    ).order_by(User.follower_count.desc())
    
    network_data = []
    for network in network_query.all():
        network_data.append({
            'user_id': network.target_user_id,
            'username': network.username,
            'full_name': network.full_name,
            'follower_count': network.follower_count,
            'following_count': network.following_count,
            'network_depth': network.network_depth
        })
    
    if output_format == 'csv':
        return export_to_csv(network_data, f"network_summary_{target_user_id}.csv")
    else:
        return save_json_report(network_data, f"network_summary_{target_user_id}.json")

def main():
    parser = argparse.ArgumentParser(description='Export Instagram analysis results')
    parser.add_argument('username', help='Target Instagram username')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Output format')
    parser.add_argument('--data-type', choices=['likes', 'hashtags', 'network', 'all'], default='all', help='Data type to export')
    
    args = parser.parse_args()
    
    # Database setup
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
        # Get target user
        target_user = db_session.query(User).filter(User.username == args.username).first()
        if not target_user:
            logger.error(f"User {args.username} not found in database")
            return
        
        target_user_id = target_user.user_id
        exported_files = []
        
        logger.info(f"Exporting data for user: {args.username}")
        
        if args.data_type in ['likes', 'all']:
            likes_file = export_user_likes(db_session, target_user_id, args.format)
            if likes_file:
                exported_files.append(likes_file)
                logger.info(f"Exported likes data: {likes_file}")
        
        if args.data_type in ['hashtags', 'all']:
            hashtags_file = export_hashtag_analysis(db_session, target_user_id, args.format)
            if hashtags_file:
                exported_files.append(hashtags_file)
                logger.info(f"Exported hashtag data: {hashtags_file}")
        
        if args.data_type in ['network', 'all']:
            network_file = export_network_summary(db_session, target_user_id, args.format)
            if network_file:
                exported_files.append(network_file)
                logger.info(f"Exported network data: {network_file}")
        
        print(f"\nExport completed! Files created:")
        for file in exported_files:
            print(f"  - {file}")
    
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise
    
    finally:
        db_session.close()

if __name__ == "__main__":
    main()