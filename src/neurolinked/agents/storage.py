from .base import BaseAgent
from ..core.events import CognitiveRegion, BaseEvent
from ..core.bus import CognitiveBus
from loguru import logger

class MemoryAgent(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus):
        super().__init__(agent_id, bus, region=CognitiveRegion.MEMORY)
        self.graph = {} # Mock cognitive memory graph

    async def setup(self):
        self.bus.subscribe("*", self.process_event)

    async def teardown(self):
        pass

    async def process_event(self, event: BaseEvent):
        # Update memory graph based on events
        if event.event_type == "execution_completed":
            action = event.payload.get("action")
            self.graph[event.event_id] = {"type": "execution", "action": action, "status": "completed"}
            logger.debug(f"Memory updated with execution: {action}")

class PersistenceAgent(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus):
        super().__init__(agent_id, bus, region=CognitiveRegion.MEMORY)
        self.journal = []

    async def setup(self):
        self.bus.subscribe("*", self.journal_event)

    async def teardown(self):
        # In real implementation, flush to Supabase
        logger.info(f"Persistence agent flushing {len(self.journal)} events")

    async def journal_event(self, event: BaseEvent):
        self.journal.append(event.model_dump_json())
        # Simulate durability
        logger.debug(f"Event {event.event_id} journaled")
