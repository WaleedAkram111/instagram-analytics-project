"""Data visualization functions"""
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any
import os

class VisualizationGenerator:
    def __init__(self, output_dir: str = 'reports/visualizations'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_category_preferences_chart(self, data: Dict[str, int], user_id: str) -> str:
        """Create category preferences pie chart"""
        if not data:
            return None
        
        fig = go.Figure(data=[go.Pie(
            labels=list(data.keys()),
            values=list(data.values()),
            hole=0.3,
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title=f"Content Category Preferences - User {user_id}",
            font_size=12
        )
        
        filename = f"{self.output_dir}/category_preferences_{user_id}.html"
        fig.write_html(filename)
        return filename
    
    def create_engagement_timeline(self, engagement_data: Dict[str, Any], user_id: str) -> str:
        """Create engagement timeline visualization"""
        if 'peak_hours' not in engagement_data:
            return None
        
        hours = list(engagement_data['peak_hours'].keys())
        counts = list(engagement_data['peak_hours'].values())
        
        fig = go.Figure(data=[go.Bar(
            x=hours,
            y=counts,
            marker_color='lightblue'
        )])
        
        fig.update_layout(
            title=f"Engagement by Hour - User {user_id}",
            xaxis_title="Hour of Day",
            yaxis_title="Number of Likes",
            font_size=12
        )
        
        filename = f"{self.output_dir}/engagement_timeline_{user_id}.html"
        fig.write_html(filename)
        return filename
    
    def create_network_depth_chart(self, depth_data: Dict[int, int], user_id: str) -> str:
        """Create network depth distribution chart"""
        if not depth_data:
            return None
        
        depths = list(depth_data.keys())
        counts = list(depth_data.values())
        
        fig = go.Figure(data=[go.Bar(
            x=[f"Depth {d}" for d in depths],
            y=counts,
            marker_color='coral'
        )])
        
        fig.update_layout(
            title=f"Network Depth Preferences - User {user_id}",
            xaxis_title="Network Depth",
            yaxis_title="Number of Likes",
            font_size=12
        )
        
        filename = f"{self.output_dir}/network_depth_{user_id}.html"
        fig.write_html(filename)
        return filename
    
    def create_comprehensive_dashboard(self, report_data: Dict[str, Any], user_id: str) -> str:
        """Create comprehensive dashboard with multiple visualizations"""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Category Preferences', 'Engagement Timeline', 
                          'Network Depth', 'Top Hashtags'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Category preferences (pie chart)
        if 'content_preferences' in report_data and 'category_preferences' in report_data['content_preferences']:
            cat_data = report_data['content_preferences']['category_preferences']
            fig.add_trace(go.Pie(
                labels=list(cat_data.keys()),
                values=list(cat_data.values()),
                name="Categories"
            ), row=1, col=1)
        
        # Engagement timeline
        if 'engagement_patterns' in report_data and 'peak_hours' in report_data['engagement_patterns']:
            eng_data = report_data['engagement_patterns']['peak_hours']
            fig.add_trace(go.Bar(
                x=list(eng_data.keys()),
                y=list(eng_data.values()),
                name="Engagement"
            ), row=1, col=2)
        
        # Network depth
        if 'network_insights' in report_data and 'network_depth_preferences' in report_data['network_insights']:
            net_data = report_data['network_insights']['network_depth_preferences']
            fig.add_trace(go.Bar(
                x=[f"Depth {d}" for d in net_data.keys()],
                y=list(net_data.values()),
                name="Network Depth"
            ), row=2, col=1)
        
        # Top hashtags
        if 'hashtag_analysis' in report_data and 'top_hashtags' in report_data['hashtag_analysis']:
            hashtag_data = report_data['hashtag_analysis']['top_hashtags']
            top_10_hashtags = dict(list(hashtag_data.items())[:10])
            fig.add_trace(go.Bar(
                x=list(top_10_hashtags.values()),
                y=list(top_10_hashtags.keys()),
                orientation='h',
                name="Hashtags"
            ), row=2, col=2)
        
        fig.update_layout(
            title=f"Instagram Analytics Dashboard - User {user_id}",
            height=800,
            showlegend=False
        )
        
        filename = f"{self.output_dir}/dashboard_{user_id}.html"
        fig.write_html(filename)
        return filename
