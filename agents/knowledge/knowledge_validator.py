#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Knowledge validator module for validating and maintaining knowledge graph integrity.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple, Set
import uuid
from datetime import datetime
from neo4j import AsyncGraphDatabase, AsyncDriver

# Configure logging
logger = logging.getLogger(__name__)


class KnowledgeValidator:
    """Validator for ensuring knowledge graph integrity and consistency."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the knowledge validator.
        
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
        
        # Validation rules
        self.rules = [
            {
                "name": "orphaned_nodes",
                "description": "Nodes without any relationships",
                "severity": "warning"
            },
            {
                "name": "conflicting_relationships",
                "description": "Conflicting relationship types between the same entities",
                "severity": "error"
            },
            {
                "name": "duplicate_entities",
                "description": "Potentially duplicate entities",
                "severity": "warning"
            },
            {
                "name": "cycle_detection",
                "description": "Cycles in hierarchical relationships",
                "severity": "error"
            }
        ]
        
        logger.info("Knowledge validator initialized")
    
    async def validate(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the knowledge graph.
        
        Args:
            task_data: Task data specifying validation parameters
            
        Returns:
            Validation results
        """
        rules = task_data.get('rules', [rule["name"] for rule in self.rules])
        entity_types = task_data.get('entity_types', [])
        relationship_types = task_data.get('relationship_types', [])
        fix_issues = task_data.get('fix_issues', False)
        
        logger.info(f"Validating knowledge graph with rules: {rules}")
        
        # Connect to Neo4j
        await self._connect()
        
        # Process the validation
        try:
            # Run the validations
            validation_results = []
            
            for rule in self.rules:
                if rule["name"] in rules:
                    logger.info(f"Running validation rule: {rule['name']}")
                    
                    # Run the specific validation rule
                    result = await getattr(self, f"_validate_{rule['name']}")(
                        entity_types, relationship_types
                    )
                    
                    # Add to results
                    validation_results.append({
                        "rule": rule["name"],
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "issues": result["issues"],
                        "issue_count": len(result["issues"]),
                        "fix_count": 0
                    })
                    
                    # Fix issues if requested
                    if fix_issues and result["issues"]:
                        logger.info(f"Fixing issues for rule: {rule['name']}")
                        
                        # Run the fix for this rule
                        fix_result = await getattr(self, f"_fix_{rule['name']}")(result["issues"])
                        
                        # Update the validation result with fix information
                        validation_results[-1]["fix_count"] = fix_result["fixed_count"]
                        validation_results[-1]["fixed"] = fix_result["fixed"]
            
            # Get overall statistics
            stats = await self._get_graph_statistics()
            
            return {
                "operation_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "validation_results": validation_results,
                "total_issues": sum(r["issue_count"] for r in validation_results),
                "total_fixed": sum(r.get("fix_count", 0) for r in validation_results),
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
    
    async def _validate_orphaned_nodes(self, entity_types: List[str], relationship_types: List[str]) -> Dict[str, Any]:
        """Validate for orphaned nodes (nodes without relationships).
        
        Args:
            entity_types: List of entity types to check
            relationship_types: List of relationship types (unused for this validation)
            
        Returns:
            Validation results
        """
        issues = []
        
        async with self.driver.session() as session:
            # Build the query based on entity types
            if entity_types:
                type_filter = " OR ".join([f"n:{entity_type}" for entity_type in entity_types])
                query = f"MATCH (n) WHERE {type_filter} AND NOT (n)--() RETURN n.id as id, labels(n) as types, n.created_at as created_at"
            else:
                query = "MATCH (n) WHERE NOT (n)--() RETURN n.id as id, labels(n) as types, n.created_at as created_at"
                
            result = await session.run(query)
            
            async for record in result:
                issues.append({
                    "id": record.get("id"),
                    "types": record.get("types"),
                    "created_at": record.get("created_at"),
                    "issue": "Orphaned node without any relationships"
                })
                
        return {
            "issues": issues
        }
    
    async def _fix_orphaned_nodes(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fix orphaned nodes by creating relationships to an 'Unclassified' node.
        
        Args:
            issues: List of orphaned node issues
            
        Returns:
            Fix results
        """
        fixed = []
        
        async with self.driver.session() as session:
            # Create an 'Unclassified' node if it doesn't exist
            await session.run(
                "MERGE (u:Category {id: 'unclassified'}) "
                "ON CREATE SET u.name = 'Unclassified', u.created_at = datetime() "
                "RETURN u.id"
            )
            
            # Connect orphaned nodes to the unclassified node
            for issue in issues:
                node_id = issue.get("id")
                if not node_id:
                    continue
                    
                try:
                    query = (
                        "MATCH (n {id: $node_id}), (u:Category {id: 'unclassified'}) "
                        "MERGE (n)-[r:BELONGS_TO {id: $rel_id}]->(u) "
                        "ON CREATE SET r.created_at = datetime(), r.automatic = true "
                        "RETURN r.id as id"
                    )
                    
                    result = await session.run(
                        query,
                        {
                            "node_id": node_id,
                            "rel_id": str(uuid.uuid4())
                        }
                    )
                    
                    record = await result.single()
                    if record:
                        fixed.append({
                            "node_id": node_id,
                            "action": "Connected to Unclassified category"
                        })
                except Exception as e:
                    logger.error(f"Error fixing orphaned node {node_id}: {e}")
                
        return {
            "fixed_count": len(fixed),
            "fixed": fixed
        }
    
    async def _validate_conflicting_relationships(self, entity_types: List[str], relationship_types: List[str]) -> Dict[str, Any]:
        """Validate for conflicting relationships.
        
        Args:
            entity_types: List of entity types to check
            relationship_types: List of relationship types to check
            
        Returns:
            Validation results
        """
        issues = []
        conflicting_pairs = [
            ["IS_A", "PART_OF"],
            ["CAUSE_EFFECT", "EFFECT_CAUSE"]
        ]
        
        async with self.driver.session() as session:
            for pair in conflicting_pairs:
                if relationship_types and not any(rel_type in relationship_types for rel_type in pair):
                    continue
                    
                rel1, rel2 = pair
                
                # Find nodes with conflicting relationships
                query = (
                    f"MATCH (a)-[r1:{rel1}]->(b) "
                    f"MATCH (a)-[r2:{rel2}]->(b) "
                    "RETURN a.id as from_id, b.id as to_id, r1.id as rel1_id, r2.id as rel2_id"
                )
                
                result = await session.run(query)
                
                async for record in result:
                    issues.append({
                        "from_id": record.get("from_id"),
                        "to_id": record.get("to_id"),
                        "rel1_id": record.get("rel1_id"),
                        "rel2_id": record.get("rel2_id"),
                        "rel1_type": rel1,
                        "rel2_type": rel2,
                        "issue": f"Conflicting relationships: {rel1} and {rel2}"
                    })
                
        return {
            "issues": issues
        }
    
    async def _fix_conflicting_relationships(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fix conflicting relationships by removing one of them.
        
        Args:
            issues: List of conflicting relationship issues
            
        Returns:
            Fix results
        """
        fixed = []
        
        async with self.driver.session() as session:
            for issue in issues:
                rel2_id = issue.get("rel2_id")
                if not rel2_id:
                    continue
                    
                try:
                    # Remove the second relationship
                    query = "MATCH ()-[r {id: $rel_id}]->() DELETE r RETURN count(r) as deleted"
                    
                    result = await session.run(query, {"rel_id": rel2_id})
                    record = await result.single()
                    
                    if record and record.get("deleted") > 0:
                        fixed.append({
                            "from_id": issue.get("from_id"),
                            "to_id": issue.get("to_id"),
                            "rel_id": rel2_id,
                            "rel_type": issue.get("rel2_type"),
                            "action": "Removed conflicting relationship"
                        })
                except Exception as e:
                    logger.error(f"Error fixing conflicting relationship {rel2_id}: {e}")
                
        return {
            "fixed_count": len(fixed),
            "fixed": fixed
        }
    
    async def _validate_duplicate_entities(self, entity_types: List[str], relationship_types: List[str]) -> Dict[str, Any]:
        """Validate for potentially duplicate entities.
        
        Args:
            entity_types: List of entity types to check
            relationship_types: List of relationship types (unused for this validation)
            
        Returns:
            Validation results
        """
        issues = []
        
        # Properties to check for similarity
        # In a real implementation, this would use more sophisticated techniques
        properties = ["name", "title", "label"]
        
        async with self.driver.session() as session:
            for prop in properties:
                # Build query based on entity types
                if entity_types:
                    type_filter = " OR ".join([f"n1:{entity_type} AND n2:{entity_type}" for entity_type in entity_types])
                    query = (
                        f"MATCH (n1), (n2) "
                        f"WHERE {type_filter} AND n1.id <> n2.id AND n1.{prop} = n2.{prop} AND n1.{prop} IS NOT NULL "
                        f"RETURN n1.id as id1, n2.id as id2, labels(n1) as types1, labels(n2) as types2, n1.{prop} as prop_value"
                    )
                else:
                    query = (
                        f"MATCH (n1), (n2) "
                        f"WHERE n1.id <> n2.id AND n1.{prop} = n2.{prop} AND n1.{prop} IS NOT NULL "
                        f"RETURN n1.id as id1, n2.id as id2, labels(n1) as types1, labels(n2) as types2, n1.{prop} as prop_value"
                    )
                    
                try:
                    result = await session.run(query)
                    
                    async for record in result:
                        issues.append({
                            "id1": record.get("id1"),
                            "id2": record.get("id2"),
                            "types1": record.get("types1"),
                            "types2": record.get("types2"),
                            "property": prop,
                            "value": record.get("prop_value"),
                            "issue": f"Potential duplicate entities with same {prop}"
                        })
                except Exception as e:
                    logger.error(f"Error validating duplicate entities with property {prop}: {e}")
        
        return {
            "issues": issues
        }
    
    async def _fix_duplicate_entities(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fix duplicate entities by merging them.
        
        Args:
            issues: List of duplicate entity issues
            
        Returns:
            Fix results
        """
        fixed = []
        
        async with self.driver.session() as session:
            for issue in issues:
                id1 = issue.get("id1")
                id2 = issue.get("id2")
                
                if not id1 or not id2:
                    continue
                    
                try:
                    # Merge the entities by redirecting relationships
                    # This is a simplified implementation that keeps the first entity
                    # and redirects relationships from the second entity
                    
                    # Redirect incoming relationships
                    query1 = (
                        "MATCH (n2 {id: $id2})<-[r]-(other) "
                        "MATCH (n1 {id: $id1}) "
                        "WHERE NOT (other)-[:SAME_TYPE_AS {id: r.id}]->(n1) "
                        "CREATE (other)-[r2:SAME_TYPE_AS {id: r.id}]->(n1) "
                        "SET r2 = r "
                        "WITH r "
                        "DELETE r "
                        "RETURN count(r) as redirected"
                    )
                    
                    # Redirect outgoing relationships
                    query2 = (
                        "MATCH (n2 {id: $id2})-[r]->(other) "
                        "MATCH (n1 {id: $id1}) "
                        "WHERE NOT (n1)-[:SAME_TYPE_AS {id: r.id}]->(other) "
                        "CREATE (n1)-[r2:SAME_TYPE_AS {id: r.id}]->(other) "
                        "SET r2 = r "
                        "WITH r "
                        "DELETE r "
                        "RETURN count(r) as redirected"
                    )
                    
                    # Add a "duplicate_of" relationship
                    query3 = (
                        "MATCH (n1 {id: $id1}), (n2 {id: $id2}) "
                        "CREATE (n2)-[r:DUPLICATE_OF {created_at: datetime()}]->(n1) "
                        "RETURN r IS NOT NULL as created"
                    )
                    
                    # Execute the queries
                    result1 = await session.run(query1, {"id1": id1, "id2": id2})
                    record1 = await result1.single()
                    
                    result2 = await session.run(query2, {"id1": id1, "id2": id2})
                    record2 = await result2.single()
                    
                    result3 = await session.run(query3, {"id1": id1, "id2": id2})
                    record3 = await result3.single()
                    
                    redirected = (record1.get("redirected") or 0) + (record2.get("redirected") or 0)
                    created = record3.get("created") or False
                    
                    if redirected > 0 or created:
                        fixed.append({
                            "id1": id1,
                            "id2": id2,
                            "redirected_relationships": redirected,
                            "created_duplicate_rel": created,
                            "action": "Merged duplicate entities"
                        })
                        
                except Exception as e:
                    logger.error(f"Error fixing duplicate entities {id1}, {id2}: {e}")
        
        return {
            "fixed_count": len(fixed),
            "fixed": fixed
        }
    
    async def _validate_cycle_detection(self, entity_types: List[str], relationship_types: List[str]) -> Dict[str, Any]:
        """Validate for cycles in hierarchical relationships.
        
        Args:
            entity_types: List of entity types to check
            relationship_types: List of relationship types to check
            
        Returns:
            Validation results
        """
        issues = []
        hierarchical_rels = ["IS_A", "PART_OF"]
        
        # Filter relationship types if specified
        if relationship_types:
            hierarchical_rels = [rel for rel in hierarchical_rels if rel in relationship_types]
            
        if not hierarchical_rels:
            return {"issues": []}
            
        async with self.driver.session() as session:
            for rel_type in hierarchical_rels:
                # Build query based on entity types
                entity_filter = ""
                if entity_types:
                    type_filter = " OR ".join([f"n:{entity_type}" for entity_type in entity_types])
                    entity_filter = f"WHERE {type_filter}"
                    
                # Find cycles in the hierarchy
                query = (
                    f"MATCH path = (n)-[:{rel_type}*2..10]->(n) {entity_filter} "
                    "WITH nodes(path) as cycle_nodes, relationships(path) as cycle_rels "
                    "RETURN [node.id for node in cycle_nodes] as node_ids, "
                    "[rel.id for rel in cycle_rels] as rel_ids, "
                    "length(cycle_nodes) as cycle_length"
                )
                
                result = await session.run(query)
                
                async for record in result:
                    node_ids = record.get("node_ids", [])
                    rel_ids = record.get("rel_ids", [])
                    cycle_length = record.get("cycle_length", 0)
                    
                    issues.append({
                        "node_ids": node_ids,
                        "relationship_ids": rel_ids,
                        "relationship_type": rel_type,
                        "cycle_length": cycle_length,
                        "issue": f"Cycle detected in {rel_type} hierarchy with {cycle_length} nodes"
                    })
        
        return {
            "issues": issues
        }
    
    async def _fix_cycle_detection(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fix cycles in hierarchical relationships by removing one relationship.
        
        Args:
            issues: List of cycle issues
            
        Returns:
            Fix results
        """
        fixed = []
        
        async with self.driver.session() as session:
            for issue in issues:
                rel_ids = issue.get("relationship_ids", [])
                if not rel_ids:
                    continue
                    
                # Remove the last relationship in the cycle to break it
                rel_id_to_remove = rel_ids[-1]
                
                try:
                    query = "MATCH ()-[r {id: $rel_id}]->() DELETE r RETURN count(r) as deleted"
                    
                    result = await session.run(query, {"rel_id": rel_id_to_remove})
                    record = await result.single()
                    
                    if record and record.get("deleted") > 0:
                        fixed.append({
                            "relationship_id": rel_id_to_remove,
                            "relationship_type": issue.get("relationship_type"),
                            "cycle_length": issue.get("cycle_length"),
                            "action": "Removed relationship to break cycle"
                        })
                except Exception as e:
                    logger.error(f"Error fixing cycle by removing relationship {rel_id_to_remove}: {e}")
        
        return {
            "fixed_count": len(fixed),
            "fixed": fixed
        }
    
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