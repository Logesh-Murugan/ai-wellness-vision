#!/usr/bin/env python3
"""
Simple CNN Server Starter
"""

import subprocess
import sys
import time
import requests
import os

def start_server():
    """Start the CNN API server"""
    print("🚀 Starting CNN API Server...")
    
    try:
        # Start server
        process = subprocess.Popen([
            sys.executable, 'main_api_server_cnn.py'
        ])
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        
        for i in range(20):
            try:
                response = requests.get("http://localhost:8000/", timeout=2)
                if response.status_code == 200:
                    print("✅ Server started successfully!")
                    print("🌐 API available at: http://localhost:8000")
                    print("📖 Documentation at: http://localhost:8000/docs")
                    print("🏥 Health check at: http://localhost:8000/health")
                    print("\nPress Ctrl+C to stop the server...")
                    return process
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
            print(f"   Waiting... ({i+1}/20)")
        
        print("❌ Server failed to start within 40 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def main():
    """Main function"""
    print("=" * 50)
    print("CNN API SERVER STARTER")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    
    if server_process:
        try:
            # Keep server running
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")
    else:
        print("❌ Failed to start server")
        return False
    
    return True

if __name__ == "__main__":
    main()