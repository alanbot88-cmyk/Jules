from .base import BaseAgent
from ..core.events import CognitiveRegion, BaseEvent
from ..core.bus import CognitiveBus
from loguru import logger

class RewardEngine(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus):
        super().__init__(agent_id, bus, region=CognitiveRegion.ORCHESTRATION)
        self.rewards = {}

    async def setup(self):
        self.bus.subscribe("execution_completed", self.handle_execution)
        self.bus.subscribe("validation_result", self.handle_validation)

    async def teardown(self):
        pass

    async def handle_execution(self, event: BaseEvent):
        # Initial neutral reward for effort
        self.rewards[event.event_id] = 0.5
        logger.debug(f"Reward engine initialized for {event.event_id}")

    async def handle_validation(self, event: BaseEvent):
        original_id = event.payload.get("original_event_id")
        is_valid = event.payload.get("is_valid")

        if original_id in self.rewards:
            if is_valid:
                self.rewards[original_id] += 0.5 # Reinforcement (STDP-like)
            else:
                self.rewards[original_id] -= 0.5 # Penalty

            logger.info(f"Updated reward for {original_id}: {self.rewards[original_id]}")

            await self.publish(
                event_type="reward_update",
                payload={"target_event": original_id, "reward": self.rewards[original_id]}
            )
