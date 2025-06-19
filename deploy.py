#!/usr/bin/env python3
"""
Production deployment script for the Knowledge Integration System.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

class ProductionDeployer:
    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent
        
    def build_frontend(self):
        """Build the frontend for production."""
        print("🏗️  Building frontend for production...")
        
        frontend_dir = self.project_root / "frontend"
        
        # Install dependencies
        print("📦 Installing frontend dependencies...")
        npm_install = subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        
        if npm_install.returncode != 0:
            print(f"❌ Failed to install frontend dependencies: {npm_install.stderr}")
            return False
            
        # Build for production
        print("🔨 Building frontend...")
        npm_build = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        
        if npm_build.returncode != 0:
            print(f"❌ Frontend build failed: {npm_build.stderr}")
            return False
            
        print("✅ Frontend built successfully")
        return True
        
    def start_backend(self):
        """Start the backend coordinator service."""
        print("🚀 Starting backend coordinator...")
        
        backend_cmd = [
            "python3", "-m", "coordinator.main",
            "--host", "0.0.0.0",
            "--port", "3100",
            "--log-level", "INFO"
        ]
        
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        self.processes.append(("Backend", backend_process))
        print("✅ Backend coordinator started on http://localhost:3100")
        return backend_process
        
    def start_frontend_production(self):
        """Start the frontend in production mode."""
        print("🎨 Starting frontend in production mode...")
        
        frontend_dir = self.project_root / "frontend"
        
        # Start Next.js production server
        frontend_cmd = ["npm", "run", "start"]
        
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        self.processes.append(("Frontend", frontend_process))
        print("✅ Frontend application started on http://localhost:3000")
        return frontend_process
        
    def wait_for_services(self):
        """Wait for services to be ready."""
        print("⏳ Waiting for services to be ready...")
        
        # Give services time to start
        time.sleep(5)
        
        # Check if processes are still running
        for name, process in self.processes:
            if process.poll() is not None:
                print(f"❌ {name} process exited unexpectedly")
                return False
                
        print("✅ All services are running")
        return True
        
    def test_deployment(self):
        """Test if the deployment is working."""
        print("🧪 Testing deployment...")
        
        try:
            # Test backend health
            import requests
            backend_response = requests.get("http://localhost:3100/health", timeout=10)
            if backend_response.status_code == 200:
                print("✅ Backend health check passed")
            else:
                print(f"❌ Backend health check failed: {backend_response.status_code}")
                return False
                
            # Test frontend
            frontend_response = requests.get("http://localhost:3000", timeout=10)
            if frontend_response.status_code == 200:
                print("✅ Frontend health check passed")
            else:
                print(f"⚠️  Frontend returned status: {frontend_response.status_code}")
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
            
        return True
        
    def monitor_processes(self):
        """Monitor running processes."""
        print("\n" + "="*60)
        print("🖥️  PRODUCTION DEPLOYMENT MONITORING - Press Ctrl+C to stop")
        print("="*60)
        
        try:
            while True:
                # Check if all processes are still running
                running_processes = []
                for name, process in self.processes:
                    if process.poll() is None:
                        running_processes.append((name, process))
                    else:
                        print(f"⚠️  {name} process has stopped")
                
                if not running_processes:
                    print("❌ All processes have stopped")
                    break
                    
                self.processes = running_processes
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown signal received")
            self.cleanup()
            
    def cleanup(self):
        """Clean up all running processes."""
        print("🧹 Cleaning up processes...")
        
        for name, process in self.processes:
            if process.poll() is None:
                print(f"   Stopping {name}...")
                try:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        print(f"   ✅ {name} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                        print(f"   ⚡ {name} force stopped")
                except Exception as e:
                    print(f"   ❌ Error stopping {name}: {e}")
        
        print("✅ Cleanup complete")
        
    def deploy(self):
        """Deploy the complete system in production mode."""
        print("🚀 PRODUCTION DEPLOYMENT")
        print("="*50)
        
        try:
            # Build frontend
            if not self.build_frontend():
                return False
                
            # Start backend
            backend_process = self.start_backend()
            if not backend_process:
                return False
                
            # Start frontend in production mode
            frontend_process = self.start_frontend_production()
            if not frontend_process:
                self.cleanup()
                return False
                
            # Wait for services to be ready
            if not self.wait_for_services():
                self.cleanup()
                return False
                
            # Test deployment
            if not self.test_deployment():
                print("⚠️  Deployment tests failed, but services are running")
                
            # Display deployment information
            print("\n" + "="*50)
            print("🎉 PRODUCTION DEPLOYMENT COMPLETE")
            print("="*50)
            print("📍 Backend API: http://localhost:3100")
            print("📍 Frontend App: http://localhost:3000")
            print("📍 API Documentation: http://localhost:3100/docs")
            print("📍 Health Check: http://localhost:3100/health")
            print("\n🔐 Demo Login Credentials:")
            print("   Email: admin@example.com")
            print("   Password: password")
            print("\n📊 Features Available:")
            print("   • Document Upload (PDF, Word, Excel)")
            print("   • Knowledge Search & Analysis")
            print("   • AI-Powered Content Processing")
            print("   • Real-time Visualization")
            
            # Monitor processes
            self.monitor_processes()
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            self.cleanup()
            return False

def main():
    """Main entry point."""
    deployer = ProductionDeployer()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Interrupt received, shutting down...")
        deployer.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 