from abc import ABC, abstractmethod


class IntermediateParser(ABC):
    # Might need to change whats optional and whatnot
    def __init__(self, keys=None, tool_indicator=None, input_indicator=None):
        self.keys = keys
        self.tool_indicator = tool_indicator
        self.input_indicator = input_indicator

    @abstractmethod
    def parse_values(self, text):
        pass
