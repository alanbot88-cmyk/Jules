import pytest
import asyncio
from src.neurolinked.core.bus import CognitiveBus
from src.neurolinked.agents.ecc import ECCAgent
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_ecc_validation():
    bus = CognitiveBus()
    ecc = ECCAgent("ecc-01", bus)
    await ecc.start()

    validation_events = []
    async def validation_handler(event: BaseEvent):
        validation_events.append(event)

    bus.subscribe("validation_result", validation_handler)

    await bus.publish(BaseEvent(
        source_agent="octgent-01",
        event_type="execution_completed",
        payload={"result": "Success"}
    ))

    await asyncio.sleep(0.1)

    assert len(validation_events) == 1
    assert validation_events[0].payload["is_valid"] is True
