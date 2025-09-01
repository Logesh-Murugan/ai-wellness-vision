# test_offline_mode.py - Tests for offline mode functionality
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

from src.services.offline_mode_service import (
    OfflineModeService, ConnectivityMonitor, FeatureDegradationManager,
    ConnectivityStatus, ServiceStatus, OfflineCapability, SystemStatus
)

class TestConnectivityMonitor:
    """Test connectivity monitoring functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.monitor = ConnectivityMonitor()
    
    def teardown_method(self):
        """Clean up after tests"""
        if self.monitor.monitoring_active:
            self.monitor.stop_monitoring()
    
    def test_connectivity_check_online(self):
        """Test connectivity check when online"""
        with patch('socket.create_connection'), \
             patch('urllib.request.urlopen'):
            status = self.monitor.check_connectivity()
            assert status == ConnectivityStatus.ONLINE
    
    def test_connectivity_check_limited(self):
        """Test connectivity check with limited connectivity"""
        with patch('socket.create_connection'), \
             patch('urllib.request.urlopen', side_effect=Exception("HTTP failed")):
            status = self.monitor.check_connectivity()
            assert status == ConnectivityStatus.LIMITED
    
    def test_connectivity_check_offline(self):
        """Test connectivity check when offline"""
        with patch('socket.create_connection', side_effect=Exception("No connection")):
            status = self.monitor.check_connectivity()
            assert status == ConnectivityStatus.OFFLINE
    
    def test_monitoring_start_stop(self):
        """Test starting and stopping monitoring"""
        assert not self.monitor.monitoring_active
        
        self.monitor.start_monitoring()
        assert self.monitor.monitoring_active
        
        self.monitor.stop_monitoring()
        assert not self.monitor.monitoring_active
    
    def test_connectivity_history_tracking(self):
        """Test connectivity history tracking"""
        initial_count = len(self.monitor.connectivity_history)
        
        with patch('socket.create_connection'):
            self.monitor.check_connectivity()
        
        # Should add entry if status changed
        if self.monitor.connectivity_status != ConnectivityStatus.UNKNOWN:
            assert len(self.monitor.connectivity_history) > initial_count
    
    def test_connectivity_stats(self):
        """Test connectivity statistics"""
        # Add some mock history
        self.monitor.connectivity_history = [
            {'timestamp': datetime.now(), 'current': 'online', 'previous': 'offline'},
            {'timestamp': datetime.now(), 'current': 'online', 'previous': 'online'},
            {'timestamp': datetime.now(), 'current': 'offline', 'previous': 'online'},
        ]
        
        stats = self.monitor.get_connectivity_stats()
        
        assert 'current_status' in stats
        assert 'uptime_percentage' in stats
        assert 'total_checks' in stats
        assert stats['total_checks'] == 3

class TestFeatureDegradationManager:
    """Test feature degradation management"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = FeatureDegradationManager()
    
    def test_offline_capabilities_definition(self):
        """Test offline capabilities are properly defined"""
        capabilities = self.manager.offline_capabilities
        
        assert 'image_analysis' in capabilities
        assert 'nlp_service' in capabilities
        assert 'speech_service' in capabilities
        assert 'explainable_ai' in capabilities
        
        # Check image analysis supports offline
        image_cap = capabilities['image_analysis']
        assert image_cap.supports_offline
        assert 'mock_analysis' in image_cap.offline_features
    
    def test_degradation_assessment_offline(self):
        """Test degradation assessment when offline"""
        service_statuses = {
            'image_analysis': ServiceStatus.UNAVAILABLE,
            'nlp_service': ServiceStatus.UNAVAILABLE,
            'speech_service': ServiceStatus.UNAVAILABLE,
            'explainable_ai': ServiceStatus.UNAVAILABLE
        }
        
        plan = self.manager.assess_degradation_needs(
            ConnectivityStatus.OFFLINE, service_statuses
        )
        
        assert 'image_analysis' in plan['services_to_degrade']
        assert 'nlp_service' in plan['services_to_degrade']
        assert 'speech_service' in plan['features_to_disable']
        assert len(plan['user_notifications']) > 0
    
    def test_degradation_assessment_online(self):
        """Test degradation assessment when online"""
        service_statuses = {
            'image_analysis': ServiceStatus.AVAILABLE,
            'nlp_service': ServiceStatus.AVAILABLE,
            'speech_service': ServiceStatus.AVAILABLE,
            'explainable_ai': ServiceStatus.AVAILABLE
        }
        
        plan = self.manager.assess_degradation_needs(
            ConnectivityStatus.ONLINE, service_statuses
        )
        
        assert len(plan['services_to_degrade']) == 0
        assert len(plan['features_to_disable']) == 0
    
    def test_apply_degradation(self):
        """Test applying degradation plan"""
        plan = {
            'services_to_degrade': ['image_analysis', 'nlp_service'],
            'features_to_disable': ['speech_service'],
            'fallback_methods': {
                'image_analysis': 'mock_analysis',
                'nlp_service': 'keyword_responses'
            },
            'user_notifications': []
        }
        
        self.manager.apply_degradation(plan)
        
        assert 'image_analysis' in self.manager.current_degradations
        assert 'nlp_service' in self.manager.current_degradations
        assert 'speech_service' in self.manager.current_degradations
        
        assert self.manager.current_degradations['image_analysis']['status'] == 'degraded'
        assert self.manager.current_degradations['speech_service']['status'] == 'disabled'
    
    def test_restore_services(self):
        """Test service restoration"""
        # First apply some degradations
        self.manager.current_degradations = {
            'image_analysis': {'status': 'degraded', 'applied_at': datetime.now()},
            'speech_service': {'status': 'disabled', 'applied_at': datetime.now()}
        }
        
        service_statuses = {
            'image_analysis': ServiceStatus.AVAILABLE,
            'speech_service': ServiceStatus.AVAILABLE
        }
        
        restored = self.manager.restore_services(
            ConnectivityStatus.ONLINE, service_statuses
        )
        
        assert 'image_analysis' in restored
        assert 'speech_service' in restored
        assert len(self.manager.current_degradations) == 0
    
    def test_degradation_status(self):
        """Test getting degradation status"""
        self.manager.current_degradations = {
            'image_analysis': {'status': 'degraded', 'applied_at': datetime.now()},
            'speech_service': {'status': 'disabled', 'applied_at': datetime.now()}
        }
        
        status = self.manager.get_degradation_status()
        
        assert status['total_degraded'] == 2
        assert 'image_analysis' in status['degraded_services']
        assert 'speech_service' in status['disabled_services']

class TestOfflineModeService:
    """Test main offline mode service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = OfflineModeService()
    
    def teardown_method(self):
        """Clean up after tests"""
        try:
            self.service.shutdown()
        except:
            pass
    
    def test_initialization(self):
        """Test service initialization"""
        with patch.object(self.service.connectivity_monitor, 'start_monitoring'):
            self.service.initialize()
            assert self.service.connectivity_monitor.start_monitoring.called
    
    def test_system_status_update_online(self):
        """Test system status update when online"""
        with patch.object(self.service.connectivity_monitor, 'check_connectivity', 
                         return_value=ConnectivityStatus.ONLINE), \
             patch.object(self.service, '_check_service_statuses', 
                         return_value={'image_analysis': ServiceStatus.AVAILABLE}):
            
            status = self.service.update_system_status()
            
            assert status.connectivity == ConnectivityStatus.ONLINE
            assert not status.offline_mode_active
    
    def test_system_status_update_offline(self):
        """Test system status update when offline"""
        with patch.object(self.service.connectivity_monitor, 'check_connectivity', 
                         return_value=ConnectivityStatus.OFFLINE), \
             patch.object(self.service, '_check_service_statuses', 
                         return_value={'image_analysis': ServiceStatus.UNAVAILABLE}):
            
            status = self.service.update_system_status()
            
            assert status.connectivity == ConnectivityStatus.OFFLINE
            assert status.offline_mode_active
    
    def test_force_offline_mode(self):
        """Test forcing offline mode"""
        self.service.force_offline_mode(True)
        assert self.service.offline_mode_active
        
        self.service.force_offline_mode(False)
        assert not self.service.offline_mode_active
    
    def test_status_callbacks(self):
        """Test status change callbacks"""
        callback_called = False
        callback_status = None
        
        def test_callback(status):
            nonlocal callback_called, callback_status
            callback_called = True
            callback_status = status
        
        self.service.register_status_callback(test_callback)
        
        with patch.object(self.service.connectivity_monitor, 'check_connectivity', 
                         return_value=ConnectivityStatus.ONLINE):
            self.service.update_system_status()
        
        assert callback_called
        assert callback_status is not None
    
    def test_health_status(self):
        """Test health status reporting"""
        health = self.service.get_health_status()
        
        assert 'service_name' in health
        assert 'status' in health
        assert 'connectivity' in health
        assert 'degradation' in health
        assert health['service_name'] == 'offline_mode_service'
    
    def test_offline_capabilities(self):
        """Test getting offline capabilities"""
        capabilities = self.service.get_offline_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'image_analysis' in capabilities
        assert isinstance(capabilities['image_analysis'], OfflineCapability)

class TestOfflineModeIntegration:
    """Integration tests for offline mode functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = OfflineModeService()
    
    def teardown_method(self):
        """Clean up after tests"""
        try:
            self.service.shutdown()
        except:
            pass
    
    def test_offline_to_online_transition(self):
        """Test transition from offline to online mode"""
        # Start offline
        with patch.object(self.service.connectivity_monitor, 'check_connectivity', 
                         return_value=ConnectivityStatus.OFFLINE):
            status = self.service.update_system_status()
            assert status.offline_mode_active
        
        # Transition to online
        with patch.object(self.service.connectivity_monitor, 'check_connectivity', 
                         return_value=ConnectivityStatus.ONLINE), \
             patch.object(self.service, '_check_service_statuses', 
                         return_value={
                             'image_analysis': ServiceStatus.AVAILABLE,
                             'nlp_service': ServiceStatus.AVAILABLE,
                             'speech_service': ServiceStatus.AVAILABLE,
                             'explainable_ai': ServiceStatus.AVAILABLE
                         }):
            status = self.service.update_system_status()
            assert not status.offline_mode_active
    
    def test_partial_service_availability(self):
        """Test handling partial service availability"""
        service_statuses = {
            'image_analysis': ServiceStatus.AVAILABLE,
            'nlp_service': ServiceStatus.DEGRADED,
            'speech_service': ServiceStatus.UNAVAILABLE,
            'explainable_ai': ServiceStatus.AVAILABLE
        }
        
        with patch.object(self.service.connectivity_monitor, 'check_connectivity', 
                         return_value=ConnectivityStatus.LIMITED), \
             patch.object(self.service, '_check_service_statuses', 
                         return_value=service_statuses):
            
            status = self.service.update_system_status()
            
            # Should have some degraded features but not full offline mode
            assert len(status.degraded_features) > 0
            assert 'speech_service' not in status.available_features

@pytest.fixture
def mock_connectivity_online():
    """Fixture for mocking online connectivity"""
    with patch('socket.create_connection'), \
         patch('urllib.request.urlopen'):
        yield

@pytest.fixture
def mock_connectivity_offline():
    """Fixture for mocking offline connectivity"""
    with patch('socket.create_connection', side_effect=Exception("No connection")):
        yield

def test_offline_mode_service_singleton():
    """Test that offline mode service works as singleton"""
    from src.services.offline_mode_service import get_offline_service, is_offline_mode_active
    
    service1 = get_offline_service()
    service2 = get_offline_service()
    
    assert service1 is service2
    
    # Test convenience functions
    service1.offline_mode_active = True
    assert is_offline_mode_active()
    
    service1.offline_mode_active = False
    assert not is_offline_mode_active()

def test_system_status_dataclass():
    """Test SystemStatus dataclass functionality"""
    status = SystemStatus(
        connectivity=ConnectivityStatus.ONLINE,
        services={'test': ServiceStatus.AVAILABLE},
        offline_mode_active=False,
        degraded_features=[],
        available_features=['test_feature']
    )
    
    assert status.connectivity == ConnectivityStatus.ONLINE
    assert not status.offline_mode_active
    assert 'test_feature' in status.available_features

def test_offline_capability_dataclass():
    """Test OfflineCapability dataclass functionality"""
    capability = OfflineCapability(
        service_name='test_service',
        supports_offline=True,
        offline_features=['feature1', 'feature2'],
        fallback_method='mock_method',
        cache_duration=3600,
        priority=1
    )
    
    assert capability.service_name == 'test_service'
    assert capability.supports_offline
    assert len(capability.offline_features) == 2
    assert capability.fallback_method == 'mock_method'