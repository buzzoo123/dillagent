from abc import ABC, abstractmethod
from typing import Dict, Any, Set
from ..graphs.BaseAgentGraph import BaseAgentGraph
from ...agents.agents.BaseAgent import BaseAgent

class BaseAgentGraphExecutor(ABC):
    def __init__(self, graph: BaseAgentGraph):
        self.graph = graph
        self.validate_graph()

    def validate_graph(self):
        """
        Basic validation to ensure the graph structure is sound.
        Subclasses may implement additional validation.
        """
        # Collect all agents in the graph
        all_agents = set(self.graph.edges.keys())
        for downstreams in self.graph.edges.values():
            all_agents.update(downstreams)
            
        # You could add additional validation here:
        # - Check for cycles in the graph
        # - Verify all agents are properly initialized
        # - Ensure the graph is connected

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph and return the results.
        Each executor implementation defines its own execution strategy.
        
        Args:
            input_data: Initial input data for the graph execution
            
        Returns:
            Output data from the graph execution
        """
        pass