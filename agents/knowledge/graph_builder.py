#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Graph builder module for constructing knowledge graphs.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from neo4j import AsyncGraphDatabase, AsyncDriver

# Configure logging
logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builder for creating and updating knowledge graphs."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the graph builder.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Neo4j connection settings
        self.neo4j_uri = config.get('databases', {}).get('neo4j', {}).get('uri', 'bolt://localhost:7687')
        self.neo4j_user = config.get('databases', {}).get('neo4j', {}).get('user', 'neo4j')
        self.neo4j_password = config.get('databases', {}).get('neo4j', {}).get('password', 'password')
        
        # Initialize Neo4j driver
        self.driver = None
        
        logger.info("Graph builder initialized")
    
    async def build(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build or update the knowledge graph.
        
        Args:
            task_data: Task data containing the entities and relationships to add
            
        Returns:
            Operation results
        """
        entities = task_data.get('entities', [])
        relationships = task_data.get('relationships', [])
        source_id = task_data.get('source_id')
        
        if not entities and not relationships:
            raise ValueError("No entities or relationships provided")
            
        logger.info(f"Building knowledge graph with {len(entities)} entities and {len(relationships)} relationships")
        
        # Connect to Neo4j
        await self._connect()
        
        # Process the operation
        try:
            # Create entities
            entity_ids = await self._create_entities(entities, source_id)
            
            # Create relationships
            relationship_ids = await self._create_relationships(relationships, source_id)
            
            # Get statistics about the operation
            stats = await self._get_graph_statistics()
            
            return {
                "operation_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source_id": source_id,
                "created_entities": len(entity_ids),
                "created_relationships": len(relationship_ids),
                "entity_ids": entity_ids,
                "relationship_ids": relationship_ids,
                "graph_statistics": stats
            }
            
        finally:
            # Close the Neo4j connection
            await self._close()
    
    async def _connect(self) -> None:
        """Connect to Neo4j database."""
        if self.driver is None:
            self.driver = AsyncGraphDatabase.driver(
                self.neo4j_uri, 
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
        # Test the connection
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as num")
                record = await result.single()
                if record and record.get("num") == 1:
                    logger.info("Connected to Neo4j")
                else:
                    raise Exception("Failed to verify Neo4j connection")
        except Exception as e:
            logger.error(f"Error connecting to Neo4j: {e}")
            raise
    
    async def _close(self) -> None:
        """Close the Neo4j connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None
    
    async def _create_entities(self, entities: List[Dict[str, Any]], source_id: Optional[str]) -> List[str]:
        """Create entities in the knowledge graph.
        
        Args:
            entities: List of entities to create
            source_id: Source identifier
            
        Returns:
            List of created entity IDs
        """
        created_ids = []
        
        if not entities:
            return created_ids
            
        async with self.driver.session() as session:
            for entity in entities:
                # Generate a unique ID if not provided
                entity_id = entity.get('id') or str(uuid.uuid4())
                entity_type = entity.get('type', 'Entity')
                properties = entity.get('properties', {})
                
                # Add metadata
                properties['created_at'] = datetime.now().isoformat()
                if source_id:
                    properties['source_id'] = source_id
                
                # Create entity
                query = (
                    f"MERGE (e:{entity_type} {{id: $id}}) "
                    "ON CREATE SET e += $properties, e.created_at = datetime() "
                    "ON MATCH SET e += $properties, e.updated_at = datetime() "
                    "RETURN e.id as id"
                )
                
                try:
                    result = await session.run(
                        query,
                        {
                            "id": entity_id,
                            "properties": properties
                        }
                    )
                    record = await result.single()
                    if record:
                        created_ids.append(record.get("id"))
                except Exception as e:
                    logger.error(f"Error creating entity {entity_id}: {e}")
                
                # Simulate processing time for each entity
                await asyncio.sleep(0.01)
                
        return created_ids
    
    async def _create_relationships(self, relationships: List[Dict[str, Any]], source_id: Optional[str]) -> List[str]:
        """Create relationships in the knowledge graph.
        
        Args:
            relationships: List of relationships to create
            source_id: Source identifier
            
        Returns:
            List of created relationship IDs
        """
        created_ids = []
        
        if not relationships:
            return created_ids
            
        async with self.driver.session() as session:
            for relationship in relationships:
                # Extract relationship data
                rel_id = relationship.get('id') or str(uuid.uuid4())
                rel_type = relationship.get('type', 'RELATED_TO')
                from_id = relationship.get('from_id')
                to_id = relationship.get('to_id')
                properties = relationship.get('properties', {})
                
                if not from_id or not to_id:
                    logger.warning(f"Skipping relationship without from_id or to_id: {rel_id}")
                    continue
                
                # Add metadata
                properties['created_at'] = datetime.now().isoformat()
                if source_id:
                    properties['source_id'] = source_id
                
                # Create relationship
                query = (
                    "MATCH (from {id: $from_id}) "
                    "MATCH (to {id: $to_id}) "
                    f"MERGE (from)-[r:{rel_type} {{id: $id}}]->(to) "
                    "ON CREATE SET r += $properties, r.created_at = datetime() "
                    "ON MATCH SET r += $properties, r.updated_at = datetime() "
                    "RETURN r.id as id"
                )
                
                try:
                    result = await session.run(
                        query,
                        {
                            "id": rel_id,
                            "from_id": from_id,
                            "to_id": to_id,
                            "properties": properties
                        }
                    )
                    record = await result.single()
                    if record:
                        created_ids.append(record.get("id"))
                except Exception as e:
                    logger.error(f"Error creating relationship {rel_id}: {e}")
                
                # Simulate processing time for each relationship
                await asyncio.sleep(0.01)
                
        return created_ids
    
    async def _get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph.
        
        Returns:
            Dictionary of graph statistics
        """
        stats = {
            "total_nodes": 0,
            "total_relationships": 0,
            "node_types": {},
            "relationship_types": {}
        }
        
        async with self.driver.session() as session:
            # Count total nodes
            result = await session.run("MATCH (n) RETURN count(n) as count")
            record = await result.single()
            if record:
                stats["total_nodes"] = record.get("count")
                
            # Count total relationships
            result = await session.run("MATCH ()-[r]->() RETURN count(r) as count")
            record = await result.single()
            if record:
                stats["total_relationships"] = record.get("count")
                
            # Count nodes by type
            result = await session.run(
                "MATCH (n) "
                "WITH labels(n) as labels "
                "UNWIND labels as label "
                "RETURN label, count(label) as count"
            )
            node_types = {}
            async for record in result:
                node_types[record.get("label")] = record.get("count")
            stats["node_types"] = node_types
            
            # Count relationships by type
            result = await session.run(
                "MATCH ()-[r]->() "
                "RETURN type(r) as type, count(r) as count"
            )
            rel_types = {}
            async for record in result:
                rel_types[record.get("type")] = record.get("count")
            stats["relationship_types"] = rel_types
            
        return stats 