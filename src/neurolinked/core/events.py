from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, UTC

class CognitiveRegion(str, Enum):
    PREFRONTAL = "PREFRONTAL"
    HIPPOCAMPUS = "HIPPOCAMPUS"
    EXECUTION = "EXECUTION"
    MEMORY = "MEMORY"
    ECC = "ECC"
    ORCHESTRATION = "ORCHESTRATION"
    SENSORIUM = "SENSORIUM"
    MOTOR = "MOTOR"

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_agent: str
    target_region: Optional[CognitiveRegion] = None
    event_type: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None

class TelemetryEvent(BaseEvent):
    event_type: str = "telemetry"
    metric_name: str
    value: Any

class ActionEvent(BaseEvent):
    event_type: str = "action"
    action_name: str
    params: Dict[str, Any]
