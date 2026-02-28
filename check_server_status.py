#!/usr/bin/env python3
"""
Quick server status check
"""

import requests
import json

def check_server_status():
    """Check if the CNN server is running"""
    
    print("🔍 Checking CNN API Server Status...")
    print("=" * 40)
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is RUNNING")
            print(f"   Message: {data.get('message', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   CNN Available: {data.get('cnn_available', 'Unknown')}")
            
            # Test health endpoint
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"   Health Status: {health_data.get('status', 'Unknown')}")
                
                services = health_data.get('services', {})
                for service, status in services.items():
                    print(f"   {service}: {status}")
            
            print("\n🌐 Available Endpoints:")
            print("   • API Base: http://localhost:8000")
            print("   • Documentation: http://localhost:8000/docs")
            print("   • Health Check: http://localhost:8000/health")
            print("   • Model Info: http://localhost:8000/api/v1/models/info")
            
            return True
            
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is NOT RUNNING")
        print("\n🚀 To start the server, run:")
        print("   python start_cnn_server.py")
        print("   OR")
        print("   start_server.bat")
        return False
        
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    check_server_status()