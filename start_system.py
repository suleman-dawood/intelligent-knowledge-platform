#!/usr/bin/env python3
"""
System startup script for the Knowledge Integration System.
Launches both backend and frontend services.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

class SystemLauncher:
    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent
        
    def start_backend(self):
        """Start the backend coordinator service."""
        print("🚀 Starting backend coordinator...")
        
        # Change to project directory and start coordinator
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
        
    def start_frontend(self):
        """Start the frontend Next.js application."""
        print("🎨 Starting frontend application...")
        
        frontend_dir = self.project_root / "frontend"
        
        # Install dependencies if needed
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            npm_install = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            
            if npm_install.returncode != 0:
                print(f"❌ Failed to install frontend dependencies: {npm_install.stderr}")
                return None
        
        # Start Next.js development server
        frontend_cmd = ["npm", "run", "dev"]
        
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
        time.sleep(3)
        
        # Check if processes are still running
        for name, process in self.processes:
            if process.poll() is not None:
                print(f"❌ {name} process exited unexpectedly")
                return False
                
        print("✅ All services are running")
        return True
        
    def monitor_processes(self):
        """Monitor running processes and display logs."""
        print("\n" + "="*60)
        print("🖥️  SYSTEM MONITORING - Press Ctrl+C to stop all services")
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
                time.sleep(5)
                
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
                    # Send SIGTERM first
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                        print(f"   ✅ {name} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        # Force kill if needed
                        process.kill()
                        process.wait()
                        print(f"   ⚡ {name} force stopped")
                        
                except Exception as e:
                    print(f"   ❌ Error stopping {name}: {e}")
        
        print("✅ Cleanup complete")
        
    def start_system(self):
        """Start the complete system."""
        print("🎯 Knowledge Integration System Launcher")
        print("="*50)
        
        try:
            # Start backend
            backend_process = self.start_backend()
            if not backend_process:
                return False
                
            # Start frontend
            frontend_process = self.start_frontend()
            if not frontend_process:
                self.cleanup()
                return False
                
            # Wait for services to be ready
            if not self.wait_for_services():
                self.cleanup()
                return False
                
            # Display startup information
            print("\n" + "="*50)
            print("🎉 SYSTEM STARTUP COMPLETE")
            print("="*50)
            print("📍 Backend API: http://localhost:3100")
            print("📍 Frontend App: http://localhost:3000")
            print("📍 API Documentation: http://localhost:3100/docs")
            print("📍 Health Check: http://localhost:3100/health")
            print("\n🔐 Demo Login Credentials:")
            print("   Email: admin@example.com")
            print("   Password: password")
            print("\n📊 To run system tests:")
            print("   python test_system.py")
            
            # Monitor processes
            self.monitor_processes()
            
            return True
            
        except Exception as e:
            print(f"❌ System startup failed: {e}")
            self.cleanup()
            return False

def main():
    """Main entry point."""
    launcher = SystemLauncher()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Interrupt received, shutting down...")
        launcher.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    success = launcher.start_system()
    
    if success:
        print("\n🎯 System shutdown complete")
        sys.exit(0)
    else:
        print("\n❌ System startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 