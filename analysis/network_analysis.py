#"""Social network analysis functions"""
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque
import networkx as nx
from sqlalchemy.orm import Session
from data.models import User, UserNetwork
from utils.logger import get_logger

logger = get_logger(__name__)

class NetworkAnalyzer:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.graph = None
    
    def build_network_graph(self, target_user_id: str) -> nx.DiGraph:
        """Build NetworkX graph from database"""
        G = nx.DiGraph()
        
        # Get all network relationships for target user
        relationships = self.db.query(UserNetwork).filter(
            UserNetwork.source_user_id == target_user_id
        ).all()
        
        # Add nodes and edges
        for rel in relationships:
            G.add_edge(rel.source_user_id, rel.target_user_id, 
                      depth=rel.network_depth,
                      relationship=rel.relationship_type)
        
        self.graph = G
        return G
    
    def calculate_network_metrics(self, target_user_id: str) -> Dict[str, Any]:
        """Calculate network analysis metrics"""
        if not self.graph:
            self.build_network_graph(target_user_id)
        
        if not self.graph or self.graph.number_of_nodes() == 0:
            return {'error': 'No network data available'}
        
        metrics = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'network_density': nx.density(self.graph),
            'average_clustering': nx.average_clustering(self.graph.to_undirected()),
        }
        
        # Central users analysis
        try:
            centrality = nx.degree_centrality(self.graph)
            metrics['most_central_users'] = sorted(
                centrality.items(), key=lambda x: x[1], reverse=True
            )[:10]
        except Exception as e:
            logger.warning(f"Could not calculate centrality: {e}")
        
        # Network depth analysis
        depth_distribution = defaultdict(int)
        for _, _, data in self.graph.edges(data=True):
            depth_distribution[data.get('depth', 1)] += 1
        
        metrics['depth_distribution'] = dict(depth_distribution)
        
        return metrics
    
    def find_influential_users(self, target_user_id: str, limit: int = 20) -> List[Dict]:
        """Find most influential users in network based on follower count"""
        network_users = self.db.query(UserNetwork).filter(
            UserNetwork.source_user_id == target_user_id
        ).all()
        
        user_ids = [rel.target_user_id for rel in network_users]
        
        influential_users = self.db.query(User).filter(
            User.user_id.in_(user_ids)
        ).order_by(User.follower_count.desc()).limit(limit).all()
        
        return [
            {
                'user_id': user.user_id,
                'username': user.username,
                'full_name': user.full_name,
                'follower_count': user.follower_count,
                'following_count': user.following_count
            }
            for user in influential_users
        ]
