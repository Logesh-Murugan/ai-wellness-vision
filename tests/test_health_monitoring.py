# test_health_monitoring.py - Tests for health monitoring system
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.utils.health_monitoring import (
    HealthMonitoringService, SystemMetricsCollector, ServiceHealthChecker,
    HealthStatus, ComponentType, HealthMetric, ComponentHealth,
    get_health_monitor, start_health_monitoring, stop_health_monitoring,
    register_service_health_check, get_current_system_health
)

class TestHealthMetric:
    """Test health metric functionality"""
    
    def test_health_metric_creation(self):
        """Test creating health metric"""
        metric = HealthMetric(
            name="cpu_usage",
            value=75.5,
            unit="percent",
            threshold_warning=80.0,
            threshold_critical=95.0
        )
        
        assert metric.name == "cpu_usage"
        assert metric.value == 75.5
        assert metric.unit == "percent"
        assert metric.threshold_warning == 80.0
        assert metric.threshold_critical == 95.0
    
    def test_health_metric_status_healthy(self):
        """Test health metric status determination - healthy"""
        metric = HealthMetric(
            name="memory_usage",
            value=60.0,
            threshold_warning=80.0,
            threshold_critical=95.0
        )
        
        assert metric.get_status() == HealthStatus.HEALTHY
    
    def test_health_metric_status_warning(self):
        """Test health metric status determination - warning"""
        metric = HealthMetric(
            name="disk_usage",
            value=85.0,
            threshold_warning=80.0,
            threshold_critical=95.0
        )
        
        assert metric.get_status() == HealthStatus.WARNING
    
    def test_health_metric_status_critical(self):
        """Test health metric status determination - critical"""
        metric = HealthMetric(
            name="cpu_usage",
            value=98.0,
            threshold_warning=80.0,
            threshold_critical=95.0
        )
        
        assert metric.get_status() == HealthStatus.CRITICAL
    
    def test_health_metric_status_unknown(self):
        """Test health metric status for non-numeric values"""
        metric = HealthMetric(
            name="service_status",
            value="running"
        )
        
        assert metric.get_status() == HealthStatus.UNKNOWN

class TestComponentHealth:
    """Test component health functionality"""
    
    def test_component_health_creation(self):
        """Test creating component health"""
        health = ComponentHealth(
            component_name="database",
            component_type=ComponentType.DATABASE,
            status=HealthStatus.HEALTHY
        )
        
        assert health.component_name == "database"
        assert health.component_type == ComponentType.DATABASE
        assert health.status == HealthStatus.HEALTHY
        assert len(health.metrics) == 0
    
    def test_add_metric_healthy(self):
        """Test adding healthy metric"""
        health = ComponentHealth(
            component_name="service",
            component_type=ComponentType.SERVICE,
            status=HealthStatus.HEALTHY
        )
        
        metric = HealthMetric(
            name="response_time",
            value=100.0,
            threshold_warning=1000.0
        )
        
        health.add_metric(metric)
        
        assert "response_time" in health.metrics
        assert health.status == HealthStatus.HEALTHY  # Should remain healthy
    
    def test_add_metric_warning(self):
        """Test adding warning metric updates status"""
        health = ComponentHealth(
            component_name="service",
            component_type=ComponentType.SERVICE,
            status=HealthStatus.HEALTHY
        )
        
        metric = HealthMetric(
            name="response_time",
            value=1500.0,
            threshold_warning=1000.0,
            threshold_critical=5000.0
        )
        
        health.add_metric(metric)
        
        assert health.status == HealthStatus.WARNING
    
    def test_add_metric_critical(self):
        """Test adding critical metric updates status"""
        health = ComponentHealth(
            component_name="service",
            component_type=ComponentType.SERVICE,
            status=HealthStatus.HEALTHY
        )
        
        metric = HealthMetric(
            name="error_rate",
            value=98.0,
            threshold_warning=80.0,
            threshold_critical=95.0
        )
        
        health.add_metric(metric)
        
        assert health.status == HealthStatus.CRITICAL
    
    def test_to_dict(self):
        """Test converting component health to dictionary"""
        health = ComponentHealth(
            component_name="api_service",
            component_type=ComponentType.SERVICE,
            status=HealthStatus.WARNING,
            error_message="High response time",
            details={"version": "1.0.0"}
        )
        
        metric = HealthMetric(
            name="response_time",
            value=1200.0,
            unit="ms"
        )
        health.add_metric(metric)
        
        health_dict = health.to_dict()
        
        assert health_dict["component_name"] == "api_service"
        assert health_dict["component_type"] == "service"
        assert health_dict["status"] == "warning"
        assert health_dict["error_message"] == "High response time"
        assert health_dict["details"]["version"] == "1.0.0"
        assert "response_time" in health_dict["metrics"]
        assert health_dict["metrics"]["response_time"]["value"] == 1200.0

class TestSystemMetricsCollector:
    """Test system metrics collection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.collector = SystemMetricsCollector()
    
    @patch('src.utils.health_monitoring.PSUTIL_AVAILABLE', True)
    @patch('src.utils.health_monitoring.psutil')
    def test_collect_metrics_with_psutil(self, mock_psutil):
        """Test metrics collection with psutil available"""
        # Mock psutil functions
        mock_psutil.cpu_percent.return_value = 45.5
        mock_psutil.virtual_memory.return_value = Mock(percent=60.0, available=8*1024**3)
        mock_psutil.disk_usage.return_value = Mock(percent=70.0, free=100*1024**3)
        mock_psutil.net_io_counters.return_value = Mock(bytes_sent=1000000, bytes_recv=2000000)
        mock_psutil.pids.return_value = list(range(150))
        
        metrics = self.collector.collect_metrics()
        
        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics
        assert "network_bytes_sent" in metrics
        assert "process_count" in metrics
        
        assert metrics["cpu_usage"].value == 45.5
        assert metrics["memory_usage"].value == 60.0
        assert metrics["disk_usage"].value == 70.0
        assert metrics["process_count"].value == 150
    
    @patch('src.utils.health_monitoring.PSUTIL_AVAILABLE', False)
    def test_collect_metrics_without_psutil(self):
        """Test metrics collection without psutil"""
        metrics = self.collector.collect_metrics()
        
        assert "system_available" in metrics
        assert metrics["system_available"].value == 1
    
    @patch('src.utils.health_monitoring.PSUTIL_AVAILABLE', True)
    @patch('src.utils.health_monitoring.psutil')
    def test_collect_metrics_with_error(self, mock_psutil):
        """Test metrics collection with error"""
        mock_psutil.cpu_percent.side_effect = Exception("CPU error")
        
        metrics = self.collector.collect_metrics()
        
        assert "collection_error" in metrics
        assert "CPU error" in str(metrics["collection_error"].value)
    
    def test_get_system_health(self):
        """Test getting system health"""
        with patch.object(self.collector, 'collect_metrics') as mock_collect:
            mock_metrics = {
                "cpu_usage": HealthMetric("cpu_usage", 50.0, "percent", 80.0, 95.0),
                "memory_usage": HealthMetric("memory_usage", 70.0, "percent", 80.0, 95.0)
            }
            mock_collect.return_value = mock_metrics
            
            health = self.collector.get_system_health()
            
            assert health.component_name == "system"
            assert health.component_type == ComponentType.SYSTEM_RESOURCE
            assert len(health.metrics) == 2
            assert "cpu_usage" in health.metrics
            assert "memory_usage" in health.metrics

class TestServiceHealthChecker:
    """Test service health checking"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.checker = ServiceHealthChecker()
    
    def test_register_service(self):
        """Test registering service for health checks"""
        def mock_health_check():
            return {"status": "ok"}
        
        self.checker.register_service("test_service", mock_health_check)
        
        assert "test_service" in self.checker.registered_services
        service_config = self.checker.registered_services["test_service"]
        assert service_config["health_check_func"] == mock_health_check
        assert service_config["check_interval"] == 60
        assert service_config["consecutive_failures"] == 0
    
    def test_check_service_health_success(self):
        """Test successful service health check"""
        def mock_health_check():
            return {"connections": 10, "response_time": 0.1}
        
        self.checker.register_service("test_service", mock_health_check)
        
        health = self.checker.check_service_health("test_service")
        
        assert health.component_name == "test_service"
        assert health.component_type == ComponentType.SERVICE
        assert health.status == HealthStatus.HEALTHY
        assert "response_time" in health.metrics
        assert health.details["connections"] == 10
        
        # Should reset consecutive failures
        service_config = self.checker.registered_services["test_service"]
        assert service_config["consecutive_failures"] == 0
    
    def test_check_service_health_failure(self):
        """Test failed service health check"""
        def mock_health_check():
            raise Exception("Service is down")
        
        self.checker.register_service("test_service", mock_health_check)
        
        health = self.checker.check_service_health("test_service")
        
        assert health.component_name == "test_service"
        assert health.status == HealthStatus.WARNING
        assert health.error_message == "Service is down"
        assert health.details["consecutive_failures"] == 1
        
        # Should increment consecutive failures
        service_config = self.checker.registered_services["test_service"]
        assert service_config["consecutive_failures"] == 1
    
    def test_check_service_health_multiple_failures(self):
        """Test multiple consecutive failures"""
        def mock_health_check():
            raise Exception("Service is down")
        
        self.checker.register_service("test_service", mock_health_check)
        
        # Trigger multiple failures
        for i in range(5):
            health = self.checker.check_service_health("test_service")
        
        # Should be critical after 5 failures
        assert health.status == HealthStatus.CRITICAL
        assert health.details["consecutive_failures"] == 5
    
    def test_check_unregistered_service(self):
        """Test checking unregistered service"""
        health = self.checker.check_service_health("unknown_service")
        
        assert health.component_name == "unknown_service"
        assert health.status == HealthStatus.UNKNOWN
        assert "not registered" in health.error_message
    
    def test_check_all_services(self):
        """Test checking all registered services"""
        def healthy_service():
            return {"status": "ok"}
        
        def failing_service():
            raise Exception("Service failed")
        
        self.checker.register_service("healthy_service", healthy_service)
        self.checker.register_service("failing_service", failing_service)
        
        results = self.checker.check_all_services()
        
        assert len(results) == 2
        assert "healthy_service" in results
        assert "failing_service" in results
        assert results["healthy_service"].status == HealthStatus.HEALTHY
        assert results["failing_service"].status == HealthStatus.WARNING
    
    def test_get_service_status_summary(self):
        """Test getting service status summary"""
        # Setup mock results
        self.checker.check_results = {
            "service1": ComponentHealth("service1", ComponentType.SERVICE, HealthStatus.HEALTHY),
            "service2": ComponentHealth("service2", ComponentType.SERVICE, HealthStatus.WARNING),
            "service3": ComponentHealth("service3", ComponentType.SERVICE, HealthStatus.CRITICAL),
            "service4": ComponentHealth("service4", ComponentType.SERVICE, HealthStatus.UNKNOWN)
        }
        
        summary = self.checker.get_service_status_summary()
        
        assert summary["total_services"] == 4
        assert summary["healthy"] == 1
        assert summary["warning"] == 1
        assert summary["critical"] == 1
        assert summary["unknown"] == 1
        assert summary["overall_status"] == "critical"  # Critical takes precedence
    
    def test_determine_overall_status(self):
        """Test overall status determination logic"""
        # Test critical precedence
        status_counts = {"healthy": 2, "warning": 1, "critical": 1, "unknown": 0}
        overall = self.checker._determine_overall_status(status_counts)
        assert overall == "critical"
        
        # Test warning precedence
        status_counts = {"healthy": 2, "warning": 1, "critical": 0, "unknown": 0}
        overall = self.checker._determine_overall_status(status_counts)
        assert overall == "warning"
        
        # Test unknown precedence
        status_counts = {"healthy": 2, "warning": 0, "critical": 0, "unknown": 1}
        overall = self.checker._determine_overall_status(status_counts)
        assert overall == "unknown"
        
        # Test healthy
        status_counts = {"healthy": 3, "warning": 0, "critical": 0, "unknown": 0}
        overall = self.checker._determine_overall_status(status_counts)
        assert overall == "healthy"

class TestHealthMonitoringService:
    """Test main health monitoring service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = HealthMonitoringService()
    
    def teardown_method(self):
        """Clean up after tests"""
        if self.service.monitoring_active:
            self.service.stop_monitoring()
    
    def test_service_initialization(self):
        """Test service initialization"""
        assert isinstance(self.service.system_collector, SystemMetricsCollector)
        assert isinstance(self.service.service_checker, ServiceHealthChecker)
        assert not self.service.monitoring_active
        assert len(self.service.health_callbacks) == 0
    
    def test_register_service(self):
        """Test registering service for monitoring"""
        def mock_health_check():
            return {"status": "ok"}
        
        self.service.register_service("test_service", mock_health_check)
        
        assert "test_service" in self.service.service_checker.registered_services
    
    def test_register_callbacks(self):
        """Test registering callbacks"""
        def health_callback(report):
            pass
        
        def alert_callback(severity, report):
            pass
        
        self.service.register_health_callback(health_callback)
        self.service.register_alert_callback(HealthStatus.CRITICAL, alert_callback)
        
        assert health_callback in self.service.health_callbacks
        assert alert_callback in self.service.alert_thresholds[HealthStatus.CRITICAL]
    
    def test_perform_health_check(self):
        """Test performing comprehensive health check"""
        # Mock system health
        mock_system_health = ComponentHealth(
            "system", ComponentType.SYSTEM_RESOURCE, HealthStatus.HEALTHY
        )
        
        # Mock service health
        mock_service_health = {
            "test_service": ComponentHealth(
                "test_service", ComponentType.SERVICE, HealthStatus.HEALTHY
            )
        }
        
        with patch.object(self.service.system_collector, 'get_system_health', return_value=mock_system_health), \
             patch.object(self.service.service_checker, 'check_all_services', return_value=mock_service_health):
            
            report = self.service.perform_health_check()
            
            assert "timestamp" in report
            assert "system" in report
            assert "services" in report
            assert "summary" in report
            assert report["summary"]["overall_status"] == "healthy"
    
    def test_health_history(self):
        """Test health history management"""
        # Mock health check
        with patch.object(self.service, 'perform_health_check') as mock_check:
            mock_report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {"overall_status": "healthy"}
            }
            mock_check.return_value = mock_report
            
            # Perform check
            self.service.perform_health_check()
            
            # Should be in history
            assert len(self.service.health_history) == 1
            assert self.service.health_history[0] == mock_report
    
    def test_get_health_trends(self):
        """Test getting health trends"""
        # Add mock history
        now = datetime.now()
        self.service.health_history = [
            {
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "summary": {"overall_status": "healthy"}
            },
            {
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "summary": {"overall_status": "warning"}
            },
            {
                "timestamp": now.isoformat(),
                "summary": {"overall_status": "healthy"}
            }
        ]
        
        trends = self.service.get_health_trends(hours=3)
        
        assert trends["total_checks"] == 3
        assert trends["uptime_percentage"] == 66.67  # 2 out of 3 healthy
        assert len(trends["status_changes"]) == 2  # healthy->warning, warning->healthy
        assert trends["current_status"] == "healthy"
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""
        assert not self.service.monitoring_active
        
        # Start monitoring
        self.service.start_monitoring(interval=1)
        assert self.service.monitoring_active
        assert self.service.monitoring_thread is not None
        
        # Stop monitoring
        self.service.stop_monitoring()
        assert not self.service.monitoring_active
    
    def test_alert_triggering(self):
        """Test alert triggering"""
        alert_triggered = False
        alert_severity = None
        alert_report = None
        
        def alert_callback(severity, report):
            nonlocal alert_triggered, alert_severity, alert_report
            alert_triggered = True
            alert_severity = severity
            alert_report = report
        
        self.service.register_alert_callback(HealthStatus.CRITICAL, alert_callback)
        
        # Mock critical health report
        critical_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"overall_status": "critical"}
        }
        
        self.service._check_alerts(critical_report)
        
        assert alert_triggered
        assert alert_severity == HealthStatus.CRITICAL
        assert alert_report == critical_report
    
    def test_export_health_report(self, tmp_path):
        """Test exporting health report"""
        output_file = tmp_path / "health_report.json"
        
        # Mock current health and trends
        with patch.object(self.service, 'get_current_health') as mock_current, \
             patch.object(self.service, 'get_health_trends') as mock_trends, \
             patch.object(self.service, 'get_health_history') as mock_history:
            
            mock_current.return_value = {"status": "healthy"}
            mock_trends.return_value = {"uptime": 99.5}
            mock_history.return_value = [{"timestamp": "2023-01-01T00:00:00"}]
            
            self.service.export_health_report(output_file)
            
            assert output_file.exists()
            
            # Verify file content
            import json
            with open(output_file) as f:
                report = json.load(f)
            
            assert "generated_at" in report
            assert "current_health" in report
            assert "trends_24h" in report
            assert "recent_history" in report

class TestHealthMonitoringIntegration:
    """Integration tests for health monitoring"""
    
    def test_global_health_monitor(self):
        """Test global health monitor functions"""
        monitor = get_health_monitor()
        assert isinstance(monitor, HealthMonitoringService)
        
        # Test global functions
        def mock_health_check():
            return {"status": "ok"}
        
        register_service_health_check("global_service", mock_health_check)
        
        assert "global_service" in monitor.service_checker.registered_services
    
    def test_current_system_health(self):
        """Test getting current system health"""
        with patch.object(get_health_monitor(), 'get_current_health') as mock_health:
            mock_health.return_value = {"overall_status": "healthy"}
            
            health = get_current_system_health()
            assert health["overall_status"] == "healthy"
    
    def test_start_stop_global_monitoring(self):
        """Test global monitoring start/stop"""
        monitor = get_health_monitor()
        
        # Ensure stopped initially
        if monitor.monitoring_active:
            stop_health_monitoring()
        
        assert not monitor.monitoring_active
        
        # Start monitoring
        start_health_monitoring(interval=1)
        assert monitor.monitoring_active
        
        # Stop monitoring
        stop_health_monitoring()
        assert not monitor.monitoring_active

def test_health_status_enum():
    """Test health status enumeration"""
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.WARNING.value == "warning"
    assert HealthStatus.CRITICAL.value == "critical"
    assert HealthStatus.UNKNOWN.value == "unknown"

def test_component_type_enum():
    """Test component type enumeration"""
    assert ComponentType.SERVICE.value == "service"
    assert ComponentType.DATABASE.value == "database"
    assert ComponentType.CACHE.value == "cache"
    assert ComponentType.EXTERNAL_API.value == "external_api"
    assert ComponentType.FILE_SYSTEM.value == "file_system"
    assert ComponentType.NETWORK.value == "network"
    assert ComponentType.SYSTEM_RESOURCE.value == "system_resource"