#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM client for DeepSeek API integration.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Client for interacting with DeepSeek API."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the DeepSeek client.
        
        Args:
            config: Configuration dictionary containing API settings
        """
        self.config = config
        llm_config = config.get('llm', {})
        
        self.api_key = llm_config.get('deepseek_api_key')
        self.base_url = llm_config.get('deepseek_base_url', 'https://api.deepseek.com/v1')
        self.model = llm_config.get('model', 'deepseek-chat')
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required")
        
        # Initialize the async client
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"DeepSeek client initialized with model: {self.model}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Response dictionary with completion
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return {"stream": response}
            else:
                return {
                    "content": response.choices[0].message.content,
                    "usage": response.usage.dict() if response.usage else None,
                    "model": response.model
                }
                
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of extracted entities
        """
        prompt = f"""
        Extract named entities from the following text. Return them as a JSON list where each entity has:
        - "text": the entity text
        - "type": the entity type (PERSON, ORGANIZATION, LOCATION, MISC, etc.)
        - "start": start position in text
        - "end": end position in text
        
        Text: {text}
        
        Return only the JSON list, no other text.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert in named entity recognition. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.1)
        
        try:
            import json
            entities = json.loads(response["content"])
            return entities
        except json.JSONDecodeError:
            logger.warning("Failed to parse entity extraction response as JSON")
            return []
    
    async def extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relations between entities.
        
        Args:
            text: Source text
            entities: List of entities found in the text
            
        Returns:
            List of relations
        """
        entity_list = [f"{e['text']} ({e['type']})" for e in entities]
        
        prompt = f"""
        Given the following text and entities, extract relationships between them.
        Return as JSON list where each relation has:
        - "subject": subject entity text
        - "predicate": relationship type
        - "object": object entity text
        - "confidence": confidence score (0.0-1.0)
        
        Text: {text}
        
        Entities: {', '.join(entity_list)}
        
        Return only the JSON list, no other text.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert in relationship extraction. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.1)
        
        try:
            import json
            relations = json.loads(response["content"])
            return relations
        except json.JSONDecodeError:
            logger.warning("Failed to parse relation extraction response as JSON")
            return []
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summary text
        """
        prompt = f"""
        Summarize the following text in approximately {max_length} words or less. 
        Focus on the key points and main ideas.
        
        Text: {text}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert at creating concise, informative summaries."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.3)
        return response["content"]
    
    async def classify_sentiment(self, text: str) -> Dict[str, Any]:
        """Classify sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result
        """
        prompt = f"""
        Analyze the sentiment of the following text. Return as JSON with:
        - "sentiment": "positive", "negative", or "neutral"
        - "confidence": confidence score (0.0-1.0)
        - "reasoning": brief explanation
        
        Text: {text}
        
        Return only the JSON, no other text.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert in sentiment analysis. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.1)
        
        try:
            import json
            sentiment = json.loads(response["content"])
            return sentiment
        except json.JSONDecodeError:
            logger.warning("Failed to parse sentiment analysis response as JSON")
            return {"sentiment": "neutral", "confidence": 0.0, "reasoning": "Parse error"}
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text.
        
        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of keywords
        """
        prompt = f"""
        Extract the top {max_keywords} most important keywords from the following text.
        Return as a JSON list of strings, ordered by importance.
        
        Text: {text}
        
        Return only the JSON list, no other text.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert in keyword extraction. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.1)
        
        try:
            import json
            keywords = json.loads(response["content"])
            return keywords
        except json.JSONDecodeError:
            logger.warning("Failed to parse keyword extraction response as JSON")
            return []


# Global client instance
_client_instance = None


def get_llm_client(config: Dict[str, Any]) -> DeepSeekClient:
    """Get or create the global LLM client instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        DeepSeek client instance
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = DeepSeekClient(config)
    
    return _client_instance 