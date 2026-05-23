import pytest
import asyncio
from src.neurolinked.core.bus import CognitiveBus
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_bus_publish_subscribe():
    bus = CognitiveBus()
    received_events = []

    async def handler(event: BaseEvent):
        received_events.append(event)

    bus.subscribe("test_event", handler)

    event = BaseEvent(
        source_agent="test_agent",
        event_type="test_event",
        payload={"data": "hello"}
    )

    await bus.publish(event)

    # Wait a bit for the task to complete
    await asyncio.sleep(0.1)

    assert len(received_events) == 1
    assert received_events[0].payload["data"] == "hello"
    assert len(bus.get_history()) == 1

@pytest.mark.asyncio
async def test_bus_global_subscribe():
    bus = CognitiveBus()
    received_events = []

    def handler(event: BaseEvent):
        received_events.append(event)

    bus.subscribe("*", handler)

    event = BaseEvent(
        source_agent="test_agent",
        event_type="any_event",
        payload={}
    )

    await bus.publish(event)

    assert len(received_events) == 1
