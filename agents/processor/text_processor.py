#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Text processor module for processing raw text data.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
import re
import hashlib
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Configure logging
logger = logging.getLogger(__name__)

# Download NLTK resources (in a real implementation, this would be done at install time)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class TextProcessor:
    """Processor for extracting and analyzing text content."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the text processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.stop_words = set(stopwords.words('english'))
        logger.info("Text processor initialized")
    
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process text content.
        
        Args:
            task_data: Task data containing text to process
            
        Returns:
            Processed text data
        """
        text = task_data.get('text')
        source_id = task_data.get('source_id')
        clean_text = task_data.get('clean_text', True)
        tokenize = task_data.get('tokenize', True)
        compute_stats = task_data.get('compute_stats', True)
        extract_keywords = task_data.get('extract_keywords', True)
        
        if not text:
            raise ValueError("Text content is required")
            
        logger.info(f"Processing text from source {source_id or 'unknown'}")
        
        # Create result structure
        result = {
            "source_id": source_id,
            "processed_at": time.time(),
            "original_length": len(text)
        }
        
        # Clean the text if requested
        if clean_text:
            cleaned_text = self._clean_text(text)
            result["cleaned_text"] = cleaned_text
        else:
            cleaned_text = text
            
        # Tokenize text if requested
        if tokenize:
            sentences = sent_tokenize(cleaned_text)
            words = word_tokenize(cleaned_text)
            
            # Remove stop words
            filtered_words = [word for word in words if word.lower() not in self.stop_words]
            
            result["sentences"] = sentences
            result["word_count"] = len(words)
            result["filtered_word_count"] = len(filtered_words)
            
            # Store tokenization results
            if task_data.get('include_tokens', False):
                result["words"] = words
                result["filtered_words"] = filtered_words
        
        # Compute text statistics if requested
        if compute_stats:
            stats = self._compute_text_statistics(cleaned_text)
            result["statistics"] = stats
            
        # Extract keywords if requested
        if extract_keywords:
            keywords = await self._extract_keywords(cleaned_text)
            result["keywords"] = keywords
            
        # Generate a content hash for deduplication
        content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
        result["content_hash"] = content_hash
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean the text by removing extra whitespace, formatting, etc.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Replace multiple newlines with a single one
        text = re.sub(r'\n+', '\n', text)
        
        # Replace multiple spaces with a single one
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _compute_text_statistics(self, text: str) -> Dict[str, Any]:
        """Compute statistics about the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of text statistics
        """
        # Split into sentences and words
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Calculate basic statistics
        num_sentences = len(sentences)
        num_words = len(words)
        num_chars = len(text)
        
        # Calculate average sentence and word length
        avg_sentence_length = num_words / num_sentences if num_sentences > 0 else 0
        avg_word_length = sum(len(word) for word in words) / num_words if num_words > 0 else 0
        
        # Calculate word frequency
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if word_lower not in self.stop_words and len(word_lower) > 1:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # Get top 10 most frequent words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "sentence_count": num_sentences,
            "word_count": num_words,
            "character_count": num_chars,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_word_length": round(avg_word_length, 2),
            "top_words": top_words
        }
    
    async def _extract_keywords(self, text: str) -> List[Dict[str, Any]]:
        """Extract keywords from the text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords with scores
        """
        # In a real implementation, this would use more sophisticated methods
        # like TF-IDF or a keyword extraction library
        
        # Simple implementation based on word frequency and filtering
        words = word_tokenize(text.lower())
        word_freq = {}
        
        # Count word occurrences, ignoring stop words and short words
        for word in words:
            if word not in self.stop_words and len(word) > 3 and word.isalpha():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 20 words
        keywords = [
            {"word": word, "score": count / len(words), "count": count}
            for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        ]
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        return keywords 