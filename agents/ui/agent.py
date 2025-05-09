#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI agent for the Intelligent Knowledge Aggregation Platform.
Responsible for handling frontend interactions and websocket connections.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import aiohttp
from aiohttp import web
import socketio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import configuration and utilities
from coordinator.config import load_config
from coordinator.utils import setup_logging
from coordinator.message_broker import MessageBroker

# Configure logging
logger = logging.getLogger(__name__)


class UIAgent:
    """UI agent for handling frontend interactions and websocket connections."""
    
    def __init__(self, agent_id: str, config_path: Optional[str] = None):
        """Initialize the UI agent.
        
        Args:
            agent_id: Unique identifier for this agent
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        setup_logging(self.config.get('logging', {}))
        
        self.agent_id = agent_id
        self.agent_type = "ui"
        
        # Initialize message broker
        self.message_broker = MessageBroker(self.config.get('rabbitmq', {}))
        
        # Initialize web server components
        self.app = web.Application()
        self.sio = socketio.AsyncServer(cors_allowed_origins='*')
        self.sio.attach(self.app)
        
        # Configure routes
        self._setup_routes()
        
        # Configure Socket.IO events
        self._setup_socketio()
        
        # Track current state
        self.is_running = False
        self.connected_clients = {}
        
        logger.info(f"UI agent {agent_id} initialized")
    
    def _setup_routes(self) -> None:
        """Set up HTTP routes."""
        # Add routes for the REST API
        self.app.router.add_get("/api/status", self._handle_status)
        self.app.router.add_get("/api/knowledge-graph", self._handle_get_knowledge_graph)
        self.app.router.add_post("/api/submit-query", self._handle_submit_query)
        self.app.router.add_post("/api/feedback", self._handle_feedback)
    
    def _setup_socketio(self) -> None:
        """Set up Socket.IO event handlers."""
        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection."""
            logger.info(f"Client connected: {sid}")
            self.connected_clients[sid] = {
                "connected_at": datetime.now().isoformat(),
                "user_id": None
            }
            
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            logger.info(f"Client disconnected: {sid}")
            if sid in self.connected_clients:
                del self.connected_clients[sid]
                
        @self.sio.event
        async def authenticate(sid, data):
            """Handle client authentication."""
            user_id = data.get('user_id')
            if user_id:
                self.connected_clients[sid]['user_id'] = user_id
                logger.info(f"Client {sid} authenticated as user {user_id}")
                return {"status": "authenticated"}
            else:
                return {"status": "error", "message": "Authentication failed"}
                
        @self.sio.event
        async def subscribe_to_updates(sid, data):
            """Handle subscription to knowledge graph updates."""
            entity_id = data.get('entity_id')
            if entity_id:
                # Subscribe the client to updates for this entity
                await self.sio.enter_room(sid, f"entity_{entity_id}")
                logger.info(f"Client {sid} subscribed to entity {entity_id} updates")
                return {"status": "subscribed"}
            else:
                return {"status": "error", "message": "No entity ID provided"}
    
    async def _handle_status(self, request: web.Request) -> web.Response:
        """Handle status request."""
        return web.json_response({
            "status": "running" if self.is_running else "stopped",
            "agent_id": self.agent_id,
            "uptime": str(datetime.now() - self.start_time) if hasattr(self, 'start_time') else None,
            "connected_clients": len(self.connected_clients)
        })
    
    async def _handle_get_knowledge_graph(self, request: web.Request) -> web.Response:
        """Handle knowledge graph request."""
        # Get query parameters
        entity_id = request.query.get('entity_id')
        depth = int(request.query.get('depth', 1))
        
        try:
            # Create a task to fetch the knowledge graph
            task_id = await self.message_broker.publish_task(
                "knowledge",
                "get_graph",
                {
                    "entity_id": entity_id,
                    "depth": depth
                }
            )
            
            # Wait for the result (with timeout)
            result = await self._wait_for_task_result(task_id, timeout=10.0)
            
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"Error handling knowledge graph request: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def _handle_submit_query(self, request: web.Request) -> web.Response:
        """Handle query submission."""
        try:
            data = await request.json()
            query = data.get('query')
            
            if not query:
                return web.json_response(
                    {"error": "No query provided"},
                    status=400
                )
                
            # Process the query
            task_id = await self.message_broker.publish_task(
                "processor",
                "process_query",
                {
                    "query": query
                }
            )
            
            # Return the task ID for the client to check the status
            return web.json_response({
                "task_id": task_id,
                "status": "processing"
            })
            
        except Exception as e:
            logger.error(f"Error handling query submission: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def _handle_feedback(self, request: web.Request) -> web.Response:
        """Handle user feedback."""
        try:
            data = await request.json()
            
            # Process the feedback
            task_id = await self.message_broker.publish_task(
                "learning",
                "analyze_feedback",
                data
            )
            
            return web.json_response({
                "status": "feedback_received",
                "task_id": task_id
            })
            
        except Exception as e:
            logger.error(f"Error handling feedback: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def _wait_for_task_result(self, task_id: str, timeout: float = 30.0) -> Dict[str, Any]:
        """Wait for a task result from the message broker.
        
        Args:
            task_id: Task ID to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            Task result
            
        Raises:
            TimeoutError: If the task does not complete within the timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check task status
            status = await self.message_broker.get_task_status(task_id)
            
            if status.get('status') == 'completed':
                return status.get('result', {})
                
            if status.get('status') == 'failed':
                raise Exception(f"Task failed: {status.get('error')}")
                
            # Wait before checking again
            await asyncio.sleep(0.1)
            
        raise TimeoutError(f"Timeout waiting for task {task_id}")
    
    async def _broadcast_update(self, entity_id: str, update_data: Dict[str, Any]) -> None:
        """Broadcast an update to all clients subscribed to an entity.
        
        Args:
            entity_id: Entity ID that was updated
            update_data: Update data to send
        """
        room = f"entity_{entity_id}"
        await self.sio.emit('entity_update', {
            'entity_id': entity_id,
            'update': update_data,
            'timestamp': datetime.now().isoformat()
        }, room=room)
        
        logger.debug(f"Broadcasted update for entity {entity_id} to {room}")
    
    async def start(self) -> None:
        """Start the UI agent."""
        if self.is_running:
            logger.warning(f"UI agent {self.agent_id} is already running")
            return
            
        logger.info(f"Starting UI agent {self.agent_id}")
        
        # Connect to message broker
        await self.message_broker.connect()
        
        # Subscribe to events
        await self.message_broker.subscribe_to_events(
            ["entity.updated", "knowledge.updated", "task.completed"],
            self._handle_system_event
        )
        
        # Start heartbeat
        asyncio.create_task(self._send_heartbeat())
        
        # Record start time
        self.start_time = datetime.now()
        self.is_running = True
        
        # Get host and port from config
        host = self.config.get('ui_agent', {}).get('host', 'localhost')
        port = self.config.get('ui_agent', {}).get('port', 3100)
        
        # Start the web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"UI agent {self.agent_id} started at http://{host}:{port}")
    
    async def stop(self) -> None:
        """Stop the UI agent."""
        if not self.is_running:
            return
            
        logger.info(f"Stopping UI agent {self.agent_id}")
        
        # Close message broker connection
        await self.message_broker.close()
        
        # Close all websocket connections
        for sid in list(self.connected_clients.keys()):
            await self.sio.disconnect(sid)
            
        self.is_running = False
        logger.info(f"UI agent {self.agent_id} stopped")
    
    async def _send_heartbeat(self) -> None:
        """Send periodic heartbeats to the coordinator."""
        while self.is_running:
            try:
                await self.message_broker.publish_event(
                    "agent.heartbeat",
                    {
                        "agent_id": self.agent_id,
                        "agent_type": self.agent_type,
                        "timestamp": datetime.now().isoformat(),
                        "connected_clients": len(self.connected_clients)
                    }
                )
                
                await asyncio.sleep(10)  # Send heartbeat every 10 seconds
                
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(5)  # Retry after a shorter delay
    
    async def _handle_system_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle system events.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if event_type == "entity.updated":
            # Broadcast the update to subscribed clients
            entity_id = event_data.get("entity_id")
            if entity_id:
                await self._broadcast_update(entity_id, event_data)
                
        elif event_type == "knowledge.updated":
            # Broadcast knowledge graph updates
            # This could trigger a full refresh on the frontend
            await self.sio.emit('knowledge_updated', {
                'update': event_data,
                'timestamp': datetime.now().isoformat()
            })
            
        elif event_type == "task.completed":
            # Notify any clients waiting for this task
            task_id = event_data.get("task_id")
            if task_id:
                await self.sio.emit('task_completed', {
                    'task_id': task_id,
                    'result': event_data.get("result"),
                    'timestamp': datetime.now().isoformat()
                })
                
        elif event_type == "agent.stopping":
            agent_id = event_data.get("agent_id")
            
            # Check if this event is for this agent
            if agent_id == self.agent_id:
                logger.info(f"Received stop signal for agent {self.agent_id}")
                await self.stop()


async def main():
    """Main entry point for running the UI agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a UI agent")
    parser.add_argument("--agent-id", type=str, help="Agent ID")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    
    args = parser.parse_args()
    
    agent_id = args.agent_id or f"ui-{os.getpid()}"
    
    agent = UIAgent(agent_id, args.config)
    
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