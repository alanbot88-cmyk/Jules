import asyncio
import websockets
import json
from .base import BaseAgent
from ..core.events import CognitiveRegion, BaseEvent
from ..core.bus import CognitiveBus
from loguru import logger

class UIRenderAgent(BaseAgent):
    def __init__(self, agent_id: str, bus: CognitiveBus, host: str = "0.0.0.0", port: int = 8765):
        super().__init__(agent_id, bus, region=CognitiveRegion.SENSORIUM)
        self.host = host
        self.port = port
        self.clients = set()
        self._server = None

    async def setup(self):
        self.bus.subscribe("*", self.project_event)
        self._server = await websockets.serve(self.ws_handler, self.host, self.port)
        logger.info(f"UI Streaming server started on ws://{self.host}:{self.port}")

    async def teardown(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def ws_handler(self, websocket):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                # Handle incoming UI messages if any (UI-to-Runtime)
                pass
        finally:
            self.clients.remove(websocket)

    async def project_event(self, event: BaseEvent):
        # Only project relevant events or all for visualization
        message = event.model_dump_json()
        if self.clients:
            # Broadcast to all connected visualization clients
            # websockets 14.0+ uses broadcast or just iterate
            to_remove = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except Exception:
                    to_remove.add(client)
            self.clients -= to_remove
