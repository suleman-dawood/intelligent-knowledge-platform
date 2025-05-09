#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper agent for the Intelligent Knowledge Aggregation Platform.
Responsible for extracting content from websites, PDFs, and other sources.
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

# Import specific scraper modules
from agents.scraper.web_scraper import WebScraper
from agents.scraper.pdf_scraper import PDFScraper
from agents.scraper.academic_scraper import AcademicScraper

# Configure logging
logger = logging.getLogger(__name__)


class ScraperAgent:
    """Scraper agent for extracting content from various sources."""
    
    def __init__(self, agent_id: str, config_path: Optional[str] = None):
        """Initialize the scraper agent.
        
        Args:
            agent_id: Unique identifier for this agent
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        setup_logging(self.config.get('logging', {}))
        
        self.agent_id = agent_id
        self.agent_type = "scraper"
        
        # Initialize message broker
        self.message_broker = MessageBroker(self.config.get('rabbitmq', {}))
        
        # Initialize scrapers
        self.web_scraper = WebScraper(self.config)
        self.pdf_scraper = PDFScraper(self.config)
        self.academic_scraper = AcademicScraper(self.config)
        
        # Track current task
        self.current_task_id = None
        self.is_running = False
        
        logger.info(f"Scraper agent {agent_id} initialized")
    
    async def start(self) -> None:
        """Start the scraper agent."""
        if self.is_running:
            logger.warning(f"Scraper agent {self.agent_id} is already running")
            return
            
        logger.info(f"Starting scraper agent {self.agent_id}")
        
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
        logger.info(f"Scraper agent {self.agent_id} started")
    
    async def stop(self) -> None:
        """Stop the scraper agent."""
        if not self.is_running:
            return
            
        logger.info(f"Stopping scraper agent {self.agent_id}")
        
        # Close message broker connection
        await self.message_broker.close()
        
        self.is_running = False
        logger.info(f"Scraper agent {self.agent_id} stopped")
    
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
            # Determine which scraper to use based on task type
            result = None
            
            if task_type == "scrape_web":
                result = await self.web_scraper.scrape(task_data)
            elif task_type == "scrape_pdf":
                result = await self.pdf_scraper.scrape(task_data)
            elif task_type == "scrape_academic":
                result = await self.academic_scraper.scrape(task_data)
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
    """Main entry point for running the scraper agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a scraper agent")
    parser.add_argument("--agent-id", type=str, help="Agent ID")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    
    args = parser.parse_args()
    
    agent_id = args.agent_id or f"scraper-{os.getpid()}"
    
    agent = ScraperAgent(agent_id, args.config)
    
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