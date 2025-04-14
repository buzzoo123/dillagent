from abc import ABC, abstractmethod
from ...tools.Tool import Tool
from typing import List


class BaseSysPrompt(ABC):
    def __init__(self):
        pass

    def generate_prompt(self):
        pass
