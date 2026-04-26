# API package for AI WellnessVision
#
# The modular API is assembled in src.api.main via create_app().
# Individual routers live under src.api.routers.*

try:
    from .main import create_app, app

    from .dependencies import get_db, get_current_user, get_optional_user

    from .routers import auth, analysis, chat, voice, visual_qa

    # Backward-compatible re-exports from legacy gateway / middleware
    try:
        from .gateway import (
            APIGateway, ServiceOrchestrator,
            AnalysisRequest, ChatRequest as GatewayChatRequest,
            SpeechRequest, ExplanationRequest, HealthResponse,
            api_gateway, get_api_app,
        )
        from .middleware import (
            RateLimitMiddleware, SecurityMiddleware, LoggingMiddleware,
            ValidationMiddleware, HealthCheckMiddleware, setup_middleware, get_health_stats,
        )
    except ImportError:
        pass  # Legacy components not required for the new modular API

    API_AVAILABLE = True

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
                "message": "API components not available - mock mode",
            }

    APIGateway = MockAPIGateway
    api_gateway = MockAPIGateway()
    API_AVAILABLE = False