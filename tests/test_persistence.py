import pytest
import asyncio
from src.neurolinked.core.bus import CognitiveBus
from src.neurolinked.agents.storage import MemoryAgent, PersistenceAgent
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_storage_agents():
    bus = CognitiveBus()
    memory = MemoryAgent("memory-01", bus)
    persistence = PersistenceAgent("persistence-01", bus)

    await memory.start()
    await persistence.start()

    event = BaseEvent(
        source_agent="test",
        event_type="execution_completed",
        payload={"action": "save_world"}
    )

    await bus.publish(event)
    await asyncio.sleep(0.1)

    assert event.event_id in memory.graph
    assert len(persistence.journal) == 1
