#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database factory for the Intelligent Knowledge Aggregation Platform.
Provides a centralized interface for accessing different database adapters.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

from .neo4j_adapter import Neo4jAdapter
from .mongodb_adapter import MongoDBAdapter
from .redis_adapter import RedisAdapter

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseFactory:
    """Factory for creating and managing database adapters."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the database factory.
        
        Args:
            config: Configuration dictionary for all databases
        """
        self.config = config
        self.adapters = {}
        
        logger.info("Database factory initialized")
    
    def get_neo4j_adapter(self) -> Neo4jAdapter:
        """Get a Neo4j adapter instance.
        
        Returns:
            Neo4j adapter
        """
        if 'neo4j' not in self.adapters:
            neo4j_config = self.config.get('neo4j', {})
            self.adapters['neo4j'] = Neo4jAdapter(neo4j_config)
            
        return self.adapters['neo4j']
    
    def get_mongodb_adapter(self) -> MongoDBAdapter:
        """Get a MongoDB adapter instance.
        
        Returns:
            MongoDB adapter
        """
        if 'mongodb' not in self.adapters:
            mongodb_config = self.config.get('mongodb', {})
            self.adapters['mongodb'] = MongoDBAdapter(mongodb_config)
            
        return self.adapters['mongodb']
    
    def get_redis_adapter(self) -> RedisAdapter:
        """Get a Redis adapter instance.
        
        Returns:
            Redis adapter
        """
        if 'redis' not in self.adapters:
            redis_config = self.config.get('redis', {})
            self.adapters['redis'] = RedisAdapter(redis_config)
            
        return self.adapters['redis']
    
    def close_all_connections(self) -> None:
        """Close all database connections."""
        for adapter_name, adapter in self.adapters.items():
            try:
                adapter.close()
                logger.info(f"Closed connection to {adapter_name}")
            except Exception as e:
                logger.error(f"Error closing connection to {adapter_name}: {e}")
                
        self.adapters = {}


# Singleton instance for easy global access
_factory_instance = None

def get_database_factory(config: Optional[Dict[str, Any]] = None) -> DatabaseFactory:
    """Get or create the singleton database factory instance.
    
    Args:
        config: Configuration dictionary (only used when creating a new instance)
        
    Returns:
        DatabaseFactory instance
    """
    global _factory_instance
    
    if _factory_instance is None:
        if config is None:
            raise ValueError("Configuration must be provided when creating the database factory")
            
        _factory_instance = DatabaseFactory(config)
        
    return _factory_instance 