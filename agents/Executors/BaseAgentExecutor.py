from abc import ABC, abstractmethod
from tools.Tool import Tool
from typing import List
from agents.agents.BaseAgent import BaseAgent
from Dependencies.Parsers.Intermediate.IntermediateParser import IntermediateParser


class BaseAgentExecutor(ABC):
    def __init__(self, agent: BaseAgent, intermediate_parser: IntermediateParser):
        self.agent = agent
        self.im_parser = intermediate_parser

    @abstractmethod
    def run(self, prompt):
        pass
