#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agent manager module for the Intelligent Knowledge Aggregation Platform.
Handles agent lifecycle management, health monitoring, and task assignment.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set

from coordinator.utils import generate_id

logger = logging.getLogger(__name__)


class AgentState:
    """Represents the state of an agent."""
    
    STARTING = "starting"
    RUNNING = "running"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"


class AgentManager:
    """Manages agent lifecycle and status."""
    
    def __init__(self, config: Dict[str, Any], message_broker):
        """Initialize the agent manager.
        
        Args:
            config: Agent configuration
            message_broker: Message broker instance
        """
        self.config = config
        self.message_broker = message_broker
        
        # Agent pools by type
        self.agents: Dict[str, Dict[str, Dict[str, Any]]] = {
            "scraper": {},
            "processor": {},
            "knowledge": {},
            "learning": {},
            "ui": {}
        }
        
        # Track tasks assigned to agents
        self.agent_tasks: Dict[str, Set[str]] = {}
        
        # Health check settings
        self.health_check_interval = 30  # seconds
        self.last_health_check = datetime.now()
        
        logger.info("Agent manager initialized")
    
    async def start_agents(self) -> None:
        """Start agents according to configuration."""
        logger.info("Starting agents...")
        
        # Start agents by type
        for agent_type, pool in self.agents.items():
            max_agents = self.config.get(f"max_{agent_type}_agents", 1)
            
            for i in range(max_agents):
                await self.start_agent(agent_type)
                
        logger.info("All agents started")
    
    async def start_agent(self, agent_type: str) -> str:
        """Start a new agent of the specified type.
        
        Args:
            agent_type: Type of agent to start
            
        Returns:
            Agent ID
        """
        # Generate a unique agent ID
        agent_id = generate_id(f"{agent_type}-")
        
        # Create agent object
        agent = {
            "id": agent_id,
            "type": agent_type,
            "state": AgentState.STARTING,
            "started_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "current_tasks": []
        }
        
        # Add to agent pool
        self.agents[agent_type][agent_id] = agent
        self.agent_tasks[agent_id] = set()
        
        # Publish agent start event
        await self.message_broker.publish_event(
            "agent.started",
            {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Set agent to idle state
        await self._update_agent_state(agent_id, AgentState.IDLE)
        
        logger.info(f"Started agent: {agent_id} ({agent_type})")
        
        return agent_id
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent.
        
        Args:
            agent_id: Agent ID to stop
            
        Returns:
            True if the agent was stopped, False otherwise
        """
        # Find the agent
        agent = None
        agent_type = None
        
        for a_type, pool in self.agents.items():
            if agent_id in pool:
                agent = pool[agent_id]
                agent_type = a_type
                break
                
        if not agent:
            logger.warning(f"Cannot stop agent {agent_id}: not found")
            return False
            
        # Update agent state
        await self._update_agent_state(agent_id, AgentState.STOPPING)
        
        # Publish agent stop event
        await self.message_broker.publish_event(
            "agent.stopping",
            {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Wait for agent to finish current tasks
        current_tasks = agent["current_tasks"]
        if current_tasks:
            logger.info(f"Waiting for agent {agent_id} to finish {len(current_tasks)} tasks")
            # In a real implementation, we would wait for tasks to complete
            # For simplicity, we're just marking the agent as stopped
        
        # Update agent state
        await self._update_agent_state(agent_id, AgentState.STOPPED)
        
        # Remove from agent pool
        del self.agents[agent_type][agent_id]
        if agent_id in self.agent_tasks:
            del self.agent_tasks[agent_id]
            
        # Publish agent stopped event
        await self.message_broker.publish_event(
            "agent.stopped",
            {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Stopped agent: {agent_id}")
        
        return True
    
    async def stop_agents(self) -> None:
        """Stop all agents gracefully."""
        logger.info("Stopping all agents...")
        
        # Collect all agent IDs
        agent_ids = []
        for pool in self.agents.values():
            agent_ids.extend(pool.keys())
            
        # Stop each agent
        for agent_id in agent_ids:
            await self.stop_agent(agent_id)
            
        logger.info("All agents stopped")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get the status of all agents.
        
        Returns:
            Dictionary with agent status information
        """
        result = {}
        
        # Collect status by agent type
        for agent_type, pool in self.agents.items():
            count = len(pool)
            idle = sum(1 for agent in pool.values() if agent["state"] == AgentState.IDLE)
            busy = sum(1 for agent in pool.values() if agent["state"] == AgentState.BUSY)
            error = sum(1 for agent in pool.values() if agent["state"] == AgentState.ERROR)
            
            result[agent_type] = {
                "total": count,
                "idle": idle,
                "busy": busy,
                "error": error
            }
            
        return result
    
    async def get_available_agents(self, agent_type: str) -> List[str]:
        """Get a list of available (idle) agents of the specified type.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            List of agent IDs
        """
        if agent_type not in self.agents:
            return []
            
        # Find idle agents
        available = [
            agent_id
            for agent_id, agent in self.agents[agent_type].items()
            if agent["state"] == AgentState.IDLE
        ]
        
        return available
    
    async def assign_task(self, agent_id: str, task_id: str, task: Dict[str, Any]) -> bool:
        """Assign a task to an agent.
        
        Args:
            agent_id: Agent ID
            task_id: Task ID
            task: Task data
            
        Returns:
            True if the task was assigned, False otherwise
        """
        # Find the agent
        agent = None
        agent_type = None
        
        for a_type, pool in self.agents.items():
            if agent_id in pool:
                agent = pool[agent_id]
                agent_type = a_type
                break
                
        if not agent:
            logger.warning(f"Cannot assign task to agent {agent_id}: not found")
            return False
            
        # Check if agent is available
        if agent["state"] != AgentState.IDLE:
            logger.warning(f"Cannot assign task to agent {agent_id}: not idle")
            return False
            
        # Update agent state
        agent["current_tasks"].append(task_id)
        await self._update_agent_state(agent_id, AgentState.BUSY)
        
        # Add task to agent tasks
        if agent_id in self.agent_tasks:
            self.agent_tasks[agent_id].add(task_id)
            
        # Publish task to agent
        await self.message_broker.publish_task(agent_type, {
            "task_id": task_id,
            "task_type": task["type"],
            "task_data": task["data"],
            "agent_id": agent_id
        })
        
        logger.info(f"Assigned task {task_id} to agent {agent_id}")
        
        return True
    
    async def complete_task(self, agent_id: str, task_id: str, result: Any) -> bool:
        """Mark a task as completed by an agent.
        
        Args:
            agent_id: Agent ID
            task_id: Task ID
            result: Task result
            
        Returns:
            True if the task was marked as completed, False otherwise
        """
        # Find the agent
        agent = None
        agent_type = None
        
        for a_type, pool in self.agents.items():
            if agent_id in pool:
                agent = pool[agent_id]
                agent_type = a_type
                break
                
        if not agent:
            logger.warning(f"Cannot complete task for agent {agent_id}: not found")
            return False
            
        # Check if the task is assigned to the agent
        if task_id not in agent["current_tasks"]:
            logger.warning(f"Cannot complete task {task_id}: not assigned to agent {agent_id}")
            return False
            
        # Remove task from agent
        agent["current_tasks"].remove(task_id)
        
        # Remove task from agent tasks
        if agent_id in self.agent_tasks and task_id in self.agent_tasks[agent_id]:
            self.agent_tasks[agent_id].remove(task_id)
            
        # Update agent state if no more tasks
        if not agent["current_tasks"]:
            await self._update_agent_state(agent_id, AgentState.IDLE)
            
        # Publish task completion event
        await self.message_broker.publish_event(
            "task.completed",
            {
                "task_id": task_id,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
        )
        
        logger.info(f"Agent {agent_id} completed task {task_id}")
        
        return True
    
    async def fail_task(self, agent_id: str, task_id: str, error: str) -> bool:
        """Mark a task as failed by an agent.
        
        Args:
            agent_id: Agent ID
            task_id: Task ID
            error: Error message
            
        Returns:
            True if the task was marked as failed, False otherwise
        """
        # Find the agent
        agent = None
        agent_type = None
        
        for a_type, pool in self.agents.items():
            if agent_id in pool:
                agent = pool[agent_id]
                agent_type = a_type
                break
                
        if not agent:
            logger.warning(f"Cannot fail task for agent {agent_id}: not found")
            return False
            
        # Check if the task is assigned to the agent
        if task_id not in agent["current_tasks"]:
            logger.warning(f"Cannot fail task {task_id}: not assigned to agent {agent_id}")
            return False
            
        # Remove task from agent
        agent["current_tasks"].remove(task_id)
        
        # Remove task from agent tasks
        if agent_id in self.agent_tasks and task_id in self.agent_tasks[agent_id]:
            self.agent_tasks[agent_id].remove(task_id)
            
        # Update agent state if no more tasks
        if not agent["current_tasks"]:
            await self._update_agent_state(agent_id, AgentState.IDLE)
            
        # Publish task failure event
        await self.message_broker.publish_event(
            "task.failed",
            {
                "task_id": task_id,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "error": error
            }
        )
        
        logger.info(f"Agent {agent_id} failed task {task_id}: {error}")
        
        return True
    
    async def check_agent_health(self) -> None:
        """Check the health of all agents and handle issues."""
        now = datetime.now()
        
        # Check if it's time for a health check
        if (now - self.last_health_check).total_seconds() < self.health_check_interval:
            return
            
        self.last_health_check = now
        logger.debug("Performing agent health check")
        
        # Check each agent
        for agent_type, pool in self.agents.items():
            for agent_id, agent in list(pool.items()):  # Use list() to avoid dict changes during iteration
                # Skip agents that are starting, stopping or stopped
                if agent["state"] in [AgentState.STARTING, AgentState.STOPPING, AgentState.STOPPED]:
                    continue
                    
                # Check for stale heartbeat
                last_heartbeat = datetime.fromisoformat(agent["last_heartbeat"])
                if (now - last_heartbeat).total_seconds() > 60:  # 1 minute timeout
                    logger.warning(f"Agent {agent_id} appears to be unresponsive")
                    
                    # Mark agent as having an error
                    await self._update_agent_state(agent_id, AgentState.ERROR)
                    
                    # Publish agent error event
                    await self.message_broker.publish_event(
                        "agent.error",
                        {
                            "agent_id": agent_id,
                            "agent_type": agent_type,
                            "timestamp": now.isoformat(),
                            "error": "Agent heartbeat timeout"
                        }
                    )
                    
                    # Handle agent tasks
                    await self._handle_agent_failure(agent_id)
    
    async def _handle_agent_failure(self, agent_id: str) -> None:
        """Handle tasks from a failed agent.
        
        Args:
            agent_id: Agent ID that failed
        """
        # Find the agent
        agent = None
        agent_type = None
        
        for a_type, pool in self.agents.items():
            if agent_id in pool:
                agent = pool[agent_id]
                agent_type = a_type
                break
                
        if not agent:
            return
            
        # Get tasks assigned to the agent
        tasks = agent["current_tasks"].copy()
        
        if not tasks:
            return
            
        logger.info(f"Handling {len(tasks)} tasks from failed agent {agent_id}")
        
        # Publish task failure events for all tasks
        for task_id in tasks:
            await self.message_broker.publish_event(
                "task.failed",
                {
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": "Agent failure"
                }
            )
            
        # Clear tasks from agent
        agent["current_tasks"] = []
        
        # Clear agent tasks
        if agent_id in self.agent_tasks:
            self.agent_tasks[agent_id] = set()
    
    async def _update_agent_state(self, agent_id: str, state: str) -> None:
        """Update the state of an agent.
        
        Args:
            agent_id: Agent ID
            state: New state
        """
        # Find the agent
        agent = None
        agent_type = None
        
        for a_type, pool in self.agents.items():
            if agent_id in pool:
                agent = pool[agent_id]
                agent_type = a_type
                break
                
        if not agent:
            return
            
        # Update agent state
        old_state = agent["state"]
        agent["state"] = state
        
        # Publish state change event
        await self.message_broker.publish_event(
            "agent.state_changed",
            {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "old_state": old_state,
                "new_state": state,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.debug(f"Agent {agent_id} state changed: {old_state} -> {state}")
    
    async def update_heartbeat(self, agent_id: str) -> bool:
        """Update the heartbeat timestamp for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if the heartbeat was updated, False otherwise
        """
        # Find the agent
        agent = None
        
        for pool in self.agents.values():
            if agent_id in pool:
                agent = pool[agent_id]
                break
                
        if not agent:
            return False
            
        # Update heartbeat
        agent["last_heartbeat"] = datetime.now().isoformat()
        
        # If agent was in error state, restore to running state
        if agent["state"] == AgentState.ERROR:
            if agent["current_tasks"]:
                await self._update_agent_state(agent_id, AgentState.BUSY)
            else:
                await self._update_agent_state(agent_id, AgentState.IDLE)
                
        return True 