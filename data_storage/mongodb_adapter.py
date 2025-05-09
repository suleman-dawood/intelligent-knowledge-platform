#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MongoDB adapter for the Intelligent Knowledge Aggregation Platform.
Handles storage of documents, raw content, and other unstructured data.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configure logging
logger = logging.getLogger(__name__)


class MongoDBAdapter:
    """MongoDB adapter for storing unstructured data."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the MongoDB adapter.
        
        Args:
            config: Configuration dictionary containing MongoDB connection parameters
        """
        self.config = config
        self.uri = config.get('uri', 'mongodb://localhost:27017/')
        self.database_name = config.get('database', 'knowledge_platform')
        
        self.client = None
        self.db = None
        self._connect()
        
        logger.info(f"MongoDB adapter initialized with URI: {self.uri}")
    
    def _connect(self) -> None:
        """Establish a connection to the MongoDB database."""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.database_name]
            
            # Test the connection
            result = self.client.admin.command('ping')
            if result.get('ok') != 1:
                raise Exception("Connection test failed")
                
            logger.info("Successfully connected to MongoDB database")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB database: {e}")
            self.client = None
            self.db = None
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed")
    
    def create_document(self, collection: str, document: Dict[str, Any]) -> str:
        """Create a new document in the specified collection.
        
        Args:
            collection: Collection name
            document: Document data
            
        Returns:
            Document ID
        """
        # Ensure document has a timestamp
        if 'created_at' not in document:
            document['created_at'] = datetime.now()
            
        if 'updated_at' not in document:
            document['updated_at'] = document['created_at']
            
        try:
            result = self.db[collection].insert_one(document)
            doc_id = str(result.inserted_id)
            
            logger.debug(f"Created document in {collection} with ID {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to create document in {collection}: {e}")
            raise
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(doc_id)
            
            document = self.db[collection].find_one({"_id": object_id})
            
            if document is None:
                logger.debug(f"Document with ID {doc_id} not found in {collection}")
                return None
                
            # Convert ObjectId to string for JSON serialization
            document['_id'] = str(document['_id'])
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to get document from {collection}: {e}")
            raise
    
    def update_document(self, collection: str, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a document.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            update_data: Fields to update
            
        Returns:
            True if successful
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(doc_id)
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.now()
            
            result = self.db[collection].update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                logger.warning(f"Document with ID {doc_id} not found in {collection} for update")
                return False
                
            logger.debug(f"Updated document {doc_id} in {collection}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document in {collection}: {e}")
            raise
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            
        Returns:
            True if successful
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(doc_id)
            
            result = self.db[collection].delete_one({"_id": object_id})
            
            if result.deleted_count == 0:
                logger.warning(f"Document with ID {doc_id} not found in {collection} for deletion")
                return False
                
            logger.debug(f"Deleted document {doc_id} from {collection}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from {collection}: {e}")
            raise
    
    def query_documents(self, collection: str, query: Dict[str, Any], 
                       sort_by: Optional[List[tuple]] = None, 
                       limit: int = 100,
                       skip: int = 0) -> List[Dict[str, Any]]:
        """Query documents from a collection.
        
        Args:
            collection: Collection name
            query: Query filter
            sort_by: List of (field, direction) tuples for sorting
            limit: Maximum number of results
            skip: Number of documents to skip
            
        Returns:
            List of matching documents
        """
        try:
            # Set up the cursor with the query
            cursor = self.db[collection].find(query)
            
            # Apply sorting if specified
            if sort_by:
                cursor = cursor.sort(sort_by)
                
            # Apply pagination
            cursor = cursor.skip(skip).limit(limit)
            
            # Convert the results to list and serialize ObjectIds
            documents = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                documents.append(doc)
                
            return documents
            
        except Exception as e:
            logger.error(f"Failed to query documents from {collection}: {e}")
            raise
    
    def count_documents(self, collection: str, query: Dict[str, Any] = None) -> int:
        """Count documents in a collection.
        
        Args:
            collection: Collection name
            query: Query filter (None for all documents)
            
        Returns:
            Document count
        """
        try:
            if query is None:
                query = {}
                
            count = self.db[collection].count_documents(query)
            return count
            
        except Exception as e:
            logger.error(f"Failed to count documents in {collection}: {e}")
            raise
    
    def store_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content with metadata.
        
        Args:
            content: Text content
            metadata: Content metadata
            
        Returns:
            Document ID
        """
        document = {
            "content": content,
            "metadata": metadata,
            "created_at": datetime.now()
        }
        
        return self.create_document("content", document)
    
    def store_scraped_data(self, url: str, content: str, metadata: Dict[str, Any]) -> str:
        """Store scraped data.
        
        Args:
            url: Source URL
            content: Scraped content
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        document = {
            "url": url,
            "content": content,
            "metadata": metadata,
            "scraped_at": datetime.now()
        }
        
        return self.create_document("scraped_data", document)
    
    def create_index(self, collection: str, fields: Dict[str, int], index_name: Optional[str] = None) -> str:
        """Create an index on a collection.
        
        Args:
            collection: Collection name
            fields: Dictionary mapping field names to index direction (1 for ascending, -1 for descending)
            index_name: Optional name for the index
            
        Returns:
            Index name
        """
        try:
            options = {}
            if index_name:
                options["name"] = index_name
                
            result = self.db[collection].create_index(
                [(field, direction) for field, direction in fields.items()],
                **options
            )
            
            logger.info(f"Created index {result} on collection {collection}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create index on {collection}: {e}")
            raise 