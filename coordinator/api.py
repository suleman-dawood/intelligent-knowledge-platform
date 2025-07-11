#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API module for the Intelligent Knowledge Aggregation Platform.
Provides HTTP endpoints for interacting with the system.
"""

import logging
import asyncio
import json
import base64
import tempfile
import os
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, Body, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.warning(f"Failed to send message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSockets."""
        if not self.active_connections:
            return
            
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast to WebSocket: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

# Global connection manager
manager = ConnectionManager()


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
    
    @app.post("/api/process-content", response_model=Dict[str, str])
    async def process_content(
        request: Dict[str, Any] = Body(...),
        coordinator=Depends(get_coordinator)
    ):
        """Process new content submitted by users."""
        try:
            content_type = request.get("content_type") or request.get("type")
            title = request.get("title")
            
            # Prepare task data based on content type
            task_data = {
                "title": title,
                "type": content_type
            }
            
            # Determine task type and add specific data
            if content_type == "text" or content_type == "academic":
                task_data["content"] = request.get("content")
                task_type = "process_text"
            elif content_type == "url":
                task_data["url"] = request.get("url")
                task_type = "scrape_web"
            elif content_type == "pdf":
                task_data["filename"] = request.get("filename")
                task_data["size"] = request.get("size")
                task_type = "scrape_pdf"
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported content type: {content_type}")
            
            # Submit the task
            task_id = await coordinator.submit_task(task_type, task_data)
            
            return {"task_id": task_id, "status": "submitted"}
            
        except Exception as e:
            logger.error(f"Error processing content: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/upload-document", response_model=Dict[str, str])
    async def upload_document(
        file: UploadFile = File(...),
        coordinator=Depends(get_coordinator)
    ):
        """Upload and process Word or Excel documents."""
        try:
            # Check file type
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            if file_extension not in ['.docx', '.doc', '.xlsx', '.xls']:
                raise HTTPException(
                    status_code=400, 
                    detail="Unsupported file type. Only Word (.docx, .doc) and Excel (.xlsx, .xls) files are supported."
                )
            
            # Read file content
            file_content = await file.read()
            
            # Encode file content as base64
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
            
            # Determine file type
            file_type = 'word' if file_extension in ['.docx', '.doc'] else 'excel'
            
            # Prepare task data
            task_data = {
                "file_name": file.filename,
                "file_type": file_type,
                "file_content": file_content_b64,
                "file_size": len(file_content)
            }
            
            # Submit document processing task
            task_id = await coordinator.submit_task("process_document", task_data)
            
            return {"task_id": task_id, "status": "submitted", "file_type": file_type}
            
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/search", response_model=List[SearchResult])
    async def search_knowledge(
        q: str = Query(..., description="Search query"),
        coordinator=Depends(get_coordinator)
    ):
        """Search the knowledge base."""
        try:
            # Submit a search task to the UI agent
            task_id = await coordinator.submit_task("search", {"query": q, "max_results": 10})
            
            # Wait for the search task to complete with improved timeout handling
            max_wait_time = 15  # Reduced from 30 to 15 seconds
            wait_time = 0
            
            while wait_time < max_wait_time:
                try:
                    task_status = await coordinator.get_task_status(task_id)
                    
                    if task_status.get("status") == "completed":
                        results = task_status.get("result", {}).get("results", [])
                        
                        # Convert results to SearchResult format
                        search_results = []
                        for i, result in enumerate(results):
                            search_results.append(SearchResult(
                                id=result.get("id", str(i)),
                                title=result.get("title", f"Result {i+1}"),
                                content=result.get("content", result.get("text", "")),
                                source=result.get("source", "knowledge_graph"),
                                score=result.get("score", 0.8),
                                entities=result.get("entities", [])
                            ))
                        
                        return search_results
                    
                    elif task_status.get("status") == "failed":
                        error_msg = task_status.get('error', 'Unknown error')
                        logger.error(f"Search task {task_id} failed: {error_msg}")
                        # Return empty results instead of raising exception for better UX
                        return []
                    
                    # Wait before checking again with exponential backoff
                    await asyncio.sleep(min(0.5 * (2 ** min(wait_time, 4)), 2.0))
                    wait_time += 1
                    
                except Exception as e:
                    logger.error(f"Error checking search task status {task_id}: {e}")
                    await asyncio.sleep(1)
                    wait_time += 1
            
            # Timeout - return empty results with warning
            logger.warning(f"Search task {task_id} timed out after {max_wait_time} seconds")
            return []
            
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/graph/overview", response_model=GraphData)
    async def get_graph_overview(coordinator=Depends(get_coordinator)):
        """Get overview of the knowledge graph."""
        try:
            # Submit a graph overview task
            task_id = await coordinator.submit_task("graph_overview", {"max_nodes": 50, "max_edges": 100})
            
            # Wait for the task to complete
            max_wait_time = 30
            wait_time = 0
            
            while wait_time < max_wait_time:
                task_status = await coordinator.get_task_status(task_id)
                
                if task_status.get("status") == "completed":
                    result = task_status.get("result", {})
                    
                    # Convert to GraphData format
                    nodes = []
                    for node in result.get("nodes", []):
                        nodes.append(GraphNode(
                            id=node.get("id", ""),
                            label=node.get("label", node.get("name", "")),
                            type=node.get("type", "entity"),
                            properties=node.get("properties", {})
                        ))
                    
                    edges = []
                    for edge in result.get("edges", []):
                        edges.append(GraphEdge(
                            source=edge.get("source", ""),
                            target=edge.get("target", ""),
                            label=edge.get("label", edge.get("relationship", "")),
                            properties=edge.get("properties", {})
                        ))
                    
                    return GraphData(nodes=nodes, edges=edges)
                
                elif task_status.get("status") == "failed":
                    raise HTTPException(status_code=500, detail=f"Graph overview failed: {task_status.get('error', 'Unknown error')}")
                
                await asyncio.sleep(1)
                wait_time += 1
            
            # Timeout - return empty graph
            logger.warning(f"Graph overview task {task_id} timed out")
            return GraphData(nodes=[], edges=[])
            
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
            # Submit a node graph task
            task_id = await coordinator.submit_task("node_graph", {
                "node_id": node_id,
                "depth": depth,
                "max_nodes": 30,
                "max_edges": 50
            })
            
            # Wait for the task to complete
            max_wait_time = 30
            wait_time = 0
            
            while wait_time < max_wait_time:
                task_status = await coordinator.get_task_status(task_id)
                
                if task_status.get("status") == "completed":
                    result = task_status.get("result", {})
                    
                    # Convert to GraphData format
                    nodes = []
                    for node in result.get("nodes", []):
                        nodes.append(GraphNode(
                            id=node.get("id", ""),
                            label=node.get("label", node.get("name", "")),
                            type=node.get("type", "entity"),
                            properties=node.get("properties", {})
                        ))
                    
                    edges = []
                    for edge in result.get("edges", []):
                        edges.append(GraphEdge(
                            source=edge.get("source", ""),
                            target=edge.get("target", ""),
                            label=edge.get("label", edge.get("relationship", "")),
                            properties=edge.get("properties", {})
                        ))
                    
                    return GraphData(nodes=nodes, edges=edges)
                
                elif task_status.get("status") == "failed":
                    raise HTTPException(status_code=500, detail=f"Node graph failed: {task_status.get('error', 'Unknown error')}")
                
                await asyncio.sleep(1)
                wait_time += 1
            
            # Timeout - return empty graph
            logger.warning(f"Node graph task {task_id} timed out")
            return GraphData(nodes=[], edges=[])
            
        except Exception as e:
            logger.error(f"Error getting node graph: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/entities/{entity_id}", response_model=Entity)
    async def get_entity_details(entity_id: str, coordinator=Depends(get_coordinator)):
        """Get details for a specific entity."""
        try:
            # Submit an entity details task
            task_id = await coordinator.submit_task("entity_details", {"entity_id": entity_id})
            
            # Wait for the task to complete
            max_wait_time = 15
            wait_time = 0
            
            while wait_time < max_wait_time:
                task_status = await coordinator.get_task_status(task_id)
                
                if task_status.get("status") == "completed":
                    result = task_status.get("result", {})
                    
                    return Entity(
                        id=entity_id,
                        name=result.get("name", f"Entity {entity_id}"),
                        type=result.get("type", "entity"),
                        properties=result.get("properties", {
                            "description": result.get("description", f"Details for entity {entity_id}"),
                            "created_at": datetime.now().isoformat(),
                            "confidence": result.get("confidence", 0.95)
                        })
                    )
                
                elif task_status.get("status") == "failed":
                    raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
                
                await asyncio.sleep(1)
                wait_time += 1
            
            # Timeout - entity not found
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting entity details: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await manager.connect(websocket)
        try:
            while True:
                # Keep the connection alive and handle incoming messages
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle different message types
                message_type = message_data.get("type")
                
                if message_type == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                        websocket
                    )
                elif message_type == "subscribe":
                    # Handle subscription to specific updates
                    await manager.send_personal_message(
                        json.dumps({"type": "subscribed", "data": message_data.get("data")}),
                        websocket
                    )
                else:
                    # Echo back for now
                    await manager.send_personal_message(
                        json.dumps({"type": "echo", "data": message_data}),
                        websocket
                    )
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "websocket_connections": len(manager.active_connections)
        }
    
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