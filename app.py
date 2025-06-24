#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple FastAPI app module for uvicorn to start the server.
"""

import os
import sys
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the coordinator and API creation function
from coordinator.main import Coordinator
from coordinator.api import create_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a mock coordinator for basic API functionality
class MockCoordinator:
    """Mock coordinator for basic API functionality when running standalone."""
    
    def __init__(self):
        self.is_running = True
        
    async def get_system_status(self):
        return {
            "status": "running",
            "uptime": "0:00:00",
            "start_time": None,
            "agents": {},
            "tasks": {
                "pending": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0
            }
        }
    
    async def submit_task(self, task_type: str, task_data: dict):
        # Return a mock task ID
        import uuid
        return str(uuid.uuid4())
    
    async def get_task_status(self, task_id: str):
        return {
            "id": task_id,
            "status": "completed",
            "type": "mock",
            "result": {"message": "Mock task completed"}
        }

# Create the coordinator instance
try:
    # Try to create a real coordinator
    coordinator = Coordinator()
    logger.info("Created real coordinator")
except Exception as e:
    # Fall back to mock coordinator
    logger.warning(f"Failed to create coordinator: {e}. Using mock coordinator.")
    coordinator = MockCoordinator()

# Create the FastAPI app
app = create_api(coordinator)

# Add additional configuration
app.title = "Homework Analyzer API"
app.description = "AI-powered homework and document analysis platform"
app.version = "1.0.0"

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Homework Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/api/content")
async def get_content_list():
    """Get list of uploaded content files."""
    try:
        # Mock content for now - in a real implementation, this would fetch from database
        content_files = [
            {
                "id": "1",
                "name": "Machine Learning Fundamentals.pdf",
                "type": "pdf",
                "size": 2048000,
                "uploadDate": "2024-01-15T10:30:00Z",
                "lastModified": "2024-01-15T10:30:00Z",
                "tags": ["machine learning", "AI", "fundamentals"],
                "summary": "Comprehensive guide to machine learning concepts and algorithms.",
            },
            {
                "id": "2",
                "name": "Data Analysis Report.xlsx",
                "type": "xlsx",
                "size": 512000,
                "uploadDate": "2024-01-14T14:20:00Z",
                "lastModified": "2024-01-16T09:15:00Z",
                "tags": ["data analysis", "statistics", "report"],
                "summary": "Statistical analysis of user behavior data with visualizations.",
            },
            {
                "id": "3",
                "name": "Project Proposal.docx",
                "type": "docx",
                "size": 256000,
                "uploadDate": "2024-01-13T16:45:00Z",
                "lastModified": "2024-01-13T16:45:00Z",
                "tags": ["proposal", "project", "business"],
                "summary": "Detailed project proposal for the new AI initiative.",
            },
        ]
        return {"files": content_files}
    except Exception as e:
        logger.error(f"Error fetching content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_files(files: list = File(...)):
    """Upload multiple files."""
    try:
        uploaded_files = []
        for file in files:
            # Process the file (mock implementation)
            file_info = {
                "id": f"upload_{datetime.now().timestamp()}",
                "name": file.filename,
                "type": file.filename.split('.')[-1].lower() if file.filename else "unknown",
                "size": 0,  # Mock size
                "uploadDate": datetime.now().isoformat(),
            }
            uploaded_files.append(file_info)
        
        return {"uploaded_files": uploaded_files, "count": len(uploaded_files)}
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3100) 