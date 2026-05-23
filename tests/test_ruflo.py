import pytest
import asyncio
from src.neurolinked.core.bus import CognitiveBus
from src.neurolinked.agents.ruflo import RufloAgent
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_ruflo_task_decomposition():
    bus = CognitiveBus()
    ruflo = RufloAgent("ruflo-01", bus)
    await ruflo.start()

    received_plans = []
    async def plan_handler(event: BaseEvent):
        received_plans.append(event)

    bus.subscribe("task_plan_generated", plan_handler)

    await bus.publish(BaseEvent(
        source_agent="user",
        event_type="task_request",
        payload={"description": "build a house"}
    ))

    await asyncio.sleep(0.1)

    assert len(received_plans) == 1
    assert "steps" in received_plans[0].payload
    assert len(received_plans[0].payload["steps"]) == 3
