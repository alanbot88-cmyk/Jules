import pytest
import asyncio
from src.neurolinked.core.bus import CognitiveBus
from src.neurolinked.agents.octgent import OctgentAgent
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_octgent_execution():
    bus = CognitiveBus()
    octgent = OctgentAgent("octgent-01", bus)
    await octgent.start()

    results = []
    async def execution_handler(event: BaseEvent):
        results.append(event)

    bus.subscribe("execution_completed", execution_handler)

    await bus.publish(BaseEvent(
        source_agent="orchestrator",
        event_type="execution_request",
        payload={"action": "test_action", "description": "do something"}
    ))

    await asyncio.sleep(0.1)

    assert len(results) == 1
    assert results[0].payload["status"] == "success"
