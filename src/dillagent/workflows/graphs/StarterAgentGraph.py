from .BaseAgentGraph import BaseAgentGraph
from ...agents.agents.BaseAgent import BaseAgent

class StarterAgentGraph(BaseAgentGraph):
    def __init__(self):
        super().__init__()
        self.input_agent = None
        self.output_agent = None

    def add_edge(self, agent_from: BaseAgent, agent_to: BaseAgent):
        self.edges[agent_from].append(agent_to)
        self.reverse_edges[agent_to].append(agent_from)

    def remove_edge(self, agent_from: BaseAgent, agent_to: BaseAgent):
        if agent_to in self.edges[agent_from]:
            self.edges[agent_from].remove(agent_to)
            self.reverse_edges[agent_to].remove(agent_from)