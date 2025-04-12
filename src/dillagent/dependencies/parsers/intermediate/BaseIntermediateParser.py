from abc import ABC, abstractmethod


class BaseIntermediateParser(ABC):
    # Might need to change whats optional and whatnot
    def __init__(self, action_keys=None):
        self.action_keys = action_keys

    @abstractmethod
    def parse_values(self, text):
        pass
