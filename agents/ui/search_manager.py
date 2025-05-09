#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Search manager for the UI agent.
Handles search queries and results.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SearchManager:
    """Manager for handling search queries and results."""
    
    def __init__(self, config: Dict[str, Any], message_broker=None):
        """Initialize the search manager.
        
        Args:
            config: Configuration dictionary
            message_broker: Message broker instance for sending tasks to other agents
        """
        self.config = config
        self.message_broker = message_broker
        
        # Default search parameters
        self.default_params = {
            "max_results": 20,
            "include_metadata": True,
            "sort_by": "relevance",
            "filter_types": [],
            "min_confidence": 0.6
        }
        
        # Recent searches (in-memory cache)
        self.recent_searches = []
        self.max_recent_searches = config.get('search_manager', {}).get('max_recent_searches', 50)
        
        # Search history per user
        self.user_search_history = {}
        
        logger.info("Search manager initialized")
    
    async def process_query(self, query: str, params: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a search query.
        
        Args:
            query: Search query
            params: Search parameters
            user_id: User ID for personalization
            
        Returns:
            Search results
        """
        # Merge parameters with defaults
        merged_params = self.default_params.copy()
        if params:
            merged_params.update(params)
            
        # Clean and normalize the query
        clean_query = self._clean_query(query)
        
        # Record the search
        self._record_search(clean_query, user_id)
        
        # Determine the type of query and route it to the appropriate agent
        query_type = self._determine_query_type(clean_query)
        
        try:
            if query_type == "knowledge_graph":
                # This type of query is looking for knowledge graph data
                return await self._process_knowledge_query(clean_query, merged_params, user_id)
                
            elif query_type == "concept":
                # This type of query is looking for concept information
                return await self._process_concept_query(clean_query, merged_params, user_id)
                
            elif query_type == "entity":
                # This type of query is looking for entity information
                return await self._process_entity_query(clean_query, merged_params, user_id)
                
            elif query_type == "factual":
                # This type of query is looking for factual information
                return await self._process_factual_query(clean_query, merged_params, user_id)
                
            else:
                # Default to a general query
                return await self._process_general_query(clean_query, merged_params, user_id)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "query": clean_query,
                "error": str(e),
                "results": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize a query.
        
        Args:
            query: Raw query string
            
        Returns:
            Cleaned query string
        """
        # Trim whitespace
        clean = query.strip()
        
        # Remove excessive whitespace
        clean = re.sub(r'\s+', ' ', clean)
        
        # Remove special characters that might interfere with processing
        clean = re.sub(r'[^\w\s?.,!]', '', clean)
        
        return clean
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query.
        
        Args:
            query: Query string
            
        Returns:
            Query type (knowledge_graph, concept, entity, factual, general)
        """
        # This is a simple heuristic-based approach
        # In a real system, this would be more sophisticated, possibly using NLP
        
        # Check for knowledge graph related queries
        if re.search(r'\b(knowledge\s*graph|graph|network|relationship|connect|link)\b', query, re.IGNORECASE):
            return "knowledge_graph"
            
        # Check for concept related queries
        if re.search(r'\b(concept|idea|theory|framework|approach)\b', query, re.IGNORECASE):
            return "concept"
            
        # Check for entity related queries
        if re.search(r'\b(person|organization|company|place|product|who|where|which)\b', query, re.IGNORECASE):
            return "entity"
            
        # Check for factual queries
        if re.search(r'\b(what|when|how|why|define|explain)\b', query, re.IGNORECASE):
            return "factual"
            
        # Default to general
        return "general"
    
    def _record_search(self, query: str, user_id: Optional[str] = None) -> None:
        """Record a search query.
        
        Args:
            query: Search query
            user_id: User ID
        """
        # Record in recent searches
        search_record = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        self.recent_searches.append(search_record)
        
        # Trim if needed
        if len(self.recent_searches) > self.max_recent_searches:
            self.recent_searches = self.recent_searches[-self.max_recent_searches:]
            
        # Record in user history if available
        if user_id:
            if user_id not in self.user_search_history:
                self.user_search_history[user_id] = []
                
            self.user_search_history[user_id].append(search_record)
            
            # Trim if needed
            if len(self.user_search_history[user_id]) > self.max_recent_searches:
                self.user_search_history[user_id] = self.user_search_history[user_id][-self.max_recent_searches:]
    
    async def _process_knowledge_query(self, query: str, params: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a knowledge graph query.
        
        Args:
            query: Query string
            params: Query parameters
            user_id: User ID
            
        Returns:
            Search results
        """
        # Send the query to the knowledge agent
        if self.message_broker:
            task_id = await self.message_broker.publish_task(
                "knowledge",
                "query_graph",
                {
                    "query": query,
                    "params": params,
                    "user_id": user_id
                }
            )
            
            # Wait for the result
            result = await self.message_broker.wait_for_task_result(task_id, timeout=10.0)
            
            return {
                "query": query,
                "type": "knowledge_graph",
                "results": result.get("results", []),
                "metadata": result.get("metadata", {}),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # If no message broker, return an error
            return {
                "query": query,
                "type": "knowledge_graph",
                "error": "No message broker available",
                "results": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_concept_query(self, query: str, params: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a concept query.
        
        Args:
            query: Query string
            params: Query parameters
            user_id: User ID
            
        Returns:
            Search results
        """
        # Send the query to the processor agent
        if self.message_broker:
            task_id = await self.message_broker.publish_task(
                "processor",
                "extract_concepts",
                {
                    "query": query,
                    "params": params,
                    "user_id": user_id
                }
            )
            
            # Wait for the result
            result = await self.message_broker.wait_for_task_result(task_id, timeout=10.0)
            
            return {
                "query": query,
                "type": "concept",
                "results": result.get("results", []),
                "metadata": result.get("metadata", {}),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # If no message broker, return an error
            return {
                "query": query,
                "type": "concept",
                "error": "No message broker available",
                "results": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_entity_query(self, query: str, params: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process an entity query.
        
        Args:
            query: Query string
            params: Query parameters
            user_id: User ID
            
        Returns:
            Search results
        """
        # Send the query to the processor agent
        if self.message_broker:
            task_id = await self.message_broker.publish_task(
                "processor",
                "recognize_entities",
                {
                    "query": query,
                    "params": params,
                    "user_id": user_id
                }
            )
            
            # Wait for the result
            result = await self.message_broker.wait_for_task_result(task_id, timeout=10.0)
            
            return {
                "query": query,
                "type": "entity",
                "results": result.get("results", []),
                "metadata": result.get("metadata", {}),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # If no message broker, return an error
            return {
                "query": query,
                "type": "entity",
                "error": "No message broker available",
                "results": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_factual_query(self, query: str, params: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a factual query.
        
        Args:
            query: Query string
            params: Query parameters
            user_id: User ID
            
        Returns:
            Search results
        """
        # Send the query to both knowledge and processor agents
        if self.message_broker:
            # Create tasks for both agents
            knowledge_task_id = await self.message_broker.publish_task(
                "knowledge",
                "query_facts",
                {
                    "query": query,
                    "params": params,
                    "user_id": user_id
                }
            )
            
            processor_task_id = await self.message_broker.publish_task(
                "processor",
                "process_query",
                {
                    "query": query,
                    "params": params,
                    "user_id": user_id
                }
            )
            
            # Wait for both results
            knowledge_result = await self.message_broker.wait_for_task_result(knowledge_task_id, timeout=10.0)
            processor_result = await self.message_broker.wait_for_task_result(processor_task_id, timeout=10.0)
            
            # Merge the results
            all_results = knowledge_result.get("results", []) + processor_result.get("results", [])
            
            # Sort by confidence/relevance
            all_results.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
            
            # Limit to the requested number of results
            max_results = params.get("max_results", self.default_params["max_results"])
            all_results = all_results[:max_results]
            
            return {
                "query": query,
                "type": "factual",
                "results": all_results,
                "metadata": {
                    "knowledge_metadata": knowledge_result.get("metadata", {}),
                    "processor_metadata": processor_result.get("metadata", {})
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            # If no message broker, return an error
            return {
                "query": query,
                "type": "factual",
                "error": "No message broker available",
                "results": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_general_query(self, query: str, params: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a general query.
        
        Args:
            query: Query string
            params: Query parameters
            user_id: User ID
            
        Returns:
            Search results
        """
        # Send the query to the processor agent
        if self.message_broker:
            task_id = await self.message_broker.publish_task(
                "processor",
                "process_query",
                {
                    "query": query,
                    "params": params,
                    "user_id": user_id
                }
            )
            
            # Wait for the result
            result = await self.message_broker.wait_for_task_result(task_id, timeout=10.0)
            
            return {
                "query": query,
                "type": "general",
                "results": result.get("results", []),
                "metadata": result.get("metadata", {}),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # If no message broker, return a stub response for testing
            return {
                "query": query,
                "type": "general",
                "results": [
                    {
                        "title": "Sample result 1",
                        "snippet": "This is a sample result for the query: " + query,
                        "confidence": 0.95,
                        "type": "text"
                    },
                    {
                        "title": "Sample result 2",
                        "snippet": "Another sample result for demonstration purposes.",
                        "confidence": 0.85,
                        "type": "text"
                    }
                ],
                "metadata": {
                    "total_results": 2,
                    "processing_time_ms": 50
                },
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_recent_searches(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent searches.
        
        Args:
            user_id: Optional user ID to get user-specific searches
            limit: Maximum number of searches to return
            
        Returns:
            List of recent searches
        """
        if user_id and user_id in self.user_search_history:
            # Get user-specific searches
            searches = self.user_search_history[user_id]
        else:
            # Get global searches
            searches = self.recent_searches
            
        # Sort by timestamp (newest first) and limit
        sorted_searches = sorted(searches, key=lambda x: x["timestamp"], reverse=True)
        return sorted_searches[:limit]
    
    async def get_trending_searches(self, timeframe: str = "day", limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending searches.
        
        Args:
            timeframe: Timeframe for trending searches (hour, day, week, month)
            limit: Maximum number of searches to return
            
        Returns:
            List of trending searches with counts
        """
        # In a real system, this would be implemented using a database and analytics
        # For now, we'll return a stub response
        
        return [
            {"query": "knowledge graphs in AI", "count": 42},
            {"query": "quantum computing basics", "count": 37},
            {"query": "neural networks vs deep learning", "count": 29},
            {"query": "climate change evidence", "count": 24},
            {"query": "blockchain technology", "count": 18},
        ] 