from abc import ABC, abstractmethod
from tools.Tool import Tool
from typing import List


class SysPrompt(ABC):
    def __init__(self):
        pass

    def generate_prompt(self, tools: List[Tool]):
        pass
