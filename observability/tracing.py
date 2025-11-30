"""
Distributed Tracing Setup
"""
import structlog
from config import settings

logger = structlog.get_logger()


def setup_tracing():
    """Setup OpenTelemetry tracing (optional)"""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource
        
        resource = Resource.create({
            "service.name": settings.app_name,
            "service.version": settings.app_version
        })
        
        provider = TracerProvider(resource=resource)
        
        # Add console exporter for development
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        
        trace.set_tracer_provider(provider)
        
        logger.info("OpenTelemetry tracing enabled")
        return trace.get_tracer(__name__)
    except ImportError:
        logger.warning("OpenTelemetry not installed, tracing disabled")
        # Return a no-op tracer
        class NoOpTracer:
            def start_as_current_span(self, *args, **kwargs):
                return self
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        return NoOpTracer()

