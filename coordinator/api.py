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
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
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


class SearchResult(BaseModel):
    """Model for search result."""
    
    id: str = Field(..., description="Result ID")
    title: str = Field(..., description="Result title")
    content: str = Field(..., description="Result content")
    source: str = Field(..., description="Result source")
    score: float = Field(..., description="Relevance score")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Associated entities")


class Entity(BaseModel):
    """Model for entity."""
    
    id: str = Field(..., description="Entity ID")
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Entity properties")


class GraphNode(BaseModel):
    """Model for graph node."""
    
    id: str = Field(..., description="Node ID")
    label: str = Field(..., description="Node label")
    type: str = Field(..., description="Node type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")


class GraphEdge(BaseModel):
    """Model for graph edge."""
    
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: str = Field(..., description="Edge label")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")


class GraphData(BaseModel):
    """Model for graph data."""
    
    nodes: List[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Graph edges")


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
    
    @app.get("/search", response_model=List[SearchResult])
    async def search_knowledge(
        q: str = Query(..., description="Search query"),
        coordinator=Depends(get_coordinator)
    ):
        """Search the knowledge base."""
        try:
            # Submit a search task and wait for results
            task_id = await coordinator.submit_task("search", {"query": q})
            
            # For now, return mock results since the search implementation would be complex
            # In a real implementation, this would query the knowledge graph and vector database
            return [
                SearchResult(
                    id="1",
                    title=f"Search result for: {q}",
                    content=f"This is a mock search result for the query '{q}'. In a real implementation, this would contain actual search results from the knowledge graph.",
                    source="knowledge_graph",
                    score=0.95,
                    entities=[]
                )
            ]
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/graph/overview", response_model=GraphData)
    async def get_graph_overview(coordinator=Depends(get_coordinator)):
        """Get overview of the knowledge graph."""
        try:
            # For now, return mock graph data
            # In a real implementation, this would query the Neo4j database
            return GraphData(
                nodes=[
                    GraphNode(id="1", label="Sample Entity", type="concept", properties={"description": "A sample entity"}),
                    GraphNode(id="2", label="Related Entity", type="person", properties={"description": "A related entity"})
                ],
                edges=[
                    GraphEdge(source="1", target="2", label="related_to", properties={"strength": 0.8})
                ]
            )
        except Exception as e:
            logger.error(f"Error getting graph overview: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/graph/node/{node_id}", response_model=GraphData)
    async def get_node_graph(
        node_id: str,
        depth: int = Query(2, description="Depth of graph traversal"),
        coordinator=Depends(get_coordinator)
    ):
        """Get graph data for a specific node."""
        try:
            # For now, return mock graph data
            # In a real implementation, this would query the Neo4j database for the specific node and its neighbors
            return GraphData(
                nodes=[
                    GraphNode(id=node_id, label=f"Node {node_id}", type="concept", properties={"description": f"Node {node_id} details"}),
                    GraphNode(id=f"{node_id}_neighbor", label=f"Neighbor of {node_id}", type="related", properties={"description": "A neighboring node"})
                ],
                edges=[
                    GraphEdge(source=node_id, target=f"{node_id}_neighbor", label="connected_to", properties={"strength": 0.9})
                ]
            )
        except Exception as e:
            logger.error(f"Error getting node graph: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/entities/{entity_id}", response_model=Entity)
    async def get_entity_details(entity_id: str, coordinator=Depends(get_coordinator)):
        """Get details for a specific entity."""
        try:
            # For now, return mock entity data
            # In a real implementation, this would query the knowledge graph database
            return Entity(
                id=entity_id,
                name=f"Entity {entity_id}",
                type="concept",
                properties={
                    "description": f"Details for entity {entity_id}",
                    "created_at": datetime.now().isoformat(),
                    "confidence": 0.95
                }
            )
        except Exception as e:
            logger.error(f"Error getting entity details: {e}")
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
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