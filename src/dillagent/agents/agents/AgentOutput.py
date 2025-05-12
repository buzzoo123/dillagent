from dataclasses import dataclass, field
from typing import List
import threading
from itertools import count
from ...llm.StandardizedLLMResponse import StandardizedLLMResponse
from ...tools.ToolResult import ToolResult

@dataclass
class AgentOutput:
    llm_response: StandardizedLLMResponse
    tool_results: List[ToolResult] = field(default_factory=list)
    id: int = field(init=False)

    # Class-level counter and lock for thread-safe unique IDs
    _id_counter = count(1)
    _lock = threading.Lock()

    def __post_init__(self):
        with AgentOutput._lock:
            self.id = next(AgentOutput._id_counter)
