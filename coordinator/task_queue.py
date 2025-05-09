#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Task queue module for the Intelligent Knowledge Aggregation Platform.
Manages task lifecycle and distribution to agents.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from coordinator.utils import build_task_id

logger = logging.getLogger(__name__)


class TaskQueue:
    """Manages tasks and their lifecycle in the system."""
    
    def __init__(self):
        """Initialize the task queue."""
        # Task storage by status
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}
        self.processing_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}
        self.failed_tasks: Dict[str, Dict[str, Any]] = {}
        
        # Task history
        self.task_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Lock for thread safety
        self.lock = asyncio.Lock()
        
        logger.info("Task queue initialized")
    
    async def add_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """Add a new task to the queue.
        
        Args:
            task_type: Type of task
            task_data: Task data
            
        Returns:
            Task ID
        """
        async with self.lock:
            # Generate task ID
            task_id = build_task_id(task_type)
            
            # Create task object
            task = {
                "id": task_id,
                "type": task_type,
                "data": task_data,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "agent_type": self._map_task_type_to_agent(task_type),
                "assigned_to": None,
                "result": None,
                "error": None
            }
            
            # Add to pending tasks
            self.pending_tasks[task_id] = task
            
            # Initialize task history
            self.task_history[task_id] = [{
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
                "message": "Task created"
            }]
            
            logger.info(f"Task added: {task_id} ({task_type})")
            
            return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information
        """
        async with self.lock:
            # Check if task exists in any queue
            task = None
            
            if task_id in self.pending_tasks:
                task = self.pending_tasks[task_id]
            elif task_id in self.processing_tasks:
                task = self.processing_tasks[task_id]
            elif task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
            elif task_id in self.failed_tasks:
                task = self.failed_tasks[task_id]
                
            if not task:
                return {"id": task_id, "status": "not_found"}
                
            # Return task status
            return {
                "id": task_id,
                "status": task["status"],
                "type": task["type"],
                "created_at": task["created_at"],
                "updated_at": task["updated_at"],
                "assigned_to": task["assigned_to"],
                "result": task["result"] if task["status"] == "completed" else None,
                "error": task["error"] if task["status"] == "failed" else None,
                "history": self.task_history.get(task_id, [])
            }
    
    async def process_pending_tasks(self, agent_manager) -> None:
        """Process pending tasks and assign them to available agents.
        
        Args:
            agent_manager: Agent manager instance for assigning tasks
        """
        async with self.lock:
            # Group tasks by agent type
            tasks_by_agent = {}
            
            for task_id, task in self.pending_tasks.items():
                agent_type = task["agent_type"]
                if agent_type not in tasks_by_agent:
                    tasks_by_agent[agent_type] = []
                tasks_by_agent[agent_type].append(task)
            
            # Assign tasks to agents by agent type
            for agent_type, tasks in tasks_by_agent.items():
                available_agents = await agent_manager.get_available_agents(agent_type)
                
                for task in tasks:
                    if not available_agents:
                        break
                        
                    # Get next available agent
                    agent_id = available_agents.pop(0)
                    
                    # Assign task to agent
                    await self._assign_task(task["id"], agent_id)
                    
                    # Notify agent manager
                    await agent_manager.assign_task(agent_id, task["id"], task)
    
    async def _assign_task(self, task_id: str, agent_id: str) -> None:
        """Assign a task to an agent.
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
        """
        if task_id not in self.pending_tasks:
            logger.warning(f"Cannot assign task {task_id}: not in pending tasks")
            return
            
        # Update task status
        task = self.pending_tasks[task_id]
        task["status"] = "processing"
        task["assigned_to"] = agent_id
        task["updated_at"] = datetime.now().isoformat()
        
        # Move task to processing queue
        self.processing_tasks[task_id] = task
        del self.pending_tasks[task_id]
        
        # Update task history
        self.task_history[task_id].append({
            "status": "processing",
            "timestamp": datetime.now().isoformat(),
            "message": f"Task assigned to agent {agent_id}"
        })
        
        logger.info(f"Task {task_id} assigned to agent {agent_id}")
    
    async def complete_task(self, task_id: str, result: Any) -> None:
        """Mark a task as completed.
        
        Args:
            task_id: Task ID
            result: Task result
        """
        async with self.lock:
            if task_id not in self.processing_tasks:
                logger.warning(f"Cannot complete task {task_id}: not in processing tasks")
                return
                
            # Update task status
            task = self.processing_tasks[task_id]
            task["status"] = "completed"
            task["result"] = result
            task["updated_at"] = datetime.now().isoformat()
            
            # Move task to completed queue
            self.completed_tasks[task_id] = task
            del self.processing_tasks[task_id]
            
            # Update task history
            self.task_history[task_id].append({
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "message": "Task completed successfully"
            })
            
            logger.info(f"Task {task_id} completed")
    
    async def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed.
        
        Args:
            task_id: Task ID
            error: Error message
        """
        async with self.lock:
            # Find task in pending or processing queue
            task = None
            
            if task_id in self.pending_tasks:
                task = self.pending_tasks[task_id]
                del self.pending_tasks[task_id]
            elif task_id in self.processing_tasks:
                task = self.processing_tasks[task_id]
                del self.processing_tasks[task_id]
                
            if not task:
                logger.warning(f"Cannot fail task {task_id}: not found in active tasks")
                return
                
            # Update task status
            task["status"] = "failed"
            task["error"] = error
            task["updated_at"] = datetime.now().isoformat()
            
            # Move task to failed queue
            self.failed_tasks[task_id] = task
            
            # Update task history
            self.task_history[task_id].append({
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "message": f"Task failed: {error}"
            })
            
            logger.info(f"Task {task_id} failed: {error}")
    
    async def retry_task(self, task_id: str) -> bool:
        """Retry a failed task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if the task was retried, False otherwise
        """
        async with self.lock:
            if task_id not in self.failed_tasks:
                logger.warning(f"Cannot retry task {task_id}: not in failed tasks")
                return False
                
            # Move task back to pending
            task = self.failed_tasks[task_id]
            task["status"] = "pending"
            task["error"] = None
            task["updated_at"] = datetime.now().isoformat()
            task["assigned_to"] = None
            
            # Move task to pending queue
            self.pending_tasks[task_id] = task
            del self.failed_tasks[task_id]
            
            # Update task history
            self.task_history[task_id].append({
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
                "message": "Task retried"
            })
            
            logger.info(f"Task {task_id} retried")
            
            return True
    
    def pending_count(self) -> int:
        """Get the number of pending tasks.
        
        Returns:
            Number of pending tasks
        """
        return len(self.pending_tasks)
    
    def processing_count(self) -> int:
        """Get the number of processing tasks.
        
        Returns:
            Number of processing tasks
        """
        return len(self.processing_tasks)
    
    def completed_count(self) -> int:
        """Get the number of completed tasks.
        
        Returns:
            Number of completed tasks
        """
        return len(self.completed_tasks)
    
    def failed_count(self) -> int:
        """Get the number of failed tasks.
        
        Returns:
            Number of failed tasks
        """
        return len(self.failed_tasks)
    
    def _map_task_type_to_agent(self, task_type: str) -> str:
        """Map a task type to an agent type.
        
        Args:
            task_type: Task type
            
        Returns:
            Agent type
        """
        # Mapping of task types to agent types
        mapping = {
            # Scraping tasks
            "scrape_web": "scraper",
            "scrape_pdf": "scraper",
            "scrape_academic": "scraper",
            
            # Processing tasks
            "process_text": "processor",
            "process_image": "processor",
            "extract_concepts": "processor",
            
            # Knowledge tasks
            "build_graph": "knowledge",
            "find_connections": "knowledge",
            "validate_knowledge": "knowledge",
            
            # Learning tasks
            "recommend_content": "learning",
            "generate_quiz": "learning",
            "create_study_plan": "learning",
            
            # UI tasks
            "generate_visualization": "ui",
            "compose_dashboard": "ui"
        }
        
        # Default to the task type if no mapping exists
        return mapping.get(task_type, task_type) 