from typing import List, Dict, Any
from .base import BaseAgent
from ..core.events import CognitiveRegion, BaseEvent
from ..core.bus import CognitiveBus
from loguru import logger

class RufloAgent(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus):
        super().__init__(agent_id, bus, region=CognitiveRegion.PREFRONTAL)
        self.ai_service = None

    async def setup(self):
        self.bus.subscribe("task_request", self.handle_task_request)

    async def teardown(self):
        pass

    async def handle_task_request(self, event: BaseEvent):
        task_description = event.payload.get("description")
        logger.info(f"Ruflo received task: {task_description}")

        if self.ai_service:
            try:
                plan = await self.ai_service.generate_decomposition(task_description)
            except Exception:
                plan = self._decompose_task(task_description)
        else:
            plan = self._decompose_task(task_description)

        await self.publish(
            event_type="task_plan_generated",
            payload={
                "original_task": task_description,
                "steps": plan
            },
            target_region=CognitiveRegion.ORCHESTRATION
        )

    def _decompose_task(self, description: str) -> List[Dict[str, Any]]:
        # Mock decomposition logic
        return [
            {"step": 1, "action": "analyze", "description": f"Analyze {description}"},
            {"step": 2, "action": "execute", "description": f"Perform {description}"},
            {"step": 3, "action": "verify", "description": f"Verify {description}"}
        ]
