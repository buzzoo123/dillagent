import uuid
import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BaseSignal:
    id: str
    type: str
    payload: dict
    source: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    @staticmethod
    def spawn(type: str, payload: dict, source: Optional[str] = None) -> "BaseSignal":
        return BaseSignal(
            id=str(uuid.uuid4()),
            type=type,
            payload=payload,
            source=source,
        )
