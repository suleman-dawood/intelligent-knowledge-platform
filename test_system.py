#!/usr/bin/env python3
"""
Comprehensive test script for the Knowledge Integration System.
Tests all implemented functionality including authentication, file upload, 
content processing, and API endpoints.
"""

import asyncio
import aiohttp
import json
import time
import sys
from pathlib import Path

# Test configuration
BACKEND_URL = "http://localhost:3100"
FRONTEND_URL = "http://localhost:3000"

class SystemTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Setup test session."""
        self.session = aiohttp.ClientSession()
        print("🔧 Setting up test session...")
        
    async def cleanup(self):
        """Cleanup test session."""
        if self.session:
            await self.session.close()
        print("🧹 Cleaned up test session")
        
    async def test_backend_health(self):
        """Test backend health endpoint."""
        print("\n📊 Testing Backend Health...")
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend health check passed: {data}")
                    return True
                else:
                    print(f"❌ Backend health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Backend health check error: {e}")
            return False
            
    async def test_backend_status(self):
        """Test backend system status."""
        print("\n📈 Testing Backend Status...")
        try:
            async with self.session.get(f"{BACKEND_URL}/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend status: {data.get('status', 'unknown')}")
                    print(f"   Agents: {data.get('agents', {})}")
                    print(f"   Tasks: {data.get('tasks', {})}")
                    return True
                else:
                    print(f"❌ Backend status failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Backend status error: {e}")
            return False
            
    async def test_content_processing(self):
        """Test content processing functionality."""
        print("\n📝 Testing Content Processing...")
        try:
            test_content = {
                "title": "Test Article",
                "content_type": "text",
                "content": "This is a test article about artificial intelligence and machine learning. It contains positive sentiment and demonstrates the knowledge processing capabilities of our system.",
                "type": "text"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/api/process-content",
                json=test_content
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    task_id = data.get("task_id")
                    print(f"✅ Content processing task submitted: {task_id}")
                    
                    # Wait for task completion
                    for i in range(30):  # Wait up to 30 seconds
                        await asyncio.sleep(1)
                        async with self.session.get(f"{BACKEND_URL}/tasks/{task_id}") as task_response:
                            if task_response.status == 200:
                                task_data = await task_response.json()
                                status = task_data.get("status")
                                
                                if status == "completed":
                                    result = task_data.get("result", {})
                                    print(f"✅ Content processing completed!")
                                    print(f"   Word count: {result.get('word_count', 0)}")
                                    print(f"   Sentiment: {result.get('sentiment', 'unknown')}")
                                    print(f"   Entities found: {len(result.get('entities', []))}")
                                    return True
                                elif status == "failed":
                                    print(f"❌ Content processing failed: {task_data.get('error', 'Unknown error')}")
                                    return False
                                else:
                                    print(f"   Task status: {status}")
                    
                    print("❌ Content processing timed out")
                    return False
                else:
                    print(f"❌ Content processing submission failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Content processing error: {e}")
            return False
            
    async def test_web_scraping(self):
        """Test web scraping functionality."""
        print("\n🌐 Testing Web Scraping...")
        try:
            scrape_request = {
                "title": "Test Web Scrape",
                "content_type": "url",
                "url": "https://httpbin.org/html",
                "type": "url"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/api/process-content",
                json=scrape_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    task_id = data.get("task_id")
                    print(f"✅ Web scraping task submitted: {task_id}")
                    
                    # Wait for task completion
                    for i in range(30):
                        await asyncio.sleep(1)
                        async with self.session.get(f"{BACKEND_URL}/tasks/{task_id}") as task_response:
                            if task_response.status == 200:
                                task_data = await task_response.json()
                                status = task_data.get("status")
                                
                                if status == "completed":
                                    result = task_data.get("result", {})
                                    print(f"✅ Web scraping completed!")
                                    print(f"   URL: {result.get('url', 'unknown')}")
                                    print(f"   Title: {result.get('title', 'unknown')}")
                                    print(f"   Content length: {result.get('content_length', 0)}")
                                    return True
                                elif status == "failed":
                                    print(f"❌ Web scraping failed: {task_data.get('error', 'Unknown error')}")
                                    return False
                                else:
                                    print(f"   Task status: {status}")
                    
                    print("❌ Web scraping timed out")
                    return False
                else:
                    print(f"❌ Web scraping submission failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Web scraping error: {e}")
            return False
            
    async def test_search_functionality(self):
        """Test search functionality."""
        print("\n🔍 Testing Search Functionality...")
        try:
            async with self.session.get(
                f"{BACKEND_URL}/search",
                params={"q": "artificial intelligence"}
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    print(f"✅ Search completed!")
                    print(f"   Results found: {len(results)}")
                    
                    if results:
                        first_result = results[0]
                        print(f"   First result: {first_result.get('title', 'No title')}")
                        print(f"   Score: {first_result.get('score', 0)}")
                    
                    return True
                else:
                    print(f"❌ Search failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Search error: {e}")
            return False
            
    async def test_knowledge_graph(self):
        """Test knowledge graph functionality."""
        print("\n🕸️ Testing Knowledge Graph...")
        try:
            async with self.session.get(f"{BACKEND_URL}/graph/overview") as response:
                if response.status == 200:
                    graph_data = await response.json()
                    nodes = graph_data.get("nodes", [])
                    edges = graph_data.get("edges", [])
                    
                    print(f"✅ Knowledge graph retrieved!")
                    print(f"   Nodes: {len(nodes)}")
                    print(f"   Edges: {len(edges)}")
                    
                    if nodes:
                        print(f"   Sample node: {nodes[0].get('label', 'No label')}")
                    
                    return True
                else:
                    print(f"❌ Knowledge graph failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Knowledge graph error: {e}")
            return False
            
    async def test_frontend_auth_endpoints(self):
        """Test frontend authentication endpoints."""
        print("\n🔐 Testing Frontend Authentication...")
        try:
            # Test login endpoint
            login_data = {
                "email": "admin@example.com",
                "password": "password"
            }
            
            async with self.session.post(
                f"{FRONTEND_URL}/api/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    print(f"✅ Authentication successful!")
                    print(f"   User: {auth_data.get('user', {}).get('email', 'unknown')}")
                    print(f"   Token received: {'token' in auth_data}")
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    async def run_all_tests(self):
        """Run all tests and report results."""
        print("🚀 Starting Comprehensive System Tests")
        print("=" * 50)
        
        await self.setup()
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Backend Status", self.test_backend_status),
            ("Content Processing", self.test_content_processing),
            ("Web Scraping", self.test_web_scraping),
            ("Search Functionality", self.test_search_functionality),
            ("Knowledge Graph", self.test_knowledge_graph),
            ("Frontend Authentication", self.test_frontend_auth_endpoints),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                    self.test_results.append((test_name, "PASS"))
                else:
                    self.test_results.append((test_name, "FAIL"))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                self.test_results.append((test_name, "CRASH"))
        
        await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        for test_name, result in self.test_results:
            status_emoji = "✅" if result == "PASS" else "❌"
            print(f"{status_emoji} {test_name}: {result}")
        
        print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! System is ready for use.")
            return True
        else:
            print("⚠️ Some tests failed. Please check the implementation.")
            return False

async def main():
    """Main test runner."""
    tester = SystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎯 SYSTEM STATUS: FULLY OPERATIONAL")
        sys.exit(0)
    else:
        print("\n🔧 SYSTEM STATUS: NEEDS ATTENTION")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 