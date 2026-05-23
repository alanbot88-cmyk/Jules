import asyncio
from typing import List
from loguru import logger
from .bus import CognitiveBus
from ..agents.base import BaseAgent
from ..agents.ruflo import RufloAgent
from ..agents.octgent import OctgentAgent
from ..agents.ecc import ECCAgent
from ..agents.orchestration import SupervisorAgent, WatchdogAgent
from ..agents.storage import MemoryAgent, PersistenceAgent
from ..agents.ui import UIRenderAgent
from ..agents.reward import RewardEngine

class Runtime:
    def __init__(self):
        self.bus = CognitiveBus()
        self.agents: List[BaseAgent] = []
        self._shutdown_event = asyncio.Event()

    def register_agent(self, agent: BaseAgent):
        self.agents.append(agent)

    async def start(self):
        logger.info("Initializing Neurolinked Runtime v3.0...")

        # Default agent set
        self.register_agent(RufloAgent("ruflo-01", self.bus))
        self.register_agent(OctgentAgent("octgent-01", self.bus))
        self.register_agent(ECCAgent("ecc-01", self.bus))
        self.register_agent(SupervisorAgent("supervisor-01", self.bus))
        self.register_agent(WatchdogAgent("watchdog-01", self.bus))
        self.register_agent(MemoryAgent("memory-01", self.bus))
        self.register_agent(PersistenceAgent("persistence-01", self.bus))
        self.register_agent(UIRenderAgent("ui-01", self.bus))
        self.register_agent(RewardEngine("reward-01", self.bus))

        for agent in self.agents:
            await agent.start()

        logger.info("Runtime started and operational.")

    async def stop(self):
        logger.info("Shutting down runtime...")
        for agent in reversed(self.agents):
            await agent.stop()
        self._shutdown_event.set()

    async def run_until_interrupted(self):
        try:
            await self._shutdown_event.wait()
        except asyncio.CancelledError:
            await self.stop()
