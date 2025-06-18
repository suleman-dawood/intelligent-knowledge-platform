#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Coordinator module for the Intelligent Knowledge Aggregation Platform.
This is the central component that orchestrates all the agents and manages
task distribution, agent lifecycle, and system communication.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration and utilities
from coordinator.config import load_config
from coordinator.utils import setup_logging
from coordinator.agent_manager import AgentManager
from coordinator.task_queue import TaskQueue
from coordinator.message_broker import MessageBroker
from coordinator.api import start_api_server

# Configure logging
logger = logging.getLogger(__name__)


class Coordinator:
    """Main coordinator class that orchestrates the entire system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the coordinator with configuration.
        
        Args:
            config_path: Path to the configuration file.
        """
        # Load configuration
        self.config = load_config(config_path)
        setup_logging(self.config.get('logging', {}))
        
        logger.info("Initializing coordinator...")
        
        # Initialize components
        self.task_queue = TaskQueue()
        self.message_broker = MessageBroker(self.config.get('rabbitmq', {}))
        self.agent_manager = AgentManager(self.config.get('agents', {}), self.message_broker)
        
        # Track system state
        self.is_running = False
        self.start_time = None
        
        logger.info("Coordinator initialized")
    
    async def start(self):
        """Start the coordinator and all its components."""
        if self.is_running:
            logger.warning("Coordinator is already running")
            return
        
        logger.info("Starting coordinator...")
        self.is_running = True
        self.start_time = datetime.now()
        
        # Start message broker
        await self.message_broker.connect()
        
        # Subscribe to task events to keep task queue in sync
        await self.message_broker.subscribe_to_events(
            ["task.completed", "task.failed"],
            self._handle_task_event
        )
        
        # Initialize and start agents
        await self.agent_manager.start_agents()
        
        # Start API server
        api_task = asyncio.create_task(
            start_api_server(
                self, 
                host=self.config.get('api', {}).get('host', 'localhost'),
                port=self.config.get('api', {}).get('port', 8000)
            )
        )
        
        logger.info(f"Coordinator started at {self.start_time}")
        
        # Keep running until shutdown is requested
        try:
            await self._main_loop()
        except asyncio.CancelledError:
            logger.info("Coordinator shutdown requested")
        finally:
            await self.shutdown()
            api_task.cancel()
    
    async def _main_loop(self):
        """Main coordinator loop that processes system events."""
        while self.is_running:
            # Process system events, monitor agent health, etc.
            await self.agent_manager.check_agent_health()
            
            # Distribute new tasks
            await self.task_queue.process_pending_tasks(self.agent_manager)
            
            # Sleep to avoid busy waiting
            await asyncio.sleep(1)
    
    async def shutdown(self):
        """Shutdown all components gracefully."""
        if not self.is_running:
            return
        
        logger.info("Shutting down coordinator...")
        
        # Stop all agents
        await self.agent_manager.stop_agents()
        
        # Close message broker connection
        await self.message_broker.close()
        
        self.is_running = False
        uptime = datetime.now() - self.start_time if self.start_time else None
        logger.info(f"Coordinator shutdown complete. Uptime: {uptime}")
    
    async def submit_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """Submit a new task to the system.
        
        Args:
            task_type: Type of task (e.g., 'scrape', 'process', etc.)
            task_data: Task parameters and data
            
        Returns:
            task_id: Unique identifier for the submitted task
        """
        task_id = await self.task_queue.add_task(task_type, task_data)
        logger.info(f"Task submitted: {task_id} ({task_type})")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Dictionary with task status information
        """
        return await self.task_queue.get_task_status(task_id)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status.
        
        Returns:
            Dictionary with system status information
        """
        uptime = datetime.now() - self.start_time if self.start_time else None
        
        return {
            "status": "running" if self.is_running else "stopped",
            "uptime": str(uptime),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "agents": await self.agent_manager.get_agent_status(),
            "tasks": {
                "pending": self.task_queue.pending_count(),
                "processing": self.task_queue.processing_count(),
                "completed": self.task_queue.completed_count(),
                "failed": self.task_queue.failed_count()
            }
        }
    
    async def _handle_task_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle task completion and failure events.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        task_id = event_data.get("task_id")
        
        if not task_id:
            logger.warning(f"Received {event_type} event without task_id")
            return
            
        if event_type == "task.completed":
            result = event_data.get("result")
            await self.task_queue.complete_task(task_id, result)
            logger.info(f"Task {task_id} marked as completed in task queue")
            
        elif event_type == "task.failed":
            error = event_data.get("error", "Unknown error")
            await self.task_queue.fail_task(task_id, error)
            logger.info(f"Task {task_id} marked as failed in task queue: {error}")


async def main():
    """Main entry point for running the coordinator."""
    coordinator = Coordinator()
    
    # Handle graceful shutdown
    loop = asyncio.get_event_loop()
    
    try:
        await coordinator.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    finally:
        await coordinator.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 