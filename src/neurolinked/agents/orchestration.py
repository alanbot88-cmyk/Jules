from .base import BaseAgent
from ..core.events import CognitiveRegion, BaseEvent
from ..core.bus import CognitiveBus
from loguru import logger
import asyncio
import time

class SupervisorAgent(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus):
        super().__init__(agent_id, bus, region=CognitiveRegion.ORCHESTRATION)
        self.active_tasks = {}

    async def setup(self):
        self.bus.subscribe("task_plan_generated", self.handle_plan)
        self.bus.subscribe("execution_completed", self.handle_execution_completed)
        self.bus.subscribe("validation_result", self.handle_validation)

    async def teardown(self):
        pass

    async def handle_plan(self, event: BaseEvent):
        steps = event.payload.get("steps", [])
        original_task = event.payload.get("original_task")
        logger.info(f"Supervisor received plan for: {original_task}")

        # Start executing the first step
        if steps:
            next_step = steps[0]
            await self.publish(
                event_type="execution_request",
                payload={
                    "task_id": event.event_id,
                    "action": next_step["action"],
                    "description": next_step["description"],
                    "all_steps": steps,
                    "current_index": 0
                },
                target_region=CognitiveRegion.EXECUTION
            )

    async def handle_execution_completed(self, event: BaseEvent):
        logger.info(f"Supervisor noted execution completion: {event.payload.get('action')}")
        # Wait for ECC validation before proceeding (in a stricter implementation)

    async def handle_validation(self, event: BaseEvent):
        is_valid = event.payload.get("is_valid")
        logger.info(f"Supervisor received validation: {is_valid}")
        # Logic to proceed to next step or retry would go here

class WatchdogAgent(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus):
        super().__init__(agent_id, bus, region=CognitiveRegion.ORCHESTRATION)
        self.last_activity = time.time()

    async def setup(self):
        self.bus.subscribe("*", self.track_activity)
        asyncio.create_task(self.monitor_health())

    async def teardown(self):
        pass

    async def track_activity(self, event: BaseEvent):
        self.last_activity = time.time()

    async def monitor_health(self):
        while self._is_running:
            if time.time() - self.last_activity > 30:
                logger.warning("Watchdog detected inactivity! Potential deadlock or hang.")
                await self.publish(
                    event_type="health_alert",
                    payload={"reason": "inactivity", "duration": time.time() - self.last_activity}
                )
            await asyncio.sleep(5)
