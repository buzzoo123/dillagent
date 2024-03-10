from tools.Tool import Tool
from agents.agents.BaseAgent import BaseAgent
from Dependencies.Prompts.SysPrompt import SysPrompt
from typing import List
from LLM.LLM import LLM


class AdvancedAgent(BaseAgent):
    def __init__(self, llm: LLM, tools: List, sys_prompt: SysPrompt):
        """
        Initialize the BaseAgent with a list of tools and an optional initial prompt.

        Parameters:
        - tools: A list of Tool instances representing the available tools for the agent.
        - initial_prompt: An optional initial prompt for the agent. If not provided, a prompt will be generated.

        Returns:
        None
        """
        self.llm = llm
        self.tools = tools
        self.sys_prompt = sys_prompt
        self.sys_prompt.generate_prompt(tools)
        self.llm.add_messages([
            {"role": "system", "content": self.sys_prompt.prompt_str},
        ])

    def run(self, prompt):
        return self.llm.run(prompt)
