# -*- coding: utf-8 -*-
"""Deployment tests for AI Wellness Vision system."""

import unittest
import requests
import time
import os
from urllib.parse import urljoin


class TestDeployment(unittest.TestCase):
    """Test deployment health and functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        self.streamlit_url = os.getenv('STREAMLIT_URL', 'http://localhost:8501')
        self.timeout = 30
        
    def test_api_health_check(self):
        """Test API health endpoint."""
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        health_data = response.json()
        self.assertIn('status', health_data)
        self.assertEqual(health_data['status'], 'healthy')
        
    def test_api_readiness(self):
        """Test API readiness endpoint."""
        response = requests.get(
            urljoin(self.base_url, '/ready'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        ready_data = response.json()
        self.assertIn('ready', ready_data)
        self.assertTrue(ready_data['ready'])
        
    def test_database_connectivity(self):
        """Test database connectivity through API."""
        response = requests.get(
            urljoin(self.base_url, '/health/database'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        db_health = response.json()
        self.assertIn('database', db_health)
        self.assertEqual(db_health['database']['status'], 'connected')
        
    def test_redis_connectivity(self):
        """Test Redis connectivity through API."""
        response = requests.get(
            urljoin(self.base_url, '/health/redis'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        redis_health = response.json()
        self.assertIn('redis', redis_health)
        self.assertEqual(redis_health['redis']['status'], 'connected')
        
    def test_streamlit_accessibility(self):
        """Test Streamlit application accessibility."""
        response = requests.get(
            self.streamlit_url,
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers.get('content-type', ''))
        
    def test_api_endpoints_availability(self):
        """Test key API endpoints availability."""
        endpoints = [
            '/docs',  # OpenAPI documentation
            '/api/v1/image/analyze',  # Image analysis endpoint
            '/api/v1/nlp/process',    # NLP processing endpoint
            '/api/v1/speech/transcribe',  # Speech transcription endpoint
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = requests.get(
                    urljoin(self.base_url, endpoint),
                    timeout=self.timeout
                )
                # Should not return 404 or 500 errors
                self.assertNotIn(response.status_code, [404, 500, 502, 503])
                
    def test_security_headers(self):
        """Test security headers are present."""
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]
        
        for header in security_headers:
            with self.subTest(header=header):
                self.assertIn(header, response.headers)
                
    def test_cors_configuration(self):
        """Test CORS configuration."""
        response = requests.options(
            urljoin(self.base_url, '/api/v1/image/analyze'),
            headers={'Origin': 'http://localhost:3000'},
            timeout=self.timeout
        )
        
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        
    def test_rate_limiting(self):
        """Test rate limiting is working."""
        # Make multiple rapid requests
        responses = []
        for _ in range(20):
            response = requests.get(
                urljoin(self.base_url, '/health'),
                timeout=self.timeout
            )
            responses.append(response.status_code)
            
        # Should eventually get rate limited (429)
        self.assertIn(429, responses[-5:])  # Check last 5 responses
        
    def test_load_balancing(self):
        """Test load balancing across multiple instances."""
        # Make multiple requests and check for different server instances
        server_ids = set()
        
        for _ in range(10):
            response = requests.get(
                urljoin(self.base_url, '/health'),
                timeout=self.timeout
            )
            
            # Check for server identifier in response headers
            server_id = response.headers.get('X-Server-ID')
            if server_id:
                server_ids.add(server_id)
                
        # Should have multiple server instances in production
        if os.getenv('ENVIRONMENT') == 'production':
            self.assertGreater(len(server_ids), 1)
    
    def test_kubernetes_health_checks(self):
        """Test Kubernetes-specific health checks."""
        # Test liveness probe endpoint
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        # Test readiness probe endpoint
        response = requests.get(
            urljoin(self.base_url, '/ready'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        # Test startup probe endpoint
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
    
    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint."""
        response = requests.get(
            urljoin(self.base_url, '/metrics'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        # Check for Prometheus format
        self.assertIn('text/plain', response.headers.get('content-type', ''))
        
        # Check for basic metrics
        metrics_text = response.text
        self.assertIn('http_requests_total', metrics_text)
        self.assertIn('http_request_duration_seconds', metrics_text)
    
    def test_service_discovery(self):
        """Test service discovery and internal communication."""
        # Test internal service communication
        response = requests.get(
            urljoin(self.base_url, '/api/v1/status'),
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            status_data = response.json()
            self.assertIn('services', status_data)
            
            # Check that services can communicate
            services = status_data.get('services', {})
            for service_name, service_status in services.items():
                self.assertIn('status', service_status)
                self.assertIn(service_status['status'], ['healthy', 'warning'])
    
    def test_horizontal_pod_autoscaler(self):
        """Test HPA configuration and scaling."""
        if os.getenv('ENVIRONMENT') != 'production':
            self.skipTest("HPA testing only in production")
        
        # This would require kubectl access in the test environment
        # For now, just test that the application can handle load
        import threading
        import time
        
        def load_test():
            for _ in range(50):
                try:
                    requests.get(
                        urljoin(self.base_url, '/health'),
                        timeout=5
                    )
                    time.sleep(0.1)
                except:
                    pass
        
        # Start load test threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=load_test)
            threads.append(thread)
            thread.start()
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()
        
        # Application should still be responsive
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)


class TestDeploymentPerformance(unittest.TestCase):
    """Test deployment performance characteristics."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        self.timeout = 30
        
    def test_response_time_health_check(self):
        """Test health check response time."""
        start_time = time.time()
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        response_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.0)  # Should respond within 1 second
        
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.get(
                    urljoin(self.base_url, '/health'),
                    timeout=self.timeout
                )
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
                
        # Start 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
                
        # At least 80% should succeed
        self.assertGreaterEqual(success_count, 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)