#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility functions for the Intelligent Knowledge Aggregation Platform.
"""

import os
import uuid
import logging
import logging.handlers
from typing import Dict, Any, Optional


def setup_logging(config: Dict[str, Any]) -> None:
    """Configure logging based on the provided configuration.
    
    Args:
        config: Logging configuration dictionary
    """
    log_level = getattr(logging, config.get('level', 'INFO').upper())
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = config.get('file')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Always add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)
    
    # Add a file handler if a log file is specified
    if log_file:
        # Create the directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Configure a rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)


def generate_id(prefix: str = '') -> str:
    """Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        A unique ID string
    """
    return f"{prefix}{uuid.uuid4().hex}"


def build_task_id(task_type: str) -> str:
    """Build a task ID based on the task type.
    
    Args:
        task_type: Type of task (e.g., 'scrape', 'process')
        
    Returns:
        A unique task ID
    """
    prefix_map = {
        'scrape': 'scr',
        'process': 'prc',
        'knowledge': 'knw',
        'learning': 'lrn',
        'ui': 'ui'
    }
    
    prefix = prefix_map.get(task_type, 'tsk')
    return generate_id(f"{prefix}-")


def safe_dict_get(d: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Safely get a nested value from a dictionary using dot notation.
    
    Args:
        d: Dictionary to get value from
        key_path: Path to the value using dot notation (e.g., 'a.b.c')
        default: Default value to return if the key doesn't exist
        
    Returns:
        The value at the specified path or the default value
    """
    if not d or not key_path:
        return default
        
    keys = key_path.split('.')
    result = d
    
    for key in keys:
        if not isinstance(result, dict) or key not in result:
            return default
        result = result[key]
        
    return result 