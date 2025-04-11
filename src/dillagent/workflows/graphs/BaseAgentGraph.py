from abc import ABC, abstractmethod
from collections import defaultdict
from ...agents.agents.BaseAgent import BaseAgent

class BaseAgentGraph(ABC):
    def __init__(self):
        self.edges = defaultdict(list)
        self.reverse_edges = defaultdict(list)

    @abstractmethod
    def add_edge(self, agent_from: BaseAgent, agent_to: BaseAgent):
        pass

    @abstractmethod
    def remove_edge(self, agent_from: BaseAgent, agent_to: BaseAgent):
        pass
    
    # No run method here - that's the executor's job