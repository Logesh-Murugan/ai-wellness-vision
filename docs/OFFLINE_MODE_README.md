# Offline Mode and Model Optimization

This document describes the offline mode and model optimization features implemented for AI WellnessVision.

## Overview

The offline mode and model optimization system provides:

1. **Offline Mode Detection**: Automatic detection of network connectivity and graceful degradation
2. **Model Optimization**: TensorFlow Lite and ONNX model conversion for mobile/edge deployment
3. **Model Caching**: Intelligent caching and lazy loading of AI models
4. **Service Integration**: Seamless integration with all AI services

## Features Implemented

### 1. Offline Mode Service (`src/services/offline_mode_service.py`)

#### Connectivity Monitoring
- Real-time network connectivity monitoring
- Automatic detection of online/offline/limited connectivity states
- Historical connectivity tracking and statistics

#### Feature Degradation Management
- Graceful degradation of services when offline
- Fallback mechanisms for each AI service
- User-friendly notifications about limited functionality

#### Service Capabilities
- **Image Analysis**: Mock analysis with basic recommendations
- **NLP Service**: Keyword-based responses and cached conversations
- **Speech Service**: Disabled (not offline-capable)
- **Explainable AI**: Template-based explanations

### 2. Model Optimization Service (`src/services/model_optimization_service.py`)

#### TensorFlow Lite Conversion
- Convert PyTorch/TensorFlow models to TFLite format
- Quantization support for size reduction
- Model pruning for further optimization
- Mobile-optimized configurations

#### ONNX Conversion
- Cross-platform model format support
- Web deployment optimization
- Model graph optimization passes
- Compatibility with ONNX Runtime

#### Model Caching
- Intelligent model caching with LRU eviction
- Lazy loading of models to save memory
- Configurable cache size limits
- Access statistics and cleanup utilities

### 3. Integration Service (`src/services/integration_service.py`)

#### Service Orchestration
- Centralized management of all AI services
- Health monitoring and status reporting
- Automatic service degradation/restoration

#### Deployment Preparation
- Batch model optimization for offline deployment
- Deployment package creation with configuration
- Size optimization and compression statistics

## Usage Examples

### Basic Offline Mode Usage

```python
from src.services.offline_mode_service import get_offline_service

# Get offline service
offline_service = get_offline_service()
offline_service.initialize()

# Check system status
status = offline_service.get_system_status()
print(f"Offline mode active: {status.offline_mode_active}")
print(f"Available features: {status.available_features}")

# Force offline mode for testing
offline_service.force_offline_mode(True)
```

### Model Optimization

```python
from src.services.model_optimization_service import (
    get_optimization_service, OptimizationConfig, 
    OptimizationTarget, ModelFormat
)

# Get optimization service
opt_service = get_optimization_service()

# Create optimization configuration
config = OptimizationConfig(
    target_platform=OptimizationTarget.MOBILE,
    target_format=ModelFormat.TFLITE,
    quantization=True,
    pruning=True,
    max_model_size_mb=10.0
)

# Optimize model
result = opt_service.optimize_model(
    model_path=Path("model.pth"),
    target_config=config
)

print(f"Optimization successful: {result.success}")
print(f"Size reduction: {result.original_size_mb - result.optimized_size_mb:.2f}MB")
```

### Integration Service

```python
from src.services.integration_service import get_integration_service

# Get integration service
integration = get_integration_service()
integration.initialize()

# Get system overview
overview = integration.get_system_overview()
print(f"Healthy services: {overview['services']['healthy']}")
print(f"Offline capable: {overview['services']['offline_capable']}")

# Prepare offline deployment
deployment = integration.prepare_offline_deployment(Path("deployment"))
print(f"Deployment ready: {deployment['success']}")
```

## Configuration

### Offline Mode Configuration

The offline mode service can be configured through environment variables or configuration files:

```json
{
  "offline_mode": {
    "connectivity_check_interval": 30,
    "max_connectivity_history": 100,
    "fallback_responses": {
      "image_analysis": {
        "message": "Image analysis unavailable offline",
        "suggestions": ["Check connection", "Try again later"]
      }
    }
  }
}
```

### Model Optimization Configuration

```json
{
  "model_optimization": {
    "cache_size_gb": 5.0,
    "max_loaded_models": 3,
    "optimization_levels": {
      "mobile": {
        "quantization": true,
        "pruning": true,
        "max_size_mb": 10.0
      },
      "web": {
        "quantization": true,
        "pruning": false,
        "max_size_mb": 25.0
      }
    }
  }
}
```

## Testing

### Running Tests

```bash
# Test offline mode functionality
python -m pytest tests/test_offline_mode.py -v

# Test model optimization
python -m pytest tests/test_model_optimization.py -v

# Test integration
python -m pytest tests/test_integration_offline.py -v
```

### Demo Script

Run the comprehensive demo to see all features in action:

```bash
python demo_offline_mode.py
```

The demo will:
1. Initialize all services
2. Test online/offline transitions
3. Demonstrate model optimization
4. Show caching functionality
5. Prepare offline deployment packages

## Architecture

### Service Dependencies

```
Integration Service
├── Offline Mode Service
│   ├── Connectivity Monitor
│   └── Feature Degradation Manager
├── Model Optimization Service
│   ├── TensorFlow Lite Converter
│   ├── ONNX Converter
│   └── Model Cache Manager
└── AI Services (Image, NLP, Speech, ExplainableAI)
```

### Data Flow

1. **Connectivity Monitoring**: Continuous monitoring of network status
2. **Status Updates**: Automatic service degradation/restoration
3. **Model Loading**: Lazy loading with caching for performance
4. **Fallback Responses**: Graceful degradation with user notifications

## Performance Considerations

### Memory Usage
- Model caching limited to 5GB by default
- Maximum 3 models loaded in memory simultaneously
- LRU eviction policy for cache management

### Storage Usage
- Optimized models typically 30-70% smaller than originals
- TFLite models generally smaller than ONNX
- Cache cleanup removes models older than 30 days

### Network Usage
- Connectivity checks every 30 seconds
- Minimal bandwidth usage for status monitoring
- No model downloads in offline mode

## Deployment

### Offline Deployment Package

The system can create self-contained offline deployment packages:

```
offline_deployment/
├── offline_deployment_config.json
├── optimized_model_1.tflite
├── optimized_model_2.onnx
└── cache/
    └── models/
```

### Requirements

- **Minimum**: Python 3.8+, basic dependencies
- **Full Features**: TensorFlow, PyTorch, ONNX Runtime
- **Storage**: 1GB+ for model cache
- **Memory**: 2GB+ for model loading

## Troubleshooting

### Common Issues

1. **Models not loading**: Check cache directory permissions
2. **Optimization failing**: Verify TensorFlow/PyTorch installation
3. **Offline mode not activating**: Check connectivity monitoring settings
4. **High memory usage**: Reduce max_loaded_models setting

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.getLogger('src.services').setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Advanced Optimization**: Support for TensorRT, OpenVINO
2. **Streaming Models**: Progressive model loading
3. **Federated Learning**: Offline model updates
4. **Edge Computing**: Specialized edge device optimizations

## Requirements Satisfied

This implementation satisfies the following requirements from the specification:

- **6.1**: Offline mode detection and graceful feature degradation ✓
- **6.2**: Model optimization for cross-platform compatibility ✓  
- **6.4**: Model caching and lazy loading mechanisms ✓

All sub-tasks have been completed:
- ✓ TensorFlow Lite model conversion pipeline
- ✓ ONNX model export and optimization
- ✓ Offline mode detection and graceful degradation
- ✓ Model caching and lazy loading mechanisms
- ✓ Comprehensive tests for offline functionality and model optimization