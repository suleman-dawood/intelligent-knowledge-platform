#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neo4j database adapter for the Intelligent Knowledge Aggregation Platform.
Handles all knowledge graph database operations.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

import neo4j
from neo4j import GraphDatabase

# Configure logging
logger = logging.getLogger(__name__)


class Neo4jAdapter:
    """Neo4j database adapter for storing and querying the knowledge graph."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Neo4j adapter.
        
        Args:
            config: Configuration dictionary containing Neo4j connection parameters
        """
        self.config = config
        self.uri = config.get('uri', 'bolt://localhost:7687')
        self.username = config.get('username', 'neo4j')
        self.password = config.get('password', 'password')
        self.database = config.get('database', 'neo4j')
        
        self.driver = None
        self._connect()
        
        logger.info(f"Neo4j adapter initialized with URI: {self.uri}")
    
    def _connect(self) -> None:
        """Establish a connection to the Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                database=self.database
            )
            
            # Test the connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]
                
                if test_value != 1:
                    raise Exception("Connection test failed")
                
            logger.info("Successfully connected to Neo4j database")
            
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j database: {e}")
            self.driver = None
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.driver is not None:
            self.driver.close()
            self.driver = None
            logger.info("Neo4j connection closed")
    
    def create_entity(self, entity_type: str, properties: Dict[str, Any]) -> str:
        """Create a new entity node in the knowledge graph.
        
        Args:
            entity_type: Type of entity (concept, person, organization, etc.)
            properties: Entity properties
            
        Returns:
            Entity ID
        """
        # Ensure properties include an ID
        if 'id' not in properties:
            properties['id'] = f"{entity_type}_{datetime.now().timestamp()}"
        
        # Create Cypher query
        query = (
            f"CREATE (e:{entity_type} $properties) "
            "RETURN e.id AS id"
        )
        
        try:
            with self.driver.session() as session:
                result = session.run(query, properties=properties)
                entity_id = result.single()["id"]
                
                logger.debug(f"Created entity {entity_type} with ID {entity_id}")
                return entity_id
                
        except Exception as e:
            logger.error(f"Failed to create entity: {e}")
            raise
    
    def create_relationship(self, 
                          source_id: str, 
                          target_id: str, 
                          relationship_type: str, 
                          properties: Dict[str, Any] = None) -> str:
        """Create a relationship between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relationship_type: Type of relationship
            properties: Relationship properties
            
        Returns:
            Relationship ID
        """
        if properties is None:
            properties = {}
            
        # Ensure properties include an ID
        if 'id' not in properties:
            properties['id'] = f"rel_{datetime.now().timestamp()}"
            
        # Create creation timestamp
        properties['created_at'] = datetime.now().isoformat()
        
        # Create Cypher query
        query = (
            "MATCH (source), (target) "
            "WHERE source.id = $source_id AND target.id = $target_id "
            f"CREATE (source)-[r:{relationship_type} $properties]->(target) "
            "RETURN r.id AS id"
        )
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query, 
                    source_id=source_id, 
                    target_id=target_id, 
                    properties=properties
                )
                relationship_id = result.single()["id"]
                
                logger.debug(f"Created relationship {relationship_type} from {source_id} to {target_id}")
                return relationship_id
                
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            raise
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity data or None if not found
        """
        query = (
            "MATCH (e) "
            "WHERE e.id = $entity_id "
            "RETURN e"
        )
        
        try:
            with self.driver.session() as session:
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                
                if record is None:
                    logger.debug(f"Entity with ID {entity_id} not found")
                    return None
                    
                # Extract node properties
                entity = dict(record["e"])
                
                # Get node labels
                labels = list(record["e"].labels)
                entity["labels"] = labels
                
                return entity
                
        except Exception as e:
            logger.error(f"Failed to get entity: {e}")
            raise
    
    def get_neighborhood(self, entity_id: str, depth: int = 1, 
                       relationship_types: List[str] = None) -> Dict[str, Any]:
        """Get the neighborhood of an entity.
        
        Args:
            entity_id: Center entity ID
            depth: Traversal depth
            relationship_types: Types of relationships to include (None for all)
            
        Returns:
            Neighborhood graph data
        """
        # Build the relationship filter
        rel_filter = ""
        if relationship_types:
            types_str = "|".join([f":{rel_type}" for rel_type in relationship_types])
            rel_filter = f"[{types_str}]"
            
        # Create Cypher query
        query = (
            "MATCH path = (center)-" + rel_filter + "*1.." + str(depth) + "->(n) "
            "WHERE center.id = $entity_id "
            "RETURN path"
        )
        
        try:
            with self.driver.session() as session:
                result = session.run(query, entity_id=entity_id)
                
                # Process results into a graph structure
                nodes = {}
                edges = []
                
                for record in result:
                    path = record["path"]
                    
                    # Extract nodes and relationships from the path
                    for node in path.nodes:
                        node_id = node["id"]
                        if node_id not in nodes:
                            node_data = dict(node)
                            node_data["labels"] = list(node.labels)
                            nodes[node_id] = node_data
                            
                    for rel in path.relationships:
                        edge = {
                            "id": rel["id"] if "id" in rel else f"rel_{len(edges)}",
                            "source": rel.start_node["id"],
                            "target": rel.end_node["id"],
                            "type": rel.type,
                            "properties": dict(rel)
                        }
                        edges.append(edge)
                
                return {
                    "center": entity_id,
                    "nodes": list(nodes.values()),
                    "edges": edges,
                    "depth": depth
                }
                
        except Exception as e:
            logger.error(f"Failed to get neighborhood: {e}")
            raise
    
    def search_entities(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for entities by property values.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching entities
        """
        # Create Cypher query for a basic text search
        cypher_query = (
            "MATCH (e) "
            "WHERE e.name CONTAINS $query OR e.description CONTAINS $query "
            "RETURN e "
            "LIMIT $limit"
        )
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query, query=query, limit=limit)
                
                entities = []
                for record in result:
                    entity = dict(record["e"])
                    entity["labels"] = list(record["e"].labels)
                    entities.append(entity)
                    
                return entities
                
        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            raise
    
    def update_entity(self, entity_id: str, properties: Dict[str, Any]) -> bool:
        """Update an entity's properties.
        
        Args:
            entity_id: Entity ID
            properties: New properties to set
            
        Returns:
            True if successful
        """
        # Create Cypher query
        query = (
            "MATCH (e) "
            "WHERE e.id = $entity_id "
            "SET e += $properties "
            "RETURN e.id AS id"
        )
        
        try:
            with self.driver.session() as session:
                result = session.run(query, entity_id=entity_id, properties=properties)
                record = result.single()
                
                if record is None:
                    logger.warning(f"Entity with ID {entity_id} not found for update")
                    return False
                    
                logger.debug(f"Updated entity {entity_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update entity: {e}")
            raise
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if successful
        """
        # Create Cypher query
        query = (
            "MATCH (e) "
            "WHERE e.id = $entity_id "
            "DETACH DELETE e "
            "RETURN count(*) AS deleted"
        )
        
        try:
            with self.driver.session() as session:
                result = session.run(query, entity_id=entity_id)
                deleted = result.single()["deleted"]
                
                logger.debug(f"Deleted entity {entity_id} and its relationships")
                return deleted > 0
                
        except Exception as e:
            logger.error(f"Failed to delete entity: {e}")
            raise
    
    def execute_cypher(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a custom Cypher query.
        
        Args:
            query: Cypher query
            params: Query parameters
            
        Returns:
            Query results
        """
        if params is None:
            params = {}
            
        try:
            with self.driver.session() as session:
                result = session.run(query, **params)
                
                # Convert result to a list of dictionaries
                records = []
                for record in result:
                    records.append(dict(record))
                    
                return records
                
        except Exception as e:
            logger.error(f"Failed to execute Cypher query: {e}")
            raise 