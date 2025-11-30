"""
Metrics Collection for Observability
"""
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge
import time


class MetricsCollector:
    """Metrics collector for agent operations"""
    
    def __init__(self):
        # Request metrics
        self.request_count = Counter(
            "nursesop_requests_total",
            "Total number of requests",
            ["endpoint", "status"]
        )
        
        self.request_duration = Histogram(
            "nursesop_request_duration_seconds",
            "Request duration in seconds",
            ["endpoint"]
        )
        
        # Agent metrics
        self.agent_operations = Counter(
            "nursesop_agent_operations_total",
            "Total agent operations",
            ["agent_type", "operation", "status"]
        )
        
        self.agent_duration = Histogram(
            "nursesop_agent_duration_seconds",
            "Agent operation duration",
            ["agent_type"]
        )
        
        # Tool metrics
        self.tool_usage = Counter(
            "nursesop_tool_usage_total",
            "Tool usage count",
            ["tool_name", "status"]
        )
        
        self.tool_duration = Histogram(
            "nursesop_tool_duration_seconds",
            "Tool execution duration",
            ["tool_name"]
        )
        
        # Session metrics
        self.active_sessions = Gauge(
            "nursesop_active_sessions",
            "Number of active sessions"
        )
        
        # Memory metrics
        self.memory_operations = Counter(
            "nursesop_memory_operations_total",
            "Memory operations",
            ["operation"]
        )
    
    def record_request(self, endpoint: str, status: str, duration: float):
        """Record request metrics"""
        self.request_count.labels(endpoint=endpoint, status=status).inc()
        self.request_duration.labels(endpoint=endpoint).observe(duration)
    
    def record_agent_operation(
        self,
        agent_type: str,
        operation: str,
        status: str,
        duration: float
    ):
        """Record agent operation metrics"""
        self.agent_operations.labels(
            agent_type=agent_type,
            operation=operation,
            status=status
        ).inc()
        self.agent_duration.labels(agent_type=agent_type).observe(duration)
    
    def record_tool_usage(
        self,
        tool_name: str,
        status: str,
        duration: float
    ):
        """Record tool usage metrics"""
        self.tool_usage.labels(tool_name=tool_name, status=status).inc()
        self.tool_duration.labels(tool_name=tool_name).observe(duration)
    
    def update_active_sessions(self, count: int):
        """Update active sessions gauge"""
        self.active_sessions.set(count)
    
    def record_memory_operation(self, operation: str):
        """Record memory operation"""
        self.memory_operations.labels(operation=operation).inc()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics as dictionary"""
        return {
            "active_sessions": self.active_sessions._value.get(),
            "metrics_available": True
        }


def setup_metrics() -> MetricsCollector:
    """Setup and return metrics collector"""
    return MetricsCollector()

