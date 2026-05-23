from .base import BaseAgent
from ..core.events import CognitiveRegion, BaseEvent
from ..core.bus import CognitiveBus
from loguru import logger

class OctgentAgent(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus):
        super().__init__(agent_id, bus, region=CognitiveRegion.EXECUTION)

    async def setup(self):
        self.bus.subscribe("execution_request", self.handle_execution_request)

    async def teardown(self):
        pass

    async def handle_execution_request(self, event: BaseEvent):
        action = event.payload.get("action")
        description = event.payload.get("description")
        logger.info(f"Octgent executing action: {action} - {description}")

        # Simulate execution using Groq Llama 3.3
        result = f"Successfully performed {action}"

        await self.publish(
            event_type="execution_completed",
            payload={
                "action": action,
                "result": result,
                "status": "success"
            },
            target_region=CognitiveRegion.ORCHESTRATION
        )
