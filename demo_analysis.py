import sys
import os
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_complete_demo():
    """Run complete demonstration of the analytics system"""
    print("INSTAGRAM ANALYTICS SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Step 1: Generate demo data
    print("\nStep 1: Generating demonstration data...")
    try:
        from scripts.generate_mock_data import generate_demo_data
        dataset = generate_demo_data()
    except Exception as e:
        print(f"Demo data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Setup database and load data
    print("\nStep 2: Setting up database...")
    try:
        # Import and run database setup
        sys.path.append('scripts')
        import setup_database
        
        # Run setup
        setup_database.create_database()
        setup_database.create_tables()
        setup_database.create_indexes()
        print("Database setup complete")
    except Exception as e:
        print(f"Database setup issue: {e}")
        print("   Make sure PostgreSQL is running and .env is configured")
        print("   You can continue with existing database...")
    
    # Step 3: Load demo data into database
    print("\nStep 3: Loading demo data...")
    try:
        load_demo_data_to_db(dataset)
        print("Demo data loaded successfully")
    except Exception as e:
        print(f"Data loading failed: {e}")
        print("   Check your database connection and try again")
        return
    
    # Step 4: Run analysis
    print("\nStep 4: Running comprehensive analysis...")
    try:
        run_demo_analysis()
        print("Analysis complete")
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nDEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("What was demonstrated:")
    print("   - Database design and management")
    print("   - Data processing and analysis")
    print("   - Statistical pattern recognition")
    print("   - Content categorization algorithms")
    print("   - Business intelligence and recommendations")
    print("   - Professional report generation")
    print("\nCheck the 'reports/' directory for generated analysis!")
    print("\nThis project demonstrates advanced data analytics skills")
    print("perfect for business analyst and data analyst roles!")

def load_demo_data_to_db(dataset):
    """Load demo data into database"""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from config.settings import settings
    from data.models import User, Post, TargetUserLike, UserNetwork
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("   Loading users...")
        # Load target user
        target_user_data = dataset['target_user']
        target_user = User(**target_user_data)
        db.merge(target_user)
        
        # Load network users
        for user_data in dataset['users']:
            user = User(**user_data)
            db.merge(user)
        
        print("   Loading posts...")
        # Load posts
        for post_data in dataset['posts']:
            # Convert post_date string back to datetime if needed
            if isinstance(post_data['post_date'], str):
                try:
                    post_data['post_date'] = datetime.fromisoformat(post_data['post_date'])
                except:
                    post_data['post_date'] = datetime.now()
            post = Post(**post_data)
            db.merge(post)
        
        print("   Loading likes...")
        # Load likes
        for like_data in dataset['likes']:
            if isinstance(like_data['like_timestamp'], str):
                try:
                    like_data['like_timestamp'] = datetime.fromisoformat(like_data['like_timestamp'])
                except:
                    like_data['like_timestamp'] = datetime.now()
            like = TargetUserLike(**like_data)
            db.merge(like)
        
        print("   Creating network relationships...")
        # Create network relationships
        for user_data in dataset['users']:
            try:
                relationship = UserNetwork(
                    source_user_id=target_user_data['user_id'],
                    target_user_id=user_data['user_id'],
                    relationship_type='following',
                    network_depth=1
                )
                db.merge(relationship)
            except Exception as e:
                print(f"   Relationship creation warning: {e}")
        
        db.commit()
        print("   All data committed to database")
        
    except Exception as e:
        db.rollback()
        print(f"   Database error: {e}")
        raise e
    finally:
        db.close()

def run_demo_analysis():
    """Run the analysis on demo data"""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from config.settings import settings
    from analysis.simplified_preference_analysis import SimplifiedPreferenceAnalyzer
    from utils.helpers import save_json_report
    from data.models import User
    
    # Database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get demo user
        target_user = db.query(User).filter(User.username == 'demo_analyzer').first()
        
        if not target_user:
            print("   Demo user not found in database")
            return
        
        print(f"   Analyzing user: @{target_user.username}")
        
        # Run analysis
        analyzer = SimplifiedPreferenceAnalyzer(db)
        report = analyzer.generate_comprehensive_report(target_user.user_id)
        
        if 'error' in report:
            print(f"   Analysis error: {report['error']}")
            return
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"demo_analysis_{timestamp}.json"
        report_path = save_json_report(report, report_filename)
        
        # Display summary
        print_demo_summary(report, report_path)
        
    except Exception as e:
        print(f"   Analysis execution error: {e}")
        raise e
    finally:
        db.close()

def print_demo_summary(report, report_path):
    """Print a summary of the analysis results"""
    print("\n" + "="*50)
    print("DEMO ANALYSIS RESULTS")
    print("="*50)
    
    # User info
    if 'user_info' in report:
        user = report['user_info']
        print(f"\nAnalyzed User: @{user['username']}")
        print(f"   Followers: {user['follower_count']:,}")
        
    # Content analysis
    if 'content_preferences' in report:
        content = report['content_preferences']
        total_likes = content.get('total_likes_analyzed', 0)
        print(f"\nAnalysis Summary:")
        print(f"   Total likes analyzed: {total_likes}")
        
        if 'category_preferences' in content and content['category_preferences']:
            print(f"\nTop Content Categories:")
            for category, count in list(content['category_preferences'].items())[:5]:
                percentage = (count / total_likes * 100) if total_likes > 0 else 0
                print(f"   {category.title()}: {count} likes ({percentage:.1f}%)")
    
    # Top hashtags
    if 'hashtag_analysis' in report and 'top_hashtags' in report['hashtag_analysis']:
        hashtags = report['hashtag_analysis']['top_hashtags']
        if hashtags:
            print(f"\nTop Hashtags:")
            for hashtag, count in list(hashtags.items())[:8]:
                print(f"   #{hashtag}: {count} times")
    
    # Recommendations
    if 'recommendations' in report and report['recommendations']:
        print(f"\nStrategic Recommendations:")
        for i, rec in enumerate(report['recommendations'][:5], 1):
            print(f"   {i}. {rec}")
    
    print(f"\nFull Report: {report_path}")
    print("="*50)

if __name__ == "__main__":
    run_complete_demo()