from collections import defaultdict

from .BaseAgentGraph import BaseAgentGraph
from ....agents.agents.BaseAgent import BaseAgent

class AgentGraph(BaseAgentGraph):
    def __init__(self):
        super().__init__()

    def add_edge(self, agent_from, agent_to):
        self.edges[agent_from].append(agent_to)

    def remove_edge(self, agent_from, agent_to_remove):
        if agent_to_remove in self.edges[agent_from]:
            self.edges[agent_from].remove(agent_to_remove)
        else:
            raise Exception(f"Attempted to remove agent: {agent_to_remove.name} but agent was NOT FOUND in {agent_from.name} edges.")
