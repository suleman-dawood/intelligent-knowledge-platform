#!/usr/bin/env python3
"""
Environment Validation Script for Intelligent Knowledge Platform
This script validates all environment variables and tests connections to external services.
"""

import os
import sys
import asyncio
import aiohttp
import socket
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from coordinator.config import load_config
from coordinator.llm_client import DeepSeekLLMClient


@dataclass
class ValidationResult:
    """Result of a validation check."""
    service: str
    status: str  # 'pass', 'fail', 'warning'
    message: str
    details: Optional[str] = None


class EnvironmentValidator:
    """Validates environment configuration and service connections."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.config = None
        
    def add_result(self, service: str, status: str, message: str, details: str = None):
        """Add a validation result."""
        self.results.append(ValidationResult(service, status, message, details))
        
    def print_results(self):
        """Print all validation results."""
        print("\n" + "="*80)
        print("🔍 ENVIRONMENT VALIDATION RESULTS")
        print("="*80)
        
        passed = failed = warnings = 0
        
        for result in self.results:
            if result.status == 'pass':
                icon = "✅"
                passed += 1
            elif result.status == 'fail':
                icon = "❌"
                failed += 1
            else:
                icon = "⚠️"
                warnings += 1
                
            print(f"{icon} {result.service}: {result.message}")
            if result.details:
                print(f"   Details: {result.details}")
                
        print("\n" + "-"*80)
        print(f"Summary: {passed} passed, {failed} failed, {warnings} warnings")
        
        if failed > 0:
            print("\n❌ VALIDATION FAILED - Please fix the issues above before running the platform.")
            return False
        elif warnings > 0:
            print("\n⚠️  VALIDATION PASSED WITH WARNINGS - Platform should work but some features may be limited.")
            return True
        else:
            print("\n✅ ALL VALIDATIONS PASSED - Platform is ready to run!")
            return True
    
    def validate_environment_file(self):
        """Validate .env file exists and has required variables."""
        if not os.path.exists('.env'):
            self.add_result(
                "Environment File", 
                "fail", 
                ".env file not found",
                "Run: cp config.env.example .env"
            )
            return False
            
        self.add_result("Environment File", "pass", ".env file found")
        return True
    
    def validate_config_loading(self):
        """Validate configuration can be loaded."""
        try:
            self.config = load_config()
            self.add_result("Configuration", "pass", "Configuration loaded successfully")
            return True
        except Exception as e:
            self.add_result(
                "Configuration", 
                "fail", 
                "Failed to load configuration",
                str(e)
            )
            return False
    
    def validate_deepseek_api_key(self):
        """Validate DeepSeek API key."""
        if not self.config:
            return False
            
        api_key = self.config.get('llm', {}).get('deepseek_api_key', '')
        
        if not api_key:
            self.add_result(
                "DeepSeek API Key", 
                "fail", 
                "DeepSeek API key not set",
                "Get key from: https://platform.deepseek.com/"
            )
            return False
        elif api_key == "your_deepseek_api_key_here":
            self.add_result(
                "DeepSeek API Key", 
                "fail", 
                "DeepSeek API key is placeholder value",
                "Replace with actual key from: https://platform.deepseek.com/"
            )
            return False
        elif not api_key.startswith('sk-'):
            self.add_result(
                "DeepSeek API Key", 
                "warning", 
                "DeepSeek API key format looks unusual",
                "Verify key format is correct"
            )
            return True
        else:
            self.add_result("DeepSeek API Key", "pass", "DeepSeek API key is set")
            return True
    
    async def test_deepseek_connection(self):
        """Test connection to DeepSeek API."""
        if not self.config:
            return False
            
        try:
            llm_client = DeepSeekLLMClient(self.config)
            response = await llm_client.chat_completion(
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            
            if response:
                self.add_result("DeepSeek API", "pass", "DeepSeek API connection successful")
                return True
            else:
                self.add_result("DeepSeek API", "fail", "DeepSeek API returned empty response")
                return False
                
        except Exception as e:
            self.add_result(
                "DeepSeek API", 
                "fail", 
                "DeepSeek API connection failed",
                str(e)
            )
            return False
    
    def test_port_connection(self, host: str, port: int, service_name: str) -> bool:
        """Test if a port is accessible."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self.add_result(f"{service_name} Port", "pass", f"Port {port} is accessible")
                return True
            else:
                self.add_result(
                    f"{service_name} Port", 
                    "fail", 
                    f"Port {port} is not accessible",
                    f"Ensure {service_name} is running on {host}:{port}"
                )
                return False
        except Exception as e:
            self.add_result(
                f"{service_name} Port", 
                "fail", 
                f"Failed to test port {port}",
                str(e)
            )
            return False
    
    def validate_database_config(self):
        """Validate database configuration."""
        if not self.config:
            return False
            
        # Neo4j
        neo4j_config = self.config.get('databases', {}).get('neo4j', {})
        neo4j_uri = neo4j_config.get('uri', '')
        if neo4j_uri:
            self.add_result("Neo4j Config", "pass", "Neo4j URI configured")
            # Extract host and port for connection test
            if 'localhost' in neo4j_uri or '127.0.0.1' in neo4j_uri:
                self.test_port_connection('localhost', 7687, 'Neo4j')
        else:
            self.add_result("Neo4j Config", "fail", "Neo4j URI not configured")
            
        # MongoDB
        mongodb_config = self.config.get('databases', {}).get('mongodb', {})
        mongodb_uri = mongodb_config.get('uri', '')
        if mongodb_uri:
            self.add_result("MongoDB Config", "pass", "MongoDB URI configured")
            if 'localhost' in mongodb_uri or '127.0.0.1' in mongodb_uri:
                self.test_port_connection('localhost', 27017, 'MongoDB')
        else:
            self.add_result("MongoDB Config", "fail", "MongoDB URI not configured")
            
        # Redis
        redis_config = self.config.get('databases', {}).get('redis', {})
        redis_host = redis_config.get('host', 'localhost')
        redis_port = redis_config.get('port', 6379)
        if redis_host and redis_port:
            self.add_result("Redis Config", "pass", "Redis configuration found")
            if redis_host in ['localhost', '127.0.0.1']:
                self.test_port_connection(redis_host, redis_port, 'Redis')
        else:
            self.add_result("Redis Config", "fail", "Redis configuration incomplete")
            
        # RabbitMQ
        rabbitmq_config = self.config.get('message_broker', {})
        rabbitmq_host = rabbitmq_config.get('host', 'localhost')
        rabbitmq_port = rabbitmq_config.get('port', 5672)
        if rabbitmq_host and rabbitmq_port:
            self.add_result("RabbitMQ Config", "pass", "RabbitMQ configuration found")
            if rabbitmq_host in ['localhost', '127.0.0.1']:
                self.test_port_connection(rabbitmq_host, rabbitmq_port, 'RabbitMQ')
        else:
            self.add_result("RabbitMQ Config", "fail", "RabbitMQ configuration incomplete")
    
    def validate_python_dependencies(self):
        """Validate Python dependencies."""
        required_packages = [
            'fastapi', 'uvicorn', 'pika', 'neo4j', 'pymongo', 'redis', 
            'nltk', 'openai', 'httpx', 'PyPDF2', 'pdfplumber', 'arxiv', 
            'scholarly', 'bibtexparser', 'beautifulsoup4', 'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.add_result(
                "Python Dependencies", 
                "fail", 
                f"Missing packages: {', '.join(missing_packages)}",
                "Run: pip install -r requirements.txt"
            )
            return False
        else:
            self.add_result("Python Dependencies", "pass", "All Python dependencies installed")
            return True
    
    def validate_frontend_setup(self):
        """Validate frontend setup."""
        if not os.path.exists('frontend/package.json'):
            self.add_result("Frontend Setup", "fail", "Frontend package.json not found")
            return False
            
        if not os.path.exists('frontend/node_modules'):
            self.add_result(
                "Frontend Dependencies", 
                "fail", 
                "Frontend dependencies not installed",
                "Run: cd frontend && npm install"
            )
            return False
        else:
            self.add_result("Frontend Dependencies", "pass", "Frontend dependencies installed")
            
        # Check if Next.js config exists
        if os.path.exists('frontend/next.config.js'):
            self.add_result("Frontend Config", "pass", "Next.js configuration found")
        else:
            self.add_result("Frontend Config", "warning", "Next.js configuration not found")
            
        return True
    
    def provide_setup_recommendations(self):
        """Provide setup recommendations based on validation results."""
        print("\n" + "="*80)
        print("📋 SETUP RECOMMENDATIONS")
        print("="*80)
        
        # Check if Docker is available
        try:
            import subprocess
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker is available")
                print("💡 Recommended: Use 'docker-compose up -d' to start all infrastructure services")
            else:
                print("❌ Docker is not available")
                print("💡 Consider installing Docker Desktop for easier setup")
        except FileNotFoundError:
            print("❌ Docker is not installed")
            print("💡 Download Docker Desktop: https://www.docker.com/products/docker-desktop/")
        
        print("\n📚 Quick Start Commands:")
        print("1. Set up environment: ./setup.sh (Linux/Mac) or setup.bat (Windows)")
        print("2. Start infrastructure: docker-compose up -d")
        print("3. Start backend: python run_local.py")
        print("4. Start frontend: cd frontend && npm run dev")
        print("5. Open browser: http://localhost:3000")
        
        print("\n🆘 Need help? Check DEPLOYMENT.md for detailed instructions")
    
    async def run_all_validations(self):
        """Run all validation checks."""
        print("🔍 Starting environment validation...")
        
        # Basic validations
        self.validate_environment_file()
        self.validate_config_loading()
        self.validate_deepseek_api_key()
        self.validate_python_dependencies()
        self.validate_frontend_setup()
        self.validate_database_config()
        
        # Async validations
        if self.config and self.config.get('llm', {}).get('deepseek_api_key'):
            await self.test_deepseek_connection()
        
        # Print results
        success = self.print_results()
        
        # Provide recommendations
        self.provide_setup_recommendations()
        
        return success


async def main():
    """Main validation function."""
    validator = EnvironmentValidator()
    success = await validator.run_all_validations()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main()) 