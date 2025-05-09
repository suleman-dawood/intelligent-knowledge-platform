#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration tests for agent communication.
Tests that the agents can communicate with each other via the message broker.
"""

import os
import sys
import unittest
import json
import time
import asyncio
from typing import Dict, Any
from datetime import datetime
import threading

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coordinator.message_broker import MessageBroker
from coordinator.config import load_config

# Test config
TEST_CONFIG = {
    'rabbitmq': {
        'host': 'localhost',
        'port': 5672,
        'username': 'guest',
        'password': 'guest',
        'virtual_host': '/',
        'exchange': 'test_exchange',
        'queue_prefix': 'test_queue_'
    }
}


class AsyncTestCase(unittest.TestCase):
    """Base class for tests that need to run async code."""
    
    def run_async(self, coro):
        """Run an async coroutine in the current event loop."""
        return asyncio.get_event_loop().run_until_complete(coro)


class TestAgentIntegration(AsyncTestCase):
    """Test the integration between agents via the message broker."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        try:
            # Create a message broker with test configuration
            cls.message_broker = MessageBroker(TEST_CONFIG['rabbitmq'])
            
            # Connect to RabbitMQ
            cls.run_async_class(cls.message_broker.connect())
            
            # Flag to indicate we're connected
            cls.skip_broker_tests = False
            
        except Exception as e:
            print(f"Warning: Could not connect to RabbitMQ: {e}")
            cls.skip_broker_tests = True
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        if not cls.skip_broker_tests:
            cls.run_async_class(cls.message_broker.close())
    
    @classmethod
    def run_async_class(cls, coro):
        """Run an async coroutine in a class method."""
        return asyncio.get_event_loop().run_until_complete(coro)
    
    def setUp(self):
        """Set up before each test."""
        if self.skip_broker_tests:
            self.skipTest("Skipping test because RabbitMQ connection is not available")
    
    async def _simulate_scraper_agent(self, url: str, task_id: str):
        """Simulate a scraper agent processing a task."""
        # Pretend to scrape content
        await asyncio.sleep(0.5)  # Simulate some processing time
        
        # Send a task completed event
        scraped_content = f"Scraped content from {url} at {datetime.now().isoformat()}"
        
        await self.message_broker.publish_task_result(
            task_id,
            {
                'status': 'completed',
                'content': scraped_content,
                'metadata': {
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'word_count': len(scraped_content.split())
                }
            }
        )
    
    async def _simulate_processor_agent(self, task_id: str, content: str):
        """Simulate a processor agent processing content."""
        # Pretend to process content
        await asyncio.sleep(0.7)  # Simulate some processing time
        
        # Extract fake entities
        entities = [
            {'type': 'person', 'name': 'John Doe', 'confidence': 0.92},
            {'type': 'organization', 'name': 'Example Corp', 'confidence': 0.87},
            {'type': 'concept', 'name': 'Artificial Intelligence', 'confidence': 0.95}
        ]
        
        # Send a task completed event
        await self.message_broker.publish_task_result(
            task_id,
            {
                'status': 'completed',
                'entities': entities,
                'summary': f"Processed content with {len(entities)} entities"
            }
        )
    
    async def _handle_events(self, event_type: str, event_data: Dict[str, Any]):
        """Handle events received from the message broker."""
        # Store the event for later assertion
        self.received_events.append((event_type, event_data))
    
    async def _handle_scraper_tasks(self, agent_type: str, task_type: str, task_data: Dict[str, Any], task_id: str):
        """Handle tasks for the scraper agent."""
        if agent_type == 'scraper' and task_type == 'scrape_url':
            url = task_data.get('url')
            if url:
                await self._simulate_scraper_agent(url, task_id)
                return True
        return False
    
    async def _handle_processor_tasks(self, agent_type: str, task_type: str, task_data: Dict[str, Any], task_id: str):
        """Handle tasks for the processor agent."""
        if agent_type == 'processor' and task_type == 'process_content':
            content = task_data.get('content')
            if content:
                await self._simulate_processor_agent(task_id, content)
                return True
        return False
    
    def test_task_delegation_and_completion(self):
        """Test that tasks can be delegated to agents and completed."""
        async def run_test():
            # List to store received events
            self.received_events = []
            
            # Subscribe to events
            await self.message_broker.subscribe_to_events(
                ["task.created", "task.completed", "entity.created"],
                self._handle_events
            )
            
            # Set up a handler for scraper agent tasks
            scraper_task_consumer = await self.message_broker.subscribe_to_tasks(
                "scraper",
                self._handle_scraper_tasks
            )
            
            # Set up a handler for processor agent tasks
            processor_task_consumer = await self.message_broker.subscribe_to_tasks(
                "processor",
                self._handle_processor_tasks
            )
            
            # Create a task for the scraper
            scraper_task_id = await self.message_broker.publish_task(
                "scraper",
                "scrape_url",
                {
                    "url": "https://example.com",
                    "depth": 1
                }
            )
            
            # Wait for the task to complete
            scraper_result = await self.message_broker.wait_for_task_result(scraper_task_id, timeout=2.0)
            
            # Verify the result
            self.assertEqual(scraper_result['status'], 'completed', "Scraper task should be completed")
            self.assertIn('content', scraper_result, "Scraper result should contain content")
            self.assertIn('url', scraper_result['metadata'], "Scraper metadata should contain the URL")
            
            # Use the scraped content to create a processor task
            processor_task_id = await self.message_broker.publish_task(
                "processor",
                "process_content",
                {
                    "content": scraper_result['content'],
                    "source_url": scraper_result['metadata']['url']
                }
            )
            
            # Wait for the processor task to complete
            processor_result = await self.message_broker.wait_for_task_result(processor_task_id, timeout=2.0)
            
            # Verify the result
            self.assertEqual(processor_result['status'], 'completed', "Processor task should be completed")
            self.assertIn('entities', processor_result, "Processor result should contain entities")
            
            # Verify that we received events
            self.assertGreaterEqual(len(self.received_events), 2, "Should have received at least 2 events")
            
            # Clean up
            await scraper_task_consumer.cancel()
            await processor_task_consumer.cancel()
        
        # Run the async test
        self.run_async(run_test())
    
    def test_pub_sub_communication(self):
        """Test that agents can communicate via pub/sub."""
        async def run_test():
            # List to store received messages
            received_messages = []
            
            # Set up a handler for messages
            async def handle_message(channel: str, message: Dict[str, Any]):
                received_messages.append((channel, message))
            
            # Subscribe to a channel
            channel = "test_channel"
            subscriber = await self.message_broker.subscribe_to_channel(channel, handle_message)
            
            # Publish some messages
            test_messages = [
                {"type": "info", "content": "Test message 1"},
                {"type": "warning", "content": "Test message 2"},
                {"type": "error", "content": "Test message 3"}
            ]
            
            for msg in test_messages:
                await self.message_broker.publish_to_channel(channel, msg)
                # Small sleep to ensure message processing
                await asyncio.sleep(0.1)
            
            # Wait a bit for messages to be processed
            await asyncio.sleep(0.5)
            
            # Verify that we received the messages
            self.assertEqual(len(received_messages), len(test_messages), 
                            f"Should have received {len(test_messages)} messages")
            
            # Verify message contents
            for i, (recv_channel, recv_message) in enumerate(received_messages):
                self.assertEqual(recv_channel, channel, f"Message {i} should be from the correct channel")
                self.assertEqual(recv_message['type'], test_messages[i]['type'], 
                                f"Message {i} should have the correct type")
                self.assertEqual(recv_message['content'], test_messages[i]['content'], 
                                f"Message {i} should have the correct content")
            
            # Clean up
            await subscriber.cancel()
        
        # Run the async test
        self.run_async(run_test())


if __name__ == '__main__':
    unittest.main() 