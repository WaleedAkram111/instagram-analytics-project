"""Simplified analysis script without external dependencies"""
import sys
import os
import argparse
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from config.settings import settings
    from data.models import User
    from analysis.simplified_preference_analysis import SimplifiedPreferenceAnalyzer
    from utils.helpers import save_json_report
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all __init__.py files exist and you're in the right directory")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Instagram User Preference Analysis (Simplified)')
    parser.add_argument('username', help='Target Instagram username to analyze')
    parser.add_argument('--skip-collection', action='store_true', help='Skip data collection, analyze existing data')
    parser.add_argument('--export', action='store_true', help='Export results to CSV')
    
    args = parser.parse_args()
    
    logger.info(f"Starting simplified analysis for user: {args.username}")
    
    # Database setup
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
        # Get target user
        target_user = db_session.query(User).filter(User.username == args.username).first()
        if not target_user:
            logger.error(f"User {args.username} not found in database.")
            logger.info("Available users in database:")
            users = db_session.query(User).limit(10).all()
            for user in users:
                logger.info(f"  - {user.username}")
            return
        
        target_user_id = target_user.user_id
        
        # Analysis
        logger.info("Starting analysis...")
        analyzer = SimplifiedPreferenceAnalyzer(db_session)
        report = analyzer.generate_comprehensive_report(target_user_id)
        
        if 'error' in report:
            logger.error(f"Analysis failed: {report['error']}")
            return
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{args.username}_analysis_{timestamp}.json"
        report_path = save_json_report(report, report_filename)
        
        logger.info(f"Analysis completed. Report saved: {report_path}")
        
        # Print comprehensive summary
        print("\n" + "="*70)
        print(f"📊 COMPREHENSIVE ANALYSIS REPORT FOR @{args.username}")
        print("="*70)
        
        # User info
        user_info = report['user_info']
        print(f"\n👤 USER PROFILE:")
        print(f"   Username: @{user_info['username']}")
        print(f"   Full Name: {user_info['full_name']}")
        print(f"   Followers: {user_info['follower_count']:,}")
        print(f"   Following: {user_info['following_count']:,}")
        
        # Content preferences
        if 'content_preferences' in report:
            content = report['content_preferences']
            print(f"\n📈 CONTENT ANALYSIS:")
            print(f"   Total likes analyzed: {content.get('total_likes_analyzed', 0)}")
            
            if 'category_preferences' in content:
                print(f"\n   🏷️ Content Categories:")
                for category, count in list(content['category_preferences'].items())[:7]:
                    percentage = (count / content['total_likes_analyzed']) * 100
                    print(f"      {category.title()}: {count} likes ({percentage:.1f}%)")
            
            if 'engagement_level_preferences' in content:
                print(f"\n   📊 Engagement Preferences:")
                for level, count in content['engagement_level_preferences'].items():
                    if count > 0:
                        percentage = (count / content['total_likes_analyzed']) * 100
                        print(f"      {level}: {count} likes ({percentage:.1f}%)")
        
        # Engagement patterns
        if 'engagement_patterns' in report:
            patterns = report['engagement_patterns']
            if 'peak_hours' in patterns:
                print(f"\n🕐 ENGAGEMENT TIMING:")
                print(f"   Peak Hours:")
                for hour, count in list(patterns['peak_hours'].items())[:5]:
                    print(f"      {hour:02d}:00 - {count} likes")
            
            if 'network_depth_distribution' in patterns:
                print(f"\n🔗 Network Depth Analysis:")
                for depth, count in patterns['network_depth_distribution'].items():
                    print(f"      Depth {depth}: {count} likes")
        
        # Hashtag analysis
        if 'hashtag_analysis' in report:
            hashtags = report['hashtag_analysis']
            if 'top_hashtags' in hashtags:
                print(f"\n#️⃣ TOP HASHTAGS:")
                for hashtag, count in list(hashtags['top_hashtags'].items())[:15]:
                    print(f"      #{hashtag}: {count} times")
        
        # Network insights
        if 'network_insights' in report:
            network = report['network_insights']
            if 'network_metrics' in network:
                metrics = network['network_metrics']
                print(f"\n🌐 NETWORK ANALYSIS:")
                print(f"   Total connections: {metrics.get('total_connections', 0)}")
            
            if 'influential_connections' in network:
                print(f"\n   👑 Most Influential Connections:")
                for user in network['influential_connections'][:5]:
                    print(f"      @{user['username']} - {user['follower_count']:,} followers")
        
        # Recommendations
        if 'recommendations' in report:
            print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        # Export option
        if args.export:
            try:
                from scripts.export_results import export_user_likes, export_hashtag_analysis
                print(f"\n📁 EXPORTING RESULTS:")
                
                likes_file = export_user_likes(db_session, target_user_id, 'csv')
                if likes_file:
                    print(f"   ✅ Likes data: {likes_file}")
                
                hashtags_file = export_hashtag_analysis(db_session, target_user_id, 'csv')
                if hashtags_file:
                    print(f"   ✅ Hashtag analysis: {hashtags_file}")
                
            except Exception as e:
                logger.warning(f"Export failed: {e}")
        
        print(f"\n📋 REPORT SUMMARY:")
        print(f"   Full JSON report: {report_path}")
        print(f"   Analysis timestamp: {report['analysis_timestamp']}")
        print("="*70)
        
        print(f"\n🎯 BUSINESS INSIGHTS:")
        print(f"   This analysis demonstrates advanced data analytics capabilities")
        print(f"   including social network analysis, preference modeling, and")
        print(f"   predictive recommendations - key skills for business analyst roles.")
        
    except Exception as e:
        logger.error(f"Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db_session.close()

if __name__ == "__main__":
    main()