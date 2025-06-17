#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration module for the Intelligent Knowledge Aggregation Platform.
Handles loading configuration from environment variables and config files.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from environment variables and optionally from a config file.
    
    Args:
        config_path: Path to a JSON configuration file (optional)
        
    Returns:
        Dictionary containing the configuration
    """
    # Start with default configuration
    config = {
        "api": {
            "host": os.getenv("API_HOST", "localhost"),
            "port": int(os.getenv("API_PORT", "3100"))
        },
        "rabbitmq": {
            "host": os.getenv("RABBITMQ_HOST", "localhost"),
            "port": int(os.getenv("RABBITMQ_PORT", "5672")),
            "user": os.getenv("RABBITMQ_USER", "guest"),
            "password": os.getenv("RABBITMQ_PASSWORD", "guest")
        },
        "databases": {
            "neo4j": {
                "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "password")
            },
            "mongodb": {
                "uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
                "db": os.getenv("MONGODB_DB", "knowledge_platform")
            },
            "redis": {
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "db": int(os.getenv("REDIS_DB", "0"))
            },
            "vector_db": {
                "host": os.getenv("VECTOR_DB_HOST", "localhost"),
                "port": int(os.getenv("VECTOR_DB_PORT", "8080"))
            }
        },
        "agents": {
            "max_scraper_agents": int(os.getenv("MAX_SCRAPER_AGENTS", "3")),
            "max_processor_agents": int(os.getenv("MAX_PROCESSOR_AGENTS", "3")),
            "max_knowledge_agents": int(os.getenv("MAX_KNOWLEDGE_AGENTS", "2")),
            "max_learning_agents": int(os.getenv("MAX_LEARNING_AGENTS", "2")),
            "max_ui_agents": int(os.getenv("MAX_UI_AGENTS", "1"))
        },
        "llm": {
            "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "deepseek_base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        },
        "logging": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": os.getenv("LOG_FILE", None)
        }
    }
    
    # If a config file is provided, load and merge it
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                
            # Deep merge the file config with the default config
            _deep_merge(config, file_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
    
    return config


def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries.
    
    Args:
        base: Base dictionary that will be updated
        update: Dictionary with values to update in the base
        
    Returns:
        Updated base dictionary
    """
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base 