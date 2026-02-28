#!/usr/bin/env python3
"""
Simple test for image analysis feature
"""

import requests
import io

def test_image_analysis():
    """Test image analysis with different types"""
    
    # Create a simple test file (simulating an image)
    test_data = b"fake_image_data_for_testing"
    
    analysis_types = ["skin", "food", "eye", "emotion"]
    
    print("🖼️  Testing Image Analysis Feature...")
    print("=" * 50)
    
    for analysis_type in analysis_types:
        try:
            # Prepare the file upload
            files = {
                'image': ('test_image.jpg', io.BytesIO(test_data), 'image/jpeg')
            }
            
            # Send request to image analysis endpoint
            response = requests.post(
                f"http://localhost:8000/api/v1/analysis/image?analysis_type={analysis_type}",
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {analysis_type.upper()} Analysis:")
                print(f"   Result: {result['result']}")
                print(f"   Confidence: {result['confidence']*100:.1f}%")
                print(f"   Recommendations: {len(result['recommendations'])} tips")
                print()
            else:
                print(f"❌ {analysis_type} analysis failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {analysis_type}: {e}")
    
    print("=" * 50)
    print("🎉 Image Analysis Test Complete!")

if __name__ == "__main__":
    test_image_analysis()