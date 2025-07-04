"""Unit tests for data collectors"""
import unittest
from unittest.mock import Mock, patch
from data.collectors import UserDataCollector
from data.processors import DataProcessor

class TestUserDataCollector(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock()
        self.mock_ig_client = Mock()
        self.collector = UserDataCollector()
        self.collector.db = self.mock_db
        self.collector.ig_client = self.mock_ig_client
    
    def test_extract_hashtags(self):
        """Test hashtag extraction"""
        processor = DataProcessor(self.mock_db)
        
        text = "Check out this amazing #food at #restaurant #yummy"
        hashtags = processor.extract_hashtags(text)
        
        expected = ['food', 'restaurant', 'yummy']
        self.assertEqual(sorted(hashtags), sorted(expected))
    
    def test_extract_mentions(self):
        """Test mention extraction"""
        processor = DataProcessor(self.mock_db)
        
        text = "Great time with @friend1 and @friend2"
        mentions = processor.extract_mentions(text)
        
        expected = ['friend1', 'friend2']
        self.assertEqual(sorted(mentions), sorted(expected))
    
    def test_categorize_post(self):
        """Test post categorization"""
        processor = DataProcessor(self.mock_db)
        
        # Create mock post
        post = Mock()
        post.hashtags = ['food', 'restaurant', 'delicious']
        
        category = processor.categorize_post(post)
        self.assertEqual(category, 'food')
