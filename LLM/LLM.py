from LLM.LLMConfig import LLMConfig
from abc import ABC, abstractmethod


class LLM(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def run(self, prompt, system_prompt):
        pass

    @abstractmethod
    def _call_api(self, prompt, system_prompt):
        pass
