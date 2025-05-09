#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis adapter for the Intelligent Knowledge Aggregation Platform.
Handles caching, pub/sub, and real-time data operations.
"""

import os
import sys
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta

import redis

# Configure logging
logger = logging.getLogger(__name__)


class RedisAdapter:
    """Redis adapter for caching and real-time operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Redis adapter.
        
        Args:
            config: Configuration dictionary containing Redis connection parameters
        """
        self.config = config
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 6379)
        self.db = config.get('db', 0)
        self.password = config.get('password')
        
        self.client = None
        self.pubsub = None
        self._connect()
        
        # Default expiration time for cached items (in seconds)
        self.default_expiry = config.get('default_expiry', 3600)  # 1 hour
        
        logger.info(f"Redis adapter initialized with {self.host}:{self.port}")
    
    def _connect(self) -> None:
        """Establish a connection to Redis."""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True  # Automatically decode responses to strings
            )
            
            # Test the connection
            if not self.client.ping():
                raise Exception("Connection test failed")
                
            # Initialize pubsub client
            self.pubsub = self.client.pubsub(ignore_subscribe_messages=True)
            
            logger.info("Successfully connected to Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
            self.pubsub = None
            raise
    
    def close(self) -> None:
        """Close the Redis connection."""
        if self.pubsub is not None:
            self.pubsub.close()
            self.pubsub = None
            
        if self.client is not None:
            self.client.close()
            self.client = None
            
        logger.info("Redis connection closed")
    
    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """Set a value in Redis.
        
        Args:
            key: Redis key
            value: Value to store
            expiry: Expiration time in seconds (None to use default)
            
        Returns:
            True if successful
        """
        try:
            # If value is not a string, serialize it to JSON
            if not isinstance(value, (str, int, float, bool)):
                value = json.dumps(value)
                
            # Use default expiry if not specified
            if expiry is None:
                expiry = self.default_expiry
                
            # Set the value with expiry
            result = self.client.setex(key, expiry, value)
            
            logger.debug(f"Set value for key {key} with expiry {expiry}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to set value in Redis: {e}")
            raise
    
    def get(self, key: str, deserialize: bool = True) -> Any:
        """Get a value from Redis.
        
        Args:
            key: Redis key
            deserialize: Whether to attempt JSON deserialization
            
        Returns:
            Stored value or None if not found
        """
        try:
            value = self.client.get(key)
            
            if value is None:
                return None
                
            # Attempt to deserialize from JSON if requested
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If deserialization fails, return the raw value
                    return value
            else:
                return value
                
        except Exception as e:
            logger.error(f"Failed to get value from Redis: {e}")
            raise
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            True if key was deleted
        """
        try:
            deleted = self.client.delete(key)
            return deleted > 0
            
        except Exception as e:
            logger.error(f"Failed to delete key from Redis: {e}")
            raise
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis.
        
        Args:
            key: Redis key
            
        Returns:
            True if key exists
        """
        try:
            return self.client.exists(key) > 0
            
        except Exception as e:
            logger.error(f"Failed to check key existence in Redis: {e}")
            raise
    
    def ttl(self, key: str) -> int:
        """Get the time-to-live for a key.
        
        Args:
            key: Redis key
            
        Returns:
            Time-to-live in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        try:
            return self.client.ttl(key)
            
        except Exception as e:
            logger.error(f"Failed to get TTL for key in Redis: {e}")
            raise
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key.
        
        Args:
            key: Redis key
            seconds: Expiration time in seconds
            
        Returns:
            True if successful
        """
        try:
            return self.client.expire(key, seconds)
            
        except Exception as e:
            logger.error(f"Failed to set expiry for key in Redis: {e}")
            raise
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a key's value.
        
        Args:
            key: Redis key
            amount: Increment amount
            
        Returns:
            New value
        """
        try:
            return self.client.incrby(key, amount)
            
        except Exception as e:
            logger.error(f"Failed to increment key in Redis: {e}")
            raise
    
    def publish(self, channel: str, message: Any) -> int:
        """Publish a message to a channel.
        
        Args:
            channel: Channel name
            message: Message to publish (will be JSON-serialized if not a string)
            
        Returns:
            Number of clients that received the message
        """
        try:
            # Serialize message if it's not a string
            if not isinstance(message, str):
                message = json.dumps(message)
                
            return self.client.publish(channel, message)
            
        except Exception as e:
            logger.error(f"Failed to publish message to Redis: {e}")
            raise
    
    def subscribe(self, channels: List[str]) -> None:
        """Subscribe to channels.
        
        Args:
            channels: List of channel names
        """
        try:
            self.pubsub.subscribe(*channels)
            logger.debug(f"Subscribed to channels: {', '.join(channels)}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to Redis channels: {e}")
            raise
    
    def listen_for_messages(self, handler: Callable[[str, str], None], timeout: float = 0.01) -> None:
        """Listen for messages on subscribed channels.
        
        Args:
            handler: Callback function that takes (channel, message)
            timeout: Time to wait for a message in seconds
        """
        try:
            message = self.pubsub.get_message(timeout=timeout)
            
            if message and message['type'] == 'message':
                channel = message['channel']
                data = message['data']
                
                # Try to deserialize JSON
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    pass
                    
                # Call the handler
                handler(channel, data)
                
        except Exception as e:
            logger.error(f"Error in Redis message listener: {e}")
            
    def add_to_set(self, key: str, *values: Any) -> int:
        """Add values to a set.
        
        Args:
            key: Set key
            *values: Values to add
            
        Returns:
            Number of values added
        """
        try:
            return self.client.sadd(key, *values)
            
        except Exception as e:
            logger.error(f"Failed to add to set in Redis: {e}")
            raise
    
    def remove_from_set(self, key: str, *values: Any) -> int:
        """Remove values from a set.
        
        Args:
            key: Set key
            *values: Values to remove
            
        Returns:
            Number of values removed
        """
        try:
            return self.client.srem(key, *values)
            
        except Exception as e:
            logger.error(f"Failed to remove from set in Redis: {e}")
            raise
    
    def get_set_members(self, key: str) -> List[str]:
        """Get all members of a set.
        
        Args:
            key: Set key
            
        Returns:
            List of set members
        """
        try:
            return list(self.client.smembers(key))
            
        except Exception as e:
            logger.error(f"Failed to get set members from Redis: {e}")
            raise
    
    def add_to_sorted_set(self, key: str, score: float, value: str) -> int:
        """Add a value to a sorted set.
        
        Args:
            key: Sorted set key
            score: Score for sorting
            value: Value to add
            
        Returns:
            1 if added, 0 if updated
        """
        try:
            return self.client.zadd(key, {value: score})
            
        except Exception as e:
            logger.error(f"Failed to add to sorted set in Redis: {e}")
            raise
    
    def get_sorted_set_range(self, key: str, start: int = 0, end: int = -1, 
                          withscores: bool = False, desc: bool = False) -> List[Any]:
        """Get a range of values from a sorted set.
        
        Args:
            key: Sorted set key
            start: Start index
            end: End index (-1 for all)
            withscores: Whether to include scores
            desc: Whether to sort in descending order
            
        Returns:
            List of values or (value, score) tuples
        """
        try:
            if desc:
                return self.client.zrevrange(key, start, end, withscores=withscores)
            else:
                return self.client.zrange(key, start, end, withscores=withscores)
                
        except Exception as e:
            logger.error(f"Failed to get sorted set range from Redis: {e}")
            raise
    
    def get_hash(self, key: str) -> Dict[str, str]:
        """Get all fields and values from a hash.
        
        Args:
            key: Hash key
            
        Returns:
            Dictionary of field-value pairs
        """
        try:
            return self.client.hgetall(key)
            
        except Exception as e:
            logger.error(f"Failed to get hash from Redis: {e}")
            raise
    
    def set_hash_field(self, key: str, field: str, value: Any) -> int:
        """Set a field in a hash.
        
        Args:
            key: Hash key
            field: Field name
            value: Field value
            
        Returns:
            1 if field is new, 0 if field was updated
        """
        try:
            # Serialize non-string values
            if not isinstance(value, (str, int, float, bool)):
                value = json.dumps(value)
                
            return self.client.hset(key, field, value)
            
        except Exception as e:
            logger.error(f"Failed to set hash field in Redis: {e}")
            raise
    
    def get_hash_field(self, key: str, field: str, deserialize: bool = True) -> Any:
        """Get a field from a hash.
        
        Args:
            key: Hash key
            field: Field name
            deserialize: Whether to attempt JSON deserialization
            
        Returns:
            Field value or None if not found
        """
        try:
            value = self.client.hget(key, field)
            
            if value is None:
                return None
                
            # Attempt to deserialize from JSON if requested
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If deserialization fails, return the raw value
                    return value
            else:
                return value
                
        except Exception as e:
            logger.error(f"Failed to get hash field from Redis: {e}")
            raise 