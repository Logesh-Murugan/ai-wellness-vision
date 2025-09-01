# offline_mode_service.py - Offline mode detection and graceful degradation
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from src.config import AppConfig
from src.utils.logging_config import get_logger, log_performance

logger = get_logger(__name__)

class ConnectivityStatus(Enum):
    """Network connectivity status"""
    ONLINE = "online"
    OFFLINE = "offline"
    LIMITED = "limited"
    UNKNOWN = "unknown"

class ServiceStatus(Enum):
    """Service availability status"""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

@dataclass
class OfflineCapability:
    """Defines offline capabilities for a service"""
    service_name: str
    supports_offline: bool = False
    offline_features: List[str] = field(default_factory=list)
    fallback_method: Optional[str] = None
    cache_duration: int = 3600  # seconds
    priority: int = 1  # 1=high, 2=medium, 3=low

@dataclass
class SystemStatus:
    """Overall system status information"""
    connectivity: ConnectivityStatus
    services: Dict[str, ServiceStatus]
    offline_mode_active: bool
    degraded_features: List[str]
    available_features: List[str]
    last_online: Optional[datetime] = None
    estimated_restoration: Optional[datetime] = None

class ConnectivityMonitor:
    """Monitors network connectivity and service availability"""
    
    def __init__(self):
        self.connectivity_status = ConnectivityStatus.UNKNOWN
        self.last_check = None
        self.check_interval = 30  # seconds
        self.monitoring_active = False
        self.connectivity_history = []
        self._stop_monitoring = threading.Event()
    
    def start_monitoring(self) -> None:
        """Start continuous connectivity monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self._stop_monitoring.clear()
        
        def monitor_loop():
            while not self._stop_monitoring.wait(self.check_interval):
                try:
                    self.check_connectivity()
                except Exception as e:
                    logger.error(f"Connectivity check failed: {e}")
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Connectivity monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop connectivity monitoring"""
        self.monitoring_active = False
        self._stop_monitoring.set()
        logger.info("Connectivity monitoring stopped")
    
    def check_connectivity(self) -> ConnectivityStatus:
        """Check current network connectivity"""
        try:
            import socket
            import urllib.request
            
            # Test basic internet connectivity
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            
            # Test HTTP connectivity
            try:
                urllib.request.urlopen('http://www.google.com', timeout=5)
                status = ConnectivityStatus.ONLINE
            except:
                status = ConnectivityStatus.LIMITED
            
        except Exception:
            status = ConnectivityStatus.OFFLINE
        
        # Update status and history
        previous_status = self.connectivity_status
        self.connectivity_status = status
        self.last_check = datetime.now()
        
        # Track connectivity changes
        if previous_status != status:
            self.connectivity_history.append({
                'timestamp': self.last_check,
                'previous': previous_status.value,
                'current': status.value
            })
            
            # Keep only last 100 entries
            if len(self.connectivity_history) > 100:
                self.connectivity_history = self.connectivity_history[-100:]
            
            logger.info(f"Connectivity status changed: {previous_status.value} -> {status.value}")
        
        return status
    
    def get_connectivity_stats(self) -> Dict[str, Any]:
        """Get connectivity statistics"""
        if not self.connectivity_history:
            return {
                'current_status': self.connectivity_status.value,
                'uptime_percentage': 0.0,
                'last_check': self.last_check,
                'total_checks': 0
            }
        
        # Calculate uptime percentage
        online_count = sum(1 for entry in self.connectivity_history 
                          if entry['current'] == ConnectivityStatus.ONLINE.value)
        uptime_percentage = (online_count / len(self.connectivity_history)) * 100
        
        return {
            'current_status': self.connectivity_status.value,
            'uptime_percentage': uptime_percentage,
            'last_check': self.last_check,
            'total_checks': len(self.connectivity_history),
            'recent_changes': self.connectivity_history[-10:]
        }

class FeatureDegradationManager:
    """Manages graceful feature degradation in offline mode"""
    
    def __init__(self):
        self.offline_capabilities = self._define_offline_capabilities()
        self.current_degradations = {}
        self.fallback_responses = self._load_fallback_responses()
    
    def _define_offline_capabilities(self) -> Dict[str, OfflineCapability]:
        """Define offline capabilities for each service"""
        return {
            'image_analysis': OfflineCapability(
                service_name='image_analysis',
                supports_offline=True,
                offline_features=['basic_validation', 'mock_analysis', 'cached_results'],
                fallback_method='mock_analysis',
                cache_duration=7200,
                priority=1
            ),
            'nlp_service': OfflineCapability(
                service_name='nlp_service',
                supports_offline=True,
                offline_features=['keyword_analysis', 'basic_responses', 'cached_conversations'],
                fallback_method='keyword_responses',
                cache_duration=3600,
                priority=1
            ),
            'speech_service': OfflineCapability(
                service_name='speech_service',
                supports_offline=False,
                offline_features=['cached_audio'],
                fallback_method='text_only',
                cache_duration=1800,
                priority=2
            ),
            'explainable_ai': OfflineCapability(
                service_name='explainable_ai',
                supports_offline=True,
                offline_features=['basic_explanations', 'template_responses'],
                fallback_method='template_explanations',
                cache_duration=3600,
                priority=2
            )
        }
    
    def _load_fallback_responses(self) -> Dict[str, Dict[str, Any]]:
        """Load fallback responses for offline mode"""
        return {
            'image_analysis': {
                'skin_analysis': {
                    'message': 'Image analysis is currently unavailable. Please try again when online.',
                    'suggestions': [
                        'Check your internet connection',
                        'Try again in a few minutes',
                        'Contact support if the issue persists'
                    ]
                },
                'food_recognition': {
                    'message': 'Food recognition requires an internet connection.',
                    'suggestions': [
                        'Manually log your food items',
                        'Use the nutrition database when online',
                        'Take photos to analyze later'
                    ]
                }
            },
            'nlp_service': {
                'conversation': {
                    'message': 'I\'m currently in offline mode with limited capabilities.',
                    'available_features': [
                        'Basic health information',
                        'Emergency contact information',
                        'Cached previous conversations'
                    ]
                }
            },
            'speech_service': {
                'transcription': {
                    'message': 'Speech recognition is not available offline.',
                    'alternatives': [
                        'Use text input instead',
                        'Record audio to process later',
                        'Use voice memos app'
                    ]
                }
            }
        }
    
    def assess_degradation_needs(self, connectivity: ConnectivityStatus, 
                                service_statuses: Dict[str, ServiceStatus]) -> Dict[str, Any]:
        """Assess what features need to be degraded"""
        degradation_plan = {
            'services_to_degrade': [],
            'features_to_disable': [],
            'fallback_methods': {},
            'user_notifications': []
        }
        
        for service_name, capability in self.offline_capabilities.items():
            service_status = service_statuses.get(service_name, ServiceStatus.UNAVAILABLE)
            
            if connectivity == ConnectivityStatus.OFFLINE or service_status == ServiceStatus.UNAVAILABLE:
                if capability.supports_offline:
                    # Service can operate in degraded mode
                    degradation_plan['services_to_degrade'].append(service_name)
                    degradation_plan['fallback_methods'][service_name] = capability.fallback_method
                else:
                    # Service must be disabled
                    degradation_plan['features_to_disable'].append(service_name)
                    
                    # Add user notification
                    fallback_info = self.fallback_responses.get(service_name, {})
                    if fallback_info:
                        degradation_plan['user_notifications'].append({
                            'service': service_name,
                            'message': fallback_info.get('message', f'{service_name} is unavailable'),
                            'suggestions': fallback_info.get('suggestions', [])
                        })
        
        return degradation_plan
    
    def apply_degradation(self, degradation_plan: Dict[str, Any]) -> None:
        """Apply the degradation plan"""
        for service_name in degradation_plan['services_to_degrade']:
            self.current_degradations[service_name] = {
                'status': 'degraded',
                'fallback_method': degradation_plan['fallback_methods'].get(service_name),
                'applied_at': datetime.now()
            }
            logger.info(f"Applied degradation to {service_name}")
        
        for service_name in degradation_plan['features_to_disable']:
            self.current_degradations[service_name] = {
                'status': 'disabled',
                'applied_at': datetime.now()
            }
            logger.info(f"Disabled {service_name}")
    
    def restore_services(self, connectivity: ConnectivityStatus,
                        service_statuses: Dict[str, ServiceStatus]) -> List[str]:
        """Restore services when connectivity is restored"""
        restored_services = []
        
        for service_name, degradation_info in list(self.current_degradations.items()):
            service_status = service_statuses.get(service_name, ServiceStatus.UNAVAILABLE)
            
            if (connectivity == ConnectivityStatus.ONLINE and 
                service_status == ServiceStatus.AVAILABLE):
                
                del self.current_degradations[service_name]
                restored_services.append(service_name)
                logger.info(f"Restored {service_name}")
        
        return restored_services
    
    def get_degradation_status(self) -> Dict[str, Any]:
        """Get current degradation status"""
        return {
            'active_degradations': self.current_degradations,
            'degraded_services': [name for name, info in self.current_degradations.items() 
                                 if info['status'] == 'degraded'],
            'disabled_services': [name for name, info in self.current_degradations.items() 
                                 if info['status'] == 'disabled'],
            'total_degraded': len(self.current_degradations)
        }

class OfflineModeService:
    """Main service for managing offline mode and graceful degradation"""
    
    def __init__(self):
        self.connectivity_monitor = ConnectivityMonitor()
        self.degradation_manager = FeatureDegradationManager()
        self.offline_mode_active = False
        self.system_status = SystemStatus(
            connectivity=ConnectivityStatus.UNKNOWN,
            services={},
            offline_mode_active=False,
            degraded_features=[],
            available_features=[]
        )
        self.status_callbacks = []
    
    def initialize(self) -> None:
        """Initialize the offline mode service"""
        try:
            # Start connectivity monitoring
            self.connectivity_monitor.start_monitoring()
            
            # Perform initial status check
            self.update_system_status()
            
            logger.info("Offline mode service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize offline mode service: {e}")
            raise
    
    def shutdown(self) -> None:
        """Shutdown the offline mode service"""
        try:
            self.connectivity_monitor.stop_monitoring()
            logger.info("Offline mode service shutdown")
        except Exception as e:
            logger.error(f"Error during offline mode service shutdown: {e}")
    
    @log_performance()
    def update_system_status(self) -> SystemStatus:
        """Update and return current system status"""
        try:
            # Check connectivity
            connectivity = self.connectivity_monitor.check_connectivity()
            
            # Check service statuses (mock implementation)
            service_statuses = self._check_service_statuses()
            
            # Assess degradation needs
            degradation_plan = self.degradation_manager.assess_degradation_needs(
                connectivity, service_statuses
            )
            
            # Apply degradation if needed
            if degradation_plan['services_to_degrade'] or degradation_plan['features_to_disable']:
                self.degradation_manager.apply_degradation(degradation_plan)
                self.offline_mode_active = True
            
            # Restore services if possible
            if connectivity == ConnectivityStatus.ONLINE:
                restored = self.degradation_manager.restore_services(connectivity, service_statuses)
                if restored and not self.degradation_manager.current_degradations:
                    self.offline_mode_active = False
            
            # Update system status
            degradation_status = self.degradation_manager.get_degradation_status()
            
            self.system_status = SystemStatus(
                connectivity=connectivity,
                services=service_statuses,
                offline_mode_active=self.offline_mode_active,
                degraded_features=degradation_status['degraded_services'],
                available_features=self._get_available_features(service_statuses, degradation_status),
                last_online=self._get_last_online_time(),
                estimated_restoration=self._estimate_restoration_time()
            )
            
            # Notify callbacks
            self._notify_status_callbacks()
            
            return self.system_status
            
        except Exception as e:
            logger.error(f"Failed to update system status: {e}")
            return self.system_status
    
    def _check_service_statuses(self) -> Dict[str, ServiceStatus]:
        """Check the status of all services"""
        # Mock implementation - in production, this would check actual services
        services = ['image_analysis', 'nlp_service', 'speech_service', 'explainable_ai']
        statuses = {}
        
        for service in services:
            # Simulate service availability based on connectivity
            if self.connectivity_monitor.connectivity_status == ConnectivityStatus.ONLINE:
                statuses[service] = ServiceStatus.AVAILABLE
            elif self.connectivity_monitor.connectivity_status == ConnectivityStatus.LIMITED:
                statuses[service] = ServiceStatus.DEGRADED
            else:
                statuses[service] = ServiceStatus.UNAVAILABLE
        
        return statuses
    
    def _get_available_features(self, service_statuses: Dict[str, ServiceStatus],
                               degradation_status: Dict[str, Any]) -> List[str]:
        """Get list of currently available features"""
        available_features = []
        
        for service_name, status in service_statuses.items():
            if status == ServiceStatus.AVAILABLE:
                available_features.append(f"{service_name}_full")
            elif service_name in degradation_status['degraded_services']:
                capability = self.degradation_manager.offline_capabilities.get(service_name)
                if capability:
                    available_features.extend([f"{service_name}_{feature}" 
                                             for feature in capability.offline_features])
        
        return available_features
    
    def _get_last_online_time(self) -> Optional[datetime]:
        """Get the last time the system was online"""
        history = self.connectivity_monitor.connectivity_history
        for entry in reversed(history):
            if entry['current'] == ConnectivityStatus.ONLINE.value:
                return entry['timestamp']
        return None
    
    def _estimate_restoration_time(self) -> Optional[datetime]:
        """Estimate when services might be restored"""
        if self.connectivity_monitor.connectivity_status == ConnectivityStatus.ONLINE:
            return None
        
        # Simple estimation based on historical data
        # In production, this could be more sophisticated
        return datetime.now() + timedelta(minutes=15)
    
    def _notify_status_callbacks(self) -> None:
        """Notify registered callbacks about status changes"""
        for callback in self.status_callbacks:
            try:
                callback(self.system_status)
            except Exception as e:
                logger.error(f"Status callback failed: {e}")
    
    def register_status_callback(self, callback) -> None:
        """Register a callback for status changes"""
        self.status_callbacks.append(callback)
    
    def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        return self.system_status
    
    def get_offline_capabilities(self) -> Dict[str, OfflineCapability]:
        """Get offline capabilities for all services"""
        return self.degradation_manager.offline_capabilities
    
    def force_offline_mode(self, enabled: bool) -> None:
        """Force offline mode on/off for testing"""
        self.offline_mode_active = enabled
        if enabled:
            # Apply full degradation
            service_statuses = {name: ServiceStatus.UNAVAILABLE 
                              for name in self.degradation_manager.offline_capabilities.keys()}
            degradation_plan = self.degradation_manager.assess_degradation_needs(
                ConnectivityStatus.OFFLINE, service_statuses
            )
            self.degradation_manager.apply_degradation(degradation_plan)
        else:
            # Restore all services
            self.degradation_manager.current_degradations.clear()
        
        logger.info(f"Forced offline mode: {enabled}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring"""
        connectivity_stats = self.connectivity_monitor.get_connectivity_stats()
        degradation_status = self.degradation_manager.get_degradation_status()
        
        return {
            'service_name': 'offline_mode_service',
            'status': 'healthy' if not self.offline_mode_active else 'degraded',
            'connectivity': connectivity_stats,
            'degradation': degradation_status,
            'offline_mode_active': self.offline_mode_active,
            'last_status_update': datetime.now(),
            'uptime_percentage': connectivity_stats.get('uptime_percentage', 0.0)
        }

# Global offline mode service instance
offline_service = OfflineModeService()

def get_offline_service() -> OfflineModeService:
    """Get the global offline mode service instance"""
    return offline_service

def is_offline_mode_active() -> bool:
    """Check if offline mode is currently active"""
    return offline_service.offline_mode_active

def get_system_status() -> SystemStatus:
    """Get current system status"""
    return offline_service.get_system_status()