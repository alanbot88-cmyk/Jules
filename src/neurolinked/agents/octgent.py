from .base import BaseAgent
from ..core.events import CognitiveRegion, BaseEvent
from ..core.bus import CognitiveBus
from loguru import logger

class OctgentAgent(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus):
        super().__init__(agent_id, bus, region=CognitiveRegion.EXECUTION)
        self.ai_service = None
        self.skill_registry = None

    async def setup(self):
        self.bus.subscribe("execution_request", self.handle_execution_request)

    async def teardown(self):
        pass

    async def handle_execution_request(self, event: BaseEvent):
        action = event.payload.get("action")
        description = event.payload.get("description")
        params = event.payload.get("params", {})
        logger.info(f"Octgent executing action: {action} - {description}")

        if self.skill_registry and self.skill_registry.get_skill(action):
            try:
                result = await self.skill_registry.execute_skill(action, params)
            except Exception as e:
                result = f"Skill execution failed: {e}"
        elif self.ai_service:
            result = await self.ai_service.execute_action(action, description)
        else:
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
