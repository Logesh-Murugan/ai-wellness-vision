# API package for AI WellnessVision

try:
    from .gateway import (
        APIGateway, ServiceOrchestrator, 
        AnalysisRequest, ChatRequest, SpeechRequest, ExplanationRequest, HealthResponse,
        api_gateway, get_api_app, create_app
    )
    from .middleware import (
        RateLimitMiddleware, SecurityMiddleware, LoggingMiddleware,
        ValidationMiddleware, HealthCheckMiddleware, setup_middleware, get_health_stats
    )
    
    API_AVAILABLE = True
    
    __all__ = [
        'APIGateway', 'ServiceOrchestrator',
        'AnalysisRequest', 'ChatRequest', 'SpeechRequest', 'ExplanationRequest', 'HealthResponse',
        'api_gateway', 'get_api_app', 'create_app',
        'RateLimitMiddleware', 'SecurityMiddleware', 'LoggingMiddleware',
        'ValidationMiddleware', 'HealthCheckMiddleware', 'setup_middleware', 'get_health_stats'
    ]
    
except ImportError as e:
    import logging
    logging.warning(f"API components not available: {e}")
    
    class MockAPIGateway:
        def __init__(self):
            pass
        
        def get_app(self):
            return None
        
        def run_mock_server(self, host="localhost", port=8000):
            return {
                "status": "mock_api_ready",
                "host": host,
                "port": port,
                "message": "API components not available - mock mode"
            }
    
    APIGateway = MockAPIGateway
    api_gateway = MockAPIGateway()
    API_AVAILABLE = False
    
    __all__ = ['APIGateway', 'api_gateway']