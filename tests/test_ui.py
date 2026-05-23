import pytest
import asyncio
import websockets
import json
from src.neurolinked.core.bus import CognitiveBus
from src.neurolinked.agents.ui import UIRenderAgent
from src.neurolinked.core.events import BaseEvent

@pytest.mark.asyncio
async def test_ui_websocket_streaming():
    bus = CognitiveBus()
    ui_agent = UIRenderAgent("ui-01", bus, port=8766)
    await ui_agent.start()

    uri = "ws://localhost:8766"
    async with websockets.connect(uri) as websocket:
        event = BaseEvent(
            source_agent="test",
            event_type="visual_update",
            payload={"region": "PREFRONTAL", "activity": 0.8}
        )
        await bus.publish(event)

        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
        data = json.loads(response)
        assert data["event_type"] == "visual_update"
        assert data["payload"]["activity"] == 0.8

    await ui_agent.stop()
