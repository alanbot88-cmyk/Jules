import pytest
import time
from src.neurolinked.core.router import ModelRouter, ModelProvider

def test_router_key_rotation():
    api_keys = {ModelProvider.GEMINI: ["key1", "key2"]}
    router = ModelRouter(api_keys)

    assert router.get_route(ModelProvider.GEMINI) == "key1"
    assert router.get_route(ModelProvider.GEMINI) == "key2"
    assert router.get_route(ModelProvider.GEMINI) == "key1"

def test_router_circuit_breaker():
    api_keys = {ModelProvider.GEMINI: ["key1"]}
    router = ModelRouter(api_keys)
    router.circuit_breaker_threshold = 2
    router.cooldown_period = 0.5

    router.report_failure(ModelProvider.GEMINI)
    assert router.get_route(ModelProvider.GEMINI) == "key1"

    router.report_failure(ModelProvider.GEMINI)
    assert router.get_route(ModelProvider.GEMINI) is None

    time.sleep(0.6)
    assert router.get_route(ModelProvider.GEMINI) == "key1"

def test_router_success_resets_failures():
    api_keys = {ModelProvider.GEMINI: ["key1"]}
    router = ModelRouter(api_keys)
    router.circuit_breaker_threshold = 2

    router.report_failure(ModelProvider.GEMINI)
    router.report_success(ModelProvider.GEMINI, 0.1)
    router.report_failure(ModelProvider.GEMINI)

    assert router.get_route(ModelProvider.GEMINI) == "key1"
