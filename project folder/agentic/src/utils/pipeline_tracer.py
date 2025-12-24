"""
Pipeline Metrics and Latency Instrumentation
Provides timing, tracing, and structured logging for the agentic pipeline
"""
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
from functools import wraps

# Create a dedicated logger for pipeline tracing (don't modify root logger)
pipeline_logger = logging.getLogger("agentic.pipeline")
pipeline_logger.setLevel(logging.INFO)

# Only add handler if not already added (prevent duplicate logs on reload)
if not pipeline_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    pipeline_logger.addHandler(handler)
    pipeline_logger.propagate = False  # Don't bubble up to root logger


@dataclass
class StageMetrics:
    """Metrics for a single pipeline stage"""
    stage_name: str
    start_time: float = 0.0
    end_time: float = 0.0
    latency_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineMetrics:
    """Complete metrics for a pipeline run"""
    trace_id: str
    ticket_id: Optional[int] = None
    
    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_latency_ms: int = 0
    
    # Stage metrics
    stages: Dict[str, StageMetrics] = field(default_factory=dict)
    
    # Processing stats
    total_llm_calls: int = 0
    rag_attempts: int = 0
    documents_retrieved: int = 0
    
    # Error tracking
    had_errors: bool = False
    error_stage: Optional[str] = None
    error_message: Optional[str] = None
    
    # Circuit breaker
    circuit_breaker_triggered: bool = False
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/logging"""
        return {
            "trace_id": self.trace_id,
            "ticket_id": self.ticket_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_latency_ms": self.total_latency_ms,
            "stages": {
                name: {
                    "latency_ms": stage.latency_ms,
                    "success": stage.success,
                    "error": stage.error_message
                }
                for name, stage in self.stages.items()
            },
            "total_llm_calls": self.total_llm_calls,
            "rag_attempts": self.rag_attempts,
            "documents_retrieved": self.documents_retrieved,
            "had_errors": self.had_errors,
            "error_stage": self.error_stage,
            "error_message": self.error_message,
            "circuit_breaker_triggered": self.circuit_breaker_triggered,
            "retry_count": self.retry_count
        }


class PipelineTracer:
    """
    Instruments the agentic pipeline with timing and tracing.
    Generates structured logs with trace_id for debugging.
    """
    
    # Target latencies (in ms)
    TARGET_TOTAL_LATENCY_MS = 10000  # <10s end-to-end
    IDEAL_TOTAL_LATENCY_MS = 5000   # <5s is better
    
    # Circuit breaker settings
    MAX_RETRIES = 3
    
    def __init__(self, ticket_id: Optional[int] = None):
        """Initialize a new pipeline trace"""
        self.trace_id = self._generate_trace_id()
        self.metrics = PipelineMetrics(
            trace_id=self.trace_id,
            ticket_id=ticket_id
        )
        self._stage_start_times: Dict[str, float] = {}
        self.logger = pipeline_logger  # Use dedicated pipeline logger
    
    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"TRC-{timestamp}-{short_uuid}"
    
    def _log(self, level: str, message: str, **kwargs):
        """Log with trace_id context"""
        extra = {"trace_id": self.trace_id, **kwargs}
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(message, extra=extra)
    
    def start_pipeline(self):
        """Mark pipeline start"""
        self.metrics.started_at = datetime.utcnow()
        self._pipeline_start = time.perf_counter()
        print(f"[TRACE:{self.trace_id}] ▶️  Pipeline started")
    
    def end_pipeline(self):
        """Mark pipeline end and calculate total latency"""
        self.metrics.completed_at = datetime.utcnow()
        if hasattr(self, '_pipeline_start'):
            self.metrics.total_latency_ms = int((time.perf_counter() - self._pipeline_start) * 1000)
        
        # Check latency targets
        latency_status = "✅ EXCELLENT" if self.metrics.total_latency_ms < self.IDEAL_TOTAL_LATENCY_MS else \
                        "✅ OK" if self.metrics.total_latency_ms < self.TARGET_TOTAL_LATENCY_MS else \
                        "⚠️ SLOW"
        
        print(f"[TRACE:{self.trace_id}] ⏱️  Total Latency: {self.metrics.total_latency_ms}ms {latency_status}")
        print(f"[TRACE:{self.trace_id}] 🏁 Pipeline completed")
        
        # Log latency breakdown
        self._print_latency_breakdown()
    
    def _print_latency_breakdown(self):
        """Print formatted latency breakdown"""
        print(f"\n[TRACE:{self.trace_id}] ━━━━ LATENCY BREAKDOWN ━━━━")
        for stage_name, stage in self.metrics.stages.items():
            status = "✅" if stage.success else "❌"
            percent = (stage.latency_ms / self.metrics.total_latency_ms * 100) if self.metrics.total_latency_ms > 0 else 0
            print(f"[TRACE:{self.trace_id}]   {status} {stage_name}: {stage.latency_ms}ms ({percent:.1f}%)")
        print(f"[TRACE:{self.trace_id}]   ────────────────────────")
        print(f"[TRACE:{self.trace_id}]   📊 TOTAL: {self.metrics.total_latency_ms}ms")
        print(f"[TRACE:{self.trace_id}] ━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    @contextmanager
    def stage(self, stage_name: str):
        """
        Context manager for timing a pipeline stage.
        
        Usage:
            with tracer.stage("classification"):
                # do classification work
        """
        stage_metrics = StageMetrics(stage_name=stage_name)
        stage_metrics.start_time = time.perf_counter()
        
        print(f"[TRACE:{self.trace_id}] 🔄 Starting stage: {stage_name}")
        
        try:
            yield stage_metrics
            stage_metrics.success = True
        except Exception as e:
            stage_metrics.success = False
            stage_metrics.error_message = str(e)
            self.metrics.had_errors = True
            self.metrics.error_stage = stage_name
            self.metrics.error_message = str(e)
            print(f"[TRACE:{self.trace_id}] ❌ Stage failed: {stage_name} - {e}")
            raise
        finally:
            stage_metrics.end_time = time.perf_counter()
            stage_metrics.latency_ms = int((stage_metrics.end_time - stage_metrics.start_time) * 1000)
            self.metrics.stages[stage_name] = stage_metrics
            
            status = "✅" if stage_metrics.success else "❌"
            print(f"[TRACE:{self.trace_id}] {status} Completed stage: {stage_name} ({stage_metrics.latency_ms}ms)")
    
    def record_llm_call(self):
        """Record an LLM API call"""
        self.metrics.total_llm_calls += 1
    
    def record_rag_attempt(self):
        """Record a RAG retrieval attempt"""
        self.metrics.rag_attempts += 1
    
    def record_documents(self, count: int):
        """Record number of documents retrieved"""
        self.metrics.documents_retrieved = count
    
    def record_retry(self):
        """Record a retry attempt"""
        self.metrics.retry_count += 1
        if self.metrics.retry_count >= self.MAX_RETRIES:
            self.metrics.circuit_breaker_triggered = True
            print(f"[TRACE:{self.trace_id}] ⚡ Circuit breaker triggered after {self.metrics.retry_count} retries")
    
    def get_metrics(self) -> PipelineMetrics:
        """Get the current metrics"""
        return self.metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary dict for API responses"""
        return {
            "trace_id": self.trace_id,
            "total_latency_ms": self.metrics.total_latency_ms,
            "latency_target_met": self.metrics.total_latency_ms < self.TARGET_TOTAL_LATENCY_MS,
            "latency_ideal_met": self.metrics.total_latency_ms < self.IDEAL_TOTAL_LATENCY_MS,
            "llm_calls": self.metrics.total_llm_calls,
            "rag_attempts": self.metrics.rag_attempts,
            "had_errors": self.metrics.had_errors,
            "stages": list(self.metrics.stages.keys())
        }


def timed_stage(stage_name: str):
    """
    Decorator for timing individual functions as pipeline stages.
    
    Usage:
        @timed_stage("classification")
        def classify_query(self, query: str, tracer: PipelineTracer):
            # classification logic
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to find tracer in args or kwargs
            tracer = kwargs.get('tracer')
            if tracer is None:
                for arg in args:
                    if isinstance(arg, PipelineTracer):
                        tracer = arg
                        break
            
            if tracer:
                with tracer.stage(stage_name):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Convenience function
def create_tracer(ticket_id: Optional[int] = None) -> PipelineTracer:
    """Create a new pipeline tracer"""
    return PipelineTracer(ticket_id=ticket_id)
