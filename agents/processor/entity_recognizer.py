#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entity recognizer module for identifying named entities in text.
"""

import logging
import asyncio
import time
import re
from typing import Dict, List, Any, Optional
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag, ne_chunk
from nltk.chunk import tree2conlltags

# Import DeepSeek LLM client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from coordinator.llm_client import get_llm_client

# Configure logging
logger = logging.getLogger(__name__)

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('chunkers/maxent_ne_chunker')
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('maxent_ne_chunker', quiet=True)
    nltk.download('words', quiet=True)


class EntityRecognizer:
    """Recognizer for identifying named entities in text."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the entity recognizer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize LLM client if available
        self.llm_client = None
        try:
            if config.get('llm', {}).get('deepseek_api_key'):
                self.llm_client = get_llm_client(config)
                logger.info("DeepSeek LLM client initialized for entity recognition")
        except Exception as e:
            logger.warning(f"Could not initialize LLM client: {e}")
        
        # Entity type mappings
        self.entity_types = {
            "PERSON": "person",
            "GPE": "location",  # Geo-Political Entity
            "ORGANIZATION": "organization",
            "FACILITY": "facility",
            "GSP": "location",
            "LOCATION": "location"
        }
        
        # Regular expressions for additional entity types
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%!$&\'()*+,;=:~]+)*(?:\?[-\w%!$&\'()*+,;=:~.]+)*',
            "date": r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            "phone": r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        }
        
        logger.info("Entity recognizer initialized")
    
    async def recognize(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize named entities in text.
        
        Args:
            task_data: Task data containing text to analyze
            
        Returns:
            Recognized entities
        """
        text = task_data.get('text')
        include_pos = task_data.get('include_pos', False)
        extract_regex = task_data.get('extract_regex', True)
        use_llm = task_data.get('use_llm', True)
        
        if not text:
            raise ValueError("Text content is required")
            
        logger.info("Recognizing entities in text")
        
        # Prepare result structure
        result = {
            "processed_at": time.time(),
            "text_length": len(text)
        }
        
        # Extract named entities using NLTK
        entities, pos_tags = await self._extract_entities_nltk(text)
        
        # Extract entities using LLM if available and requested
        if use_llm and self.llm_client:
            try:
                llm_entities = await self._extract_entities_llm(text)
                # Merge LLM entities with NLTK entities
                entities = self._merge_entities(entities, llm_entities)
            except Exception as e:
                logger.warning(f"LLM entity extraction failed: {e}")
        
        # Group entities by type
        grouped_entities = {}
        for entity in entities:
            entity_type = entity["type"]
            if entity_type not in grouped_entities:
                grouped_entities[entity_type] = []
                
            grouped_entities[entity_type].append(entity)
            
        result["entities"] = grouped_entities
        result["entity_count"] = len(entities)
        
        # Include POS tags if requested
        if include_pos:
            result["pos_tags"] = pos_tags
            
        # Extract regex-based entities if requested
        if extract_regex:
            regex_entities = await self._extract_regex_entities(text)
            
            # Add regex entities to result
            for entity_type, entities_list in regex_entities.items():
                if entity_type not in grouped_entities:
                    grouped_entities[entity_type] = []
                    
                grouped_entities[entity_type].extend(entities_list)
                result["entity_count"] += len(entities_list)
            
        # Create a summary of entity counts by type
        entity_summary = {
            entity_type: len(entities_list)
            for entity_type, entities_list in grouped_entities.items()
        }
        result["entity_summary"] = entity_summary
        
        return result
    
    async def _extract_entities_nltk(self, text: str) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Extract named entities using NLTK.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (list of entities, POS tag counts)
        """
        # Tokenize sentences
        sentences = sent_tokenize(text)
        
        entities = []
        pos_tag_counts = {}
        
        for sentence in sentences:
            # Tokenize words
            tokens = word_tokenize(sentence)
            
            # Perform POS tagging
            pos_tagged = pos_tag(tokens)
            
            # Count POS tags
            for _, tag in pos_tagged:
                pos_tag_counts[tag] = pos_tag_counts.get(tag, 0) + 1
            
            # Perform named entity recognition
            ne_tree = ne_chunk(pos_tagged)
            
            # Extract named entities
            iob_tagged = tree2conlltags(ne_tree)
            
            # Process entities
            current_entity = None
            current_type = None
            
            for word, pos, iob in iob_tagged:
                if iob.startswith('B-'):
                    # Begin a new entity
                    if current_entity:
                        # Add the previous entity to the results
                        self._add_entity(entities, current_entity, current_type, sentence)
                        
                    current_entity = word
                    current_type = iob[2:]  # Remove the 'B-' prefix
                    
                elif iob.startswith('I-') and current_entity:
                    # Inside an entity
                    current_entity += f" {word}"
                    
                elif current_entity:
                    # End of an entity
                    self._add_entity(entities, current_entity, current_type, sentence)
                    current_entity = None
                    current_type = None
                    
        # Handle any remaining entity
        if current_entity:
            self._add_entity(entities, current_entity, current_type, sentence)
            
        # Simulate processing time
        await asyncio.sleep(0.1)
            
        return entities, pos_tag_counts
    
    def _add_entity(self, entities: List[Dict[str, Any]], entity: str, entity_type: str, context: str) -> None:
        """Add an entity to the results.
        
        Args:
            entities: List to add the entity to
            entity: Entity text
            entity_type: Original entity type
            context: Sentence context
        """
        # Map the entity type to our standardized types
        mapped_type = self.entity_types.get(entity_type, entity_type.lower())
        
        entities.append({
            "text": entity,
            "type": mapped_type,
            "original_type": entity_type,
            "context": context
        })
    
    async def _extract_entities_llm(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using DeepSeek LLM.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of entities
        """
        if not self.llm_client:
            return []
        
        try:
            # Limit text length for LLM processing
            if len(text) > 4000:
                text = text[:4000] + "..."
            
            llm_entities = await self.llm_client.extract_entities(text)
            
            # Convert LLM format to our format
            entities = []
            for entity in llm_entities:
                entities.append({
                    "text": entity.get("text", ""),
                    "type": entity.get("type", "").lower(),
                    "start": entity.get("start", 0),
                    "end": entity.get("end", 0),
                    "confidence": 0.8,  # Default confidence for LLM
                    "source": "llm",
                    "context": text[max(0, entity.get("start", 0) - 50):entity.get("end", 0) + 50]
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities with LLM: {e}")
            return []
    
    def _merge_entities(self, nltk_entities: List[Dict[str, Any]], llm_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge entities from different sources, removing duplicates.
        
        Args:
            nltk_entities: Entities from NLTK
            llm_entities: Entities from LLM
            
        Returns:
            Merged list of entities
        """
        merged = []
        seen_entities = set()
        
        # Add NLTK entities first
        for entity in nltk_entities:
            entity_key = (entity["text"].lower(), entity["type"])
            if entity_key not in seen_entities:
                merged.append(entity)
                seen_entities.add(entity_key)
        
        # Add LLM entities that aren't duplicates
        for entity in llm_entities:
            entity_key = (entity["text"].lower(), entity["type"])
            if entity_key not in seen_entities:
                merged.append(entity)
                seen_entities.add(entity_key)
        
        return merged
    
    async def _extract_regex_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities using regular expressions.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of entity types with their entities
        """
        regex_entities = {}
        
        # Apply each regex pattern
        for entity_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            
            entities_list = []
            for match in matches:
                entity_text = match.group(0)
                
                # Find the context (sentence) containing this entity
                entity_start = match.start()
                entity_end = match.end()
                
                # Find the sentence containing this entity
                sentences = sent_tokenize(text)
                context = ""
                current_pos = 0
                
                for sentence in sentences:
                    sentence_start = current_pos
                    sentence_end = sentence_start + len(sentence)
                    
                    if sentence_start <= entity_start < sentence_end:
                        context = sentence
                        break
                        
                    current_pos = sentence_end + 1
                
                entities_list.append({
                    "text": entity_text,
                    "type": entity_type,
                    "original_type": entity_type,
                    "context": context
                })
                
            if entities_list:
                regex_entities[entity_type] = entities_list
                
        # Simulate processing time
        await asyncio.sleep(0.1)
                
        return regex_entities 