#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Processor agent for the Intelligent Knowledge Aggregation Platform.
Responsible for processing and analyzing content from various sources.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import configuration and utilities
from coordinator.config import load_config
from coordinator.utils import setup_logging
from coordinator.message_broker import MessageBroker

# Import specific processor modules
from agents.processor.text_processor import TextProcessor
from agents.processor.concept_extractor import ConceptExtractor
from agents.processor.entity_recognizer import EntityRecognizer
from agents.processor.sentiment_analyzer import SentimentAnalyzer
from agents.processor.document_processor import DocumentProcessor

# Configure logging
logger = logging.getLogger(__name__)


class ProcessorAgent:
    """Processor agent for analyzing and extracting meaning from content."""
    
    def __init__(self, agent_id: str, config_path: Optional[str] = None):
        """Initialize the processor agent.
        
        Args:
            agent_id: Unique identifier for this agent
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        setup_logging(self.config.get('logging', {}))
        
        self.agent_id = agent_id
        self.agent_type = "processor"
        
        # Initialize message broker
        self.message_broker = MessageBroker(self.config.get('rabbitmq', {}))
        
        # Initialize processors
        self.text_processor = TextProcessor(self.config)
        self.concept_extractor = ConceptExtractor(self.config)
        self.entity_recognizer = EntityRecognizer(self.config)
        self.sentiment_analyzer = SentimentAnalyzer(self.config)
        self.document_processor = DocumentProcessor(self.config)
        
        # Track current task
        self.current_task_id = None
        self.is_running = False
        
        logger.info(f"Processor agent {agent_id} initialized")
    
    async def start(self) -> None:
        """Start the processor agent."""
        if self.is_running:
            logger.warning(f"Processor agent {self.agent_id} is already running")
            return
            
        logger.info(f"Starting processor agent {self.agent_id}")
        
        # Connect to message broker
        await self.message_broker.connect()
        
        # Subscribe to tasks
        await self.message_broker.subscribe(
            self.agent_type,
            self._process_task
        )
        
        # Subscribe to system events
        await self.message_broker.subscribe_to_events(
            ["agent.stopping"],
            self._handle_system_event
        )
        
        # Start heartbeat
        asyncio.create_task(self._send_heartbeat())
        
        self.is_running = True
        logger.info(f"Processor agent {self.agent_id} started")
    
    async def stop(self) -> None:
        """Stop the processor agent."""
        if not self.is_running:
            return
            
        logger.info(f"Stopping processor agent {self.agent_id}")
        
        # Close message broker connection
        await self.message_broker.close()
        
        self.is_running = False
        logger.info(f"Processor agent {self.agent_id} stopped")
    
    async def _send_heartbeat(self) -> None:
        """Send periodic heartbeats to the coordinator."""
        while self.is_running:
            try:
                await self.message_broker.publish_event(
                    "agent.heartbeat",
                    {
                        "agent_id": self.agent_id,
                        "agent_type": self.agent_type,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                await asyncio.sleep(10)  # Send heartbeat every 10 seconds
                
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(5)  # Retry after a shorter delay
    
    async def _process_task(self, task: Dict[str, Any]) -> None:
        """Process a task received from the message broker.
        
        Args:
            task: Task data
        """
        task_id = task.get("task_id")
        agent_id = task.get("agent_id")
        task_type = task.get("task_type")
        task_data = task.get("task_data", {})
        
        # Verify the task is for this agent
        if agent_id != self.agent_id:
            logger.warning(f"Received task for another agent: {agent_id}")
            return
            
        logger.info(f"Processing task {task_id} of type {task_type}")
        
        self.current_task_id = task_id
        
        try:
            # Determine which processor to use based on task type
            result = None
            
            if task_type == "process_text":
                result = await self.text_processor.process(task_data)
            elif task_type == "extract_concepts":
                result = await self.concept_extractor.extract(task_data)
            elif task_type == "recognize_entities":
                result = await self.entity_recognizer.recognize(task_data)
            elif task_type == "analyze_sentiment":
                result = await self.sentiment_analyzer.analyze(task_data)
            elif task_type == "process_document":
                result = await self.document_processor.process(task_data)
            elif task_type == "process_word":
                result = await self.document_processor.process(task_data)
            elif task_type == "process_excel":
                result = await self.document_processor.process(task_data)
            else:
                logger.warning(f"Unknown task type: {task_type}")
                
                # Publish task failure
                await self.message_broker.publish_event(
                    "task.failed",
                    {
                        "task_id": task_id,
                        "agent_id": self.agent_id,
                        "error": f"Unsupported task type: {task_type}",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                return
                
            # Publish task completion
            await self.message_broker.publish_event(
                "task.completed",
                {
                    "task_id": task_id,
                    "agent_id": self.agent_id,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Completed task {task_id}")
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            
            # Publish task failure
            await self.message_broker.publish_event(
                "task.failed",
                {
                    "task_id": task_id,
                    "agent_id": self.agent_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        finally:
            self.current_task_id = None
    
    async def _handle_system_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle system events.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if event_type == "agent.stopping":
            agent_id = event_data.get("agent_id")
            
            # Check if this event is for this agent
            if agent_id == self.agent_id:
                logger.info(f"Received stop signal for agent {self.agent_id}")
                await self.stop()


async def main():
    """Main entry point for running the processor agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a processor agent")
    parser.add_argument("--agent-id", type=str, help="Agent ID")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    
    args = parser.parse_args()
    
    agent_id = args.agent_id or f"processor-{os.getpid()}"
    
    agent = ProcessorAgent(agent_id, args.config)
    
    try:
        await agent.start()
        
        # Keep running until interrupted
        while agent.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main()) 