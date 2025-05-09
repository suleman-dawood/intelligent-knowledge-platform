#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Relation extractor module for identifying relationships between entities.
"""

import logging
import asyncio
import time
import re
from typing import Dict, List, Any, Optional, Tuple, Set
import uuid
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize

# Configure logging
logger = logging.getLogger(__name__)

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class RelationExtractor:
    """Extractor for identifying relationships between entities."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the relation extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Define relationship patterns (simplified)
        # In a real implementation, these would be more sophisticated
        self.relation_patterns = [
            {
                "name": "is_a",
                "patterns": [
                    r"(\w+)\s+is\s+a\s+(\w+)",
                    r"(\w+)\s+are\s+(\w+)",
                    r"(\w+)\s+as\s+a\s+(\w+)"
                ],
                "symmetric": False
            },
            {
                "name": "part_of",
                "patterns": [
                    r"(\w+)\s+is\s+part\s+of\s+(\w+)",
                    r"(\w+)\s+belongs\s+to\s+(\w+)",
                    r"(\w+)\s+consists\s+of\s+(\w+)"
                ],
                "symmetric": False
            },
            {
                "name": "related_to",
                "patterns": [
                    r"(\w+)\s+relates\s+to\s+(\w+)",
                    r"(\w+)\s+is\s+related\s+to\s+(\w+)",
                    r"(\w+)\s+connects\s+with\s+(\w+)"
                ],
                "symmetric": True
            },
            {
                "name": "cause_effect",
                "patterns": [
                    r"(\w+)\s+causes\s+(\w+)",
                    r"(\w+)\s+leads\s+to\s+(\w+)",
                    r"(\w+)\s+results\s+in\s+(\w+)"
                ],
                "symmetric": False
            }
        ]
        
        logger.info("Relation extractor initialized")
    
    async def extract(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relationships from text or entities.
        
        Args:
            task_data: Task data containing text and/or entities
            
        Returns:
            Extracted relationships
        """
        text = task_data.get('text')
        entities = task_data.get('entities', [])
        entity_ids = task_data.get('entity_ids', [])
        source_id = task_data.get('source_id')
        
        if not text and not entities:
            raise ValueError("No text or entities provided")
            
        logger.info("Extracting relationships")
        
        # Prepare result structure
        result = {
            "operation_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "source_id": source_id
        }
        
        # Process based on input type
        if text:
            # Extract entities and relationships from text
            extracted_entities, relationships = await self._extract_from_text(text)
            
            result["extracted_entities"] = extracted_entities
            result["relationships"] = relationships
            result["entity_count"] = len(extracted_entities)
            result["relationship_count"] = len(relationships)
            
        elif entities and entity_ids:
            # Analyze relationships between provided entities
            relationships = await self._analyze_entity_relationships(entities, entity_ids)
            
            result["relationships"] = relationships
            result["relationship_count"] = len(relationships)
            
        return result
    
    async def _extract_from_text(self, text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extract entities and relationships from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (entities, relationships)
        """
        # Tokenize text into sentences
        sentences = sent_tokenize(text)
        
        # Track extracted entities and relationships
        entities: Dict[str, Dict[str, Any]] = {}  # Using dict for deduplication
        relationships: List[Dict[str, Any]] = []
        
        # Process each sentence
        for sentence in sentences:
            # Extract potential entities and relationships from the sentence
            sentence_entities, sentence_relationships = self._process_sentence(sentence)
            
            # Add entities (deduplicating by mention)
            for entity in sentence_entities:
                mention = entity["mention"].lower()
                if mention not in entities:
                    entity_id = str(uuid.uuid4())
                    entities[mention] = {
                        "id": entity_id,
                        "type": entity["type"],
                        "mention": entity["mention"],
                        "properties": {
                            "source_text": entity["context"]
                        }
                    }
            
            # Add relationships
            for relationship in sentence_relationships:
                from_entity = relationship["from_entity"].lower()
                to_entity = relationship["to_entity"].lower()
                
                # Skip if either entity is not recognized
                if from_entity not in entities or to_entity not in entities:
                    continue
                    
                # Create relationship
                relationships.append({
                    "id": str(uuid.uuid4()),
                    "type": relationship["type"],
                    "from_id": entities[from_entity]["id"],
                    "to_id": entities[to_entity]["id"],
                    "properties": {
                        "confidence": relationship["confidence"],
                        "source_text": relationship["context"]
                    }
                })
                
            # Simulate processing time
            await asyncio.sleep(0.01)
            
        return list(entities.values()), relationships
    
    def _process_sentence(self, sentence: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Process a sentence to extract entities and relationships.
        
        Args:
            sentence: Sentence to process
            
        Returns:
            Tuple of (entities, relationships)
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP techniques
        
        entities = []
        relationships = []
        
        # Extract entities (simplified approach using capitalized words as potential entities)
        # In a real implementation, this would use named entity recognition
        words = sentence.split()
        for word in words:
            # Simple heuristic: capitalized words that aren't at the start of a sentence
            if word != words[0] and word[0].isupper() and len(word) > 3:
                entities.append({
                    "mention": word,
                    "type": "Concept",  # Simplified entity typing
                    "context": sentence
                })
        
        # Extract relationships using patterns
        for relation in self.relation_patterns:
            relation_type = relation["name"]
            
            for pattern in relation["patterns"]:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                
                for match in matches:
                    try:
                        from_entity = match.group(1)
                        to_entity = match.group(2)
                        
                        # Add the relationship
                        relationships.append({
                            "from_entity": from_entity,
                            "to_entity": to_entity,
                            "type": relation_type.upper(),
                            "confidence": 0.7,  # Simplified confidence score
                            "context": sentence
                        })
                        
                        # If the relationship is symmetric, add the reverse relationship
                        if relation["symmetric"]:
                            relationships.append({
                                "from_entity": to_entity,
                                "to_entity": from_entity,
                                "type": relation_type.upper(),
                                "confidence": 0.7,  # Simplified confidence score
                                "context": sentence
                            })
                    except Exception as e:
                        logger.warning(f"Error processing match: {e}")
        
        return entities, relationships
    
    async def _analyze_entity_relationships(self, entities: List[Dict[str, Any]], entity_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze relationships between provided entities.
        
        Args:
            entities: List of entities
            entity_ids: List of entity IDs
            
        Returns:
            List of relationships
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated methods to infer relationships
        
        relationships = []
        entity_map = {entity.get('id'): entity for entity in entities if entity.get('id')}
        
        # Find potential relationships based on entity properties
        for i, entity_id1 in enumerate(entity_ids):
            for entity_id2 in entity_ids[i+1:]:
                entity1 = entity_map.get(entity_id1)
                entity2 = entity_map.get(entity_id2)
                
                if not entity1 or not entity2:
                    continue
                    
                # Analyze potential relationship
                potential_relationships = self._infer_relationships(entity1, entity2)
                
                # Add to results
                relationships.extend(potential_relationships)
                
            # Simulate processing time
            await asyncio.sleep(0.01)
            
        return relationships
    
    def _infer_relationships(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Infer potential relationships between two entities.
        
        Args:
            entity1: First entity
            entity2: Second entity
            
        Returns:
            List of potential relationships
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated methods
        
        relationships = []
        entity1_type = entity1.get('type', 'Entity')
        entity2_type = entity2.get('type', 'Entity')
        
        # Simple heuristic: if entities have the same type, they might be related
        if entity1_type == entity2_type:
            relationships.append({
                "id": str(uuid.uuid4()),
                "type": "RELATED_TO",
                "from_id": entity1['id'],
                "to_id": entity2['id'],
                "properties": {
                    "confidence": 0.5,
                    "reason": f"Both entities are of type {entity1_type}"
                }
            })
        
        # If one entity type is a known subtype of another, create an IS_A relationship
        entity_hierarchy = {
            "Person": ["Author", "Scientist", "Artist"],
            "Location": ["City", "Country", "Landmark"],
            "Organization": ["Company", "University", "Government"]
        }
        
        for parent_type, child_types in entity_hierarchy.items():
            if entity1_type == parent_type and entity2_type in child_types:
                relationships.append({
                    "id": str(uuid.uuid4()),
                    "type": "IS_A",
                    "from_id": entity2['id'],
                    "to_id": entity1['id'],
                    "properties": {
                        "confidence": 0.8,
                        "reason": f"{entity2_type} is a {entity1_type}"
                    }
                })
            elif entity2_type == parent_type and entity1_type in child_types:
                relationships.append({
                    "id": str(uuid.uuid4()),
                    "type": "IS_A",
                    "from_id": entity1['id'],
                    "to_id": entity2['id'],
                    "properties": {
                        "confidence": 0.8,
                        "reason": f"{entity1_type} is a {entity2_type}"
                    }
                })
        
        return relationships 