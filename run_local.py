#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Local runner for the Intelligent Knowledge Aggregation Platform.
This script starts the coordinator and a set of agents for local development.
"""

import os
import sys
import argparse
import asyncio
import logging
import signal
from typing import List, Dict, Any
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def start_coordinator():
    """Start the coordinator."""
    logger.info("Starting coordinator")
    
    # Import the coordinator module
    from coordinator.main import Coordinator
    
    # Create and start the coordinator
    coordinator = Coordinator()
    await coordinator.start()
    
    return coordinator


async def start_agent(agent_type: str, agent_id: str):
    """Start an agent of the specified type.
    
    Args:
        agent_type: Type of agent to start
        agent_id: Unique identifier for the agent
    """
    logger.info(f"Starting {agent_type} agent {agent_id}")
    
    # Import the appropriate agent module
    if agent_type == "scraper":
        from agents.scraper.agent import ScraperAgent
        agent = ScraperAgent(agent_id)
    elif agent_type == "processor":
        # This would be implemented in a real system
        logger.warning(f"Agent type {agent_type} not implemented yet")
        return None
    elif agent_type == "knowledge":
        # This would be implemented in a real system
        logger.warning(f"Agent type {agent_type} not implemented yet")
        return None
    elif agent_type == "learning":
        # This would be implemented in a real system
        logger.warning(f"Agent type {agent_type} not implemented yet")
        return None
    elif agent_type == "ui":
        # This would be implemented in a real system
        logger.warning(f"Agent type {agent_type} not implemented yet")
        return None
    else:
        logger.error(f"Unknown agent type: {agent_type}")
        return None
    
    # Start the agent
    if agent:
        await agent.start()
    
    return agent


async def main():
    """Main entry point for the local runner."""
    parser = argparse.ArgumentParser(description="Run the Intelligent Knowledge Platform locally")
    parser.add_argument("--no-coordinator", action="store_true", help="Don't start the coordinator")
    parser.add_argument("--scraper-agents", type=int, default=1, help="Number of scraper agents to start")
    parser.add_argument("--processor-agents", type=int, default=0, help="Number of processor agents to start")
    parser.add_argument("--knowledge-agents", type=int, default=0, help="Number of knowledge agents to start")
    parser.add_argument("--learning-agents", type=int, default=0, help="Number of learning agents to start")
    parser.add_argument("--ui-agents", type=int, default=0, help="Number of UI agents to start")
    
    args = parser.parse_args()
    
    # Start the coordinator if requested
    coordinator = None
    if not args.no_coordinator:
        coordinator = await start_coordinator()
    
    # Start the requested agents
    agents = []
    
    # Scraper agents
    for i in range(args.scraper_agents):
        agent = await start_agent("scraper", f"scraper-{i+1}")
        if agent:
            agents.append(agent)
    
    # Processor agents
    for i in range(args.processor_agents):
        agent = await start_agent("processor", f"processor-{i+1}")
        if agent:
            agents.append(agent)
    
    # Knowledge agents
    for i in range(args.knowledge_agents):
        agent = await start_agent("knowledge", f"knowledge-{i+1}")
        if agent:
            agents.append(agent)
    
    # Learning agents
    for i in range(args.learning_agents):
        agent = await start_agent("learning", f"learning-{i+1}")
        if agent:
            agents.append(agent)
    
    # UI agents
    for i in range(args.ui_agents):
        agent = await start_agent("ui", f"ui-{i+1}")
        if agent:
            agents.append(agent)
    
    logger.info(f"Started {len(agents)} agents")
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("Shutdown signal received")
        asyncio.create_task(shutdown())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    async def shutdown():
        """Shutdown all components gracefully."""
        logger.info("Shutting down")
        
        # Stop all agents
        for agent in agents:
            try:
                await agent.stop()
            except Exception as e:
                logger.error(f"Error stopping agent: {e}")
        
        # Stop the coordinator
        if coordinator:
            try:
                await coordinator.shutdown()
            except Exception as e:
                logger.error(f"Error stopping coordinator: {e}")
        
        # Stop the event loop
        loop.stop()
    
    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        # Ensure everything is shut down
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 