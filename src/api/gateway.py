
# gateway.py - Unified API gateway for AI WellnessVision
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# Optional imports with fallbacks
try:
    from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logging.warning("FastAPI not available - using mock API gateway")
    
    # Mock FastAPI classes
    class FastAPI:
        def __init__(self, **kwargs):
            self.routes = []
        
        def post(self, path: str, **kwargs):
            def decorator(func):
                self.routes.append((path, func))
                return func
            return decorator
        
        def get(self, path: str, **kwargs):
            def decorator(func):
                self.routes.append((path, func))
                return func
            return decorator
    
    class BaseModel:
        pass
    
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
    
    class UploadFile:
        def __init__(self, filename: str = None):
            self.filename = filename

from src.config import AppConfig
from src.models import (
    UserSession, HealthAnalysisResult, ConversationContext, 
    AnalysisType, MessageType, SentimentType
)
from src.services import (
    ImageService, NLPService, SpeechService, ExplainableAIService,
    FULL_SERVICE_AVAILABLE, NLP_SERVICE_AVAILABLE, SPEECH_SERVICE_AVAILABLE, 
    EXPLAINABLE_AI_SERVICE_AVAILABLE
)
from src.utils.logging_config import get_logger, log_performance
from src.api.auth import (
    auth_manager, get_current_user, require_user, require_admin, 
    TokenData, AuthenticationError, AuthorizationError, ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = get_logger(__name__)

# Pydantic models for API requests/responses
if FASTAPI_AVAILABLE:
    class AnalysisRequest(BaseModel):
        analysis_type: str = Field(..., description="Type of analysis to perform")
        session_id: str = Field(..., description="User session ID")
        user_id: Optional[str] = Field(None, description="User ID if authenticated")
        language: Optional[str] = Field("en", description="Preferred language")
        metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class ChatRequest(BaseModel):
        message: str = Field(..., description="User message")
        session_id: str = Field(..., description="Session ID")
        user_id: Optional[str] = Field(None, description="User ID")
        language: Optional[str] = Field("en", description="Message language")
        message_type: str = Field("text", description="Message type (text/voice)")
    
    class SpeechRequest(BaseModel):
        text: str = Field(..., description="Text to synthesize")
        language: str = Field("en", description="Target language")
        voice_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class ExplanationRequest(BaseModel):
        analysis_id: str = Field(..., description="Analysis ID to explain")
        explanation_types: List[str] = Field(default=["decision_path"], description="Types of explanations")
    
    class LoginRequest(BaseModel):
        username: str = Field(..., description="Username")
        password: str = Field(..., description="Password")
    
    class TokenResponse(BaseModel):
        access_token: str
        refresh_token: str
        token_type: str = "bearer"
        expires_in: int
        user_info: Dict[str, Any]
    
    class HealthResponse(BaseModel):
        status: str
        data: Optional[Dict[str, Any]] = None
        message: Optional[str] = None
        timestamp: datetime = Field(default_factory=datetime.utcnow)
        processing_time: Optional[float] = None
        request_id: Optional[str] = None
else:
    # Mock Pydantic models
    class AnalysisRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ChatRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            # Set defaults for missing attributes
            if not hasattr(self, 'message_type'):
                self.message_type = 'text'
            if not hasattr(self, 'user_id'):
                self.user_id = None
    
    class SpeechRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            # Set defaults for missing attributes
            if not hasattr(self, 'voice_settings'):
                self.voice_settings = {}
    
    class ExplanationRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class LoginRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class TokenResponse:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class HealthResponse:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

class ServiceOrchestrator:
    """Orchestrates communication between different AI services"""
    
    def __init__(self):
        self.image_service = ImageService()
        self.nlp_service = NLPService()
        self.speech_service = SpeechService()
        self.explainable_ai_service = ExplainableAIService()
        
        self.active_sessions = {}
        self.analysis_cache = {}
        
        logger.info("Service Orchestrator initialized")
    
    def get_session(self, session_id: str, user_id: str = None, language: str = "en") -> UserSession:
        """Get or create user session"""
        if session_id not in self.active_sessions:
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                language_preference=language
            )
            self.active_sessions[session_id] = session
        
        return self.active_sessions[session_id]
    
    @log_performance()
    async def process_image_analysis(self, image_file: UploadFile, 
                                   analysis_request: AnalysisRequest) -> Dict[str, Any]:
        """Process image analysis request"""
        try:
            start_time = time.time()
            
            # Validate analysis type
            try:
                analysis_type = AnalysisType(analysis_request.analysis_type)
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid analysis type: {analysis_request.analysis_type}"
                )
            
            # Get user session
            session = self.get_session(
                analysis_request.session_id, 
                analysis_request.user_id,
                analysis_request.language
            )
            
            # Save uploaded file temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{image_file.filename.split('.')[-1]}") as temp_file:
                if hasattr(image_file, 'read'):
                    content = await image_file.read()
                    temp_file.write(content)
                else:
                    # Mock file for testing
                    temp_file.write(b"mock image data")
                temp_path = temp_file.name
            
            try:
                # Perform image analysis
                analysis_result = self.image_service.analyze_image(
                    temp_path, 
                    analysis_type,
                    f"api_{analysis_request.session_id}_{int(time.time())}"
                )
                
                # Add to session history
                session.add_analysis_entry(analysis_type.value, analysis_result.to_dict())
                
                # Cache result for potential explanation requests
                self.analysis_cache[analysis_result.analysis_id] = analysis_result
                
                processing_time = time.time() - start_time
                
                return {
                    'status': 'success',
                    'analysis_result': analysis_result.to_dict(),
                    'session_id': analysis_request.session_id,
                    'processing_time': processing_time
                }
                
            finally:
                # Clean up temporary file
                try:
                    Path(temp_path).unlink()
                except Exception as e:
                    logger.warning(f"Could not delete temp file: {e}")
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    @log_performance()
    async def process_chat_message(self, chat_request: ChatRequest) -> Dict[str, Any]:
        """Process chat message request"""
        try:
            start_time = time.time()
            
            # Get user session
            session = self.get_session(
                chat_request.session_id,
                chat_request.user_id,
                chat_request.language
            )
            
            # Process message with NLP service
            nlp_result = self.nlp_service.process_message(
                chat_request.message,
                chat_request.user_id or "anonymous",
                chat_request.session_id,
                chat_request.language
            )
            
            # Add to session conversation history
            session.add_conversation_entry(
                chat_request.message,
                nlp_result['response'],
                chat_request.message_type
            )
            
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'response': nlp_result['response'],
                'language': nlp_result['language'],
                'sentiment': nlp_result['sentiment'],
                'entities': nlp_result['entities'],
                'confidence': nlp_result['confidence'],
                'session_id': chat_request.session_id,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    @log_performance()
    async def process_speech_synthesis(self, speech_request: SpeechRequest) -> Dict[str, Any]:
        """Process text-to-speech request"""
        try:
            start_time = time.time()
            
            # Synthesize speech
            tts_result = self.speech_service.synthesize_speech(
                speech_request.text,
                speech_request.language,
                speech_request.voice_settings
            )
            
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'audio_data': tts_result,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    @log_performance()
    async def process_speech_transcription(self, audio_file: UploadFile, 
                                         language: str = None) -> Dict[str, Any]:
        """Process speech-to-text request"""
        try:
            start_time = time.time()
            
            # Save uploaded audio file temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                if hasattr(audio_file, 'read'):
                    content = await audio_file.read()
                    temp_file.write(content)
                else:
                    # Mock audio for testing
                    temp_file.write(b"mock audio data")
                temp_path = temp_file.name
            
            try:
                # Transcribe audio
                transcription_result = self.speech_service.transcribe_audio(
                    temp_path, language=language
                )
                
                processing_time = time.time() - start_time
                
                return {
                    'status': 'success',
                    'transcription': transcription_result,
                    'processing_time': processing_time
                }
                
            finally:
                # Clean up temporary file
                try:
                    Path(temp_path).unlink()
                except Exception as e:
                    logger.warning(f"Could not delete temp audio file: {e}")
            
        except Exception as e:
            logger.error(f"Speech transcription failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    @log_performance()
    async def process_explanation_request(self, explanation_request: ExplanationRequest) -> Dict[str, Any]:
        """Process explanation request"""
        try:
            start_time = time.time()
            
            # Get analysis result from cache
            analysis_result = self.analysis_cache.get(explanation_request.analysis_id)
            if not analysis_result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Analysis result not found: {explanation_request.analysis_id}"
                )
            
            # Generate explanation
            explanation_result = self.explainable_ai_service.explain_prediction(
                analysis_result,
                explanation_types=explanation_request.explanation_types
            )
            
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'explanation': explanation_result,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    async def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get session conversation and analysis history"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return {
                    'status': 'error',
                    'message': 'Session not found'
                }
            
            return {
                'status': 'success',
                'session_id': session_id,
                'conversation_history': session.get_recent_conversations(),
                'analysis_history': session.get_recent_analyses(),
                'language_preference': session.language_preference
            }
            
        except Exception as e:
            logger.error(f"Session history retrieval failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        return {
            'image_service': {
                'available': FULL_SERVICE_AVAILABLE,
                'info': self.image_service.get_model_info() if hasattr(self.image_service, 'get_model_info') else {}
            },
            'nlp_service': {
                'available': NLP_SERVICE_AVAILABLE,
                'supported_languages': self.nlp_service.get_supported_languages() if hasattr(self.nlp_service, 'get_supported_languages') else []
            },
            'speech_service': {
                'available': SPEECH_SERVICE_AVAILABLE,
                'info': self.speech_service.get_service_info() if hasattr(self.speech_service, 'get_service_info') else {}
            },
            'explainable_ai_service': {
                'available': EXPLAINABLE_AI_SERVICE_AVAILABLE,
                'capabilities': self.explainable_ai_service.get_explanation_capabilities() if hasattr(self.explainable_ai_service, 'get_explanation_capabilities') else {}
            }
        }

class APIGateway:
    """Main API Gateway class that sets up FastAPI routes and middleware"""
    
    def __init__(self):
        self.orchestrator = ServiceOrchestrator()
        self.app = self._create_app() if FASTAPI_AVAILABLE else None
        
        if self.app:
            self._setup_middleware()
            self._setup_routes()
            logger.info("API Gateway initialized with FastAPI")
        else:
            logger.warning("API Gateway initialized in mock mode (FastAPI not available)")
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        return FastAPI(
            title="AI WellnessVision API",
            description="Comprehensive AI-powered health and wellness analysis API",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
    
    def _setup_middleware(self):
        """Setup middleware for security and CORS"""
        if not self.app:
            return
        
        # Import and setup custom middleware
        from src.api.middleware import setup_middleware
        setup_middleware(self.app)
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=AppConfig.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        if AppConfig.ENVIRONMENT.value == "production":
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["localhost", "127.0.0.1", "*.wellnessvision.ai"]
            )
    
    def _setup_routes(self):
        """Setup API routes"""
        if not self.app:
            return
        
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow(),
                "services": self.orchestrator.get_service_status()
            }
        
        # Authentication endpoints
        @self.app.post("/api/v1/auth/login")
        async def login(request: LoginRequest):
            """User login endpoint"""
            try:
                user = auth_manager.authenticate_user(request.username, request.password)
                
                access_token = auth_manager.create_access_token(user)
                refresh_token = auth_manager.create_refresh_token(user)
                
                return TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    user_info={
                        "username": user.username,
                        "email": user.email,
                        "roles": user.roles,
                        "last_login": user.last_login.isoformat() if user.last_login else None
                    }
                )
                
            except AuthenticationError as e:
                raise HTTPException(status_code=401, detail=str(e))
            except Exception as e:
                logger.error(f"Login endpoint failed: {e}")
                raise HTTPException(status_code=500, detail="Login failed")
        
        @self.app.post("/api/v1/auth/logout")
        async def logout(current_user: TokenData = Depends(get_current_user)):
            """User logout endpoint"""
            try:
                # In a real implementation, you'd get the token from the request
                # For now, we'll just log the logout
                logger.info(f"User logged out: {current_user.username}")
                
                return HealthResponse(
                    status="success",
                    message="Logged out successfully"
                )
                
            except Exception as e:
                logger.error(f"Logout endpoint failed: {e}")
                raise HTTPException(status_code=500, detail="Logout failed")
        
        @self.app.get("/api/v1/auth/me")
        async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
            """Get current user information"""
            try:
                return HealthResponse(
                    status="success",
                    data={
                        "username": current_user.username,
                        "user_id": current_user.user_id,
                        "roles": current_user.roles,
                        "token_expires": current_user.exp.isoformat()
                    }
                )
                
            except Exception as e:
                logger.error(f"User info endpoint failed: {e}")
                raise HTTPException(status_code=500, detail="Failed to get user info")
        
        # Image analysis endpoint
        @self.app.post("/api/v1/analyze/image")
        async def analyze_image(
            file: UploadFile = File(...),
            analysis_type: str = Form(...),
            session_id: str = Form(...),
            user_id: str = Form(None),
            language: str = Form("en"),
            current_user: TokenData = Depends(require_user)
        ):
            """Analyze uploaded image"""
            try:
                request = AnalysisRequest(
                    analysis_type=analysis_type,
                    session_id=session_id,
                    user_id=user_id,
                    language=language
                )
                
                result = await self.orchestrator.process_image_analysis(file, request)
                
                if result['status'] == 'error':
                    raise HTTPException(status_code=500, detail=result['message'])
                
                return HealthResponse(
                    status="success",
                    data=result,
                    processing_time=result.get('processing_time')
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Image analysis endpoint failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Chat endpoint
        @self.app.post("/api/v1/chat")
        async def chat(request: ChatRequest, current_user: TokenData = Depends(require_user)):
            """Process chat message"""
            try:
                result = await self.orchestrator.process_chat_message(request)
                
                if result['status'] == 'error':
                    raise HTTPException(status_code=500, detail=result['message'])
                
                return HealthResponse(
                    status="success",
                    data=result,
                    processing_time=result.get('processing_time')
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Chat endpoint failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Speech synthesis endpoint
        @self.app.post("/api/v1/speech/synthesize")
        async def synthesize_speech(request: SpeechRequest, current_user: TokenData = Depends(require_user)):
            """Convert text to speech"""
            try:
                result = await self.orchestrator.process_speech_synthesis(request)
                
                if result['status'] == 'error':
                    raise HTTPException(status_code=500, detail=result['message'])
                
                return HealthResponse(
                    status="success",
                    data=result,
                    processing_time=result.get('processing_time')
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Speech synthesis endpoint failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Speech transcription endpoint
        @self.app.post("/api/v1/speech/transcribe")
        async def transcribe_speech(
            file: UploadFile = File(...),
            language: str = Form(None),
            current_user: TokenData = Depends(require_user)
        ):
            """Convert speech to text"""
            try:
                result = await self.orchestrator.process_speech_transcription(file, language)
                
                if result['status'] == 'error':
                    raise HTTPException(status_code=500, detail=result['message'])
                
                return HealthResponse(
                    status="success",
                    data=result,
                    processing_time=result.get('processing_time')
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Speech transcription endpoint failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Explanation endpoint
        @self.app.post("/api/v1/explain")
        async def explain_prediction(request: ExplanationRequest, current_user: TokenData = Depends(require_user)):
            """Generate explanation for analysis result"""
            try:
                result = await self.orchestrator.process_explanation_request(request)
                
                if result['status'] == 'error':
                    raise HTTPException(status_code=500, detail=result['message'])
                
                return HealthResponse(
                    status="success",
                    data=result,
                    processing_time=result.get('processing_time')
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Explanation endpoint failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Session history endpoint
        @self.app.get("/api/v1/session/{session_id}/history")
        async def get_session_history(session_id: str, current_user: TokenData = Depends(require_user)):
            """Get session conversation and analysis history"""
            try:
                result = await self.orchestrator.get_session_history(session_id)
                
                if result['status'] == 'error':
                    raise HTTPException(status_code=404, detail=result['message'])
                
                return HealthResponse(
                    status="success",
                    data=result
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Session history endpoint failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Service status endpoint (admin only)
        @self.app.get("/api/v1/status")
        async def get_service_status(current_user: TokenData = Depends(require_admin)):
            """Get status of all AI services"""
            try:
                status = self.orchestrator.get_service_status()
                
                return HealthResponse(
                    status="success",
                    data=status
                )
                
            except Exception as e:
                logger.error(f"Service status endpoint failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Supported languages endpoint
        @self.app.get("/api/v1/languages")
        async def get_supported_languages():
            """Get list of supported languages"""
            try:
                languages = AppConfig.SUPPORTED_LANGUAGES
                
                return HealthResponse(
                    status="success",
                    data={
                        "supported_languages": languages,
                        "default_language": AppConfig.DEFAULT_LANGUAGE
                    }
                )
                
            except Exception as e:
                logger.error(f"Languages endpoint failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def get_app(self):
        """Get FastAPI application instance"""
        return self.app
    
    def run_mock_server(self, host: str = "localhost", port: int = 8000):
        """Run mock server when FastAPI is not available"""
        logger.info(f"Mock API server would run on {host}:{port}")
        logger.info("Available endpoints:")
        logger.info("  POST /api/v1/analyze/image - Image analysis")
        logger.info("  POST /api/v1/chat - Chat with AI")
        logger.info("  POST /api/v1/speech/synthesize - Text to speech")
        logger.info("  POST /api/v1/speech/transcribe - Speech to text")
        logger.info("  POST /api/v1/explain - Explain predictions")
        logger.info("  GET /api/v1/session/{session_id}/history - Session history")
        logger.info("  GET /api/v1/status - Service status")
        logger.info("  GET /api/v1/languages - Supported languages")
        logger.info("  GET /health - Health check")
        
        return {
            "status": "mock_server_ready",
            "host": host,
            "port": port,
            "fastapi_available": FASTAPI_AVAILABLE
        }

# Global API gateway instance
api_gateway = APIGateway()

def get_api_app():
    """Get the FastAPI application instance"""
    return api_gateway.get_app()

def create_app():
    """Create and configure the FastAPI application"""
    return api_gateway.get_app()

# For testing and development
if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn
        app = get_api_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        result = api_gateway.run_mock_server()
        print("Mock server info:", result)