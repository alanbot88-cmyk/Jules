import asyncio
import os
from typing import List
from loguru import logger
from .bus import CognitiveBus
from .router import ModelRouter, ModelProvider
from .ai import AIService
from .telemetry import TelemetryManager
from .skills import SkillRegistry, Skill
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
        self.skill_registry = SkillRegistry()
        self._init_skills()
        self.router = ModelRouter({
            ModelProvider.GEMINI: [os.getenv("GEMINI_API_KEY", "mock-key")],
            ModelProvider.GROQ: [os.getenv("GROQ_API_KEY", "mock-key")],
        })
        self.ai_service = AIService(self.router)
        self.telemetry = TelemetryManager(self.bus)
        self.agents: List[BaseAgent] = []
        self._shutdown_event = asyncio.Event()

    def register_agent(self, agent: BaseAgent):
        # Inject dependencies if needed
        if hasattr(agent, 'ai_service'):
            agent.ai_service = self.ai_service
        if hasattr(agent, 'skill_registry'):
            agent.skill_registry = self.skill_registry
        self.agents.append(agent)

    def _init_skills(self):
        async def write_file(filename: str, content: str):
            with open(filename, 'w') as f:
                f.write(content)
            return f"File {filename} written"

        self.skill_registry.register_skill(
            Skill(name="write_file", description="Write content to a file", parameters={"filename": "str", "content": "str"}),
            write_file
        )

        async def web_search(query: str):
            return f"Found results for: {query}"

        self.skill_registry.register_skill(
            Skill(name="web_search", description="Search the web", parameters={"query": "str"}),
            web_search
        )

    async def start(self):
        logger.info("Initializing Neurolinked Runtime v3.0...")

        self.telemetry.start()

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
