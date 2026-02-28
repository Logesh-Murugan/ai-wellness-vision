#!/usr/bin/env python3
"""
Start CNN API server and run comprehensive tests
"""

import subprocess
import sys
import time
import requests
import threading
import os
from pathlib import Path

def start_server():
    """Start the CNN API server"""
    print("🚀 Starting CNN API Server...")
    
    try:
        # Start server in a separate process
        process = subprocess.Popen([
            sys.executable, 'main_api_server_cnn.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8000/", timeout=2)
                if response.status_code == 200:
                    print("✅ Server started successfully!")
                    return process
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ Server failed to start within 30 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def run_tests():
    """Run the CNN API tests"""
    print("\n🧪 Running CNN API Tests...")
    
    try:
        # Run the test script
        result = subprocess.run([
            sys.executable, 'test_cnn_api.py'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def test_flutter_integration():
    """Test Flutter app integration"""
    print("\n📱 Testing Flutter Integration...")
    
    flutter_dir = Path("flutter_app")
    if not flutter_dir.exists():
        print("❌ Flutter app directory not found")
        return False
    
    try:
        # Check if Flutter is available
        result = subprocess.run(['flutter', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("❌ Flutter not installed or not in PATH")
            print("   Install Flutter from: https://flutter.dev/docs/get-started/install")
            return False
        
        print("✅ Flutter is available")
        
        # Test Flutter dependencies
        print("📦 Checking Flutter dependencies...")
        result = subprocess.run(['flutter', 'pub', 'get'], 
                              cwd=flutter_dir, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Flutter dependencies are ready")
        else:
            print("⚠️ Flutter dependencies may need updating")
            print("   Run: cd flutter_app && flutter pub get")
        
        return True
        
    except Exception as e:
        print(f"❌ Flutter integration test failed: {e}")
        return False

def create_demo_images():
    """Create demo images for testing"""
    print("\n🖼️ Creating demo images...")
    
    try:
        from PIL import Image
        import numpy as np
        
        demo_dir = Path("demo_images")
        demo_dir.mkdir(exist_ok=True)
        
        # Create different demo images
        demo_images = {
            'skin_healthy.jpg': (255, 220, 177),  # Healthy skin tone
            'eye_normal.jpg': (139, 69, 19),      # Brown eye
            'food_healthy.jpg': (255, 165, 0),    # Orange/healthy food
            'general_sample.jpg': (128, 128, 128) # General sample
        }
        
        for filename, color in demo_images.items():
            # Create image with some texture
            img_array = np.full((224, 224, 3), color, dtype=np.uint8)
            noise = np.random.randint(-20, 20, (224, 224, 3))
            img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            
            image = Image.fromarray(img_array)
            image.save(demo_dir / filename)
        
        print(f"✅ Created {len(demo_images)} demo images in {demo_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating demo images: {e}")
        return False

def show_usage_guide():
    """Show usage guide"""
    print("\n" + "="*60)
    print("🎯 CNN HEALTH ANALYSIS SYSTEM - READY!")
    print("="*60)
    print()
    print("🌐 API Endpoints:")
    print("   • Main API: http://localhost:8000")
    print("   • Documentation: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("   • Model Info: http://localhost:8000/api/v1/models/info")
    print()
    print("📸 Image Analysis:")
    print("   POST /api/v1/analysis/image")
    print("   Parameters: image (file), analysis_type (skin|eye|food|wellness)")
    print()
    print("🧠 Available Analysis Types:")
    print("   • skin - Skin condition analysis")
    print("   • eye - Eye health assessment")
    print("   • food - Nutritional analysis")
    print("   • wellness - General health screening")
    print()
    print("📱 Flutter Integration:")
    print("   Your Flutter app can now connect to the CNN-powered backend!")
    print("   The image analysis will use advanced deep learning models.")
    print()
    print("🔧 Manual Testing:")
    print("   1. Open http://localhost:8000/docs in your browser")
    print("   2. Try the /api/v1/analysis/image endpoint")
    print("   3. Upload demo images from the demo_images/ folder")
    print()
    print("🛑 To stop the server: Press Ctrl+C")

def main():
    """Main function"""
    print("="*60)
    print("🏥 AI WELLNESS VISION - CNN SYSTEM LAUNCHER")
    print("="*60)
    print()
    
    # Step 1: Create demo images
    create_demo_images()
    
    # Step 2: Start server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start server. Exiting.")
        return False
    
    try:
        # Step 3: Run tests
        test_success = run_tests()
        
        # Step 4: Test Flutter integration
        flutter_ready = test_flutter_integration()
        
        # Step 5: Show usage guide
        show_usage_guide()
        
        if test_success:
            print("\n🎉 ALL SYSTEMS GO! Your CNN health analysis system is ready!")
        else:
            print("\n⚠️ Some tests failed, but the server is running.")
        
        print("\nPress Ctrl+C to stop the server...")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped successfully")
        
        return test_success
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        server_process.terminate()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)