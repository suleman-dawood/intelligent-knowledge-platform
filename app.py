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
        import os
        import mimetypes
        from pathlib import Path
        
        # Path to the uploads directory
        uploads_dir = Path("frontend/uploads")
        content_files = []
        
        if uploads_dir.exists():
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    # Get file stats
                    stat = file_path.stat()
                    
                    # Determine file type from extension
                    file_ext = file_path.suffix.lower()
                    if file_ext in ['.pdf']:
                        file_type = 'pdf'
                    elif file_ext in ['.docx', '.doc']:
                        file_type = 'docx'
                    elif file_ext in ['.xlsx', '.xls']:
                        file_type = 'xlsx'
                    elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                        file_type = 'image'
                    elif file_ext in ['.mp4', '.avi', '.mov', '.wmv']:
                        file_type = 'video'
                    elif file_ext in ['.mp3', '.wav', '.flac', '.aac']:
                        file_type = 'audio'
                    else:
                        file_type = 'other'
                    
                    # Create file info
                    file_info = {
                        "id": file_path.name,  # Use filename as ID
                        "name": file_path.name,
                        "type": file_type,
                        "size": stat.st_size,
                        "uploadDate": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
                        "lastModified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
                        "tags": [file_type, "uploaded"],  # Basic tags
                        "summary": f"Uploaded {file_type} file: {file_path.name}",
                        "url": f"/uploads/{file_path.name}"
                    }
                    content_files.append(file_info)
        
        # Sort by upload date (newest first)
        content_files.sort(key=lambda x: x["uploadDate"], reverse=True)
        
        return {"files": content_files}
    except Exception as e:
        logger.error(f"Error fetching content: {e}")
        # Fallback to empty list instead of mock data
        return {"files": []}

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