from abc import ABC, abstractmethod
from ..graphs.BaseAgentGraph import BaseAgentGraph
from ....agents.agents.BaseAgent import BaseAgent

class BaseAgentCluster(ABC):
    def __init__(self, graph: BaseAgentGraph, input_agent: BaseAgent, output_agent: BaseAgent):
        self.graph = graph
        self.input_agent = input_agent
        self.output_agent = output_agent

    @abstractmethod
    def set_output_agent(self, output_agent):
        pass
    
    @abstractmethod
    def set_input_agent(self, input_agent):
        pass


        #Highkey will change