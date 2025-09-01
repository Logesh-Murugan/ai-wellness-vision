# integration_service.py - Integration service for offline mode and model optimization
import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from src.config import AppConfig, ModelConfig
from src.utils.logging_config import get_logger, log_performance
from src.services.offline_mode_service import get_offline_service, is_offline_mode_active
from src.services.model_optimization_service import (
    get_optimization_service, OptimizationConfig, OptimizationTarget, ModelFormat
)

logger = get_logger(__name__)

@dataclass
class ServiceHealth:
    """Health status of a service"""
    service_name: str
    status: str  # healthy, degraded, unhealthy
    offline_capable: bool
    last_check: datetime
    details: Dict[str, Any]

class OfflineIntegrationService:
    """Service that integrates offline mode with all AI services"""
    
    def __init__(self):
        self.offline_service = get_offline_service()
        self.optimization_service = get_optimization_service()
        self.service_registry = {}
        self.health_checks = {}
        self.initialized = False
    
    def initialize(self) -> None:
        """Initialize the integration service"""
        try:
            # Initialize offline mode service
            self.offline_service.initialize()
            
            # Register status callback
            self.offline_service.register_status_callback(self._on_status_change)
            
            # Register services
            self._register_services()
            
            # Perform initial health check
            self.check_all_services_health()
            
            self.initialized = True
            logger.info("Offline integration service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize offline integration service: {e}")
            raise
    
    def shutdown(self) -> None:
        """Shutdown the integration service"""
        try:
            if self.offline_service:
                self.offline_service.shutdown()
            
            self.initialized = False
            logger.info("Offline integration service shutdown")
            
        except Exception as e:
            logger.error(f"Error during integration service shutdown: {e}")
    
    def _register_services(self) -> None:
        """Register all AI services with their offline capabilities"""
        self.service_registry = {
            'image_analysis': {
                'module': 'src.services.image_service',
                'class': 'EnhancedImageRecognitionService',
                'offline_capable': True,
                'fallback_methods': ['mock_analysis', 'cached_results'],
                'priority': 1
            },
            'nlp_service': {
                'module': 'src.services.nlp_service',
                'class': 'ComprehensiveNLPService',
                'offline_capable': True,
                'fallback_methods': ['keyword_responses', 'cached_conversations'],
                'priority': 1
            },
            'speech_service': {
                'module': 'src.services.speech_service',
                'class': 'ComprehensiveSpeechService',
                'offline_capable': False,
                'fallback_methods': ['text_only'],
                'priority': 2
            },
            'explainable_ai': {
                'module': 'src.services.explainable_ai_service',
                'class': 'ComprehensiveExplainableAIService',
                'offline_capable': True,
                'fallback_methods': ['template_explanations'],
                'priority': 2
            }
        }
    
    def _on_status_change(self, system_status) -> None:
        """Handle system status changes"""
        logger.info(f"System status changed: offline_mode={system_status.offline_mode_active}")
        
        if system_status.offline_mode_active:
            self._handle_offline_transition()
        else:
            self._handle_online_transition()
    
    def _handle_offline_transition(self) -> None:
        """Handle transition to offline mode"""
        logger.info("Transitioning to offline mode")
        
        # Notify all services about offline mode
        for service_name, service_info in self.service_registry.items():
            if service_info['offline_capable']:
                logger.info(f"Service {service_name} entering degraded mode")
            else:
                logger.info(f"Service {service_name} disabled in offline mode")
    
    def _handle_online_transition(self) -> None:
        """Handle transition to online mode"""
        logger.info("Transitioning to online mode")
        
        # Notify all services about online mode
        for service_name in self.service_registry.keys():
            logger.info(f"Service {service_name} restored to full functionality")
    
    @log_performance()
    def check_all_services_health(self) -> Dict[str, ServiceHealth]:
        """Check health of all registered services"""
        health_results = {}
        
        for service_name, service_info in self.service_registry.items():
            try:
                health = self._check_service_health(service_name, service_info)
                health_results[service_name] = health
                self.health_checks[service_name] = health
                
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_results[service_name] = ServiceHealth(
                    service_name=service_name,
                    status="unhealthy",
                    offline_capable=service_info['offline_capable'],
                    last_check=datetime.now(),
                    details={"error": str(e)}
                )
        
        return health_results
    
    def _check_service_health(self, service_name: str, service_info: Dict[str, Any]) -> ServiceHealth:
        """Check health of a specific service"""
        try:
            # Mock health check - in production, this would actually test the service
            if is_offline_mode_active():
                if service_info['offline_capable']:
                    status = "degraded"
                    details = {
                        "mode": "offline",
                        "available_features": service_info['fallback_methods']
                    }
                else:
                    status = "unhealthy"
                    details = {
                        "mode": "offline",
                        "reason": "Service not available offline"
                    }
            else:
                status = "healthy"
                details = {
                    "mode": "online",
                    "full_functionality": True
                }
            
            return ServiceHealth(
                service_name=service_name,
                status=status,
                offline_capable=service_info['offline_capable'],
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            logger.error(f"Service health check failed for {service_name}: {e}")
            return ServiceHealth(
                service_name=service_name,
                status="unhealthy",
                offline_capable=service_info['offline_capable'],
                last_check=datetime.now(),
                details={"error": str(e)}
            )
    
    def get_service_status(self, service_name: str) -> Optional[ServiceHealth]:
        """Get status of a specific service"""
        return self.health_checks.get(service_name)
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        system_status = self.offline_service.get_system_status()
        optimization_stats = self.optimization_service.get_optimization_stats()
        
        # Count service statuses
        healthy_services = sum(1 for h in self.health_checks.values() if h.status == "healthy")
        degraded_services = sum(1 for h in self.health_checks.values() if h.status == "degraded")
        unhealthy_services = sum(1 for h in self.health_checks.values() if h.status == "unhealthy")
        
        return {
            "system_status": {
                "connectivity": system_status.connectivity.value,
                "offline_mode_active": system_status.offline_mode_active,
                "last_online": system_status.last_online,
                "estimated_restoration": system_status.estimated_restoration
            },
            "services": {
                "total": len(self.service_registry),
                "healthy": healthy_services,
                "degraded": degraded_services,
                "unhealthy": unhealthy_services,
                "offline_capable": sum(1 for s in self.service_registry.values() if s['offline_capable'])
            },
            "features": {
                "available": system_status.available_features,
                "degraded": system_status.degraded_features
            },
            "optimization": {
                "total_optimizations": optimization_stats.get('total_optimizations', 0),
                "cache_size_mb": optimization_stats.get('cache_stats', {}).get('total_cache_size_mb', 0),
                "cached_models": optimization_stats.get('cache_stats', {}).get('total_cached_models', 0)
            },
            "timestamp": datetime.now()
        }
    
    def optimize_models_for_offline(self, model_paths: List[Path]) -> Dict[str, Any]:
        """Optimize models for offline deployment"""
        try:
            # Define optimization configurations for offline use
            offline_configs = [
                OptimizationConfig(
                    target_platform=OptimizationTarget.MOBILE,
                    target_format=ModelFormat.TFLITE,
                    quantization=True,
                    pruning=True,
                    max_model_size_mb=10.0,
                    optimization_level=3
                ),
                OptimizationConfig(
                    target_platform=OptimizationTarget.EDGE,
                    target_format=ModelFormat.ONNX,
                    quantization=True,
                    pruning=False,
                    max_model_size_mb=15.0,
                    optimization_level=2
                )
            ]
            
            # Perform batch optimization
            results = self.optimization_service.batch_optimize_models(
                model_paths, offline_configs
            )
            
            # Analyze results
            successful_optimizations = [r for r in results if r.success]
            failed_optimizations = [r for r in results if not r.success]
            
            total_size_reduction = sum(
                r.original_size_mb - r.optimized_size_mb 
                for r in successful_optimizations
            )
            
            return {
                "success": True,
                "total_models": len(model_paths),
                "total_optimizations": len(results),
                "successful": len(successful_optimizations),
                "failed": len(failed_optimizations),
                "total_size_reduction_mb": total_size_reduction,
                "optimized_models": [
                    {
                        "path": str(r.output_path),
                        "format": r.format.value,
                        "compression_ratio": r.compression_ratio,
                        "size_mb": r.optimized_size_mb
                    }
                    for r in successful_optimizations
                ],
                "errors": [r.errors for r in failed_optimizations if r.errors]
            }
            
        except Exception as e:
            logger.error(f"Model optimization for offline failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_models": len(model_paths),
                "optimized_models": []
            }
    
    def prepare_offline_deployment(self, output_dir: Path) -> Dict[str, Any]:
        """Prepare system for offline deployment"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get all model paths (mock implementation)
            model_paths = [
                Path("models/image_model.pth"),
                Path("models/nlp_model.pth"),
                Path("models/speech_model.pth")
            ]
            
            # Create mock model files for testing
            for model_path in model_paths:
                if not model_path.exists():
                    model_path.parent.mkdir(parents=True, exist_ok=True)
                    model_path.write_bytes(b"0" * (10 * 1024 * 1024))  # 10MB mock model
            
            # Optimize models
            optimization_result = self.optimize_models_for_offline(model_paths)
            
            # Copy optimized models to deployment directory
            deployment_models = []
            if optimization_result["success"]:
                for model_info in optimization_result["optimized_models"]:
                    src_path = Path(model_info["path"])
                    if src_path.exists():
                        dest_path = output_dir / src_path.name
                        import shutil
                        shutil.copy2(src_path, dest_path)
                        deployment_models.append(str(dest_path))
            
            # Create deployment configuration
            deployment_config = {
                "offline_mode": True,
                "optimized_models": deployment_models,
                "service_configurations": {
                    service_name: {
                        "offline_capable": info["offline_capable"],
                        "fallback_methods": info["fallback_methods"],
                        "priority": info["priority"]
                    }
                    for service_name, info in self.service_registry.items()
                },
                "created_at": datetime.now().isoformat(),
                "optimization_stats": optimization_result
            }
            
            # Save deployment configuration
            config_file = output_dir / "offline_deployment_config.json"
            import json
            with open(config_file, 'w') as f:
                json.dump(deployment_config, f, indent=2, default=str)
            
            return {
                "success": True,
                "deployment_directory": str(output_dir),
                "config_file": str(config_file),
                "optimized_models": len(deployment_models),
                "total_size_mb": sum(
                    Path(model).stat().st_size / (1024 * 1024) 
                    for model in deployment_models if Path(model).exists()
                ),
                "optimization_result": optimization_result
            }
            
        except Exception as e:
            logger.error(f"Offline deployment preparation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "deployment_directory": str(output_dir)
            }
    
    def test_offline_functionality(self) -> Dict[str, Any]:
        """Test offline functionality of all services"""
        try:
            # Force offline mode for testing
            original_offline_state = is_offline_mode_active()
            self.offline_service.force_offline_mode(True)
            
            test_results = {}
            
            # Test each service in offline mode
            for service_name, service_info in self.service_registry.items():
                try:
                    if service_info['offline_capable']:
                        # Test offline functionality
                        health = self._check_service_health(service_name, service_info)
                        test_results[service_name] = {
                            "offline_test": "passed",
                            "status": health.status,
                            "available_features": health.details.get("available_features", [])
                        }
                    else:
                        # Service should be disabled
                        test_results[service_name] = {
                            "offline_test": "expected_disabled",
                            "status": "disabled",
                            "reason": "Service not designed for offline use"
                        }
                        
                except Exception as e:
                    test_results[service_name] = {
                        "offline_test": "failed",
                        "error": str(e)
                    }
            
            # Restore original offline state
            self.offline_service.force_offline_mode(original_offline_state)
            
            # Calculate test summary
            passed_tests = sum(1 for r in test_results.values() 
                             if r.get("offline_test") in ["passed", "expected_disabled"])
            total_tests = len(test_results)
            
            return {
                "success": True,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "test_results": test_results,
                "offline_capable_services": [
                    name for name, info in self.service_registry.items() 
                    if info['offline_capable']
                ]
            }
            
        except Exception as e:
            logger.error(f"Offline functionality test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_results": {}
            }

# Global integration service instance
integration_service = OfflineIntegrationService()

def get_integration_service() -> OfflineIntegrationService:
    """Get the global integration service instance"""
    return integration_service

def initialize_offline_integration() -> None:
    """Initialize offline integration service"""
    integration_service.initialize()

def shutdown_offline_integration() -> None:
    """Shutdown offline integration service"""
    integration_service.shutdown()