#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration tests for database adapters.
Tests that the Neo4j, MongoDB, and Redis adapters work correctly together.
"""

import os
import sys
import unittest
import json
import time
from typing import Dict, Any
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_storage.neo4j_adapter import Neo4jAdapter
from data_storage.mongodb_adapter import MongoDBAdapter
from data_storage.redis_adapter import RedisAdapter
from data_storage.database_factory import DatabaseFactory, get_database_factory

# Test config - modify for your local environment if needed
TEST_CONFIG = {
    'neo4j': {
        'uri': 'bolt://localhost:7687',
        'username': 'neo4j',
        'password': 'password',
        'database': 'neo4j'
    },
    'mongodb': {
        'uri': 'mongodb://localhost:27017/',
        'database': 'knowledge_platform_test'
    },
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'default_expiry': 60  # Use a shorter expiry for tests
    }
}


class TestDatabaseIntegration(unittest.TestCase):
    """Test the integration between database adapters."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        # Create a database factory with test configuration
        cls.db_factory = DatabaseFactory(TEST_CONFIG)
        
        # Create necessary adapters
        try:
            cls.neo4j = cls.db_factory.get_neo4j_adapter()
            cls.mongodb = cls.db_factory.get_mongodb_adapter()
            cls.redis = cls.db_factory.get_redis_adapter()
            
            # Flag to track if we're running in a CI environment without actual databases
            cls.skip_db_tests = False
            
        except Exception as e:
            print(f"Warning: Could not connect to test databases: {e}")
            cls.skip_db_tests = True
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        if not cls.skip_db_tests:
            cls.db_factory.close_all_connections()
    
    def setUp(self):
        """Set up before each test."""
        if self.skip_db_tests:
            self.skipTest("Skipping test because database connections are not available")
    
    def test_entity_creation_and_retrieval(self):
        """Test creating an entity and retrieving it."""
        # Create an entity in Neo4j
        entity_data = {
            'name': 'Test Entity',
            'description': 'An entity for testing',
            'created_at': datetime.now().isoformat()
        }
        
        entity_id = self.neo4j.create_entity('TestEntity', entity_data)
        self.assertIsNotNone(entity_id, "Entity ID should not be None")
        
        # Store a reference in Redis
        self.redis.set(f"entity:{entity_id}", {
            'id': entity_id,
            'type': 'TestEntity'
        })
        
        # Check that the entity can be retrieved from Neo4j
        entity = self.neo4j.get_entity(entity_id)
        self.assertIsNotNone(entity, "Entity should be retrievable from Neo4j")
        self.assertEqual(entity['name'], 'Test Entity', "Entity name should match")
        
        # Check that the reference can be retrieved from Redis
        cached_ref = self.redis.get(f"entity:{entity_id}")
        self.assertIsNotNone(cached_ref, "Entity reference should be retrievable from Redis")
        self.assertEqual(cached_ref['id'], entity_id, "Entity ID in Redis should match")
    
    def test_document_storage_and_entity_linking(self):
        """Test storing a document and linking it to an entity."""
        # Store a document in MongoDB
        document_data = {
            'title': 'Test Document',
            'content': 'This is a test document about knowledge graphs.',
            'metadata': {
                'source': 'integration_test',
                'author': 'test_user'
            }
        }
        
        doc_id = self.mongodb.create_document('documents', document_data)
        self.assertIsNotNone(doc_id, "Document ID should not be None")
        
        # Create an entity in Neo4j
        entity_data = {
            'name': 'Knowledge Graph',
            'description': 'A graph-based representation of knowledge',
            'created_at': datetime.now().isoformat()
        }
        
        entity_id = self.neo4j.create_entity('Concept', entity_data)
        self.assertIsNotNone(entity_id, "Entity ID should not be None")
        
        # Create a relationship from entity to document
        rel_props = {
            'source_type': 'document',
            'source_id': doc_id
        }
        
        rel_id = self.neo4j.create_relationship(
            entity_id,
            f"doc_{doc_id}", # Create a node ID for the document
            'MENTIONED_IN',
            rel_props
        )
        
        self.assertIsNotNone(rel_id, "Relationship ID should not be None")
        
        # Store a cache of the document in Redis
        self.redis.set(f"document:{doc_id}", {
            'id': doc_id,
            'title': document_data['title'],
            'related_concepts': [entity_id]
        })
        
        # Retrieve the document from MongoDB
        retrieved_doc = self.mongodb.get_document('documents', doc_id)
        self.assertIsNotNone(retrieved_doc, "Document should be retrievable from MongoDB")
        self.assertEqual(retrieved_doc['title'], 'Test Document', "Document title should match")
        
        # Check the cache in Redis
        cached_doc = self.redis.get(f"document:{doc_id}")
        self.assertIsNotNone(cached_doc, "Document reference should be retrievable from Redis")
        self.assertIn(entity_id, cached_doc['related_concepts'], "Related concepts should include the entity ID")
    
    def test_graph_neighborhood(self):
        """Test querying the neighborhood of an entity in the knowledge graph."""
        # Create a central entity
        center_entity_data = {
            'name': 'Artificial Intelligence',
            'description': 'A branch of computer science',
            'created_at': datetime.now().isoformat()
        }
        
        center_id = self.neo4j.create_entity('Concept', center_entity_data)
        
        # Create related entities
        related_entities = []
        for i in range(3):
            entity_data = {
                'name': f'Related Concept {i}',
                'description': f'A concept related to AI - {i}',
                'created_at': datetime.now().isoformat()
            }
            
            entity_id = self.neo4j.create_entity('Concept', entity_data)
            related_entities.append(entity_id)
            
            # Create relationship from center to this entity
            rel_id = self.neo4j.create_relationship(
                center_id,
                entity_id,
                'INCLUDES',
                {'weight': 0.5 + i*0.1}
            )
        
        # Get the neighborhood graph
        neighborhood = self.neo4j.get_neighborhood(center_id, depth=1)
        
        # Cache in Redis
        self.redis.set(f"neighborhood:{center_id}", neighborhood, expiry=120)
        
        # Verify the neighborhood contents
        self.assertEqual(neighborhood['center'], center_id, "Neighborhood center should match")
        self.assertGreaterEqual(len(neighborhood['nodes']), 4, "Should have at least 4 nodes (center + 3 related)")
        self.assertGreaterEqual(len(neighborhood['edges']), 3, "Should have at least 3 edges")
        
        # Check Redis cache
        cached_neighborhood = self.redis.get(f"neighborhood:{center_id}")
        self.assertIsNotNone(cached_neighborhood, "Neighborhood should be cached in Redis")
        self.assertEqual(cached_neighborhood['center'], center_id, "Cached neighborhood center should match")
    
    def test_database_factory_singleton(self):
        """Test that the database factory singleton works correctly."""
        # Get the singleton instance with the test config
        factory1 = get_database_factory(TEST_CONFIG)
        
        # Get it again - should be the same instance
        factory2 = get_database_factory()
        
        self.assertIs(factory1, factory2, "Factory instances should be the same singleton")
        
        # Check that we can get adapters from both instances
        neo4j1 = factory1.get_neo4j_adapter()
        neo4j2 = factory2.get_neo4j_adapter()
        
        self.assertIs(neo4j1, neo4j2, "Adapters from different factory references should be the same instance")


if __name__ == '__main__':
    unittest.main() 