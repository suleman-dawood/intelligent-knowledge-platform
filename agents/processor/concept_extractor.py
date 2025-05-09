#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Concept extractor module for identifying high-level concepts in text.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams

# Configure logging
logger = logging.getLogger(__name__)


class ConceptExtractor:
    """Extractor for identifying concepts within content."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the concept extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Load stop words
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
            
        # Define concept categories (in a real implementation, these would be more extensive)
        self.concept_categories = {
            "technology": [
                "algorithm", "software", "hardware", "data", "internet", "computer", 
                "network", "programming", "artificial intelligence", "machine learning"
            ],
            "science": [
                "physics", "biology", "chemistry", "mathematics", "research", "experiment",
                "theory", "hypothesis", "scientific", "molecule", "atom", "cell"
            ],
            "business": [
                "finance", "economics", "market", "investment", "entrepreneurship", "startup",
                "corporation", "profit", "revenue", "strategy", "management", "innovation"
            ],
            "academic": [
                "education", "university", "college", "study", "research", "thesis", 
                "dissertation", "academic", "scholarship", "journal", "publication"
            ]
        }
        
        # Flatten the concept list for faster matching
        self.all_concepts = {}
        for category, concepts in self.concept_categories.items():
            for concept in concepts:
                self.all_concepts[concept] = category
                
        logger.info("Concept extractor initialized")
    
    async def extract(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract concepts from content.
        
        Args:
            task_data: Task data containing content to analyze
            
        Returns:
            Extracted concepts and related information
        """
        text = task_data.get('text')
        max_concepts = task_data.get('max_concepts', 20)
        extract_phrases = task_data.get('extract_phrases', True)
        categorize = task_data.get('categorize', True)
        
        if not text:
            raise ValueError("Text content is required")
            
        logger.info("Extracting concepts from text")
        
        # Prepare result structure
        result = {
            "processed_at": time.time(),
            "text_length": len(text)
        }
        
        # Extract single-word concepts
        single_concepts = await self._extract_concepts(text)
        
        # Extract multi-word phrases if requested
        if extract_phrases:
            phrases = await self._extract_phrases(text)
            result["phrases"] = phrases[:max_concepts]
            
        # Categorize concepts if requested
        if categorize:
            categorized = self._categorize_concepts(single_concepts)
            result["categorized_concepts"] = categorized
            
        # Get the top concepts
        top_concepts = sorted(single_concepts.items(), key=lambda x: x[1], reverse=True)[:max_concepts]
        result["concepts"] = [{"concept": c, "score": s} for c, s in top_concepts]
        
        # Add the most relevant concept categories
        if categorize:
            category_scores = {}
            for concept, score in single_concepts.items():
                category = self._get_concept_category(concept)
                if category:
                    category_scores[category] = category_scores.get(category, 0) + score
                    
            top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            result["top_categories"] = [{"category": c, "relevance": s} for c, s in top_categories]
        
        return result
    
    async def _extract_concepts(self, text: str) -> Dict[str, float]:
        """Extract single-word concepts from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of concepts with their relevance scores
        """
        # Tokenize and normalize text
        tokens = word_tokenize(text.lower())
        
        # Filter out stop words and short words
        filtered_tokens = [token for token in tokens if token.isalpha() and 
                         token not in self.stop_words and len(token) > 3]
        
        # Count occurrences of each token
        concept_counts = {}
        for token in filtered_tokens:
            concept_counts[token] = concept_counts.get(token, 0) + 1
            
        # Calculate relevance scores (simple frequency-based approach)
        total_tokens = len(filtered_tokens) or 1  # Avoid division by zero
        concept_scores = {concept: count / total_tokens for concept, count in concept_counts.items()}
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        return concept_scores
    
    async def _extract_phrases(self, text: str) -> List[Dict[str, Any]]:
        """Extract multi-word phrases that might represent concepts.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of phrases with their relevance scores
        """
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Generate n-grams (2 and 3 word phrases)
        bigrams_list = list(ngrams(tokens, 2))
        trigrams_list = list(ngrams(tokens, 3))
        
        # Filter n-grams to only include those without stop words
        filtered_bigrams = []
        for bigram in bigrams_list:
            if all(token not in self.stop_words and token.isalpha() for token in bigram):
                filtered_bigrams.append(" ".join(bigram))
                
        filtered_trigrams = []
        for trigram in trigrams_list:
            if all(token not in self.stop_words and token.isalpha() for token in trigram):
                filtered_trigrams.append(" ".join(trigram))
        
        # Count phrase occurrences
        bigram_counts = {}
        for bigram in filtered_bigrams:
            bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1
            
        trigram_counts = {}
        for trigram in filtered_trigrams:
            trigram_counts[trigram] = trigram_counts.get(trigram, 0) + 1
            
        # Combine and sort by count
        all_phrases = list(bigram_counts.items()) + list(trigram_counts.items())
        sorted_phrases = sorted(all_phrases, key=lambda x: x[1], reverse=True)
        
        # Convert to result format
        result_phrases = [
            {"phrase": phrase, "count": count, "words": len(phrase.split())}
            for phrase, count in sorted_phrases
        ]
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        return result_phrases
    
    def _categorize_concepts(self, concepts: Dict[str, float]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize concepts into predefined categories.
        
        Args:
            concepts: Dictionary of concepts with their scores
            
        Returns:
            Dictionary of categories with their concepts
        """
        categorized = {}
        
        for concept, score in concepts.items():
            category = self._get_concept_category(concept)
            
            if category:
                if category not in categorized:
                    categorized[category] = []
                    
                categorized[category].append({
                    "concept": concept,
                    "score": score
                })
                
        # Sort concepts within each category by score
        for category in categorized:
            categorized[category] = sorted(
                categorized[category], 
                key=lambda x: x["score"], 
                reverse=True
            )
            
        return categorized
    
    def _get_concept_category(self, concept: str) -> Optional[str]:
        """Get the category for a concept.
        
        Args:
            concept: Concept to categorize
            
        Returns:
            Category name or None if not found
        """
        # Check for exact matches
        if concept in self.all_concepts:
            return self.all_concepts[concept]
            
        # Check for partial matches
        for known_concept, category in self.all_concepts.items():
            if concept in known_concept or known_concept in concept:
                return category
                
        return None 