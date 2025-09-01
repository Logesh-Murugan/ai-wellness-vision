#!/usr/bin/env python3
"""
Demo script for comprehensive error handling, health monitoring, and logging
"""

import time
import tempfile
from pathlib import Path
from datetime import datetime

from src.services.monitoring_integration_service import (
    get_monitoring_integration, start_comprehensive_monitoring, 
    stop_comprehensive_monitoring, get_system_overview
)
from src.utils.error_handling import (
    handle_error, ErrorCode, ErrorSeverity, ErrorContext,
    get_error_handler, get_fallback_manager, with_fallback
)
from src.utils.health_monitoring import (
    get_health_monitor, register_service_health_check,
    HealthStatus, ComponentType
)
from src.utils.logging_config import (
    get_structured_logger, get_log_aggregator, setup_enhanced_logging
)

def demo_comprehensive_monitoring():
    """Demonstrate comprehensive monitoring system"""
    print("=== AI WellnessVision Comprehensive Monitoring Demo ===\n")
    
    # Setup enhanced logging
    setup_enhanced_logging()
    logger = get_structured_logger(__name__)
    logger.set_context(demo_session="comprehensive_monitoring", user_id="demo_user")
    
    print("1. Initializing monitoring services...")
    
    # Get monitoring integration service
    monitoring_service = get_monitoring_integration()
    
    print("✓ Monitoring integration service initialized")
    print("✓ Error handling system ready")
    print("✓ Health monitoring system ready")
    print("✓ Enhanced logging configured")
    
    print("\n2. Registering mock services for health monitoring...")
    
    # Register mock services
    def healthy_service_check():
        return {"status": "ok", "connections": 10, "response_time": 0.1}
    
    def degraded_service_check():
        return {"status": "degraded", "connections": 5, "response_time": 2.5}
    
    def failing_service_check():
        raise Exception("Service is down")
    
    register_service_health_check("image_service", healthy_service_check, 30)
    register_service_health_check("nlp_service", degraded_service_check, 30)
    register_service_health_check("speech_service", failing_service_check, 30)
    
    print("✓ Registered 3 mock services for health monitoring")
    
    print("\n3. Setting up fallback mechanisms...")
    
    # Setup fallback mechanisms
    fallback_manager = get_fallback_manager()
    
    def image_service_fallback():
        return {"status": "fallback", "message": "Using cached results"}
    
    def nlp_service_fallback():
        return {"status": "fallback", "message": "Using basic keyword matching"}
    
    fallback_manager.register_fallback("image_service", image_service_fallback)
    fallback_manager.register_fallback("nlp_service", nlp_service_fallback)
    
    print("✓ Fallback mechanisms configured")
    
    print("\n4. Starting comprehensive monitoring...")
    
    start_comprehensive_monitoring(interval=10)  # Short interval for demo
    
    print("✓ Comprehensive monitoring started")
    
    print("\n5. Simulating various system events...")
    
    # Simulate user actions and errors
    logger.log_user_action("upload_image", file_size=2048, file_type="jpg")
    logger.log_performance_metric("image_analysis", 1.5, accuracy=0.95, model="resnet50")
    
    # Simulate some errors
    context = ErrorContext(
        user_id="demo_user",
        session_id="demo_session",
        service_name="image_service",
        function_name="analyze_image"
    )
    
    # Low severity error
    handle_error(
        ErrorCode.IMAGE_PROCESSING_ERROR,
        "Image quality too low for analysis",
        ErrorSeverity.LOW,
        context
    )
    
    # Medium severity error
    handle_error(
        ErrorCode.NETWORK_ERROR,
        "Temporary network connectivity issue",
        ErrorSeverity.MEDIUM,
        context
    )
    
    # High severity error
    handle_error(
        ErrorCode.SERVICE_UNAVAILABLE,
        "External API service is down",
        ErrorSeverity.HIGH,
        context
    )
    
    print("✓ Simulated user actions and errors")
    
    print("\n6. Testing fallback mechanisms...")
    
    @with_fallback("image_service")
    def simulate_image_service():
        raise Exception("Primary service failed")
    
    @with_fallback("nlp_service")
    def simulate_nlp_service():
        return {"status": "success", "result": "Primary service working"}
    
    # Test fallback
    fallback_result = simulate_image_service()
    print(f"✓ Image service fallback: {fallback_result}")
    
    # Test normal operation
    normal_result = simulate_nlp_service()
    print(f"✓ NLP service normal: {normal_result}")
    
    print("\n7. Generating performance data...")
    
    # Simulate various operations with different performance characteristics
    operations = [
        ("image_analysis", [1.2, 1.5, 1.8, 2.1, 1.9]),
        ("text_processing", [0.3, 0.5, 0.4, 0.6, 0.8]),
        ("speech_recognition", [3.2, 2.8, 3.5, 4.1, 3.0])
    ]
    
    for operation, durations in operations:
        for duration in durations:
            logger.log_performance_metric(operation, duration, success=True)
    
    print("✓ Performance data generated")
    
    print("\n8. Simulating security events...")
    
    logger.log_security_event("failed_login", severity="medium", 
                             ip_address="192.168.1.100", attempts=3)
    logger.log_security_event("suspicious_activity", severity="high",
                             user_id="suspicious_user", activity="multiple_rapid_requests")
    
    print("✓ Security events logged")
    
    print("\n9. Waiting for monitoring data collection...")
    time.sleep(15)  # Wait for monitoring to collect data
    
    print("\n10. Getting system overview...")
    
    overview = get_system_overview()
    
    print(f"✓ Overall Status: {overview['overall_status']}")
    print(f"✓ System Health: {overview['system_health']['status']}")
    print(f"✓ Healthy Components: {overview['system_health']['healthy_components']}/{overview['system_health']['total_components']}")
    print(f"✓ Total Errors: {overview['error_summary']['total_errors']}")
    print(f"✓ Critical Errors: {overview['error_summary']['critical_errors']}")
    print(f"✓ Performance Status: {overview['performance']['overall_performance']}")
    print(f"✓ Active Alerts: {overview['alerts']['active_alerts']}")
    print(f"✓ Critical Alerts: {overview['alerts']['critical_alerts']}")
    
    if overview['recommendations']:
        print("\n📋 System Recommendations:")
        for i, recommendation in enumerate(overview['recommendations'], 1):
            print(f"   {i}. {recommendation}")
    
    print("\n11. Getting detailed statistics...")
    
    # Error statistics
    error_handler = get_error_handler()
    error_stats = error_handler.get_error_statistics()
    
    print(f"✓ Error Statistics:")
    print(f"   - Total errors: {error_stats['total_errors']}")
    print(f"   - By severity: {error_stats['by_severity']}")
    print(f"   - Most common: {error_stats['most_common_errors'][:3]}")
    
    # Log analysis
    log_aggregator = get_log_aggregator()
    error_analysis = log_aggregator.get_error_summary()
    perf_analysis = log_aggregator.get_performance_summary()
    
    print(f"✓ Log Analysis:")
    print(f"   - Log errors tracked: {error_analysis['total_errors']}")
    print(f"   - Performance operations: {len(perf_analysis['operations'])}")
    
    # Health monitoring
    health_monitor = get_health_monitor()
    health_trends = health_monitor.get_health_trends(1)  # Last hour
    
    print(f"✓ Health Trends:")
    print(f"   - Total checks: {health_trends.get('total_checks', 0)}")
    print(f"   - Uptime: {health_trends.get('uptime_percentage', 0):.1f}%")
    print(f"   - Current status: {health_trends.get('current_status', 'unknown')}")
    
    print("\n12. Testing alert system...")
    
    # Get alert manager
    alert_manager = monitoring_service.alert_manager
    
    # Create test alert
    test_alert = alert_manager.create_alert(
        alert_type="test",
        severity="medium",
        message="Demo alert for testing",
        source_component="demo_system",
        test_data="demo_value"
    )
    
    print(f"✓ Created test alert: {test_alert.alert_id}")
    
    # Get alert statistics
    alert_stats = alert_manager.get_alert_statistics()
    print(f"✓ Alert Statistics:")
    print(f"   - Total alerts: {alert_stats['total_alerts']}")
    print(f"   - Active alerts: {alert_stats['active_alerts']}")
    print(f"   - By severity: {alert_stats['by_severity']}")
    
    # Resolve test alert
    alert_manager.resolve_alert(test_alert.alert_id, "Demo completed")
    print(f"✓ Resolved test alert")
    
    print("\n13. Exporting comprehensive report...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        report_file = Path(temp_dir) / "comprehensive_monitoring_report.json"
        
        try:
            monitoring_service.export_comprehensive_report(report_file)
            
            # Get file size
            file_size = report_file.stat().st_size
            print(f"✓ Report exported: {report_file.name} ({file_size} bytes)")
            
            # Show sample content
            import json
            with open(report_file) as f:
                report_data = json.load(f)
            
            print(f"✓ Report sections:")
            for section in report_data.keys():
                print(f"   - {section}")
                
        except Exception as e:
            print(f"✗ Report export failed: {e}")
    
    print("\n14. Testing circuit breaker functionality...")
    
    # Test circuit breaker
    circuit_status = fallback_manager.get_circuit_breaker_status()
    print(f"✓ Circuit Breaker Status:")
    for service, status in circuit_status.items():
        print(f"   - {service}: {status['state']} ({status['failures']} failures)")
    
    print("\n15. Performance analysis...")
    
    performance_analyzer = monitoring_service.performance_analyzer
    perf_trends = performance_analyzer.get_performance_trends(1)
    
    print(f"✓ Performance Trends:")
    print(f"   - Current performance: {perf_trends.get('current_performance', 'unknown')}")
    print(f"   - Trend: {perf_trends.get('trend', 'unknown')}")
    print(f"   - Issues detected: {perf_trends.get('total_issues_detected', 0)}")
    
    print("\n16. Cleanup...")
    
    try:
        stop_comprehensive_monitoring()
        print("✓ Monitoring stopped")
    except Exception as e:
        print(f"✗ Cleanup error: {e}")
    
    print("\n=== Demo completed successfully! ===")
    
    print("\n📊 Summary:")
    print(f"   - System Status: {overview['overall_status']}")
    print(f"   - Services Monitored: {len(circuit_status)}")
    print(f"   - Errors Handled: {error_stats['total_errors']}")
    print(f"   - Alerts Generated: {alert_stats['total_alerts']}")
    print(f"   - Performance Operations: {len(perf_analysis['operations'])}")

def demo_individual_components():
    """Demonstrate individual monitoring components"""
    print("\n=== Individual Components Demo ===\n")
    
    print("1. Error Handling System...")
    
    error_handler = get_error_handler()
    
    # Test different error types
    errors_to_test = [
        (ErrorCode.IMAGE_UPLOAD_ERROR, "Image file corrupted", ErrorSeverity.MEDIUM),
        (ErrorCode.SPEECH_TO_TEXT_ERROR, "Audio quality too poor", ErrorSeverity.LOW),
        (ErrorCode.DATABASE_ERROR, "Connection timeout", ErrorSeverity.HIGH),
        (ErrorCode.SECURITY_VALIDATION_FAILED, "Invalid token", ErrorSeverity.CRITICAL)
    ]
    
    for error_code, message, severity in errors_to_test:
        context = ErrorContext(
            user_id="component_test",
            service_name="test_service",
            function_name="test_function"
        )
        
        app_error = handle_error(error_code, message, severity, context)
        print(f"✓ {error_code.value}: {severity.value} - {app_error.user_message[:50]}...")
    
    print(f"✓ Error handler processed {len(errors_to_test)} errors")
    
    print("\n2. Health Monitoring System...")
    
    health_monitor = get_health_monitor()
    
    # Test service registration
    def test_service_health():
        return {"status": "healthy", "version": "1.0.0", "uptime": 3600}
    
    register_service_health_check("test_component", test_service_health)
    
    # Get current health
    current_health = health_monitor.get_current_health()
    print(f"✓ System health: {current_health['summary']['overall_status']}")
    print(f"✓ Components monitored: {current_health['summary']['total_components']}")
    
    print("\n3. Enhanced Logging System...")
    
    logger = get_structured_logger("component_demo")
    logger.set_context(component="demo", test_id="individual_test")
    
    # Test different log types
    logger.info("Component demo started")
    logger.log_user_action("test_action", component="demo")
    logger.log_performance_metric("demo_operation", 0.5, success=True)
    logger.log_security_event("demo_security_check", severity="low")
    
    # Test log aggregation
    log_aggregator = get_log_aggregator()
    print(f"✓ Log entries in buffer: {len(log_aggregator.log_buffer)}")
    
    print("\n4. Fallback Management...")
    
    fallback_manager = get_fallback_manager()
    
    def demo_fallback():
        return "Fallback executed successfully"
    
    fallback_manager.register_fallback("demo_service", demo_fallback)
    
    def failing_function():
        raise Exception("Primary function failed")
    
    result = fallback_manager.execute_with_fallback("demo_service", failing_function)
    print(f"✓ Fallback result: {result}")
    
    print("\n=== Individual components demo completed! ===")

if __name__ == "__main__":
    try:
        demo_comprehensive_monitoring()
        demo_individual_components()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        try:
            stop_comprehensive_monitoring()
        except:
            pass
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        try:
            stop_comprehensive_monitoring()
        except:
            pass