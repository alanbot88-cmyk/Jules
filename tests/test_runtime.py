import pytest
import asyncio
from src.neurolinked.core.runtime import Runtime
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_runtime_lifecycle():
    runtime = Runtime()
    await runtime.start()

    # Ensure all agents are registered and started
    assert len(runtime.agents) == 9

    # Trigger a task to see end-to-end flow
    await runtime.bus.publish(BaseEvent(
        source_agent="user",
        event_type="task_request",
        payload={"description": "initialize system"}
    ))

    await asyncio.sleep(0.5) # Allow events to propagate

    # Verify some agent activity in the bus history
    history = runtime.bus.get_history()
    event_types = [e.event_type for e in history]

    assert "task_request" in event_types
    assert "task_plan_generated" in event_types
    assert "execution_request" in event_types

    await runtime.stop()
