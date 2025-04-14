from abc import ABC, abstractmethod

class BaseIntermediateParser(ABC):
    def __init__(self, state_keys=None):
        self.state_keys = state_keys or []

    @abstractmethod
    def parse_values(self, text: str) -> dict:
        """
        Parses LLM output into a dict with keys matching self.state_keys
        """
        pass

    def create_state_dict(self) -> dict:
        if not self.state_keys:
            raise KeyError("No state keys defined for this parser.")
        return {key: None for key in self.state_keys}
