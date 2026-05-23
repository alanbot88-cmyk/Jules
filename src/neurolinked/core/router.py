from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
import time
from loguru import logger

class ModelProvider(str, Enum):
    GEMINI = "gemini"
    GROQ = "groq"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"

class ModelID(str, Enum):
    GEMINI_3_5_FLASH = "gemini-3.5-flash"
    GROQ_LLAMA_3_3 = "llama-3.3-70b-versatile" # Canonical ID for Llama 3.3 on Groq
    QWEN_3_CODER = "qwen3-coder"
    DEEPSEEK_V4_FLASH = "deepseek-v4-flash"

class ProviderHealth(BaseModel):
    is_available: bool = True
    consecutive_failures: int = 0
    cooldown_until: float = 0.0
    last_latency: float = 0.0

class ModelRouter:
    def __init__(self, api_keys: Dict[ModelProvider, List[str]]):
        self.api_keys = api_keys
        self.key_indices = {p: 0 for p in api_keys}
        self.health = {p: ProviderHealth() for p in ModelProvider}
        self.circuit_breaker_threshold = 3
        self.cooldown_period = 60 # seconds

    def get_key(self, provider: ModelProvider) -> Optional[str]:
        keys = self.api_keys.get(provider, [])
        if not keys:
            return None

        # Round-robin key rotation
        idx = self.key_indices[provider]
        key = keys[idx]
        self.key_indices[provider] = (idx + 1) % len(keys)
        return key

    def get_route(self, provider: ModelProvider) -> Optional[str]:
        health = self.health[provider]
        if not health.is_available:
            if time.time() > health.cooldown_until:
                health.is_available = True
                health.consecutive_failures = 0
                logger.info(f"Provider {provider} recovered from cooldown")
            else:
                return None

        return self.get_key(provider)

    def report_failure(self, provider: ModelProvider):
        health = self.health[provider]
        health.consecutive_failures += 1
        if health.consecutive_failures >= self.circuit_breaker_threshold:
            health.is_available = False
            health.cooldown_until = time.time() + self.cooldown_period
            logger.warning(f"Provider {provider} entered cooldown after {health.consecutive_failures} failures")

    def report_success(self, provider: ModelProvider, latency: float):
        health = self.health[provider]
        health.consecutive_failures = 0
        health.last_latency = latency
