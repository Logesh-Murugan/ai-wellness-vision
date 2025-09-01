#!/usr/bin/env python3
"""
Demo script for offline mode and model optimization functionality
"""

import time
import tempfile
from pathlib import Path
from src.services.integration_service import get_integration_service
from src.services.offline_mode_service import get_offline_service
from src.services.model_optimization_service import (
    get_optimization_service, OptimizationConfig, OptimizationTarget, ModelFormat
)

def demo_offline_mode():
    """Demonstrate offline mode functionality"""
    print("=== AI WellnessVision Offline Mode Demo ===\n")
    
    # Get services
    integration_service = get_integration_service()
    offline_service = get_offline_service()
    optimization_service = get_optimization_service()
    
    print("1. Initializing services...")
    try:
        integration_service.initialize()
        print("✓ Integration service initialized")
    except Exception as e:
        print(f"✗ Integration service initialization failed: {e}")
        return
    
    print("\n2. Checking system status (online mode)...")
    system_overview = integration_service.get_system_overview()
    print(f"✓ Connectivity: {system_overview['system_status']['connectivity']}")
    print(f"✓ Offline mode active: {system_overview['system_status']['offline_mode_active']}")
    print(f"✓ Total services: {system_overview['services']['total']}")
    print(f"✓ Healthy services: {system_overview['services']['healthy']}")
    print(f"✓ Offline capable services: {system_overview['services']['offline_capable']}")
    
    print("\n3. Testing offline mode transition...")
    print("Forcing offline mode...")
    offline_service.force_offline_mode(True)
    
    # Update system status
    integration_service.check_all_services_health()
    offline_overview = integration_service.get_system_overview()
    
    print(f"✓ Offline mode active: {offline_overview['system_status']['offline_mode_active']}")
    print(f"✓ Degraded services: {offline_overview['services']['degraded']}")
    print(f"✓ Unhealthy services: {offline_overview['services']['unhealthy']}")
    print(f"✓ Available features: {len(offline_overview['features']['available'])}")
    print(f"✓ Degraded features: {len(offline_overview['features']['degraded'])}")
    
    print("\n4. Testing offline functionality...")
    test_results = integration_service.test_offline_functionality()
    if test_results['success']:
        print(f"✓ Offline functionality test passed")
        print(f"✓ Total tests: {test_results['total_tests']}")
        print(f"✓ Passed tests: {test_results['passed_tests']}")
        print(f"✓ Offline capable services: {test_results['offline_capable_services']}")
    else:
        print(f"✗ Offline functionality test failed: {test_results.get('error', 'Unknown error')}")
    
    print("\n5. Demonstrating model optimization...")
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock model files
        model_paths = []
        for i in range(2):
            model_path = temp_path / f"demo_model_{i}.pth"
            model_path.write_bytes(b"0" * (10 * 1024 * 1024))  # 10MB mock model
            model_paths.append(model_path)
            print(f"✓ Created mock model: {model_path.name} (10MB)")
        
        # Test model optimization
        print("\nOptimizing models for offline deployment...")
        optimization_result = integration_service.optimize_models_for_offline(model_paths)
        
        if optimization_result['success']:
            print(f"✓ Model optimization successful")
            print(f"✓ Total models: {optimization_result['total_models']}")
            print(f"✓ Successful optimizations: {optimization_result['successful']}")
            print(f"✓ Total size reduction: {optimization_result['total_size_reduction_mb']:.2f}MB")
            
            for model in optimization_result['optimized_models']:
                print(f"  - {Path(model['path']).name}: {model['format']} "
                      f"({model['size_mb']:.2f}MB, {model['compression_ratio']:.2f} compression)")
        else:
            print(f"✗ Model optimization failed: {optimization_result.get('error', 'Unknown error')}")
        
        print("\n6. Preparing offline deployment...")
        deployment_dir = temp_path / "offline_deployment"
        deployment_result = integration_service.prepare_offline_deployment(deployment_dir)
        
        if deployment_result['success']:
            print(f"✓ Offline deployment prepared")
            print(f"✓ Deployment directory: {deployment_result['deployment_directory']}")
            print(f"✓ Optimized models: {deployment_result['optimized_models']}")
            print(f"✓ Total deployment size: {deployment_result['total_size_mb']:.2f}MB")
            print(f"✓ Config file: {Path(deployment_result['config_file']).name}")
        else:
            print(f"✗ Offline deployment preparation failed: {deployment_result.get('error', 'Unknown error')}")
    
    print("\n7. Testing model caching...")
    cache_stats = optimization_service.cache_manager.get_cache_stats()
    print(f"✓ Cache directory: {cache_stats['cache_directory']}")
    print(f"✓ Cached models: {cache_stats['total_cached_models']}")
    print(f"✓ Cache size: {cache_stats['total_cache_size_mb']:.2f}MB")
    print(f"✓ Cache limit: {cache_stats['cache_size_limit_gb']:.1f}GB")
    
    print("\n8. Restoring online mode...")
    offline_service.force_offline_mode(False)
    integration_service.check_all_services_health()
    restored_overview = integration_service.get_system_overview()
    
    print(f"✓ Offline mode active: {restored_overview['system_status']['offline_mode_active']}")
    print(f"✓ Healthy services: {restored_overview['services']['healthy']}")
    
    print("\n9. Getting optimization statistics...")
    opt_stats = optimization_service.get_optimization_stats()
    print(f"✓ Total optimizations: {opt_stats['total_optimizations']}")
    print(f"✓ Successful optimizations: {opt_stats['successful_optimizations']}")
    if opt_stats['total_optimizations'] > 0:
        print(f"✓ Success rate: {opt_stats['success_rate']:.2%}")
        print(f"✓ Average compression ratio: {opt_stats['average_compression_ratio']:.2f}")
        print(f"✓ Average accuracy retained: {opt_stats['average_accuracy_retained']:.2%}")
        print(f"✓ Total size saved: {opt_stats['total_size_saved_mb']:.2f}MB")
    
    print("\n10. Cleanup...")
    try:
        integration_service.shutdown()
        print("✓ Services shutdown successfully")
    except Exception as e:
        print(f"✗ Shutdown error: {e}")
    
    print("\n=== Demo completed successfully! ===")

def demo_individual_services():
    """Demonstrate individual service capabilities"""
    print("\n=== Individual Service Capabilities Demo ===\n")
    
    print("1. Offline Mode Service...")
    offline_service = get_offline_service()
    
    # Test connectivity monitoring
    print("✓ Connectivity monitoring available")
    print("✓ Feature degradation management available")
    print("✓ System status tracking available")
    
    # Get offline capabilities
    capabilities = offline_service.get_offline_capabilities()
    print(f"✓ Offline capabilities defined for {len(capabilities)} services")
    
    for service_name, capability in capabilities.items():
        print(f"  - {service_name}: offline_capable={capability.supports_offline}, "
              f"features={len(capability.offline_features)}")
    
    print("\n2. Model Optimization Service...")
    optimization_service = get_optimization_service()
    
    # Test optimization configurations
    mobile_config = OptimizationConfig(
        target_platform=OptimizationTarget.MOBILE,
        target_format=ModelFormat.TFLITE,
        quantization=True,
        pruning=True
    )
    
    web_config = OptimizationConfig(
        target_platform=OptimizationTarget.WEB,
        target_format=ModelFormat.ONNX,
        quantization=True
    )
    
    print(f"✓ Mobile optimization config: {mobile_config.target_platform.value} -> {mobile_config.target_format.value}")
    print(f"✓ Web optimization config: {web_config.target_platform.value} -> {web_config.target_format.value}")
    
    # Test cache manager
    cache_manager = optimization_service.cache_manager
    print(f"✓ Model cache manager initialized")
    print(f"✓ Cache directory: {cache_manager.cache_dir}")
    print(f"✓ Max cache size: {cache_manager.max_cache_size_gb}GB")
    print(f"✓ Max loaded models: {cache_manager.max_loaded_models}")
    
    print("\n3. Integration Service...")
    integration_service = get_integration_service()
    integration_service._register_services()
    
    print(f"✓ Service registry contains {len(integration_service.service_registry)} services")
    
    for service_name, service_info in integration_service.service_registry.items():
        print(f"  - {service_name}: offline_capable={service_info['offline_capable']}, "
              f"priority={service_info['priority']}")
    
    print("\n=== Individual service demo completed! ===")

if __name__ == "__main__":
    try:
        demo_offline_mode()
        demo_individual_services()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()