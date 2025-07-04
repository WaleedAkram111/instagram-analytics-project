import sys
import os
from datetime import datetime, timedelta
import json
import random

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def generate_demo_data():
    """Generate comprehensive demo dataset"""
    print("Generating Demo Instagram Analytics Data...")
    
    # Sample data for realistic demo
    sample_users = [
        ("foodie_explorer", "Sarah Johnson", "Food & Travel Blogger", 45000, 1200),
        ("tech_insights", "Alex Chen", "Technology Analyst & Consultant", 32000, 890),
        ("fitness_journey", "Mike Rodriguez", "Personal Trainer & Wellness Coach", 28000, 650),
        ("art_creative", "Emma Wilson", "Digital Artist & Designer", 19000, 420),
        ("travel_wanderer", "David Kim", "Adventure Photographer", 67000, 1800),
    ]
    
    categories = {
        'food': ['food', 'foodie', 'restaurant', 'cooking', 'delicious', 'chef'],
        'technology': ['tech', 'innovation', 'ai', 'coding', 'startup', 'digital'],
        'fitness': ['fitness', 'workout', 'health', 'training', 'wellness', 'gym'],
        'art': ['art', 'design', 'creative', 'artist', 'photography', 'aesthetic'],
        'travel': ['travel', 'adventure', 'explore', 'wanderlust', 'vacation', 'journey']
    }
    
    # Generate users
    users = []
    posts = []
    likes = []
    
    # Target user
    target_user = {
        'user_id': 'target_user_001',
        'username': 'demo_analyzer',
        'full_name': 'Demo User',
        'follower_count': 5000,
        'following_count': 500,
        'is_private': False,
        'bio': 'Analytics enthusiast interested in social media trends'
    }
    users.append(target_user)
    
    # Generate network users and their posts
    for i, (username, full_name, bio, followers, following) in enumerate(sample_users):
        user = {
            'user_id': f'user_{i+1:03d}',
            'username': username,
            'full_name': full_name,
            'follower_count': followers,
            'following_count': following,
            'is_private': False,
            'bio': bio
        }
        users.append(user)
        
        # Generate posts for this user
        category = list(categories.keys())[i % len(categories)]
        hashtags_pool = categories[category]
        
        for j in range(random.randint(8, 15)):
            post_hashtags = random.sample(hashtags_pool, random.randint(3, 5))
            
            post = {
                'post_id': f'post_{i+1:03d}_{j+1:03d}',
                'author_user_id': user['user_id'],
                'post_url': f"https://instagram.com/p/post_{i+1:03d}_{j+1:03d}",
                'caption': f"Amazing {category} content! " + " ".join([f"#{tag}" for tag in post_hashtags]),
                'like_count': random.randint(15000, 150000),
                'comment_count': random.randint(500, 5000),
                'post_type': random.choice(['photo', 'video', 'carousel']),
                'hashtags': post_hashtags,
                'mentions': [],
                'location': random.choice(['New York', 'Los Angeles', 'London', 'Tokyo', '']),
                'post_date': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
            }
            posts.append(post)
            
            # Generate likes from target user (30% probability)
            if random.random() < 0.30:
                like = {
                    'target_user_id': target_user['user_id'],
                    'post_id': post['post_id'],
                    'like_timestamp': (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
                    'network_depth': random.randint(1, 3),
                    'post_category': category,
                    'discovery_method': 'demo_data'
                }
                likes.append(like)
    
    # Create dataset
    dataset = {
        'metadata': {
            'dataset_type': 'demo_instagram_analytics',
            'generated_at': datetime.now().isoformat(),
            'description': 'Demonstration dataset for Instagram analytics system',
            'total_users': len(users),
            'total_posts': len(posts),
            'total_likes': len(likes),
            'version': '1.0'
        },
        'target_user': target_user,
        'users': users[1:],
        'posts': posts,
        'likes': likes
    }
    
    # Save dataset with proper encoding
    os.makedirs('sample_data', exist_ok=True)
    with open('sample_data/mock_instagram_data.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print("Demo dataset created successfully:")
    print(f"   File: sample_data/mock_instagram_data.json")
    print(f"   Users: {len(users)}")
    print(f"   Posts: {len(posts)}")
    print(f"   Likes: {len(likes)}")
    print(f"   Target: @{target_user['username']}")
    
    return dataset

if __name__ == "__main__":
    generate_demo_data()