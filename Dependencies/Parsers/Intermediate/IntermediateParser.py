from abc import ABC, abstractmethod


class IntermediateParser(ABC):
    def __init__(self, keys, tool_indicator=None, input_indicator=None):
        self.keys = keys
        self.tool_indicator = tool_indicator
        self.input_indicator = input_indicator

    @abstractmethod
    def parse_values(self, text):
        pass
