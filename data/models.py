#"""SQLAlchemy database models"""
from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, ARRAY, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String(50), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(200))
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    is_private = Column(Boolean, default=False)
    profile_pic_url = Column(Text)
    bio = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="author")
    likes = relationship("TargetUserLike", back_populates="user")

class UserNetwork(Base):
    __tablename__ = 'user_network'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_user_id = Column(String(50), ForeignKey('users.user_id'))
    target_user_id = Column(String(50), ForeignKey('users.user_id'))
    relationship_type = Column(String(20), nullable=False)  # 'following', 'follower'
    network_depth = Column(Integer, default=1)
    discovered_date = Column(TIMESTAMP, default=datetime.utcnow)

class Post(Base):
    __tablename__ = 'posts'
    
    post_id = Column(String(50), primary_key=True)
    author_user_id = Column(String(50), ForeignKey('users.user_id'))
    post_url = Column(Text, nullable=False)
    caption = Column(Text)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    post_type = Column(String(20))  # 'photo', 'video', 'carousel'
    hashtags = Column(ARRAY(Text))
    mentions = Column(ARRAY(Text))
    location = Column(String(200))
    post_date = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    likes = relationship("TargetUserLike", back_populates="post")

class TargetUserLike(Base):
    __tablename__ = 'target_user_likes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_user_id = Column(String(50), ForeignKey('users.user_id'))
    post_id = Column(String(50), ForeignKey('posts.post_id'))
    like_timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    network_depth = Column(Integer)
    post_category = Column(String(100))
    discovery_method = Column(String(50))
    
    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

class HashtagAnalysis(Base):
    __tablename__ = 'hashtag_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hashtag = Column(String(100))
    target_user_id = Column(String(50), ForeignKey('users.user_id'))
    frequency = Column(Integer, default=1)
    avg_like_count = Column(DECIMAL(10,2))
    last_seen = Column(TIMESTAMP, default=datetime.utcnow)

class ProcessingLog(Base):
    __tablename__ = 'processing_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    process_type = Column(String(50))
    status = Column(String(20))  # 'started', 'completed', 'failed'
    target_user_id = Column(String(50))
    records_processed = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(TIMESTAMP, default=datetime.utcnow)
    completed_at = Column(TIMESTAMP)