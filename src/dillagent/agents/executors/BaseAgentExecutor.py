from abc import ABC, abstractmethod
from ...tools.Tool import Tool
from typing import List
from ..agents.BaseAgent import BaseAgent
from ...dependencies.parsers.intermediate.BaseIntermediateParser import BaseIntermediateParser


class BaseAgentExecutor(ABC):
    def __init__(self, agent: BaseAgent, intermediate_parser: BaseIntermediateParser):
        self.agent = agent
        self.im_parser = intermediate_parser

    @abstractmethod
    async def run(self, prompt):
        pass
    
    #Make a use_tool method when extending if tools should be available for use.
