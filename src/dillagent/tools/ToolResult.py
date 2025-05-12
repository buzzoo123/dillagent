from dataclasses import dataclass, field
from typing import Any, Optional, Dict
import time

@dataclass
class ToolResult:
    tool_name: str
    arguments: Dict[str, Any]
    output: Any = None
    success: bool = True
    error: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: float = None

    def mark_complete(self, output: Any):
        self.output = output
        self.success = True
        self.end_time = time.time()

    def mark_failed(self, error: Exception):
        self.output = None
        self.success = False
        self.error = str(error)
        self.end_time = time.time()
