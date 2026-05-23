import pytest
import asyncio
from src.neurolinked.core.bus import CognitiveBus
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_high_concurrency_load():
    bus = CognitiveBus()
    received_count = 0
    lock = asyncio.Lock()

    async def fast_handler(event: BaseEvent):
        nonlocal received_count
        async with lock:
            received_count += 1

    bus.subscribe("stress_test", fast_handler)

    num_events = 1000
    tasks = []
    for i in range(num_events):
        tasks.append(bus.publish(BaseEvent(
            source_agent=f"agent-{i}",
            event_type="stress_test",
            payload={"i": i}
        )))

    await asyncio.gather(*tasks)

    # Wait for all async tasks spawned by the bus to finish
    # Since we use asyncio.create_task in bus.py, we need to wait a bit
    await asyncio.sleep(0.5)

    assert received_count == num_events

@pytest.mark.asyncio
async def test_error_resilience():
    bus = CognitiveBus()

    async def failing_handler(event: BaseEvent):
        raise RuntimeError("Intentional failure")

    received_events = []
    async def success_handler(event: BaseEvent):
        received_events.append(event)

    bus.subscribe("mixed_test", failing_handler)
    bus.subscribe("mixed_test", success_handler)

    await bus.publish(BaseEvent(source_agent="test", event_type="mixed_test", payload={}))

    await asyncio.sleep(0.1)

    # success_handler should still have run despite failing_handler crashing
    assert len(received_events) == 1
