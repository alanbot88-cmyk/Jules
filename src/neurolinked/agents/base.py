from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger
from ..core.bus import CognitiveBus
from ..core.events import BaseEvent, CognitiveRegion

class BaseAgent(ABC):
    def __init__(self, agent_id: str, bus: CognitiveBus, region: Optional[CognitiveRegion] = None):
        self.agent_id = agent_id
        self.bus = bus
        self.region = region
        self._is_running = False

    async def start(self):
        self._is_running = True
        logger.info(f"Agent {self.agent_id} started in region {self.region}")
        await self.setup()

    async def stop(self):
        self._is_running = False
        logger.info(f"Agent {self.agent_id} stopped")
        await self.teardown()

    @abstractmethod
    async def setup(self):
        pass

    @abstractmethod
    async def teardown(self):
        pass

    async def publish(self, event_type: str, payload: dict, target_region: Optional[CognitiveRegion] = None):
        event = BaseEvent(
            source_agent=self.agent_id,
            event_type=event_type,
            payload=payload,
            target_region=target_region or self.region
        )
        await self.bus.publish(event)

    def subscribe(self, event_type: str):
        def decorator(handler):
            self.bus.subscribe(event_type, handler)
            return handler
        return decorator
