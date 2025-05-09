#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualization manager for the UI agent.
Handles generation of visualizations for knowledge graphs and data.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
import networkx as nx
from datetime import datetime

logger = logging.getLogger(__name__)


class VisualizationManager:
    """Manager for generating visualizations of knowledge graphs and data."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the visualization manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Supported visualization types
        self.supported_types = [
            "knowledge_graph",
            "concept_map",
            "timeline",
            "hierarchy",
            "comparison",
            "statistics"
        ]
        
        # Default visualization settings
        self.default_settings = {
            "knowledge_graph": {
                "layout": "force_directed",
                "node_size": 20,
                "edge_width": 1.5,
                "font_size": 12,
                "highlight_color": "#ff7700",
                "node_color": "#3388cc",
                "edge_color": "#aaaaaa"
            },
            "concept_map": {
                "layout": "radial",
                "node_size": 25,
                "edge_width": 2.0,
                "font_size": 14,
                "root_color": "#ff5500",
                "node_color": "#44aadd",
                "edge_color": "#888888"
            }
        }
        
        logger.info("Visualization manager initialized")
    
    async def generate_visualization(self, 
                                    vis_type: str, 
                                    data: Dict[str, Any], 
                                    settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a visualization of the specified type.
        
        Args:
            vis_type: Type of visualization (knowledge_graph, concept_map, etc.)
            data: Data to visualize
            settings: Visualization settings
            
        Returns:
            Visualization data in a format suitable for rendering
        """
        if vis_type not in self.supported_types:
            logger.warning(f"Unsupported visualization type: {vis_type}")
            return {
                "error": f"Unsupported visualization type: {vis_type}",
                "supported_types": self.supported_types
            }
            
        # Merge settings with defaults
        merged_settings = self._merge_settings(vis_type, settings)
        
        if vis_type == "knowledge_graph":
            return await self._generate_knowledge_graph(data, merged_settings)
            
        elif vis_type == "concept_map":
            return await self._generate_concept_map(data, merged_settings)
            
        elif vis_type == "timeline":
            return await self._generate_timeline(data, merged_settings)
            
        elif vis_type == "hierarchy":
            return await self._generate_hierarchy(data, merged_settings)
            
        elif vis_type == "comparison":
            return await self._generate_comparison(data, merged_settings)
            
        elif vis_type == "statistics":
            return await self._generate_statistics(data, merged_settings)
            
        else:
            logger.error(f"Visualization type {vis_type} is supported but not implemented")
            return {"error": "Internal error: Visualization not implemented"}
    
    def _merge_settings(self, vis_type: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Merge custom settings with defaults.
        
        Args:
            vis_type: Visualization type
            settings: Custom settings
            
        Returns:
            Merged settings
        """
        default = self.default_settings.get(vis_type, {})
        
        if not settings:
            return default
            
        # Merge the settings
        merged = default.copy()
        merged.update(settings)
        
        return merged
    
    async def _generate_knowledge_graph(self, data: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a knowledge graph visualization.
        
        Args:
            data: Knowledge graph data
            settings: Visualization settings
            
        Returns:
            Visualization data
        """
        # Extract nodes and edges from the data
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        
        # Create a networkx graph
        G = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            G.add_node(
                node["id"],
                label=node.get("label", node["id"]),
                type=node.get("type", "entity"),
                properties=node.get("properties", {})
            )
            
        # Add edges
        for edge in edges:
            G.add_edge(
                edge["source"],
                edge["target"],
                label=edge.get("label", "related"),
                weight=edge.get("weight", 1.0),
                properties=edge.get("properties", {})
            )
            
        # Compute layout
        layout_type = settings.get("layout", "force_directed")
        positions = self._compute_layout(G, layout_type)
        
        # Convert positions to a format suitable for the frontend
        node_positions = {node: {"x": float(pos[0]), "y": float(pos[1])} for node, pos in positions.items()}
        
        # Prepare the visualization data
        visualization = {
            "type": "knowledge_graph",
            "settings": settings,
            "nodes": [
                {
                    "id": node,
                    "label": G.nodes[node]["label"],
                    "type": G.nodes[node]["type"],
                    "properties": G.nodes[node]["properties"],
                    "position": node_positions[node]
                }
                for node in G.nodes
            ],
            "edges": [
                {
                    "source": edge[0],
                    "target": edge[1],
                    "label": G.edges[edge]["label"],
                    "weight": G.edges[edge]["weight"],
                    "properties": G.edges[edge]["properties"]
                }
                for edge in G.edges
            ]
        }
        
        return visualization
    
    def _compute_layout(self, G: nx.Graph, layout_type: str) -> Dict[Any, Tuple[float, float]]:
        """Compute a layout for a graph.
        
        Args:
            G: Networkx graph
            layout_type: Type of layout to compute
            
        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        if layout_type == "force_directed":
            return nx.spring_layout(G)
            
        elif layout_type == "circular":
            return nx.circular_layout(G)
            
        elif layout_type == "radial":
            # For radial layout, we need to choose a root node
            # We'll use the node with the highest degree
            degrees = dict(G.degree())
            root = max(degrees, key=degrees.get)
            return nx.shell_layout(G, [[root], list(set(G.nodes()) - {root})])
            
        elif layout_type == "spectral":
            try:
                return nx.spectral_layout(G)
            except:
                logger.warning("Spectral layout failed, falling back to spring layout")
                return nx.spring_layout(G)
                
        elif layout_type == "hierarchical":
            try:
                # This is an approximation of hierarchical layout
                # For a proper hierarchical layout, you might need more complex algorithms
                return nx.multipartite_layout(G, subset_key="level")
            except:
                logger.warning("Hierarchical layout failed, falling back to spring layout")
                return nx.spring_layout(G)
                
        else:
            logger.warning(f"Unknown layout type: {layout_type}, falling back to force_directed")
            return nx.spring_layout(G)
    
    async def _generate_concept_map(self, data: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a concept map visualization.
        
        Args:
            data: Concept map data
            settings: Visualization settings
            
        Returns:
            Visualization data
        """
        # Concept maps are similar to knowledge graphs but with a more hierarchical structure
        # and typically centered around a root concept
        
        # Extract concepts and relationships
        concepts = data.get("concepts", [])
        relationships = data.get("relationships", [])
        root_id = data.get("root_id")
        
        # Create a graph
        G = nx.DiGraph()
        
        # Add concepts as nodes
        for concept in concepts:
            G.add_node(
                concept["id"],
                label=concept.get("label", concept["id"]),
                level=concept.get("level", 0),
                importance=concept.get("importance", 1.0),
                properties=concept.get("properties", {})
            )
            
        # Add relationships as edges
        for rel in relationships:
            G.add_edge(
                rel["source"],
                rel["target"],
                label=rel.get("label", "related"),
                strength=rel.get("strength", 1.0),
                properties=rel.get("properties", {})
            )
            
        # Compute layout, preferring a radial layout for concept maps
        layout_type = settings.get("layout", "radial")
        
        # For radial layout, use the specified root if available
        if layout_type == "radial" and root_id:
            positions = nx.shell_layout(G, [[root_id], list(set(G.nodes()) - {root_id})])
        else:
            positions = self._compute_layout(G, layout_type)
            
        # Convert positions to a format suitable for the frontend
        node_positions = {node: {"x": float(pos[0]), "y": float(pos[1])} for node, pos in positions.items()}
        
        # Prepare the visualization data
        visualization = {
            "type": "concept_map",
            "settings": settings,
            "root_id": root_id,
            "concepts": [
                {
                    "id": node,
                    "label": G.nodes[node]["label"],
                    "level": G.nodes[node]["level"],
                    "importance": G.nodes[node]["importance"],
                    "properties": G.nodes[node]["properties"],
                    "position": node_positions[node],
                    "is_root": node == root_id
                }
                for node in G.nodes
            ],
            "relationships": [
                {
                    "source": edge[0],
                    "target": edge[1],
                    "label": G.edges[edge]["label"],
                    "strength": G.edges[edge]["strength"],
                    "properties": G.edges[edge]["properties"]
                }
                for edge in G.edges
            ]
        }
        
        return visualization
    
    async def _generate_timeline(self, data: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a timeline visualization.
        
        Args:
            data: Timeline data
            settings: Visualization settings
            
        Returns:
            Visualization data
        """
        # This would be implemented in a real system to generate timeline visualizations
        # For now, we'll return a placeholder
        
        return {
            "type": "timeline",
            "settings": settings,
            "data": data,
            "error": "Timeline visualization not yet implemented"
        }
    
    async def _generate_hierarchy(self, data: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a hierarchy visualization.
        
        Args:
            data: Hierarchy data
            settings: Visualization settings
            
        Returns:
            Visualization data
        """
        # This would be implemented in a real system to generate hierarchy visualizations
        # For now, we'll return a placeholder
        
        return {
            "type": "hierarchy",
            "settings": settings,
            "data": data,
            "error": "Hierarchy visualization not yet implemented"
        }
    
    async def _generate_comparison(self, data: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comparison visualization.
        
        Args:
            data: Comparison data
            settings: Visualization settings
            
        Returns:
            Visualization data
        """
        # This would be implemented in a real system to generate comparison visualizations
        # For now, we'll return a placeholder
        
        return {
            "type": "comparison",
            "settings": settings,
            "data": data,
            "error": "Comparison visualization not yet implemented"
        }
    
    async def _generate_statistics(self, data: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a statistics visualization.
        
        Args:
            data: Statistics data
            settings: Visualization settings
            
        Returns:
            Visualization data
        """
        # This would be implemented in a real system to generate statistics visualizations
        # For now, we'll return a placeholder
        
        return {
            "type": "statistics",
            "settings": settings,
            "data": data,
            "error": "Statistics visualization not yet implemented"
        } 