from typing import Dict, Any, Callable, List
from pydantic import BaseModel
from loguru import logger

class Skill(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class SkillRegistry:
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.handlers: Dict[str, Callable] = {}

    def register_skill(self, skill: Skill, handler: Callable):
        self.skills[skill.name] = skill
        self.handlers[skill.name] = handler
        logger.info(f"Registered skill: {skill.name}")

    def get_skill(self, name: str) -> Skill:
        return self.skills.get(name)

    async def execute_skill(self, name: str, params: Dict[str, Any]) -> Any:
        handler = self.handlers.get(name)
        if not handler:
            raise ValueError(f"Skill {name} not found")

        logger.info(f"Executing skill {name} with params {params}")
        return await handler(**params)

    def list_skills(self) -> List[Skill]:
        return list(self.skills.values())
