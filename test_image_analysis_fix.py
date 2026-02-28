#!/usr/bin/env python3
"""
Test script to debug image analysis issues
"""

import requests
import os
from pathlib import Path

def test_image_analysis():
    """Test the image analysis endpoint"""
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/analysis/image"
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\xc1\x1e\x1d\x1d\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Save test image
    test_image_path = "test_image.png"
    with open(test_image_path, 'wb') as f:
        f.write(test_image_data)
    
    print("🧪 Testing Image Analysis Endpoint...")
    print(f"📡 Server: {base_url}{endpoint}")
    print("=" * 60)
    
    # Test different analysis types
    analysis_types = ['skin', 'food', 'eye', 'wellness', 'emotion']
    
    for i, analysis_type in enumerate(analysis_types, 1):
        print(f"\n{i}. Testing: '{analysis_type}' analysis")
        print("-" * 40)
        
        try:
            # Prepare multipart form data
            files = {'image': ('test_image.png', open(test_image_path, 'rb'), 'image/png')}
            data = {'analysis_type': analysis_type}
            
            # Make request
            response = requests.post(
                f"{base_url}{endpoint}",
                files=files,
                data=data,
                timeout=30
            )
            
            files['image'][1].close()  # Close file handle
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Status: {response.status_code}")
                print(f"🔍 Analysis Type: {result.get('type', 'Unknown')}")
                print(f"🎯 Confidence: {result.get('confidence', 0)}")
                print(f"⚙️  Processing Method: {result.get('processing_method', 'Unknown')}")
                print(f"📝 Result: {result.get('result', 'No result')[:100]}...")
                
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"💡 Recommendations: {len(recommendations)} items")
                    for j, rec in enumerate(recommendations[:2], 1):
                        print(f"   {j}. {rec}")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Is the server running on localhost:8000?")
        except requests.exceptions.Timeout:
            print("❌ Timeout: Server took too long to respond")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Clean up test image
    try:
        os.remove(test_image_path)
    except:
        pass
    
    print("\n" + "=" * 60)
    print("🏁 Image analysis testing complete!")
    print("\n💡 Check the 'Processing Method' field:")
    print("   ✅ 'Gemini Vision AI' = Using AI analysis (good)")
    print("   ⚠️  'Fallback Analysis' = Using generic responses (issue)")
    print("   🔧 'CNN Analysis' = Using CNN model (best)")

if __name__ == "__main__":
    test_image_analysis()