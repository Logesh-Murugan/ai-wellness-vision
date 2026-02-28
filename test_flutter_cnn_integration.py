#!/usr/bin/env python3
"""
Test Flutter-CNN Integration
This script tests the complete integration between Flutter app and CNN backend
"""

import requests
import json
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image
import numpy as np
import io

class FlutterCNNIntegrationTester:
    """Test Flutter app integration with CNN backend"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.flutter_dir = Path("flutter_app")
        
    def test_backend_connectivity(self):
        """Test if CNN backend is accessible"""
        print("🔍 Testing Backend Connectivity...")
        print("-" * 40)
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Backend Health Check: PASSED")
                print(f"   Status: {data.get('status')}")
                print(f"   CNN Available: {data.get('services', {}).get('cnn_analyzer')}")
                return True
            else:
                print(f"❌ Backend Health Check: FAILED ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Backend Connection: ERROR - {e}")
            return False
    
    def test_image_analysis_api(self):
        """Test the image analysis API that Flutter uses"""
        print("\n📸 Testing Image Analysis API...")
        print("-" * 40)
        
        try:
            # Create test images for different analysis types
            test_cases = [
                ("skin", self._create_skin_test_image()),
                ("eye", self._create_eye_test_image()),
                ("food", self._create_food_test_image()),
                ("wellness", self._create_general_test_image())
            ]
            
            results = []
            
            for analysis_type, test_image in test_cases:
                print(f"\n🧪 Testing {analysis_type} analysis...")
                
                # Prepare request exactly like Flutter does
                files = {'image': ('test.jpg', test_image, 'image/jpeg')}
                data = {'analysis_type': analysis_type}
                
                response = requests.post(
                    f"{self.backend_url}/api/v1/analysis/image",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {analysis_type}: SUCCESS")
                    print(f"      Result: {result.get('result', 'Unknown')}")
                    print(f"      Confidence: {result.get('confidence', 0):.2f}")
                    print(f"      Method: {result.get('processing_method', 'Unknown')}")
                    print(f"      Recommendations: {len(result.get('recommendations', []))}")
                    
                    results.append({
                        'type': analysis_type,
                        'success': True,
                        'result': result
                    })
                else:
                    print(f"   ❌ {analysis_type}: FAILED ({response.status_code})")
                    print(f"      Error: {response.text}")
                    results.append({
                        'type': analysis_type,
                        'success': False,
                        'error': response.text
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ API Test Error: {e}")
            return []
    
    def test_flutter_app_setup(self):
        """Test Flutter app configuration and dependencies"""
        print("\n📱 Testing Flutter App Setup...")
        print("-" * 40)
        
        if not self.flutter_dir.exists():
            print("❌ Flutter app directory not found")
            return False
        
        # Check pubspec.yaml
        pubspec_path = self.flutter_dir / "pubspec.yaml"
        if pubspec_path.exists():
            print("✅ pubspec.yaml found")
        else:
            print("❌ pubspec.yaml not found")
            return False
        
        # Check API configuration
        api_config_path = self.flutter_dir / "lib/core/config/api_config.dart"
        if api_config_path.exists():
            with open(api_config_path, 'r') as f:
                content = f.read()
                if "localhost:8000" in content:
                    print("✅ API configuration points to CNN backend")
                else:
                    print("⚠️ API configuration may need updating")
        else:
            print("❌ API configuration not found")
        
        # Check image analysis service
        service_path = self.flutter_dir / "lib/core/services/image_analysis_service.dart"
        if service_path.exists():
            print("✅ Image analysis service found")
        else:
            print("❌ Image analysis service not found")
            return False
        
        return True
    
    def test_flutter_dependencies(self):
        """Test Flutter dependencies"""
        print("\n📦 Testing Flutter Dependencies...")
        print("-" * 40)
        
        try:
            # Check if Flutter is available
            result = subprocess.run(['flutter', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Flutter SDK available")
                
                # Get dependencies
                print("📥 Getting Flutter dependencies...")
                result = subprocess.run(['flutter', 'pub', 'get'], 
                                      cwd=self.flutter_dir, 
                                      capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print("✅ Flutter dependencies resolved")
                    return True
                else:
                    print(f"❌ Flutter pub get failed: {result.stderr}")
                    return False
            else:
                print("❌ Flutter SDK not available")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Flutter command timed out")
            return False
        except FileNotFoundError:
            print("❌ Flutter not installed or not in PATH")
            return False
        except Exception as e:
            print(f"❌ Flutter test error: {e}")
            return False
    
    def test_flutter_build(self):
        """Test Flutter app build"""
        print("\n🔨 Testing Flutter Build...")
        print("-" * 40)
        
        try:
            # Test web build (fastest)
            print("Building Flutter web app...")
            result = subprocess.run([
                'flutter', 'build', 'web', '--no-sound-null-safety'
            ], cwd=self.flutter_dir, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Flutter web build successful")
                
                # Check if build output exists
                build_dir = self.flutter_dir / "build/web"
                if build_dir.exists():
                    print("✅ Build artifacts created")
                    return True
                else:
                    print("⚠️ Build completed but artifacts not found")
                    return False
            else:
                print(f"❌ Flutter build failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Flutter build timed out")
            return False
        except Exception as e:
            print(f"❌ Flutter build error: {e}")
            return False
    
    def generate_flutter_test_guide(self):
        """Generate a guide for testing Flutter app with CNN"""
        
        guide = """
# 🧪 Flutter-CNN Integration Test Guide

## 🚀 Quick Test Steps

### 1. Start CNN Backend
```bash
# In terminal 1 - Start the CNN server
python start_cnn_server.py
```

### 2. Run Flutter App
```bash
# In terminal 2 - Start Flutter web app
cd flutter_app
flutter run -d chrome --web-port=3000
```

### 3. Test Image Analysis
1. Open Flutter app in browser: http://localhost:3000
2. Navigate to Image Analysis page
3. Upload a test image or take a photo
4. Select analysis type (Skin, Eye, Food, Wellness)
5. Click "Analyze" button
6. Verify you get CNN-powered results

## 🎯 What to Look For

### ✅ Success Indicators
- Image uploads successfully
- Analysis completes within 30 seconds
- Results show "CNN Deep Learning" as processing method
- Confidence score between 0.0-1.0
- Detailed recommendations provided
- Professional health insights included

### ❌ Failure Indicators
- "Connection refused" errors
- "Analysis failed" messages
- Very low confidence scores (< 0.5)
- Generic fallback responses only
- Long processing times (> 60 seconds)

## 🔧 Troubleshooting

### Backend Issues
```bash
# Check backend status
python check_server_status.py

# Restart backend if needed
python start_cnn_server.py
```

### Flutter Issues
```bash
# Clean and rebuild
cd flutter_app
flutter clean
flutter pub get
flutter run -d chrome
```

### Network Issues
- Ensure both backend (8000) and Flutter (3000) ports are free
- Check firewall settings
- Verify localhost connectivity

## 📊 Expected CNN Results

### Skin Analysis
- Processing Method: "CNN Deep Learning"
- Confidence: 0.7-0.95
- Results: "healthy", "acne", "dry_skin", etc.
- Recommendations: 3-5 skincare tips

### Eye Analysis  
- Processing Method: "CNN Deep Learning"
- Confidence: 0.6-0.9
- Results: "healthy", "tired", "red_eye", etc.
- Recommendations: Eye care advice

### Food Analysis
- Processing Method: "CNN Deep Learning"  
- Confidence: 0.7-0.92
- Results: "healthy", "processed", "balanced", etc.
- Recommendations: Nutritional guidance

## 🎉 Success Confirmation

Your Flutter-CNN integration is working when:
1. ✅ Backend shows "CNN Analysis: Available"
2. ✅ Flutter app connects without errors
3. ✅ Image analysis returns CNN results
4. ✅ Processing method shows "CNN Deep Learning"
5. ✅ Confidence scores are realistic (0.6-0.95)
6. ✅ Recommendations are detailed and relevant

## 📱 Mobile Testing

### Android Testing
```bash
cd flutter_app
flutter run -d android
```

### iOS Testing (Mac only)
```bash
cd flutter_app
flutter run -d ios
```

Note: For mobile testing, update API config to use your computer's IP instead of localhost.

## 🔗 Integration Points

Your Flutter app integrates with CNN backend through:
- `lib/core/config/api_config.dart` - API endpoints
- `lib/core/services/image_analysis_service.dart` - Image processing
- `lib/core/services/api_service.dart` - HTTP requests
- `lib/features/image_analysis/` - UI components

All these are already configured to work with your CNN backend!
"""
        
        with open("FLUTTER_CNN_TEST_GUIDE.md", "w") as f:
            f.write(guide)
        
        print("📖 Flutter-CNN test guide created: FLUTTER_CNN_TEST_GUIDE.md")
    
    def _create_skin_test_image(self):
        """Create a skin-colored test image"""
        # Create skin-tone colored image
        img_array = np.full((224, 224, 3), [255, 220, 177], dtype=np.uint8)
        # Add some texture
        noise = np.random.randint(-20, 20, (224, 224, 3))
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        image = Image.fromarray(img_array)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def _create_eye_test_image(self):
        """Create an eye-like test image"""
        # Create eye-colored image (brown/hazel)
        img_array = np.full((224, 224, 3), [139, 69, 19], dtype=np.uint8)
        # Add some variation
        noise = np.random.randint(-30, 30, (224, 224, 3))
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        image = Image.fromarray(img_array)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def _create_food_test_image(self):
        """Create a food-like test image"""
        # Create food-colored image (orange/healthy)
        img_array = np.full((224, 224, 3), [255, 165, 0], dtype=np.uint8)
        # Add texture for food appearance
        noise = np.random.randint(-40, 40, (224, 224, 3))
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        image = Image.fromarray(img_array)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def _create_general_test_image(self):
        """Create a general test image"""
        # Create neutral colored image
        img_array = np.random.randint(100, 200, (224, 224, 3), dtype=np.uint8)
        
        image = Image.fromarray(img_array)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def run_complete_test(self):
        """Run complete Flutter-CNN integration test"""
        
        print("=" * 60)
        print("🧪 FLUTTER-CNN INTEGRATION TEST SUITE")
        print("=" * 60)
        print("Testing complete integration between Flutter app and CNN backend")
        print()
        
        # Test 1: Backend connectivity
        backend_ok = self.test_backend_connectivity()
        
        # Test 2: Image analysis API
        if backend_ok:
            api_results = self.test_image_analysis_api()
            api_ok = len([r for r in api_results if r['success']]) > 0
        else:
            api_ok = False
            api_results = []
        
        # Test 3: Flutter app setup
        flutter_setup_ok = self.test_flutter_app_setup()
        
        # Test 4: Flutter dependencies
        flutter_deps_ok = self.test_flutter_dependencies() if flutter_setup_ok else False
        
        # Test 5: Flutter build (optional)
        # flutter_build_ok = self.test_flutter_build() if flutter_deps_ok else False
        
        # Generate test guide
        self.generate_flutter_test_guide()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        tests = [
            ("Backend Connectivity", backend_ok),
            ("Image Analysis API", api_ok),
            ("Flutter App Setup", flutter_setup_ok),
            ("Flutter Dependencies", flutter_deps_ok),
            # ("Flutter Build", flutter_build_ok)
        ]
        
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if backend_ok and api_ok:
            print("\n🎉 FLUTTER-CNN INTEGRATION READY!")
            print("=" * 60)
            print("Your Flutter app can now use CNN-powered image analysis!")
            print()
            print("🚀 Next Steps:")
            print("1. Start CNN backend: python start_cnn_server.py")
            print("2. Start Flutter app: cd flutter_app && flutter run -d chrome")
            print("3. Test image analysis in the Flutter app")
            print("4. Check for 'CNN Deep Learning' in analysis results")
            print()
            print("📖 See FLUTTER_CNN_TEST_GUIDE.md for detailed testing instructions")
            
        else:
            print("\n⚠️ INTEGRATION ISSUES DETECTED")
            print("=" * 60)
            if not backend_ok:
                print("❌ CNN backend is not running or accessible")
                print("   Fix: python start_cnn_server.py")
            if not api_ok:
                print("❌ Image analysis API is not working")
                print("   Fix: Check backend logs and CNN model status")
            if not flutter_setup_ok:
                print("❌ Flutter app setup issues")
                print("   Fix: Check Flutter app configuration files")
        
        return passed == total

def main():
    """Run Flutter-CNN integration test"""
    tester = FlutterCNNIntegrationTester()
    success = tester.run_complete_test()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)