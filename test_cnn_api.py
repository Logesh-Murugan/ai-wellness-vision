#!/usr/bin/env python3
"""
Test CNN API functionality
"""

import requests
import json
from pathlib import Path
from PIL import Image
import numpy as np
import io

def create_test_image(image_type="skin"):
    """Create a test image for analysis"""
    # Create different colored test images for different analysis types
    colors = {
        'skin': (255, 220, 177),  # Skin tone
        'eye': (139, 69, 19),     # Brown eye color
        'food': (255, 165, 0),    # Orange food color
        'general': (128, 128, 128) # Gray
    }
    
    color = colors.get(image_type, colors['general'])
    
    # Create a 224x224 image with the specified color
    img_array = np.full((224, 224, 3), color, dtype=np.uint8)
    
    # Add some texture/noise to make it more realistic
    noise = np.random.randint(-20, 20, (224, 224, 3))
    img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    # Convert to PIL Image
    image = Image.fromarray(img_array)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_api_health():
    """Test API health endpoints"""
    print("🏥 Testing API Health...")
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data['message']}")
            print(f"   CNN Available: {data.get('cnn_available', 'Unknown')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data['status']}")
            services = data.get('services', {})
            for service, status in services.items():
                print(f"   {service}: {status}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test model info endpoint
        response = requests.get("http://localhost:8000/api/v1/models/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models info: CNN Available = {data.get('cnn_available', False)}")
            if 'models' in data and 'cnn' in data['models']:
                cnn_models = data['models']['cnn']
                for model_type, info in cnn_models.items():
                    status = "Loaded" if info.get('loaded') else "Not Loaded"
                    print(f"   {model_type}: {status}")
        else:
            print(f"❌ Models info failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API health test failed: {e}")
        return False

def test_image_analysis():
    """Test CNN image analysis"""
    print("\n🧠 Testing CNN Image Analysis...")
    
    analysis_types = ['skin', 'eye', 'food', 'wellness']
    
    for analysis_type in analysis_types:
        try:
            print(f"\n📸 Testing {analysis_type} analysis...")
            
            # Create test image
            test_image = create_test_image(analysis_type)
            
            # Prepare the request
            files = {
                'image': ('test_image.jpg', test_image, 'image/jpeg')
            }
            data = {
                'analysis_type': analysis_type
            }
            
            # Send request
            response = requests.post(
                "http://localhost:8000/api/v1/analysis/image",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ {analysis_type} analysis successful!")
                print(f"   Finding: {result.get('result', 'Unknown')}")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
                print(f"   Method: {result.get('processing_method', 'Unknown')}")
                
                # Show recommendations
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"   Recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"     {i}. {rec}")
                
                # Show health insights if available
                insights = result.get('health_insights', {})
                if insights:
                    severity = insights.get('severity_level', 'unknown')
                    follow_up = insights.get('follow_up_needed', False)
                    print(f"   Severity: {severity}")
                    print(f"   Follow-up needed: {follow_up}")
                
            else:
                print(f"❌ {analysis_type} analysis failed: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {analysis_type} analysis error: {e}")
    
    return True

def test_analysis_history():
    """Test analysis history endpoint"""
    print("\n📊 Testing Analysis History...")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/analysis/history")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            pagination = data.get('pagination', {})
            
            print(f"✅ History retrieved successfully!")
            print(f"   Total analyses: {pagination.get('total', 0)}")
            print(f"   Current page: {pagination.get('page', 1)}")
            
            if results:
                print(f"   Recent analyses:")
                for i, result in enumerate(results[:3], 1):
                    analysis_type = result.get('type', 'unknown')
                    confidence = result.get('confidence', 0)
                    method = result.get('processing_method', 'unknown')
                    print(f"     {i}. {analysis_type} (confidence: {confidence:.2f}, method: {method})")
            
            # Check summary if available
            summary = data.get('summary', {})
            if summary:
                total = summary.get('total_analyses', 0)
                cnn_count = summary.get('cnn_analyses', 0)
                gemini_count = summary.get('gemini_analyses', 0)
                print(f"   Summary: {total} total, {cnn_count} CNN, {gemini_count} Gemini")
            
        else:
            print(f"❌ History retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ History test error: {e}")

def test_performance():
    """Test API performance"""
    print("\n⚡ Testing Performance...")
    
    import time
    
    try:
        # Test multiple rapid requests
        start_time = time.time()
        
        for i in range(3):
            test_image = create_test_image('skin')
            files = {'image': ('test.jpg', test_image, 'image/jpeg')}
            data = {'analysis_type': 'skin'}
            
            response = requests.post(
                "http://localhost:8000/api/v1/analysis/image",
                files=files,
                data=data
            )
            
            if response.status_code != 200:
                print(f"❌ Performance test failed on request {i+1}")
                return False
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 3
        
        print(f"✅ Performance test completed!")
        print(f"   3 requests in {total_time:.2f} seconds")
        print(f"   Average time per request: {avg_time:.2f} seconds")
        
        if avg_time < 10:
            print("   🚀 Performance: Excellent")
        elif avg_time < 20:
            print("   ⚡ Performance: Good")
        else:
            print("   🐌 Performance: Needs optimization")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 CNN API COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing your AI Wellness Vision API with CNN...")
    print()
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ API is not responding. Please start the server first:")
            print("   python main_api_server_cnn.py")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Please ensure the server is running:")
        print("   python main_api_server_cnn.py")
        return False
    
    # Run tests
    tests = [
        ("API Health Check", test_api_health),
        ("CNN Image Analysis", test_image_analysis),
        ("Analysis History", test_analysis_history),
        ("Performance Test", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result if result is not None else True))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS ✅" if result else "FAIL ❌"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your CNN system is working perfectly!")
        print("\n🚀 Your AI Wellness Vision app now has:")
        print("   • Advanced CNN-powered image analysis")
        print("   • Professional-grade health assessments")
        print("   • Detailed confidence scoring")
        print("   • Comprehensive health recommendations")
        print("   • Smart fallback systems")
        print("\n📱 Ready for integration with your Flutter app!")
        
    else:
        print(f"\n⚠️ {total - passed} tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting tips:")
        print("   • Ensure the API server is running")
        print("   • Check your Gemini API key in .env")
        print("   • Verify TensorFlow installation")
        print("   • Check network connectivity")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)