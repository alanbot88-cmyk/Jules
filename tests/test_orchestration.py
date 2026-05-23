import pytest
import asyncio
from src.neurolinked.core.bus import CognitiveBus
from src.neurolinked.agents.orchestration import SupervisorAgent, WatchdogAgent
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_orchestration_flow():
    bus = CognitiveBus()
    supervisor = SupervisorAgent("supervisor-01", bus)
    await supervisor.start()

    execution_requests = []
    async def exec_handler(event: BaseEvent):
        execution_requests.append(event)

    bus.subscribe("execution_request", exec_handler)

    await bus.publish(BaseEvent(
        source_agent="ruflo-01",
        event_type="task_plan_generated",
        payload={
            "original_task": "test",
            "steps": [{"action": "test_act", "description": "test_desc"}]
        }
    ))

    await asyncio.sleep(0.1)
    assert len(execution_requests) == 1
    assert execution_requests[0].payload["action"] == "test_act"
