#!/usr/bin/env python3
"""
AI Wellness Vision - Simple Project Launcher
Handles common Windows issues and starts available services
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_header():
    """Print simple header without Unicode"""
    print("=" * 60)
    print("AI WELLNESS VISION - PROJECT LAUNCHER")
    print("=" * 60)
    print()

def kill_port(port):
    """Kill process using a specific port on Windows"""
    try:
        # Find process using the port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True, capture_output=True, text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"Killing process {pid} on port {port}")
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                        time.sleep(1)
                        return True
        return False
    except Exception as e:
        print(f"Error killing port {port}: {e}")
        return False

def start_backend():
    """Start the backend API server"""
    print("Starting Backend API Server...")
    
    # Kill any existing process on port 8000
    kill_port(8000)
    
    try:
        # Set environment to handle Unicode properly
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        process = subprocess.Popen([
            sys.executable, 'main_api_server.py'
        ], env=env, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        # Wait to see if it starts
        time.sleep(3)
        
        # Check if port is now in use (indicates success)
        result = subprocess.run(
            'netstat -an | findstr :8000',
            shell=True, capture_output=True, text=True
        )
        
        if ':8000' in result.stdout:
            print("✓ Backend API Server started on http://localhost:8000")
            return process
        else:
            print("✗ Backend failed to start")
            return None
            
    except Exception as e:
        print(f"✗ Error starting backend: {e}")
        return None

def start_streamlit():
    """Start Streamlit web interface"""
    print("Starting Streamlit Web Interface...")
    
    # Kill any existing process on port 8501
    kill_port(8501)
    
    try:
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.port=8501', '--server.headless=true'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        time.sleep(5)
        
        # Check if port is now in use
        result = subprocess.run(
            'netstat -an | findstr :8501',
            shell=True, capture_output=True, text=True
        )
        
        if ':8501' in result.stdout:
            print("✓ Streamlit Web Interface started on http://localhost:8501")
            return process
        else:
            print("✗ Streamlit failed to start")
            return None
            
    except Exception as e:
        print(f"✗ Error starting Streamlit: {e}")
        return None

def check_flutter():
    """Check if Flutter is available"""
    try:
        result = subprocess.run(['flutter', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def start_flutter():
    """Start Flutter web app if available"""
    if not check_flutter():
        print("✗ Flutter not installed - skipping mobile app")
        print("  Install Flutter from: https://flutter.dev/docs/get-started/install")
        return None
    
    print("Starting Flutter Web App...")
    
    flutter_dir = Path("flutter_app")
    if not flutter_dir.exists():
        print("✗ Flutter app directory not found")
        return None
    
    # Kill any existing process on port 8080
    kill_port(8080)
    
    try:
        # Get dependencies first
        subprocess.run(['flutter', 'pub', 'get'], 
                      cwd=flutter_dir, check=True, timeout=30)
        
        # Start Flutter web
        process = subprocess.Popen([
            'flutter', 'run', '-d', 'chrome', '--web-port=8080'
        ], cwd=flutter_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        time.sleep(8)
        
        # Check if port is now in use
        result = subprocess.run(
            'netstat -an | findstr :8080',
            shell=True, capture_output=True, text=True
        )
        
        if ':8080' in result.stdout:
            print("✓ Flutter Web App started on http://localhost:8080")
            return process
        else:
            print("✗ Flutter failed to start")
            return None
            
    except Exception as e:
        print(f"✗ Error starting Flutter: {e}")
        return None

def open_browsers():
    """Open browsers for running services"""
    print("\nOpening web browsers...")
    time.sleep(2)
    
    # Check which services are running and open browsers
    services = [
        (8000, "Backend API", "http://localhost:8000/docs"),
        (8501, "Streamlit Web", "http://localhost:8501"),
        (8080, "Flutter Mobile", "http://localhost:8080")
    ]
    
    for port, name, url in services:
        result = subprocess.run(
            f'netstat -an | findstr :{port}',
            shell=True, capture_output=True, text=True
        )
        
        if f':{port}' in result.stdout:
            try:
                webbrowser.open(url)
                print(f"✓ Opened {name}: {url}")
            except:
                print(f"✗ Could not open browser for {name}")

def main():
    """Main launcher function"""
    print_header()
    
    print("Checking and starting services...")
    print()
    
    # Start services
    backend = start_backend()
    streamlit = start_streamlit()
    flutter = start_flutter()
    
    # Count running services
    running = sum(1 for service in [backend, streamlit, flutter] if service is not None)
    
    print()
    print("=" * 60)
    print(f"STARTUP COMPLETE - {running} services running")
    print("=" * 60)
    
    if running > 0:
        print("Available services:")
        if backend:
            print("  • Backend API:      http://localhost:8000")
            print("  • API Docs:         http://localhost:8000/docs")
        if streamlit:
            print("  • Streamlit Web:    http://localhost:8501")
        if flutter:
            print("  • Flutter Mobile:   http://localhost:8080")
        
        print()
        print("Features available:")
        print("  • Health Chat with Gemini AI")
        print("  • Image Analysis (Skin, Food, Eye, Wellness)")
        print("  • User Authentication")
        print("  • Analysis History")
        print("  • Voice Processing")
        
        # Open browsers
        open_browsers()
        
        print()
        print("Press Ctrl+C to stop all services...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down services...")
            
    else:
        print("No services could be started.")
        print("Check the error messages above for troubleshooting.")

if __name__ == "__main__":
    main()