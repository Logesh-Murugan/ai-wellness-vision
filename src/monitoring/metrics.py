from prometheus_client import Histogram, Counter, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator

# ---------------------------------------------------------
# AI-Specific Prometheus Metrics Definitions
# ---------------------------------------------------------

# Tracks how long internal ML models take to predict/analyze (isolated from network latency)
MODEL_PREDICTION_DURATION = Histogram(
    "wellness_model_prediction_duration_seconds",
    "Time spent running ML inference models",
    labels=["model_type", "analysis_type"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Tracks the confidence scores output by models to monitor drift/quality
PREDICTION_CONFIDENCE = Histogram(
    "wellness_prediction_confidence",
    "Confidence score of ML predictions (0.0 to 1.0)",
    labels=["model_type", "predicted_class"],
    buckets=[0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99]
)

# Tracks the total volume of analysis requests per type and status
ANALYSIS_REQUESTS = Counter(
    "wellness_analysis_requests_total",
    "Total number of AI health analysis requests",
    labels=["analysis_type", "status", "model_used"]
)

# Tracks currently active concurrent users
ACTIVE_USERS = Gauge(
    "wellness_active_users",
    "Number of currently active users executing requests"
)

# Tracks conversational AI throughput
CHAT_MESSAGES = Counter(
    "wellness_chat_messages_total",
    "Total number of conversational chat requests processed",
    labels=["language", "response_source"] # response_source: llm, fallback, cache
)

# Tracks the time spent processing speech
VOICE_PROCESSING = Histogram(
    "wellness_voice_processing_duration_seconds",
    "Time spent handling Whisper STT or Edge TTS",
    labels=["operation"], # operation: transcribe, synthesize
    buckets=[0.5, 1.0, 3.0, 5.0, 10.0, 20.0, 30.0]
)

# Exposes static information about the deployed models
MODEL_INFO = Info(
    "wellness_model",
    "Information about currently loaded AI models"
)

# Tracks the efficiency of the Redis cache layer
CACHE_HIT_RATE = Gauge(
    "wellness_cache_hit_rate",
    "Cache hit rate percentage (0-100)",
    labels=["cache_type"] # cache_type: image, nutrition, chat
)


# ---------------------------------------------------------
# FastAPI Instrumentation Hook
# ---------------------------------------------------------
def setup_metrics(app):
    """
    Mounts Prometheus metrics onto the FastAPI application.
    Exposes the /metrics endpoint which Prometheus scrapes.
    """
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS"
    )
    
    # Expose the /metrics route (hidden from Swagger UI docs)
    instrumentator.instrument(app).expose(app, include_in_schema=False, tags=["metrics"])
