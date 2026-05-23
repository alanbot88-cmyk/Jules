from prometheus_client import Counter, Histogram, start_http_server
from .bus import CognitiveBus
from .events import BaseEvent
from loguru import logger

# Metrics definitions
EVENTS_PUBLISHED = Counter("cognitive_bus_events_total", "Total events published", ["event_type", "source_agent"])
EVENT_LATENCY = Histogram("cognitive_bus_event_latency_seconds", "Latency of event processing", ["event_type"])

class TelemetryManager:
    def __init__(self, bus: CognitiveBus, port: int = 9090):
        self.bus = bus
        self.port = port

    def start(self):
        try:
            start_http_server(self.port)
            logger.info(f"Metrics server started on port {self.port}")
            self.bus.subscribe("*", self.observe_event)
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")

    def observe_event(self, event: BaseEvent):
        EVENTS_PUBLISHED.labels(event_type=event.event_type, source_agent=event.source_agent).inc()
        # Latency tracking would require timing the handlers, which is complex for fire-and-forget
