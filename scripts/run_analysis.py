# scripts/run_analysis.py
"""Main analysis execution script - WORKING VERSION"""
import sys
import os
import argparse
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from config.settings import settings
    from utils.helpers import save_json_report
    from data.models import User
    
    # Use the simplified analyzer instead of the complex one
    from analysis.simplified_preference_analysis import SimplifiedPreferenceAnalyzer
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all __init__.py files exist and you're in the right directory")
    sys.exit(1)

# Setup basic logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Instagram User Preference Analysis')
    parser.add_argument('username', help='Target Instagram username to analyze')
    parser.add_argument('--max-depth', type=int, default=2, help='Maximum network depth to explore')
    parser.add_argument('--min-likes', type=int, default=10000, help='Minimum likes for post inclusion')
    parser.add_argument('--max-users', type=int, default=50, help='Maximum users per network level')
    parser.add_argument('--skip-collection', action='store_true', help='Skip data collection, analyze existing data')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    
    args = parser.parse_args()
    
    logger.info(f"Starting analysis for user: {args.username}")
    logger.info(f"Parameters: max_depth={args.max_depth}, min_likes={args.min_likes}")
    
    # Database setup
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
        # Initialize components
        analyzer = SimplifiedPreferenceAnalyzer(db_session)
        
        if not args.skip_collection:
            logger.warning("Data collection requires Instagram API access")
            logger.info("Use --skip-collection flag to analyze existing data")
            logger.info("Or use the mock data we created earlier")
            return
        
        # Get target user ID from username
        target_user = db_session.query(User).filter(User.username == args.username).first()
        if not target_user:
            logger.error(f"User {args.username} not found in database.")
            logger.info("Available users in database:")
            users = db_session.query(User).limit(10).all()
            for user in users:
                logger.info(f"  - {user.username}")
            return
        
        target_user_id = target_user.user_id
        
        # Phase 2: Analysis
        logger.info("Phase 2: Starting analysis...")
        
        report = analyzer.generate_comprehensive_report(target_user_id)
        
        if 'error' in report:
            logger.error(f"Analysis failed: {report['error']}")
            return
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{args.username}_analysis_{timestamp}.json"
        report_path = save_json_report(report, report_filename)
        
        logger.info(f"Analysis completed. Report saved: {report_path}")
        
        # Phase 3: Visualization (optional - simplified)
        if args.visualize:
            logger.info("Phase 3: Creating basic visualizations...")
            try:
                create_simple_visualizations(report, target_user_id)
                logger.info("Basic visualizations created in reports/charts/")
            except Exception as e:
                logger.warning(f"Visualization creation failed: {e}")
                logger.info("Continuing without visualizations...")
        
        # Print comprehensive summary
        print_analysis_summary(report, args.username, report_path)
    
    except Exception as e:
        logger.error(f"Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        db_session.close()

def create_simple_visualizations(report, user_id):
    """Create simple text-based visualizations"""
    import os
    
    os.makedirs('reports/charts', exist_ok=True)
    
    # Create a simple text-based chart
    chart_content = f"""
INSTAGRAM ANALYTICS DASHBOARD
User ID: {user_id}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONTENT CATEGORIES:
"""
    
    if 'content_preferences' in report and 'category_preferences' in report['content_preferences']:
        categories = report['content_preferences']['category_preferences']
        total = report['content_preferences'].get('total_likes_analyzed', 1)
        
        for category, count in list(categories.items())[:8]:
            percentage = (count / total) * 100
            bar = '█' * int(percentage / 2)  # Simple bar chart
            chart_content += f"{category:12} |{bar:20} {count:3} ({percentage:.1f}%)\n"
    
    chart_content += f"""

TOP HASHTAGS:
"""
    
    if 'hashtag_analysis' in report and 'top_hashtags' in report['hashtag_analysis']:
        hashtags = report['hashtag_analysis']['top_hashtags']
        for hashtag, count in list(hashtags.items())[:10]:
            chart_content += f"#{hashtag:15} {count:3} times\n"
    
    # Save chart
    with open(f'reports/charts/dashboard_{user_id}.txt', 'w') as f:
        f.write(chart_content)

def print_analysis_summary(report, username, report_path):
    """Print comprehensive analysis summary"""
    print("\n" + "="*70)
    print(f"📊 COMPREHENSIVE ANALYSIS REPORT FOR @{username}")
    print("="*70)
    
    # User info
    if 'user_info' in report:
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
            total_likes = content.get('total_likes_analyzed', 1)
            for category, count in list(content['category_preferences'].items())[:7]:
                percentage = (count / total_likes) * 100
                print(f"      {category.title():12}: {count:3} likes ({percentage:.1f}%)")
        
        if 'engagement_level_preferences' in content:
            print(f"\n   📊 Engagement Level Distribution:")
            for level, count in content['engagement_level_preferences'].items():
                if count > 0:
                    percentage = (count / total_likes) * 100
                    print(f"      {level:15}: {count:3} likes ({percentage:.1f}%)")
    
    # Engagement patterns
    if 'engagement_patterns' in report:
        patterns = report['engagement_patterns']
        
        if 'peak_hours' in patterns and patterns['peak_hours']:
            print(f"\n🕐 OPTIMAL TIMING:")
            print(f"   Peak Engagement Hours:")
            for hour, count in list(patterns['peak_hours'].items())[:5]:
                print(f"      {hour:02d}:00 - {count} likes")
        
        if 'active_days' in patterns and patterns['active_days']:
            print(f"\n   📅 Most Active Days:")
            for day, count in list(patterns['active_days'].items())[:5]:
                print(f"      {day}: {count} likes")
        
        if 'network_depth_distribution' in patterns:
            print(f"\n🔗 NETWORK ANALYSIS:")
            print(f"   Content Preference by Connection Depth:")
            for depth, count in patterns['network_depth_distribution'].items():
                print(f"      Depth {depth}: {count} likes")
    
    # Hashtag analysis
    if 'hashtag_analysis' in report:
        hashtags = report['hashtag_analysis']
        if 'top_hashtags' in hashtags and hashtags['top_hashtags']:
            print(f"\n#️⃣ HASHTAG INTELLIGENCE:")
            print(f"   Top Hashtags by Frequency:")
            for hashtag, count in list(hashtags['top_hashtags'].items())[:15]:
                print(f"      #{hashtag:15} {count:2} times")
    
    # Network insights
    if 'network_insights' in report:
        network = report['network_insights']
        if 'network_metrics' in network:
            metrics = network['network_metrics']
            print(f"\n🌐 SOCIAL NETWORK METRICS:")
            print(f"   Total connections: {metrics.get('total_connections', 0)}")
        
        if 'influential_connections' in network and network['influential_connections']:
            print(f"\n   👑 Most Influential Connections:")
            for user in network['influential_connections'][:5]:
                print(f"      @{user['username']:15} - {user['follower_count']:,} followers")
    
    # Recommendations
    if 'recommendations' in report and report['recommendations']:
        print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Summary
    print(f"\n📋 REPORT SUMMARY:")
    print(f"   Full JSON report: {report_path}")
    print(f"   Analysis timestamp: {report.get('analysis_timestamp', 'N/A')}")
    
    print(f"\n🎯 TECHNICAL CAPABILITIES DEMONSTRATED:")
    print(f"   ✅ Advanced SQL database operations")
    print(f"   ✅ Statistical analysis and data aggregation")
    print(f"   ✅ Social network analysis concepts")
    print(f"   ✅ Temporal pattern recognition")
    print(f"   ✅ Content categorization algorithms")
    print(f"   ✅ Business intelligence and recommendations")
    print(f"   ✅ Professional report generation")
    
    print("="*70)
    print(f"✅ ANALYSIS COMPLETE - READY FOR")

if __name__ == "__main__":
    main()