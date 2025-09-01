# test_integration_offline.py - Integration tests for offline mode and model optimization
import pytest
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.services.integration_service import (
    OfflineIntegrationService, ServiceHealth, get_integration_service
)
from src.services.offline_mode_service import ConnectivityStatus, ServiceStatus
from src.services.model_optimization_service import OptimizationTarget, ModelFormat

class TestOfflineIntegrationService:
    """Test offline integration service functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = OfflineIntegrationService()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        try:
            self.service.shutdown()
        except:
            pass
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_service_registration(self):
        """Test service registration"""
        self.service._register_services()
        
        assert 'image_analysis' in self.service.service_registry
        assert 'nlp_service' in self.service.service_registry
        assert 'speech_service' in self.service.service_registry
        assert 'explainable_ai' in self.service.service_registry
        
        # Check offline capabilities
        image_service = self.service.service_registry['image_analysis']
        assert image_service['offline_capable']
        assert 'mock_analysis' in image_service['fallback_methods']
        
        speech_service = self.service.service_registry['speech_service']
        assert not speech_service['offline_capable']
    
    def test_initialization(self):
        """Test service initialization"""
        with patch.object(self.service.offline_service, 'initialize'), \
             patch.object(self.service.offline_service, 'register_status_callback'), \
             patch.object(self.service, 'check_all_services_health'):
            
            self.service.initialize()
            
            assert self.service.initialized
            assert self.service.offline_service.initialize.called
            assert self.service.offline_service.register_status_callback.called
    
    def test_status_change_handling(self):
        """Test handling of system status changes"""
        # Mock system status
        mock_status = Mock()
        mock_status.offline_mode_active = True
        
        with patch.object(self.service, '_handle_offline_transition') as mock_offline, \
             patch.object(self.service, '_handle_online_transition') as mock_online:
            
            # Test offline transition
            self.service._on_status_change(mock_status)
            mock_offline.assert_called_once()
            
            # Test online transition
            mock_status.offline_mode_active = False
            self.service._on_status_change(mock_status)
            mock_online.assert_called_once()
    
    def test_service_health_check_online(self):
        """Test service health check when online"""
        self.service._register_services()
        
        with patch('src.services.integration_service.is_offline_mode_active', return_value=False):
            health_results = self.service.check_all_services_health()
            
            assert len(health_results) == len(self.service.service_registry)
            
            # All services should be healthy when online
            for service_name, health in health_results.items():
                assert isinstance(health, ServiceHealth)
                assert health.status == "healthy"
                assert health.details["mode"] == "online"
    
    def test_service_health_check_offline(self):
        """Test service health check when offline"""
        self.service._register_services()
        
        with patch('src.services.integration_service.is_offline_mode_active', return_value=True):
            health_results = self.service.check_all_services_health()
            
            # Check offline-capable services
            image_health = health_results['image_analysis']
            assert image_health.status == "degraded"
            assert image_health.offline_capable
            
            # Check non-offline-capable services
            speech_health = health_results['speech_service']
            assert speech_health.status == "unhealthy"
            assert not speech_health.offline_capable
    
    def test_system_overview(self):
        """Test system overview generation"""
        self.service._register_services()
        
        with patch.object(self.service.offline_service, 'get_system_status') as mock_status, \
             patch.object(self.service.optimization_service, 'get_optimization_stats') as mock_stats:
            
            # Mock system status
            mock_system_status = Mock()
            mock_system_status.connectivity.value = "online"
            mock_system_status.offline_mode_active = False
            mock_system_status.available_features = ["feature1", "feature2"]
            mock_system_status.degraded_features = []
            mock_system_status.last_online = None
            mock_system_status.estimated_restoration = None
            mock_status.return_value = mock_system_status
            
            # Mock optimization stats
            mock_stats.return_value = {
                'total_optimizations': 5,
                'cache_stats': {
                    'total_cache_size_mb': 100.0,
                    'total_cached_models': 3
                }
            }
            
            # Add some health checks
            self.service.health_checks = {
                'service1': ServiceHealth('service1', 'healthy', True, datetime.now(), {}),
                'service2': ServiceHealth('service2', 'degraded', True, datetime.now(), {})
            }
            
            overview = self.service.get_system_overview()
            
            assert 'system_status' in overview
            assert 'services' in overview
            assert 'features' in overview
            assert 'optimization' in overview
            assert 'timestamp' in overview
            
            assert overview['services']['total'] == len(self.service.service_registry)
            assert overview['services']['healthy'] == 1
            assert overview['services']['degraded'] == 1
    
    def test_model_optimization_for_offline(self):
        """Test model optimization for offline deployment"""
        # Create mock model files
        model_paths = []
        for i in range(2):
            model_path = self.temp_dir / f"model_{i}.pth"
            model_path.write_bytes(b"0" * (5 * 1024 * 1024))  # 5MB
            model_paths.append(model_path)
        
        with patch.object(self.service.optimization_service, 'batch_optimize_models') as mock_optimize:
            # Mock successful optimization results
            mock_results = [
                Mock(
                    success=True,
                    original_size_mb=5.0,
                    optimized_size_mb=2.0,
                    compression_ratio=0.4,
                    output_path=self.temp_dir / "optimized_1.tflite",
                    format=Mock(value="tflite"),
                    errors=[]
                ),
                Mock(
                    success=True,
                    original_size_mb=5.0,
                    optimized_size_mb=1.5,
                    compression_ratio=0.3,
                    output_path=self.temp_dir / "optimized_2.onnx",
                    format=Mock(value="onnx"),
                    errors=[]
                )
            ]
            mock_optimize.return_value = mock_results
            
            result = self.service.optimize_models_for_offline(model_paths)
            
            assert result["success"]
            assert result["total_models"] == 2
            assert result["successful"] == 2
            assert result["failed"] == 0
            assert result["total_size_reduction_mb"] == 6.5  # (5-2) + (5-1.5)
            assert len(result["optimized_models"]) == 2
    
    def test_offline_deployment_preparation(self):
        """Test offline deployment preparation"""
        output_dir = self.temp_dir / "deployment"
        
        with patch.object(self.service, 'optimize_models_for_offline') as mock_optimize:
            # Mock optimization result
            mock_optimize.return_value = {
                "success": True,
                "total_models": 2,
                "successful": 2,
                "failed": 0,
                "optimized_models": [
                    {
                        "path": str(self.temp_dir / "opt1.tflite"),
                        "format": "tflite",
                        "compression_ratio": 0.4,
                        "size_mb": 2.0
                    }
                ]
            }
            
            # Create mock optimized model
            opt_model = self.temp_dir / "opt1.tflite"
            opt_model.write_bytes(b"0" * (2 * 1024 * 1024))
            
            self.service._register_services()
            result = self.service.prepare_offline_deployment(output_dir)
            
            assert result["success"]
            assert output_dir.exists()
            
            # Check config file was created
            config_file = output_dir / "offline_deployment_config.json"
            assert config_file.exists()
            
            # Verify config content
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            assert config["offline_mode"]
            assert "service_configurations" in config
            assert "optimization_stats" in config
    
    def test_offline_functionality_testing(self):
        """Test offline functionality testing"""
        self.service._register_services()
        
        with patch.object(self.service.offline_service, 'force_offline_mode') as mock_force, \
             patch('src.services.integration_service.is_offline_mode_active') as mock_offline:
            
            # Mock offline mode state
            mock_offline.side_effect = [False, True, False]  # original, during test, restored
            
            result = self.service.test_offline_functionality()
            
            assert result["success"]
            assert result["total_tests"] == len(self.service.service_registry)
            assert result["passed_tests"] > 0
            assert "test_results" in result
            assert "offline_capable_services" in result
            
            # Verify offline mode was toggled
            assert mock_force.call_count == 2  # Enable and restore
    
    def test_error_handling_in_health_check(self):
        """Test error handling during health checks"""
        self.service._register_services()
        
        with patch.object(self.service, '_check_service_health', side_effect=Exception("Test error")):
            health_results = self.service.check_all_services_health()
            
            # Should handle errors gracefully
            for service_name, health in health_results.items():
                assert health.status == "unhealthy"
                assert "error" in health.details
    
    def test_get_service_status(self):
        """Test getting individual service status"""
        # Add mock health check
        mock_health = ServiceHealth(
            service_name="test_service",
            status="healthy",
            offline_capable=True,
            last_check=datetime.now(),
            details={}
        )
        self.service.health_checks["test_service"] = mock_health
        
        status = self.service.get_service_status("test_service")
        assert status is mock_health
        
        # Test non-existent service
        status = self.service.get_service_status("non_existent")
        assert status is None

class TestIntegrationServiceIntegration:
    """Integration tests for the complete offline system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = OfflineIntegrationService()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        try:
            self.service.shutdown()
        except:
            pass
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_offline_workflow(self):
        """Test complete offline workflow"""
        # Initialize service
        with patch.object(self.service.offline_service, 'initialize'), \
             patch.object(self.service.offline_service, 'register_status_callback'):
            self.service.initialize()
        
        # Register services
        self.service._register_services()
        
        # Check initial health
        with patch('src.services.integration_service.is_offline_mode_active', return_value=False):
            health = self.service.check_all_services_health()
            assert all(h.status == "healthy" for h in health.values())
        
        # Simulate offline transition
        mock_status = Mock()
        mock_status.offline_mode_active = True
        
        with patch.object(self.service, '_handle_offline_transition') as mock_offline:
            self.service._on_status_change(mock_status)
            mock_offline.assert_called_once()
        
        # Check health in offline mode
        with patch('src.services.integration_service.is_offline_mode_active', return_value=True):
            offline_health = self.service.check_all_services_health()
            
            # Offline-capable services should be degraded
            assert offline_health['image_analysis'].status == "degraded"
            assert offline_health['nlp_service'].status == "degraded"
            
            # Non-offline-capable services should be unhealthy
            assert offline_health['speech_service'].status == "unhealthy"
    
    def test_model_optimization_integration(self):
        """Test integration with model optimization service"""
        # Create mock models
        model_paths = [self.temp_dir / "model.pth"]
        model_paths[0].write_bytes(b"0" * (10 * 1024 * 1024))
        
        # Test optimization
        with patch.object(self.service.optimization_service, 'batch_optimize_models') as mock_opt:
            mock_opt.return_value = [
                Mock(
                    success=True,
                    original_size_mb=10.0,
                    optimized_size_mb=3.0,
                    compression_ratio=0.3,
                    output_path=self.temp_dir / "opt.tflite",
                    format=Mock(value="tflite"),
                    errors=[]
                )
            ]
            
            result = self.service.optimize_models_for_offline(model_paths)
            
            assert result["success"]
            assert result["total_size_reduction_mb"] == 7.0
            
            # Verify optimization configs were used
            call_args = mock_opt.call_args
            configs = call_args[0][1]  # Second argument is configs
            
            # Should have configs for mobile and edge deployment
            target_platforms = [c.target_platform for c in configs]
            assert OptimizationTarget.MOBILE in target_platforms
            assert OptimizationTarget.EDGE in target_platforms

def test_integration_service_singleton():
    """Test integration service singleton pattern"""
    service1 = get_integration_service()
    service2 = get_integration_service()
    
    assert service1 is service2

def test_service_health_dataclass():
    """Test ServiceHealth dataclass"""
    health = ServiceHealth(
        service_name="test_service",
        status="healthy",
        offline_capable=True,
        last_check=datetime.now(),
        details={"mode": "online"}
    )
    
    assert health.service_name == "test_service"
    assert health.status == "healthy"
    assert health.offline_capable
    assert health.details["mode"] == "online"

@pytest.fixture
def mock_offline_service():
    """Fixture for mocking offline service"""
    with patch('src.services.integration_service.get_offline_service') as mock:
        mock_service = Mock()
        mock_service.get_system_status.return_value = Mock(
            connectivity=Mock(value="online"),
            offline_mode_active=False,
            available_features=[],
            degraded_features=[],
            last_online=None,
            estimated_restoration=None
        )
        mock.return_value = mock_service
        yield mock_service

@pytest.fixture
def mock_optimization_service():
    """Fixture for mocking optimization service"""
    with patch('src.services.integration_service.get_optimization_service') as mock:
        mock_service = Mock()
        mock_service.get_optimization_stats.return_value = {
            'total_optimizations': 0,
            'cache_stats': {
                'total_cache_size_mb': 0.0,
                'total_cached_models': 0
            }
        }
        mock.return_value = mock_service
        yield mock_service

def test_integration_with_mocked_services(mock_offline_service, mock_optimization_service):
    """Test integration service with mocked dependencies"""
    service = OfflineIntegrationService()
    service._register_services()
    
    overview = service.get_system_overview()
    
    assert 'system_status' in overview
    assert 'services' in overview
    assert 'optimization' in overview
    
    # Verify mocked services were called
    mock_offline_service.get_system_status.assert_called_once()
    mock_optimization_service.get_optimization_stats.assert_called_once()