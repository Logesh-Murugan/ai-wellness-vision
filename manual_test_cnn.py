#!/usr/bin/env python3
"""
Manual test for CNN API - Windows compatible
"""

import requests
import json
from pathlib import Path

def test_api_endpoints():
    """Test basic API endpoints"""
    print("Testing CNN API Endpoints...")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Message: {data['message']}")
            print(f"   CNN Available: {data.get('cnn_available', 'Unknown')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   Status: {data['status']}")
            services = data.get('services', {})
            for service, status in services.items():
                print(f"   {service}: {status}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test model info
    try:
        response = requests.get("http://localhost:8000/api/v1/models/info")
        if response.status_code == 200:
            data = response.json()
            print("✅ Model info endpoint working")
            print(f"   CNN Available: {data.get('cnn_available', False)}")
            print(f"   Gemini Available: {data.get('gemini_available', False)}")
        else:
            print(f"❌ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model info error: {e}")

def test_image_analysis():
    """Test image analysis with demo images"""
    print("\nTesting Image Analysis...")
    print("=" * 40)
    
    demo_dir = Path("demo_images")
    if not demo_dir.exists():
        print("❌ Demo images not found. Run start_and_test_cnn.py first.")
        return
    
    # Test with a demo image
    demo_image = demo_dir / "skin_healthy.jpg"
    if demo_image.exists():
        try:
            with open(demo_image, 'rb') as f:
                files = {'image': ('skin_healthy.jpg', f, 'image/jpeg')}
                data = {'analysis_type': 'skin'}
                
                response = requests.post(
                    "http://localhost:8000/api/v1/analysis/image",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Image analysis working!")
                    print(f"   Analysis Type: {result.get('type', 'Unknown')}")
                    print(f"   Result: {result.get('result', 'Unknown')}")
                    print(f"   Confidence: {result.get('confidence', 0):.2f}")
                    print(f"   Method: {result.get('processing_method', 'Unknown')}")
                    
                    recommendations = result.get('recommendations', [])
                    if recommendations:
                        print("   Recommendations:")
                        for i, rec in enumerate(recommendations[:3], 1):
                            print(f"     {i}. {rec}")
                else:
                    print(f"❌ Image analysis failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Image analysis error: {e}")
    else:
        print("❌ Demo image not found")

def main():
    """Run manual tests"""
    print("CNN API Manual Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Start it with:")
            print("   python start_and_test_cnn.py")
            return
    except:
        print("❌ Cannot connect to server. Start it with:")
        print("   python start_and_test_cnn.py")
        return
    
    print("✅ Server is running!")
    print()
    
    # Run tests
    test_api_endpoints()
    test_image_analysis()
    
    print("\n" + "=" * 50)
    print("Manual Test Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Open http://localhost:8000/docs in your browser")
    print("2. Test the API endpoints interactively")
    print("3. Upload your own images for analysis")
    print("4. Connect your Flutter app to the API")

if __name__ == "__main__":
    main()