"""Unit tests for analysis functions"""
import unittest
from unittest.mock import Mock
from analysis.preference_analysis import PreferenceAnalyzer

class TestPreferenceAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock()
        self.analyzer = PreferenceAnalyzer(self.mock_db)
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        # Mock data
        content_prefs = {
            'category_preferences': {'food': 10, 'travel': 5, 'fashion': 3}
        }
        engagement_patterns = {
            'peak_hours': {14: 15, 18: 12, 20: 8}
        }
        hashtag_prefs = {
            'top_hashtags': {'food': 8, 'yummy': 6, 'restaurant': 4}
        }
        
        # Mock methods
        self.analyzer._analyze_content_preferences = Mock(return_value=content_prefs)
        self.analyzer._analyze_engagement_patterns = Mock(return_value=engagement_patterns)
        self.analyzer._analyze_hashtag_preferences = Mock(return_value=hashtag_prefs)
        
        recommendations = self.analyzer._generate_recommendations('test_user')
        
        self.assertIsInstance(recommendations, list)
        self.assertTrue(any('food' in rec for rec in recommendations))
        self.assertTrue(any('14:00' in rec for rec in recommendations))

if __name__ == '__main__':
    unittest.main()