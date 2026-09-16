"""System health and uptime metrics collector."""
from typing import Dict, Any
import time

_START_TIME = time.time()

def get_system_metrics() -> Dict[str, Any]:
    """Return uptime and service operational status metrics."""
    uptime_seconds = round(time.time() - _START_TIME, 2)
    return {
        "service": "fintech-payment-service",
        "status": "healthy",
        "uptime_seconds": uptime_seconds,
        "version": "1.0.0",
    }
