#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API module for the Intelligent Knowledge Aggregation Platform.
Provides HTTP endpoints for interacting with the system.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Request & Response Models
class TaskSubmitRequest(BaseModel):
    """Model for submitting a new task."""
    
    task_type: str = Field(..., description="Type of task to execute")
    task_data: Dict[str, Any] = Field(..., description="Task parameters and data")


class TaskStatusResponse(BaseModel):
    """Model for task status response."""
    
    id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Current status of the task")
    type: Optional[str] = Field(None, description="Type of task")
    created_at: Optional[str] = Field(None, description="Timestamp when task was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when task was last updated")
    assigned_to: Optional[str] = Field(None, description="Agent ID the task is assigned to")
    result: Optional[Any] = Field(None, description="Task result (if completed)")
    error: Optional[str] = Field(None, description="Error message (if failed)")
    history: Optional[List[Dict[str, Any]]] = Field(None, description="Task status history")


class SystemStatusResponse(BaseModel):
    """Model for system status response."""
    
    status: str = Field(..., description="Current system status")
    uptime: Optional[str] = Field(None, description="System uptime")
    start_time: Optional[str] = Field(None, description="Timestamp when system was started")
    agents: Dict[str, Dict[str, int]] = Field(..., description="Agent status by type")
    tasks: Dict[str, int] = Field(..., description="Task counts by status")


# API configuration
def create_api(coordinator):
    """Create the FastAPI application.
    
    Args:
        coordinator: Coordinator instance
        
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Intelligent Knowledge Aggregation Platform API",
        description="API for interacting with the knowledge platform",
        version="0.1.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create dependency for accessing the coordinator
    async def get_coordinator():
        return coordinator
    
    # Routes
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Intelligent Knowledge Aggregation Platform API"}
    
    @app.get("/status", response_model=SystemStatusResponse)
    async def get_system_status(coordinator=Depends(get_coordinator)):
        """Get overall system status."""
        return await coordinator.get_system_status()
    
    @app.post("/tasks", response_model=Dict[str, str])
    async def submit_task(
        request: TaskSubmitRequest,
        coordinator=Depends(get_coordinator)
    ):
        """Submit a new task to the system."""
        try:
            task_id = await coordinator.submit_task(request.task_type, request.task_data)
            return {"task_id": task_id}
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
    async def get_task_status(task_id: str, coordinator=Depends(get_coordinator)):
        """Get the status of a specific task."""
        status = await coordinator.get_task_status(task_id)
        
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
        return status
    
    @app.post("/tasks/{task_id}/retry", response_model=Dict[str, str])
    async def retry_task(
        task_id: str,
        background_tasks: BackgroundTasks,
        coordinator=Depends(get_coordinator)
    ):
        """Retry a failed task."""
        # This would be implemented on the task queue
        # For now, we'll just return a placeholder response
        return {"status": "retry_requested", "task_id": task_id}
    
    @app.get("/agents", response_model=Dict[str, Dict[str, int]])
    async def get_agents(coordinator=Depends(get_coordinator)):
        """Get agent status information."""
        return await coordinator.agent_manager.get_agent_status()
    
    return app


async def start_api_server(coordinator, host: str = "localhost", port: int = 8000):
    """Start the API server.
    
    Args:
        coordinator: Coordinator instance
        host: Host to bind to
        port: Port to listen on
    """
    app = create_api(coordinator)
    
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    logger.info(f"Starting API server at http://{host}:{port}")
    
    await server.serve()
    
    logger.info("API server stopped") 