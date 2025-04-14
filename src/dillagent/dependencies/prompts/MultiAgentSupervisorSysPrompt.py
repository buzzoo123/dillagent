from typing import List, Optional
from ...agents.agents import BaseAgent
from .BaseSysPrompt import BaseSysPrompt

class MultiAgentSupervisorSysPrompt(BaseSysPrompt):
    def __init__(self, header):
        self.header = header
        self.prompt_str = None

    def get_agent_names(self, agents):
        res = ""
        for i in range(len(agents)):
            if i != len(agents)-1:
                res += f"'{agents[i].name}, '"
            else:
                res += f"'{agents[i].name}'"

    def generate_prompt(self, agents: Optional[List[BaseAgent]]):
        self.prompt_str = self.header
        return self.header
