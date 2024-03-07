from LLM.LLMConfig import LLMConfig
from abc import ABC, abstractmethod


class LLM(ABC):
    def __init__(self, config: LLMConfig, messages=[]):
        self.config = config
        self.messages = messages

    @abstractmethod
    def run(self, prompt):
        pass

    @abstractmethod
    def _call_api(self, prompt):
        pass

    @abstractmethod
    def add_messages(self, messages):
        pass
