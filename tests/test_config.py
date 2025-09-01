# test_config.py - Tests for configuration system
import unittest
import tempfile
import json
from pathlib import Path
from src.config import get_config, validate_config, AppConfig, Environment
from src.utils.config_manager import ConfigManager
from src.utils.app_initializer import initialize_app, get_app_status

class TestConfiguration(unittest.TestCase):
    """Test configuration system functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager()
    
    def test_get_config(self):
        """Test basic configuration loading"""
        config = get_config()
        
        # Check that all major sections exist
        self.assertIn('app', config)
        self.assertIn('model', config)
        self.assertIn('api', config)
        self.assertIn('paths', config)
    
    def test_validate_config(self):
        """Test configuration validation"""
        # Should pass with default configuration
        self.assertTrue(validate_config())
    
    def test_config_manager_get_set(self):
        """Test configuration manager get/set functionality"""
        # Test setting and getting a value
        self.config_manager.set('test.value', 'test_data')
        self.assertEqual(self.config_manager.get('test.value'), 'test_data')
        
        # Test default value
        self.assertEqual(self.config_manager.get('nonexistent.key', 'default'), 'default')
    
    def test_environment_config_loading(self):
        """Test environment-specific configuration loading"""
        # Create temporary config file
        temp_config = Path(self.temp_dir) / 'test.json'
        test_config = {
            'app': {
                'DEBUG': True,
                'TEST_VALUE': 'from_file'
            }
        }
        
        with open(temp_config, 'w') as f:
            json.dump(test_config, f)
        
        # Load the config
        self.config_manager.load_environment_config(temp_config)
        
        # Verify the value was loaded
        self.assertEqual(self.config_manager.get('app.TEST_VALUE'), 'from_file')
    
    def test_app_initialization(self):
        """Test application initialization"""
        # Test initialization
        result = initialize_app()
        self.assertTrue(result)
        
        # Check status
        status = get_app_status()
        self.assertTrue(status['initialized'])
        self.assertIn('environment', status)
    
    def test_config_export(self):
        """Test configuration export functionality"""
        # Export config
        exported_config = self.config_manager.export_config()
        
        # Verify structure
        self.assertIsInstance(exported_config, dict)
        self.assertIn('app', exported_config)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()