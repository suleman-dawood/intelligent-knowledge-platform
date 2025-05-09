#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard manager for the UI agent.
Handles rendering and configuration of dashboard components.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DashboardManager:
    """Manager for dashboard components and layouts."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the dashboard manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Default layouts for different user roles
        self.default_layouts = {
            "admin": self._load_layout("admin"),
            "researcher": self._load_layout("researcher"),
            "student": self._load_layout("student"),
            "default": self._load_layout("default")
        }
        
        # User custom layouts
        self.user_layouts = {}
        
        logger.info("Dashboard manager initialized")
    
    def _load_layout(self, layout_name: str) -> Dict[str, Any]:
        """Load a dashboard layout from the configuration.
        
        Args:
            layout_name: Name of the layout to load
            
        Returns:
            Dashboard layout configuration
        """
        layout_config = self.config.get('dashboard_layouts', {}).get(layout_name)
        
        if not layout_config:
            logger.warning(f"Layout {layout_name} not found in configuration, using empty layout")
            return {
                "layout": "grid",
                "components": []
            }
            
        return layout_config
    
    async def get_dashboard(self, user_id: Optional[str] = None, role: str = "default") -> Dict[str, Any]:
        """Get a dashboard configuration for a user.
        
        Args:
            user_id: User ID
            role: User role (admin, researcher, student, etc.)
            
        Returns:
            Dashboard configuration
        """
        # First check if the user has a custom layout
        if user_id and user_id in self.user_layouts:
            return self.user_layouts[user_id]
            
        # Otherwise return the default layout for the role
        if role in self.default_layouts:
            return self.default_layouts[role]
            
        # Fallback to the default layout
        return self.default_layouts["default"]
    
    async def save_dashboard(self, user_id: str, layout: Dict[str, Any]) -> None:
        """Save a custom dashboard layout for a user.
        
        Args:
            user_id: User ID
            layout: Dashboard layout
        """
        self.user_layouts[user_id] = layout
        logger.info(f"Saved custom dashboard layout for user {user_id}")
    
    async def get_available_components(self) -> List[Dict[str, Any]]:
        """Get a list of available dashboard components.
        
        Returns:
            List of available components
        """
        # Return the list of available components from the configuration
        return self.config.get('dashboard_components', [])
    
    async def get_component_data(self, component_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for a dashboard component.
        
        Args:
            component_id: Component ID
            parameters: Component parameters
            
        Returns:
            Component data
        """
        # This method would fetch data for a specific component
        # For example, it might fetch recent queries, statistics, etc.
        # For now, we'll return some sample data
        
        if component_id == "recent_queries":
            return {
                "component_id": component_id,
                "data": {
                    "queries": [
                        {"id": "q1", "text": "What is knowledge integration?", "timestamp": datetime.now().isoformat()},
                        {"id": "q2", "text": "Show me quantum physics concepts", "timestamp": datetime.now().isoformat()},
                        {"id": "q3", "text": "Explain artificial intelligence", "timestamp": datetime.now().isoformat()}
                    ]
                }
            }
            
        elif component_id == "knowledge_stats":
            return {
                "component_id": component_id,
                "data": {
                    "total_entities": 12580,
                    "total_relations": 35624,
                    "recent_entities": 156,
                    "recent_sources": 42
                }
            }
            
        elif component_id == "trending_topics":
            return {
                "component_id": component_id,
                "data": {
                    "topics": [
                        {"name": "Quantum Computing", "score": 0.95},
                        {"name": "Neural Networks", "score": 0.87},
                        {"name": "Climate Science", "score": 0.82},
                        {"name": "Vaccine Research", "score": 0.78},
                        {"name": "Space Exploration", "score": 0.76}
                    ]
                }
            }
            
        else:
            logger.warning(f"Unknown component ID: {component_id}")
            return {
                "component_id": component_id,
                "data": {},
                "error": "Unknown component"
            } 