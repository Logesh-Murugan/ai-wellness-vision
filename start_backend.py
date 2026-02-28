#!/usr/bin/env python3
"""
Simple script to start the AI Wellness Vision backend server
"""

import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'python-multipart',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def start_server():
    """Start the backend server"""
    print("\n🚀 Starting AI Wellness Vision Backend Server...")
    
    # Check if main_api_server.py exists
    if not Path("main_api_server.py").exists():
        print("❌ main_api_server.py not found!")
        return False
    
    try:
        # Start the server
        print("📡 Server starting on http://localhost:8000")
        print("📖 API docs will be available at http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/health")
        print("\n💡 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main_api_server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def test_server():
    """Test if server is running"""
    print("\n🔍 Testing server...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is running and healthy!")
                print(f"📡 Server URL: http://localhost:8000")
                print(f"📖 API Docs: http://localhost:8000/docs")
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            print(f"⏳ Waiting for server... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
    
    print("❌ Server is not responding")
    return False

def main():
    """Main function"""
    print("🏥 AI Wellness Vision Backend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return 1
    
    # Start server
    if not start_server():
        print("❌ Failed to start server")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())