import json
import threading
from itertools import count

class StandardizedLLMResponse:
    _id_counter = count(1)
    _lock = threading.Lock()

    def __init__(self, type, name=None, arguments=None, content=None):
        with StandardizedLLMResponse._lock:
            self.id = next(StandardizedLLMResponse._id_counter)
        self.type = type
        self.name = name
        self.arguments = arguments
        self.content = content

    def serialize(self):
        base = {"id": self.id, "type": self.type}
        if self.type == "function":
            base.update({
                "name": self.name,
                "arguments": self.arguments
            })
        elif self.type == "natural language":
            base["content"] = self.content
        return json.dumps(base)
