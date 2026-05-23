import asyncio
from typing import Callable, Dict, List, Type, TypeVar
import json
from loguru import logger
from .events import BaseEvent

T = TypeVar("T", bound=BaseEvent)

class CognitiveBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[BaseEvent] = []
        self._lock = asyncio.Lock()

    async def publish(self, event: BaseEvent):
        async with self._lock:
            self._history.append(event)
            logger.info(f"Published event: {event.event_type} from {event.source_agent} to {event.target_region}")

            # Simple fan-out
            handlers = self._subscribers.get(event.event_type, [])
            handlers += self._subscribers.get("*", []) # Global subscribers

            for handler in handlers:
                # Fire and forget handlers or await them?
                # For deterministic propagation, we might want to await them or use a queue.
                # Per requirements: deterministic event propagation.
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(self._safe_execute(handler, event))
                else:
                    handler(event)

    async def _safe_execute(self, handler, event):
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in handler for {event.event_type}: {e}")

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def get_history(self) -> List[BaseEvent]:
        return self._history

    def clear_history(self):
        self._history = []
