#!/usr/bin/env python3
"""
AI Wellness Vision - Full Project Launcher
This script starts all components of the AI Wellness Vision project
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path
import webbrowser

def print_banner():
    """Print project banner"""
    print("=" * 80)
    print("🏥 AI WELLNESS VISION - FULL PROJECT LAUNCHER")
    print("=" * 80)
    print("🚀 Starting all project components...")
    print()

def check_requirements():
    """Check if all requirements are installed"""
    print("📋 Checking requirements...")
    
    # Check Python packages
    required_packages = [
        'fastapi', 'uvicorn', 'google-generativeai', 
        'python-dotenv', 'streamlit', 'psycopg2-binary'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️ Installing missing packages: {', '.join(missing_packages)}")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
    
    # Check Flutter
    try:
        result = subprocess.run(['flutter', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Flutter SDK")
        else:
            print("❌ Flutter SDK - Please install Flutter")
    except FileNotFoundError:
        print("❌ Flutter SDK - Please install Flutter")
    
    print()

def start_backend():
    """Start the FastAPI backend server"""
    print("🔧 Starting Backend API Server...")
    try:
        # Start the main API server
        process = subprocess.Popen([
            sys.executable, 'main_api_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment to check if it started successfully
        time.sleep(3)
        if process.poll() is None:
            print("✅ Backend API Server started on http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_streamlit():
    """Start the Streamlit web interface"""
    print("🌐 Starting Streamlit Web Interface...")
    try:
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py', 
            '--server.port=8501', '--server.headless=true'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        time.sleep(5)
        if process.poll() is None:
            print("✅ Streamlit Web Interface started on http://localhost:8501")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return None

def start_flutter():
    """Start the Flutter mobile app"""
    print("📱 Starting Flutter Mobile App...")
    try:
        # Change to flutter_app directory
        flutter_dir = Path("flutter_app")
        if not flutter_dir.exists():
            print("❌ Flutter app directory not found")
            return None
        
        # Get Flutter dependencies
        print("📦 Getting Flutter dependencies...")
        subprocess.run(['flutter', 'pub', 'get'], cwd=flutter_dir, check=True)
        
        # Start Flutter app
        process = subprocess.Popen([
            'flutter', 'run', '-d', 'chrome', '--web-port=8080'
        ], cwd=flutter_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        time.sleep(10)
        if process.poll() is None:
            print("✅ Flutter Mobile App started on http://localhost:8080")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Flutter failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting Flutter: {e}")
        return None

def open_browsers():
    """Open web browsers for all interfaces"""
    print("🌐 Opening web browsers...")
    time.sleep(2)
    
    urls = [
        ("Backend API Docs", "http://localhost:8000/docs"),
        ("Streamlit Web App", "http://localhost:8501"),
        ("Flutter Mobile App", "http://localhost:8080")
    ]
    
    for name, url in urls:
        try:
            webbrowser.open(url)
            print(f"✅ Opened {name}: {url}")
        except Exception as e:
            print(f"❌ Could not open {name}: {e}")

def monitor_processes(processes):
    """Monitor running processes"""
    print("\n" + "=" * 80)
    print("🎯 ALL SERVICES RUNNING!")
    print("=" * 80)
    print("📊 Service Status:")
    print("  • Backend API:      http://localhost:8000")
    print("  • API Documentation: http://localhost:8000/docs")
    print("  • Streamlit Web:    http://localhost:8501")
    print("  • Flutter Mobile:   http://localhost:8080")
    print()
    print("🔧 Available Features:")
    print("  • 🏥 Health Chat with Gemini AI")
    print("  • 📸 Image Analysis (Skin, Food, Eye, Wellness)")
    print("  • 🎤 Voice Interactions")
    print("  • 📊 Health Analytics & History")
    print("  • 👤 User Authentication & Profiles")
    print("  • 🔒 Security & Privacy Protection")
    print()
    print("Press Ctrl+C to stop all services...")
    
    try:
        while True:
            time.sleep(1)
            # Check if any process has died
            for name, process in processes.items():
                if process and process.poll() is not None:
                    print(f"⚠️ {name} has stopped unexpectedly")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")
        for name, process in processes.items():
            if process:
                process.terminate()
                print(f"✅ Stopped {name}")

def main():
    """Main function to start all services"""
    print_banner()
    check_requirements()
    
    # Start all services
    processes = {}
    
    # Start backend
    backend_process = start_backend()
    processes['Backend API'] = backend_process
    
    # Start Streamlit
    streamlit_process = start_streamlit()
    processes['Streamlit Web'] = streamlit_process
    
    # Start Flutter
    flutter_process = start_flutter()
    processes['Flutter Mobile'] = flutter_process
    
    # Check if at least one service started
    running_services = [name for name, proc in processes.items() if proc is not None]
    
    if not running_services:
        print("❌ No services could be started. Please check the error messages above.")
        return
    
    print(f"\n✅ Successfully started {len(running_services)} services:")
    for service in running_services:
        print(f"  • {service}")
    
    # Open browsers
    threading.Thread(target=open_browsers, daemon=True).start()
    
    # Monitor processes
    monitor_processes(processes)

if __name__ == "__main__":
    main()