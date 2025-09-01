# monitoring_integration_service.py - Integration service for error handling, health monitoring, and logging
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from src.utils.error_handling import (
    get_error_handler, get_fallback_manager, ErrorCode, ErrorSeverity, 
    ErrorContext, handle_error
)
from src.utils.health_monitoring import (
    get_health_monitor, HealthStatus, ComponentType, HealthMetric, 
    ComponentHealth, register_service_health_check
)
from src.utils.logging_config import (
    get_structured_logger, get_log_aggregator, setup_enhanced_logging
)

logger = get_structured_logger(__name__)

@dataclass
class SystemAlert:
    """System alert information"""
    alert_id: str
    alert_type: str  # error, health, performance
    severity: str
    message: str
    timestamp: datetime
    source_component: str
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class MonitoringReport:
    """Comprehensive monitoring report"""
    timestamp: datetime
    system_health: Dict[str, Any]
    error_statistics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    active_alerts: List[SystemAlert]
    recommendations: List[str]
    overall_status: str

class AlertManager:
    """Manages system alerts and notifications"""
    
    def __init__(self):
        self.active_alerts = {}
        self.alert_history = []
        self.max_history_size = 1000
        self.alert_callbacks = []
        self.alert_rules = self._load_default_alert_rules()
    
    def _load_default_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load default alert rules"""
        return {
            "high_error_rate": {
                "condition": "error_rate > 10 per minute",
                "severity": "high",
                "cooldown": 300  # 5 minutes
            },
            "critical_service_down": {
                "condition": "service_status == critical",
                "severity": "critical",
                "cooldown": 60  # 1 minute
            },
            "high_response_time": {
                "condition": "avg_response_time > 5000ms",
                "severity": "medium",
                "cooldown": 600  # 10 minutes
            },
            "low_disk_space": {
                "condition": "disk_usage > 90%",
                "severity": "high",
                "cooldown": 1800  # 30 minutes
            },
            "high_memory_usage": {
                "condition": "memory_usage > 95%",
                "severity": "critical",
                "cooldown": 300  # 5 minutes
            }
        }
    
    def create_alert(self, alert_type: str, severity: str, message: str,
                    source_component: str, **details) -> SystemAlert:
        """Create a new system alert"""
        alert_id = f"{alert_type}_{source_component}_{int(time.time())}"
        
        alert = SystemAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            source_component=source_component,
            details=details
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Maintain history size
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size:]
        
        # Notify callbacks
        self._notify_alert_callbacks(alert)
        
        logger.warning(f"Alert created: {alert_type} - {message}",
                      alert_id=alert_id,
                      severity=severity,
                      source_component=source_component)
        
        return alert
    
    def resolve_alert(self, alert_id: str, resolution_message: str = None) -> bool:
        """Resolve an active alert"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolution_time = datetime.now()
        
        if resolution_message:
            alert.details["resolution_message"] = resolution_message
        
        del self.active_alerts[alert_id]
        
        logger.info(f"Alert resolved: {alert_id}",
                   alert_id=alert_id,
                   resolution_time=alert.resolution_time.isoformat())
        
        return True
    
    def get_active_alerts(self, severity: str = None) -> List[SystemAlert]:
        """Get active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        if not self.alert_history:
            return {
                "total_alerts": 0,
                "active_alerts": 0,
                "resolved_alerts": 0,
                "by_severity": {},
                "by_type": {},
                "avg_resolution_time": 0
            }
        
        # Count by severity
        severity_counts = {}
        type_counts = {}
        resolution_times = []
        
        for alert in self.alert_history:
            # Severity counts
            severity = alert.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Type counts
            alert_type = alert.alert_type
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            
            # Resolution times
            if alert.resolved and alert.resolution_time:
                resolution_time = (alert.resolution_time - alert.timestamp).total_seconds()
                resolution_times.append(resolution_time)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            "total_alerts": len(self.alert_history),
            "active_alerts": len(self.active_alerts),
            "resolved_alerts": len([a for a in self.alert_history if a.resolved]),
            "by_severity": severity_counts,
            "by_type": type_counts,
            "avg_resolution_time": avg_resolution_time
        }
    
    def register_alert_callback(self, callback: Callable[[SystemAlert], None]) -> None:
        """Register callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def _notify_alert_callbacks(self, alert: SystemAlert) -> None:
        """Notify alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}", 
                           callback=str(callback),
                           alert_id=alert.alert_id)

class PerformanceAnalyzer:
    """Analyzes system performance and identifies issues"""
    
    def __init__(self):
        self.performance_history = []
        self.max_history_size = 1000
        self.baseline_metrics = {}
    
    def analyze_performance(self, health_report: Dict[str, Any], 
                          error_stats: Dict[str, Any],
                          log_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system performance"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "overall_performance": "good",
            "issues_detected": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Analyze system metrics
        system_metrics = health_report.get("system", {}).get("metrics", {})
        self._analyze_system_metrics(system_metrics, analysis)
        
        # Analyze service performance
        services = health_report.get("services", {})
        self._analyze_service_performance(services, analysis)
        
        # Analyze error patterns
        self._analyze_error_patterns(error_stats, analysis)
        
        # Analyze performance trends
        perf_analysis = log_analysis.get("performance_analysis", {})
        self._analyze_performance_trends(perf_analysis, analysis)
        
        # Add to history
        self.performance_history.append(analysis)
        if len(self.performance_history) > self.max_history_size:
            self.performance_history = self.performance_history[-self.max_history_size:]
        
        return analysis
    
    def _analyze_system_metrics(self, metrics: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Analyze system-level metrics"""
        for metric_name, metric_data in metrics.items():
            if isinstance(metric_data, dict) and "value" in metric_data:
                value = metric_data["value"]
                status = metric_data.get("status", "unknown")
                
                analysis["metrics"][metric_name] = {
                    "value": value,
                    "status": status
                }
                
                if status == "critical":
                    analysis["issues_detected"].append(f"Critical {metric_name}: {value}")
                    analysis["overall_performance"] = "critical"
                elif status == "warning" and analysis["overall_performance"] == "good":
                    analysis["overall_performance"] = "degraded"
    
    def _analyze_service_performance(self, services: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Analyze service performance"""
        service_issues = []
        
        for service_name, service_data in services.items():
            status = service_data.get("status", "unknown")
            metrics = service_data.get("metrics", {})
            
            if status == "critical":
                service_issues.append(f"Service {service_name} is critical")
            elif status == "warning":
                service_issues.append(f"Service {service_name} has warnings")
            
            # Check response time
            if "response_time" in metrics:
                response_time = metrics["response_time"].get("value", 0)
                if response_time > 5000:  # 5 seconds
                    service_issues.append(f"High response time for {service_name}: {response_time}ms")
        
        analysis["issues_detected"].extend(service_issues)
        
        if service_issues:
            if any("critical" in issue for issue in service_issues):
                analysis["overall_performance"] = "critical"
            elif analysis["overall_performance"] == "good":
                analysis["overall_performance"] = "degraded"
    
    def _analyze_error_patterns(self, error_stats: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Analyze error patterns"""
        total_errors = error_stats.get("total_errors", 0)
        
        if total_errors > 100:  # High error count
            analysis["issues_detected"].append(f"High error count: {total_errors}")
            analysis["recommendations"].append("Investigate error patterns and root causes")
        
        # Check for critical errors
        by_severity = error_stats.get("by_severity", {})
        critical_errors = by_severity.get("critical", 0)
        
        if critical_errors > 0:
            analysis["issues_detected"].append(f"Critical errors detected: {critical_errors}")
            analysis["overall_performance"] = "critical"
    
    def _analyze_performance_trends(self, perf_analysis: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Analyze performance trends"""
        operations = perf_analysis.get("operations", [])
        
        for operation in operations:
            op_name = operation.get("operation", "unknown")
            avg_duration = operation.get("avg_duration", 0)
            trend = operation.get("performance_trend", "stable")
            
            if trend == "degrading":
                analysis["issues_detected"].append(f"Performance degrading for {op_name}")
                analysis["recommendations"].append(f"Optimize {op_name} operation")
            
            if avg_duration > 10:  # 10 seconds
                analysis["issues_detected"].append(f"Slow operation: {op_name} ({avg_duration:.2f}s)")
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        relevant_analyses = [
            analysis for analysis in self.performance_history
            if datetime.fromisoformat(analysis["timestamp"]) >= cutoff_time
        ]
        
        if not relevant_analyses:
            return {"error": "No performance data available"}
        
        # Calculate trends
        performance_levels = [a["overall_performance"] for a in relevant_analyses]
        
        good_count = performance_levels.count("good")
        degraded_count = performance_levels.count("degraded")
        critical_count = performance_levels.count("critical")
        
        total_issues = sum(len(a["issues_detected"]) for a in relevant_analyses)
        
        return {
            "time_period_hours": hours,
            "total_analyses": len(relevant_analyses),
            "performance_distribution": {
                "good": good_count,
                "degraded": degraded_count,
                "critical": critical_count
            },
            "total_issues_detected": total_issues,
            "current_performance": relevant_analyses[-1]["overall_performance"],
            "trend": self._calculate_performance_trend(relevant_analyses)
        }
    
    def _calculate_performance_trend(self, analyses: List[Dict[str, Any]]) -> str:
        """Calculate overall performance trend"""
        if len(analyses) < 2:
            return "insufficient_data"
        
        # Simple trend calculation based on recent vs older performance
        recent_analyses = analyses[-5:]  # Last 5 analyses
        older_analyses = analyses[:-5] if len(analyses) > 5 else analyses[:len(analyses)//2]
        
        if not older_analyses:
            return "insufficient_data"
        
        recent_good = sum(1 for a in recent_analyses if a["overall_performance"] == "good")
        older_good = sum(1 for a in older_analyses if a["overall_performance"] == "good")
        
        recent_ratio = recent_good / len(recent_analyses)
        older_ratio = older_good / len(older_analyses)
        
        if recent_ratio > older_ratio + 0.1:
            return "improving"
        elif recent_ratio < older_ratio - 0.1:
            return "degrading"
        else:
            return "stable"

class MonitoringIntegrationService:
    """Main service that integrates error handling, health monitoring, and logging"""
    
    def __init__(self):
        self.error_handler = get_error_handler()
        self.fallback_manager = get_fallback_manager()
        self.health_monitor = get_health_monitor()
        self.log_aggregator = get_log_aggregator()
        self.alert_manager = AlertManager()
        self.performance_analyzer = PerformanceAnalyzer()
        
        self.monitoring_active = False
        self.monitoring_thread = None
        self.report_callbacks = []
        
        # Setup enhanced logging
        setup_enhanced_logging()
        
        # Register callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Setup callbacks between components"""
        # Error handler callback
        self.error_handler.register_callback(self._on_error_occurred)
        
        # Health monitor callbacks
        self.health_monitor.register_health_callback(self._on_health_update)
        self.health_monitor.register_alert_callback(HealthStatus.CRITICAL, self._on_critical_health)
        self.health_monitor.register_alert_callback(HealthStatus.WARNING, self._on_warning_health)
        
        # Alert manager callback
        self.alert_manager.register_alert_callback(self._on_alert_created)
    
    def _on_error_occurred(self, error) -> None:
        """Handle error occurrence"""
        # Create alert for high severity errors
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.alert_manager.create_alert(
                alert_type="error",
                severity=error.severity.value,
                message=f"Error in {error.context.service_name}: {error.message}",
                source_component=error.context.service_name or "unknown",
                error_code=error.error_code.value,
                user_id=error.context.user_id
            )
    
    def _on_health_update(self, health_report: Dict[str, Any]) -> None:
        """Handle health update"""
        summary = health_report.get("summary", {})
        overall_status = summary.get("overall_status", "unknown")
        
        # Log health status
        logger.info("Health status update",
                   overall_status=overall_status,
                   healthy_components=summary.get("healthy_components", 0),
                   issues_detected=summary.get("issues_detected", 0))
    
    def _on_critical_health(self, severity: HealthStatus, health_report: Dict[str, Any]) -> None:
        """Handle critical health status"""
        self.alert_manager.create_alert(
            alert_type="health",
            severity="critical",
            message="Critical health status detected",
            source_component="system",
            health_report=health_report
        )
    
    def _on_warning_health(self, severity: HealthStatus, health_report: Dict[str, Any]) -> None:
        """Handle warning health status"""
        self.alert_manager.create_alert(
            alert_type="health",
            severity="warning",
            message="Warning health status detected",
            source_component="system",
            health_report=health_report
        )
    
    def _on_alert_created(self, alert: SystemAlert) -> None:
        """Handle alert creation"""
        logger.warning(f"System alert: {alert.message}",
                      alert_id=alert.alert_id,
                      alert_type=alert.alert_type,
                      severity=alert.severity,
                      source_component=alert.source_component)
    
    def start_monitoring(self, interval: int = 300) -> None:
        """Start comprehensive monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        
        # Start health monitoring
        self.health_monitor.start_monitoring(interval // 5)  # More frequent health checks
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self.generate_monitoring_report()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Monitoring loop error: {e}")
                    time.sleep(interval)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info(f"Comprehensive monitoring started with {interval}s interval")
    
    def stop_monitoring(self) -> None:
        """Stop comprehensive monitoring"""
        self.monitoring_active = False
        
        # Stop health monitoring
        self.health_monitor.stop_monitoring()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        logger.info("Comprehensive monitoring stopped")
    
    def generate_monitoring_report(self) -> MonitoringReport:
        """Generate comprehensive monitoring report"""
        try:
            # Get current health status
            health_report = self.health_monitor.get_current_health()
            
            # Get error statistics
            error_stats = self.error_handler.get_error_statistics()
            
            # Get log analysis
            log_error_analysis = self.log_aggregator.get_error_summary()
            log_perf_analysis = self.log_aggregator.get_performance_summary()
            log_analysis = {
                "error_analysis": log_error_analysis,
                "performance_analysis": log_perf_analysis
            }
            
            # Analyze performance
            performance_analysis = self.performance_analyzer.analyze_performance(
                health_report, error_stats, log_analysis
            )
            
            # Get active alerts
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                health_report, error_stats, performance_analysis, active_alerts
            )
            
            # Determine overall status
            overall_status = self._determine_overall_status(
                health_report, error_stats, performance_analysis, active_alerts
            )
            
            report = MonitoringReport(
                timestamp=datetime.now(),
                system_health=health_report,
                error_statistics=error_stats,
                performance_metrics=performance_analysis,
                active_alerts=active_alerts,
                recommendations=recommendations,
                overall_status=overall_status
            )
            
            # Notify callbacks
            self._notify_report_callbacks(report)
            
            # Log report summary
            logger.info("Monitoring report generated",
                       overall_status=overall_status,
                       active_alerts=len(active_alerts),
                       total_errors=error_stats.get("total_errors", 0),
                       performance=performance_analysis.get("overall_performance", "unknown"))
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate monitoring report: {e}")
            raise
    
    def _generate_recommendations(self, health_report: Dict[str, Any], 
                                error_stats: Dict[str, Any],
                                performance_analysis: Dict[str, Any],
                                active_alerts: List[SystemAlert]) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        # Health-based recommendations
        summary = health_report.get("summary", {})
        if summary.get("overall_status") == "critical":
            recommendations.append("Immediate attention required for critical system components")
        
        # Error-based recommendations
        total_errors = error_stats.get("total_errors", 0)
        if total_errors > 50:
            recommendations.append("High error rate detected - investigate error patterns")
        
        # Performance-based recommendations
        perf_issues = performance_analysis.get("issues_detected", [])
        if perf_issues:
            recommendations.append("Performance issues detected - review system resources")
        
        # Alert-based recommendations
        critical_alerts = [a for a in active_alerts if a.severity == "critical"]
        if critical_alerts:
            recommendations.append("Critical alerts require immediate attention")
        
        # Add performance-specific recommendations
        recommendations.extend(performance_analysis.get("recommendations", []))
        
        return recommendations
    
    def _determine_overall_status(self, health_report: Dict[str, Any],
                                error_stats: Dict[str, Any],
                                performance_analysis: Dict[str, Any],
                                active_alerts: List[SystemAlert]) -> str:
        """Determine overall system status"""
        # Check for critical conditions
        health_status = health_report.get("summary", {}).get("overall_status", "unknown")
        performance_status = performance_analysis.get("overall_performance", "good")
        
        critical_alerts = [a for a in active_alerts if a.severity == "critical"]
        critical_errors = error_stats.get("by_severity", {}).get("critical", 0)
        
        if (health_status == "critical" or 
            performance_status == "critical" or 
            critical_alerts or 
            critical_errors > 0):
            return "critical"
        
        # Check for warning conditions
        warning_alerts = [a for a in active_alerts if a.severity in ["high", "warning"]]
        high_errors = error_stats.get("by_severity", {}).get("high", 0)
        
        if (health_status == "warning" or 
            performance_status == "degraded" or 
            warning_alerts or 
            high_errors > 5):
            return "warning"
        
        return "healthy"
    
    def _notify_report_callbacks(self, report: MonitoringReport) -> None:
        """Notify report callbacks"""
        for callback in self.report_callbacks:
            try:
                callback(report)
            except Exception as e:
                logger.error(f"Report callback failed: {e}")
    
    def register_report_callback(self, callback: Callable[[MonitoringReport], None]) -> None:
        """Register callback for monitoring reports"""
        self.report_callbacks.append(callback)
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        try:
            report = self.generate_monitoring_report()
            
            return {
                "timestamp": report.timestamp.isoformat(),
                "overall_status": report.overall_status,
                "system_health": {
                    "status": report.system_health.get("summary", {}).get("overall_status", "unknown"),
                    "healthy_components": report.system_health.get("summary", {}).get("healthy_components", 0),
                    "total_components": report.system_health.get("summary", {}).get("total_components", 0)
                },
                "error_summary": {
                    "total_errors": report.error_statistics.get("total_errors", 0),
                    "critical_errors": report.error_statistics.get("by_severity", {}).get("critical", 0),
                    "recent_errors": len(report.error_statistics.get("recent_errors", []))
                },
                "performance": {
                    "overall_performance": report.performance_metrics.get("overall_performance", "unknown"),
                    "issues_detected": len(report.performance_metrics.get("issues_detected", []))
                },
                "alerts": {
                    "active_alerts": len(report.active_alerts),
                    "critical_alerts": len([a for a in report.active_alerts if a.severity == "critical"]),
                    "alert_statistics": self.alert_manager.get_alert_statistics()
                },
                "recommendations": report.recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to get system overview: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "unknown",
                "error": str(e)
            }
    
    def export_comprehensive_report(self, output_file: Path) -> None:
        """Export comprehensive monitoring report"""
        try:
            report = self.generate_monitoring_report()
            
            # Get additional data
            health_trends = self.health_monitor.get_health_trends(24)
            performance_trends = self.performance_analyzer.get_performance_trends(24)
            alert_stats = self.alert_manager.get_alert_statistics()
            
            comprehensive_report = {
                "generated_at": datetime.now().isoformat(),
                "current_status": {
                    "overall_status": report.overall_status,
                    "system_health": report.system_health,
                    "error_statistics": report.error_statistics,
                    "performance_metrics": report.performance_metrics,
                    "active_alerts": [
                        {
                            "alert_id": alert.alert_id,
                            "type": alert.alert_type,
                            "severity": alert.severity,
                            "message": alert.message,
                            "timestamp": alert.timestamp.isoformat(),
                            "source": alert.source_component
                        }
                        for alert in report.active_alerts
                    ],
                    "recommendations": report.recommendations
                },
                "trends_24h": {
                    "health_trends": health_trends,
                    "performance_trends": performance_trends
                },
                "alert_statistics": alert_stats,
                "log_analysis": {
                    "error_analysis": self.log_aggregator.get_error_summary(),
                    "performance_analysis": self.log_aggregator.get_performance_summary()
                }
            }
            
            import json
            with open(output_file, 'w') as f:
                json.dump(comprehensive_report, f, indent=2, default=str)
            
            logger.info(f"Comprehensive report exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export comprehensive report: {e}")
            raise

# Global monitoring integration service
monitoring_integration = MonitoringIntegrationService()

def get_monitoring_integration() -> MonitoringIntegrationService:
    """Get global monitoring integration service"""
    return monitoring_integration

def start_comprehensive_monitoring(interval: int = 300) -> None:
    """Start comprehensive monitoring"""
    monitoring_integration.start_monitoring(interval)

def stop_comprehensive_monitoring() -> None:
    """Stop comprehensive monitoring"""
    monitoring_integration.stop_monitoring()

def get_system_overview() -> Dict[str, Any]:
    """Get comprehensive system overview"""
    return monitoring_integration.get_system_overview()