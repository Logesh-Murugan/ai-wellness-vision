#!/usr/bin/env python3
"""
Comprehensive Production Testing Suite for CNN Health Analysis System
"""

import pytest
import requests
import json
import time
import threading
from pathlib import Path
from PIL import Image
import numpy as np
import io

class TestCNNProductionSystem:
    """Production-level testing for CNN system"""
    
    @pytest.fixture
    def api_base_url(self):
        """Base URL for API testing"""
        return "http://localhost:8000"
    
    @pytest.fixture
    def test_image(self):
        """Create a test image for analysis"""
        # Create a 224x224 RGB test image
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        image = Image.fromarray(img_array)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return img_bytes
    
    def test_api_health_check(self, api_base_url):
        """Test API health check endpoint"""
        response = requests.get(f"{api_base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "services" in data
        assert "timestamp" in data
        
        # Check required services
        services = data["services"]
        assert services["api"] == "running"
        assert "cnn_analyzer" in services
    
    def test_model_info_endpoint(self, api_base_url):
        """Test model information endpoint"""
        response = requests.get(f"{api_base_url}/api/v1/models/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "cnn_available" in data
        assert "gemini_available" in data
        assert "models" in data
    
    @pytest.mark.parametrize("analysis_type", ["skin", "eye", "food", "wellness"])
    def test_image_analysis_endpoints(self, api_base_url, test_image, analysis_type):
        """Test image analysis for all types"""
        
        files = {'image': ('test.jpg', test_image, 'image/jpeg')}
        data = {'analysis_type': analysis_type}
        
        response = requests.post(
            f"{api_base_url}/api/v1/analysis/image",
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check required fields
        assert "id" in result
        assert "type" in result
        assert "result" in result
        assert "confidence" in result
        assert "recommendations" in result
        assert "timestamp" in result
        
        # Check data types
        assert isinstance(result["confidence"], (int, float))
        assert 0 <= result["confidence"] <= 1
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0
    
    def test_analysis_history_endpoint(self, api_base_url):
        """Test analysis history endpoint"""
        response = requests.get(f"{api_base_url}/api/v1/analysis/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "pagination" in data
        assert isinstance(data["results"], list)
    
    def test_performance_metrics_endpoint(self, api_base_url):
        """Test performance metrics endpoint"""
        response = requests.get(f"{api_base_url}/api/v1/performance")
        
        # This might return 503 if monitoring is not available
        if response.status_code == 200:
            data = response.json()
            assert "system_status" in data
            assert "analysis_performance" in data
        elif response.status_code == 503:
            # Monitoring not available, which is acceptable
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_concurrent_requests(self, api_base_url, test_image):
        """Test system under concurrent load"""
        
        def make_request():
            files = {'image': ('test.jpg', test_image, 'image/jpeg')}
            data = {'analysis_type': 'skin'}
            
            response = requests.post(
                f"{api_base_url}/api/v1/analysis/image",
                files=files,
                data=data
            )
            return response.status_code == 200
        
        # Run 10 concurrent requests
        threads = []
        results = []
        
        for _ in range(10):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # At least 80% should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"Success rate too low: {success_rate}"
    
    def test_large_image_handling(self, api_base_url):
        """Test handling of large images"""
        
        # Create a large image (2MB+)
        large_img = np.random.randint(0, 255, (2000, 2000, 3), dtype=np.uint8)
        image = Image.fromarray(large_img)
        
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        files = {'image': ('large_test.jpg', img_bytes, 'image/jpeg')}
        data = {'analysis_type': 'skin'}
        
        response = requests.post(
            f"{api_base_url}/api/v1/analysis/image",
            files=files,
            data=data
        )
        
        # Should either succeed or return appropriate error
        assert response.status_code in [200, 400, 413]  # 413 = Payload Too Large
    
    def test_invalid_file_types(self, api_base_url):
        """Test handling of invalid file types"""
        
        # Create a text file disguised as image
        text_content = b"This is not an image"
        
        files = {'image': ('fake.jpg', io.BytesIO(text_content), 'image/jpeg')}
        data = {'analysis_type': 'skin'}
        
        response = requests.post(
            f"{api_base_url}/api/v1/analysis/image",
            files=files,
            data=data
        )
        
        # Should return error for invalid image
        assert response.status_code in [400, 422]
    
    def test_response_time_performance(self, api_base_url, test_image):
        """Test API response time performance"""
        
        files = {'image': ('test.jpg', test_image, 'image/jpeg')}
        data = {'analysis_type': 'skin'}
        
        start_time = time.time()
        
        response = requests.post(
            f"{api_base_url}/api/v1/analysis/image",
            files=files,
            data=data
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 30, f"Response time too slow: {response_time}s"
    
    def test_error_handling(self, api_base_url):
        """Test error handling for various scenarios"""
        
        # Test missing image
        response = requests.post(f"{api_base_url}/api/v1/analysis/image")
        assert response.status_code == 422
        
        # Test invalid analysis type
        files = {'image': ('test.jpg', io.BytesIO(b'fake'), 'image/jpeg')}
        data = {'analysis_type': 'invalid_type'}
        
        response = requests.post(
            f"{api_base_url}/api/v1/analysis/image",
            files=files,
            data=data
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_cors_headers(self, api_base_url):
        """Test CORS headers are properly set"""
        
        response = requests.options(f"{api_base_url}/api/v1/analysis/image")
        
        # Check CORS headers
        headers = response.headers
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers

class TestCNNModelPerformance:
    """Test CNN model performance and accuracy"""
    
    def test_model_loading(self):
        """Test that CNN models load correctly"""
        try:
            from src.ai_models.cnn_health_analyzer import get_cnn_analyzer
            
            analyzer = get_cnn_analyzer()
            model_info = analyzer.get_model_info()
            
            # Check that at least one model is loaded
            loaded_models = [
                model for model, info in model_info.items() 
                if info.get('loaded', False)
            ]
            
            assert len(loaded_models) > 0, "No CNN models loaded"
            
        except ImportError:
            pytest.skip("CNN analyzer not available")
    
    def test_model_prediction_consistency(self):
        """Test that models produce consistent predictions"""
        try:
            from src.ai_models.cnn_health_analyzer import get_cnn_analyzer
            
            analyzer = get_cnn_analyzer()
            
            # Create test image
            test_image_path = "test_consistency.jpg"
            img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            image = Image.fromarray(img_array)
            image.save(test_image_path)
            
            # Run analysis multiple times
            results = []
            for _ in range(3):
                result = analyzer.analyze_image(test_image_path, 'skin')
                results.append(result)
            
            # Check consistency (confidence should be similar)
            confidences = [r.get('confidence', 0) for r in results]
            confidence_std = np.std(confidences)
            
            assert confidence_std < 0.1, f"Inconsistent predictions: {confidences}"
            
            # Cleanup
            Path(test_image_path).unlink(missing_ok=True)
            
        except ImportError:
            pytest.skip("CNN analyzer not available")

def run_production_tests():
    """Run all production tests"""
    
    print("Running CNN Production Test Suite...")
    print("=" * 50)
    
    # Run pytest with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])

if __name__ == "__main__":
    run_production_tests()