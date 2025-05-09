#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Knowledge enhancer module for improving the knowledge graph based on feedback and analytics.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple, Set
import uuid
from datetime import datetime
from neo4j import AsyncGraphDatabase

# Configure logging
logger = logging.getLogger(__name__)


class KnowledgeEnhancer:
    """Enhancer for improving the knowledge graph based on feedback and analytics."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the knowledge enhancer.
        
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
        
        # Enhancement strategies
        self.strategies = {
            "add_missing_relationships": self._enhance_add_missing_relationships,
            "improve_entity_classifications": self._enhance_entity_classifications,
            "merge_similar_entities": self._enhance_merge_similar_entities,
            "add_temporal_relationships": self._enhance_temporal_relationships,
            "enrich_properties": self._enhance_enrich_properties
        }
        
        logger.info("Knowledge enhancer initialized")
    
    async def enhance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the knowledge graph based on feedback and analytics.
        
        Args:
            task_data: Task data specifying enhancement parameters
            
        Returns:
            Enhancement results
        """
        strategy_name = task_data.get('strategy')
        entity_types = task_data.get('entity_types', [])
        relationship_types = task_data.get('relationship_types', [])
        target_entities = task_data.get('target_entities', [])
        feedback_data = task_data.get('feedback_data', {})
        model_id = task_data.get('model_id')  # Optional model to use
        
        if not strategy_name:
            raise ValueError("Enhancement strategy must be specified")
            
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown enhancement strategy: {strategy_name}. Supported strategies: {', '.join(self.strategies.keys())}")
            
        logger.info(f"Enhancing knowledge graph with strategy: {strategy_name}")
        
        # Connect to Neo4j
        await self._connect()
        
        try:
            # Apply the enhancement strategy
            strategy_func = self.strategies[strategy_name]
            enhancement_results = await strategy_func(
                entity_types, relationship_types, target_entities, feedback_data, model_id
            )
            
            # Get graph statistics after enhancement
            stats = await self._get_graph_statistics()
            
            return {
                "operation_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "strategy": strategy_name,
                "enhancement_results": enhancement_results,
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
    
    async def _enhance_add_missing_relationships(self, entity_types: List[str], 
                                              relationship_types: List[str],
                                              target_entities: List[str],
                                              feedback_data: Dict[str, Any],
                                              model_id: Optional[str]) -> Dict[str, Any]:
        """Enhance the graph by adding missing relationships based on entity similarity.
        
        Args:
            entity_types: Entity types to focus on
            relationship_types: Relationship types to add
            target_entities: Specific entities to focus on
            feedback_data: Feedback data to guide enhancement
            model_id: Optional model ID to use
            
        Returns:
            Enhancement results
        """
        added_relationships = []
        
        # Default relationship type if none specified
        rel_type = relationship_types[0] if relationship_types else "RELATED_TO"
        
        async with self.driver.session() as session:
            # Find entities with similar properties but no direct relationship
            query = """
            MATCH (a), (b)
            WHERE a <> b
            AND (a:$entity_type) AND (b:$entity_type)
            AND (a.name IS NOT NULL) AND (b.name IS NOT NULL)
            AND NOT (a)-[:$rel_type]-(b)
            AND a.name =~ ('(?i).*' + b.name + '.*') OR b.name =~ ('(?i).*' + a.name + '.*')
            RETURN a.id as source_id, b.id as target_id, a.name as source_name, b.name as target_name
            LIMIT 100
            """
            
            for entity_type in entity_types:
                try:
                    result = await session.run(
                        query,
                        {
                            "entity_type": entity_type,
                            "rel_type": rel_type
                        }
                    )
                    
                    # Process the results
                    async for record in result:
                        source_id = record.get("source_id")
                        target_id = record.get("target_id")
                        source_name = record.get("source_name")
                        target_name = record.get("target_name")
                        
                        # Create relationship
                        create_query = """
                        MATCH (a {id: $source_id}), (b {id: $target_id})
                        CREATE (a)-[r:$rel_type {id: $rel_id, created_at: datetime(), automatic: true}]->(b)
                        RETURN r.id as rel_id
                        """
                        
                        rel_id = str(uuid.uuid4())
                        create_result = await session.run(
                            create_query,
                            {
                                "source_id": source_id,
                                "target_id": target_id,
                                "rel_type": rel_type,
                                "rel_id": rel_id
                            }
                        )
                        
                        rel_record = await create_result.single()
                        if rel_record:
                            added_relationships.append({
                                "source_id": source_id,
                                "target_id": target_id,
                                "source_name": source_name,
                                "target_name": target_name,
                                "relationship_type": rel_type,
                                "relationship_id": rel_id,
                                "confidence": 0.7,
                                "reason": "Name similarity"
                            })
                            
                except Exception as e:
                    logger.error(f"Error processing entity type {entity_type}: {e}")
                    
        return {
            "added_relationships": added_relationships,
            "relationship_count": len(added_relationships),
            "entity_types_processed": entity_types
        }
    
    async def _enhance_entity_classifications(self, entity_types: List[str], 
                                           relationship_types: List[str],
                                           target_entities: List[str],
                                           feedback_data: Dict[str, Any],
                                           model_id: Optional[str]) -> Dict[str, Any]:
        """Enhance entity classifications based on connections and properties.
        
        Args:
            entity_types: Entity types to focus on
            relationship_types: Relationship types to consider
            target_entities: Specific entities to focus on
            feedback_data: Feedback data to guide enhancement
            model_id: Optional model ID to use
            
        Returns:
            Enhancement results
        """
        updated_entities = []
        
        async with self.driver.session() as session:
            # Find entities with ambiguous classifications
            for entity_type in entity_types:
                # Find entities with multiple types
                query = """
                MATCH (n)
                WHERE $entity_type IN labels(n)
                WITH n, labels(n) as types
                WHERE size(types) > 1
                RETURN n.id as id, n.name as name, types
                LIMIT 50
                """
                
                try:
                    result = await session.run(query, {"entity_type": entity_type})
                    
                    async for record in result:
                        entity_id = record.get("id")
                        entity_name = record.get("name")
                        current_types = record.get("types")
                        
                        # Determine the most appropriate type based on connections
                        type_query = """
                        MATCH (n {id: $entity_id})-[r]-(related)
                        WITH labels(related) as rel_types, count(*) as rel_count
                        ORDER BY rel_count DESC
                        LIMIT 1
                        RETURN rel_types[0] as suggested_type
                        """
                        
                        type_result = await session.run(type_query, {"entity_id": entity_id})
                        type_record = await type_result.single()
                        
                        if type_record:
                            suggested_type = type_record.get("suggested_type")
                            
                            if suggested_type and suggested_type != entity_type:
                                # Update the entity's primary type
                                update_query = """
                                MATCH (n {id: $entity_id})
                                REMOVE n:$old_type
                                SET n:$new_type, n.primary_type = $new_type
                                RETURN n.id as id
                                """
                                
                                await session.run(
                                    update_query,
                                    {
                                        "entity_id": entity_id,
                                        "old_type": entity_type,
                                        "new_type": suggested_type
                                    }
                                )
                                
                                updated_entities.append({
                                    "id": entity_id,
                                    "name": entity_name,
                                    "old_type": entity_type,
                                    "new_type": suggested_type,
                                    "reason": "Connection-based reclassification"
                                })
                                
                except Exception as e:
                    logger.error(f"Error processing entity type {entity_type}: {e}")
                    
        return {
            "updated_entities": updated_entities,
            "entity_count": len(updated_entities),
            "entity_types_processed": entity_types
        }
    
    async def _enhance_merge_similar_entities(self, entity_types: List[str], 
                                           relationship_types: List[str],
                                           target_entities: List[str],
                                           feedback_data: Dict[str, Any],
                                           model_id: Optional[str]) -> Dict[str, Any]:
        """Enhance by merging highly similar entities to reduce duplication.
        
        Args:
            entity_types: Entity types to focus on
            relationship_types: Relationship types to consider
            target_entities: Specific entities to focus on
            feedback_data: Feedback data to guide enhancement
            model_id: Optional model ID to use
            
        Returns:
            Enhancement results
        """
        merged_entities = []
        
        # Skip if no entity types specified
        if not entity_types:
            return {
                "merged_entities": [],
                "entity_count": 0,
                "entity_types_processed": []
            }
            
        async with self.driver.session() as session:
            for entity_type in entity_types:
                # Find similar entities based on name
                query = """
                MATCH (a:$entity_type), (b:$entity_type)
                WHERE a.id <> b.id
                AND a.name IS NOT NULL AND b.name IS NOT NULL
                AND (
                    a.name = b.name OR
                    a.name =~ ('(?i).*' + b.name + '.*') OR
                    b.name =~ ('(?i).*' + a.name + '.*')
                )
                RETURN a.id as id1, b.id as id2, a.name as name1, b.name as name2
                LIMIT 50
                """
                
                try:
                    result = await session.run(query, {"entity_type": entity_type})
                    
                    async for record in result:
                        id1 = record.get("id1")
                        id2 = record.get("id2")
                        name1 = record.get("name1")
                        name2 = record.get("name2")
                        
                        # Determine which entity to keep (prefer the one with more relationships)
                        count_query = """
                        MATCH (a {id: $id1})-[r1]-()
                        WITH count(r1) as count1
                        MATCH (b {id: $id2})-[r2]-()
                        WITH count1, count(r2) as count2
                        RETURN count1, count2
                        """
                        
                        count_result = await session.run(count_query, {"id1": id1, "id2": id2})
                        count_record = await count_result.single()
                        
                        if count_record:
                            count1 = count_record.get("count1")
                            count2 = count_record.get("count2")
                            
                            # Keep the entity with more relationships
                            keep_id = id1 if count1 >= count2 else id2
                            merge_id = id2 if count1 >= count2 else id1
                            keep_name = name1 if count1 >= count2 else name2
                            merge_name = name2 if count1 >= count2 else name1
                            
                            # Redirect relationships from the entity to be merged
                            redirect_query = """
                            MATCH (merge {id: $merge_id})-[r]->(other)
                            WHERE NOT (keep {id: $keep_id})-[:SAME_TYPE_AS]->(other)
                            MATCH (keep {id: $keep_id})
                            CREATE (keep)-[r2:SAME_TYPE_AS]->(other)
                            SET r2 = r
                            WITH r
                            DELETE r
                            RETURN count(r) as redirected
                            """
                            
                            redirect_result = await session.run(
                                redirect_query,
                                {
                                    "keep_id": keep_id,
                                    "merge_id": merge_id
                                }
                            )
                            
                            # Mark the merged entity
                            mark_query = """
                            MATCH (keep {id: $keep_id}), (merge {id: $merge_id})
                            CREATE (merge)-[r:MERGED_INTO {created_at: datetime()}]->(keep)
                            SET merge.merged = true, merge.active = false
                            RETURN r.id as rel_id
                            """
                            
                            await session.run(mark_query, {"keep_id": keep_id, "merge_id": merge_id})
                            
                            merged_entities.append({
                                "keep_id": keep_id,
                                "keep_name": keep_name,
                                "merge_id": merge_id,
                                "merge_name": merge_name,
                                "entity_type": entity_type,
                                "reason": "Name similarity"
                            })
                            
                except Exception as e:
                    logger.error(f"Error processing entity type {entity_type}: {e}")
                    
        return {
            "merged_entities": merged_entities,
            "entity_count": len(merged_entities),
            "entity_types_processed": entity_types
        }
    
    async def _enhance_temporal_relationships(self, entity_types: List[str], 
                                           relationship_types: List[str],
                                           target_entities: List[str],
                                           feedback_data: Dict[str, Any],
                                           model_id: Optional[str]) -> Dict[str, Any]:
        """Enhance by adding temporal relationships between entities with timestamps.
        
        Args:
            entity_types: Entity types to focus on
            relationship_types: Relationship types to consider
            target_entities: Specific entities to focus on
            feedback_data: Feedback data to guide enhancement
            model_id: Optional model ID to use
            
        Returns:
            Enhancement results
        """
        added_relationships = []
        
        # Set temporal relationship type
        temporal_rel_type = "FOLLOWS"
        
        async with self.driver.session() as session:
            for entity_type in entity_types:
                # Find entities with timestamp properties
                query = """
                MATCH (a:$entity_type), (b:$entity_type)
                WHERE a <> b
                AND a.timestamp IS NOT NULL AND b.timestamp IS NOT NULL
                AND NOT (a)-[:$rel_type]->(b)
                AND a.timestamp < b.timestamp
                RETURN a.id as before_id, b.id as after_id, a.name as before_name, b.name as after_name,
                       a.timestamp as before_time, b.timestamp as after_time
                ORDER BY a.timestamp, b.timestamp
                LIMIT 100
                """
                
                try:
                    result = await session.run(
                        query,
                        {
                            "entity_type": entity_type,
                            "rel_type": temporal_rel_type
                        }
                    )
                    
                    async for record in result:
                        before_id = record.get("before_id")
                        after_id = record.get("after_id")
                        before_name = record.get("before_name")
                        after_name = record.get("after_name")
                        
                        # Create temporal relationship
                        create_query = """
                        MATCH (a {id: $before_id}), (b {id: $after_id})
                        CREATE (a)-[r:$rel_type {
                            id: $rel_id, 
                            created_at: datetime(), 
                            automatic: true,
                            time_difference: duration.between(a.timestamp, b.timestamp)
                        }]->(b)
                        RETURN r.id as rel_id
                        """
                        
                        rel_id = str(uuid.uuid4())
                        create_result = await session.run(
                            create_query,
                            {
                                "before_id": before_id,
                                "after_id": after_id,
                                "rel_type": temporal_rel_type,
                                "rel_id": rel_id
                            }
                        )
                        
                        rel_record = await create_result.single()
                        if rel_record:
                            added_relationships.append({
                                "source_id": before_id,
                                "target_id": after_id,
                                "source_name": before_name,
                                "target_name": after_name,
                                "relationship_type": temporal_rel_type,
                                "relationship_id": rel_id,
                                "reason": "Temporal sequence"
                            })
                            
                except Exception as e:
                    logger.error(f"Error processing entity type {entity_type}: {e}")
                    
        return {
            "added_relationships": added_relationships,
            "relationship_count": len(added_relationships),
            "entity_types_processed": entity_types
        }
    
    async def _enhance_enrich_properties(self, entity_types: List[str], 
                                      relationship_types: List[str],
                                      target_entities: List[str],
                                      feedback_data: Dict[str, Any],
                                      model_id: Optional[str]) -> Dict[str, Any]:
        """Enhance by enriching entity properties based on connections and feedback.
        
        Args:
            entity_types: Entity types to focus on
            relationship_types: Relationship types to consider
            target_entities: Specific entities to focus on
            feedback_data: Feedback data to guide enhancement
            model_id: Optional model ID to use
            
        Returns:
            Enhancement results
        """
        enriched_entities = []
        
        # Use feedback data to enhance entity properties
        if feedback_data and 'entity_properties' in feedback_data:
            properties_to_add = feedback_data['entity_properties']
            
            async with self.driver.session() as session:
                for entity_id, properties in properties_to_add.items():
                    # Check if entity exists
                    check_query = "MATCH (n {id: $entity_id}) RETURN n.id as id, labels(n) as types"
                    check_result = await session.run(check_query, {"entity_id": entity_id})
                    check_record = await check_result.single()
                    
                    if check_record:
                        entity_types = check_record.get("types")
                        
                        # Update entity properties
                        props_str = ", ".join([f"n.{key} = ${key}" for key in properties.keys()])
                        update_query = f"MATCH (n {{id: $entity_id}}) SET {props_str} RETURN n.id as id"
                        
                        params = {"entity_id": entity_id}
                        params.update(properties)
                        
                        update_result = await session.run(update_query, params)
                        update_record = await update_result.single()
                        
                        if update_record:
                            enriched_entities.append({
                                "id": entity_id,
                                "types": entity_types,
                                "added_properties": list(properties.keys()),
                                "reason": "User feedback"
                            })
        
        # Propagate common properties from related entities
        async with self.driver.session() as session:
            for entity_type in entity_types:
                # Find entities with connections that share common properties
                query = """
                MATCH (a:$entity_type)-[r]-(b)
                WHERE a.name IS NOT NULL AND b.name IS NOT NULL
                WITH a, b, keys(a) as a_keys, keys(b) as b_keys
                WHERE size([k in b_keys WHERE NOT k in a_keys]) > 0
                RETURN a.id as entity_id, a.name as entity_name, 
                       b.id as related_id, b.name as related_name,
                       [k in b_keys WHERE NOT k in a_keys] as missing_props
                LIMIT 50
                """
                
                try:
                    result = await session.run(query, {"entity_type": entity_type})
                    
                    async for record in result:
                        entity_id = record.get("entity_id")
                        entity_name = record.get("entity_name")
                        related_id = record.get("related_id")
                        related_name = record.get("related_name")
                        missing_props = record.get("missing_props")
                        
                        # Get property values from related entity
                        prop_query = f"MATCH (b {{id: $related_id}}) RETURN {', '.join(['b.' + prop + ' as ' + prop for prop in missing_props])}"
                        prop_result = await session.run(prop_query, {"related_id": related_id})
                        prop_record = await prop_result.single()
                        
                        if prop_record:
                            # Add properties to entity
                            props_to_add = {}
                            for prop in missing_props:
                                value = prop_record.get(prop)
                                if value is not None:
                                    props_to_add[prop] = value
                                    
                            if props_to_add:
                                # Update entity
                                props_str = ", ".join([f"a.{key} = ${key}" for key in props_to_add.keys()])
                                update_query = f"MATCH (a {{id: $entity_id}}) SET {props_str} RETURN a.id as id"
                                
                                params = {"entity_id": entity_id}
                                params.update(props_to_add)
                                
                                await session.run(update_query, params)
                                
                                enriched_entities.append({
                                    "id": entity_id,
                                    "name": entity_name,
                                    "related_id": related_id,
                                    "related_name": related_name,
                                    "added_properties": list(props_to_add.keys()),
                                    "reason": "Property propagation"
                                })
                                
                except Exception as e:
                    logger.error(f"Error processing entity type {entity_type}: {e}")
                    
        return {
            "enriched_entities": enriched_entities,
            "entity_count": len(enriched_entities),
            "entity_types_processed": entity_types
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