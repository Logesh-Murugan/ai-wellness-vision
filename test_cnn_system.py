#!/usr/bin/env python3
"""
Test script for CNN Health Analysis System
"""

import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow {tf.__version__}")
    except ImportError as e:
        print(f"✗ TensorFlow: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
        return False
    
    try:
        import cv2
        print(f"✓ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV: {e}")
        return False
    
    try:
        from PIL import Image
        print(f"✓ Pillow")
    except ImportError as e:
        print(f"✗ Pillow: {e}")
        return False
    
    return True

def test_cnn_analyzer():
    """Test CNN analyzer initialization"""
    print("\nTesting CNN analyzer...")
    
    try:
        from src.ai_models.cnn_health_analyzer import CNNHealthAnalyzer, get_cnn_analyzer
        
        # Test initialization
        analyzer = CNNHealthAnalyzer()
        print("✓ CNN analyzer initialized")
        
        # Test model info
        model_info = analyzer.get_model_info()
        print("✓ Model info retrieved")
        
        # Print model status
        for model_type, info in model_info.items():
            status = "Loaded" if info.get('loaded') else "Not loaded"
            print(f"  {model_type}: {status}")
        
        # Test global instance
        global_analyzer = get_cnn_analyzer()
        print("✓ Global analyzer instance works")
        
        return True
        
    except Exception as e:
        print(f"✗ CNN analyzer test failed: {e}")
        return False

def create_test_image():
    """Create a simple test image for analysis"""
    try:
        import numpy as np
        from PIL import Image
        
        # Create a simple test image (224x224 RGB)
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        # Save test image
        test_dir = Path("test_images")
        test_dir.mkdir(exist_ok=True)
        
        test_image_path = test_dir / "test_image.jpg"
        Image.fromarray(test_image).save(test_image_path)
        
        print(f"✓ Test image created: {test_image_path}")
        return str(test_image_path)
        
    except Exception as e:
        print(f"✗ Failed to create test image: {e}")
        return None

def test_image_analysis():
    """Test image analysis functionality"""
    print("\nTesting image analysis...")
    
    try:
        from src.ai_models.cnn_health_analyzer import get_cnn_analyzer
        
        # Create test image
        test_image_path = create_test_image()
        if not test_image_path:
            return False
        
        # Get analyzer
        analyzer = get_cnn_analyzer()
        
        # Test different analysis types
        analysis_types = ['skin', 'eye', 'food', 'general']
        
        for analysis_type in analysis_types:
            try:
                result = analyzer.analyze_image(test_image_path, analysis_type)
                
                if result and 'primary_finding' in result:
                    print(f"✓ {analysis_type} analysis: {result['primary_finding']} (confidence: {result.get('confidence', 0):.2f})")
                else:
                    print(f"✗ {analysis_type} analysis failed")
                    
            except Exception as e:
                print(f"✗ {analysis_type} analysis error: {e}")
        
        # Clean up test image
        os.remove(test_image_path)
        print("✓ Test image cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ Image analysis test failed: {e}")
        return False

def test_api_integration():
    """Test API integration"""
    print("\nTesting API integration...")
    
    try:
        # Test if enhanced API server can be imported
        import main_api_server_cnn
        print("✓ Enhanced API server can be imported")
        
        # Test CNN availability flag
        from main_api_server_cnn import CNN_AVAILABLE
        print(f"✓ CNN availability: {CNN_AVAILABLE}")
        
        return True
        
    except Exception as e:
        print(f"✗ API integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CNN HEALTH ANALYSIS SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("CNN Analyzer Test", test_cnn_analyzer),
        ("Image Analysis Test", test_image_analysis),
        ("API Integration Test", test_api_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! CNN system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main_api_server_cnn.py")
        print("2. Test with real images through the API")
        print("3. Integrate with your Flutter app")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Install dependencies: pip install -r requirements_cnn.txt")
        print("2. Run setup: python setup_cnn_models.py")
        print("3. Check TensorFlow installation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)