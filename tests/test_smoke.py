# -*- coding: utf-8 -*-
"""Smoke tests for AI Wellness Vision system."""

import unittest
import requests
import os
from urllib.parse import urljoin


class TestSmokeTests(unittest.TestCase):
    """Critical smoke tests for production deployment."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        self.timeout = 10
        
    def test_application_is_running(self):
        """Test that the application is running and responding."""
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
    def test_database_is_accessible(self):
        """Test that database is accessible."""
        response = requests.get(
            urljoin(self.base_url, '/health/database'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['database']['status'], 'connected')
        
    def test_redis_is_accessible(self):
        """Test that Redis is accessible."""
        response = requests.get(
            urljoin(self.base_url, '/health/redis'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['redis']['status'], 'connected')
        
    def test_api_documentation_accessible(self):
        """Test that API documentation is accessible."""
        response = requests.get(
            urljoin(self.base_url, '/docs'),
            timeout=self.timeout
        )
        self.assertEqual(response.status_code, 200)
        
    def test_critical_endpoints_respond(self):
        """Test that critical endpoints respond without errors."""
        critical_endpoints = [
            '/health',
            '/ready',
            '/metrics',
            '/docs'
        ]
        
        for endpoint in critical_endpoints:
            with self.subTest(endpoint=endpoint):
                response = requests.get(
                    urljoin(self.base_url, endpoint),
                    timeout=self.timeout
                )
                # Should not return server errors
                self.assertLess(response.status_code, 500)
                
    def test_environment_configuration(self):
        """Test that environment is properly configured."""
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        
        data = response.json()
        
        # Check environment-specific configurations
        if os.getenv('ENVIRONMENT') == 'production':
            self.assertIn('environment', data)
            self.assertEqual(data['environment'], 'production')
            
    def test_security_basics(self):
        """Test basic security configurations."""
        response = requests.get(
            urljoin(self.base_url, '/health'),
            timeout=self.timeout
        )
        
        # Check for basic security headers
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertIn('X-Frame-Options', response.headers)


if __name__ == "__main__":
    unittest.main(verbosity=2)