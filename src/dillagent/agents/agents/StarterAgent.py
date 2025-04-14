import asyncio
from ...tools import Tool
from .BaseAgent import BaseAgent
from ...dependencies.prompts.BaseSysPrompt import BaseSysPrompt
from ...dependencies.parsers.intermediate.BaseIntermediateParser import BaseIntermediateParser
from typing import List, Optional
from ...llm.LLM import LLM

class StarterAgent(BaseAgent):
    def __init__(self, llm: LLM, tools: List, intermediate_parser: BaseIntermediateParser, sys_prompt: BaseSysPrompt, name: str = "Starter Agent"):
        """
        Initialize the BaseAgent with a list of tools and an optional initial prompt.

        Parameters:
        - tools: A list of Tool instances representing the available tools for the agent.
        - initial_prompt: An optional initial prompt for the agent. If not provided, a prompt will be generated.

        Returns:
        None
        """
        super().__init__(llm, tools, sys_prompt, name, intermediate_parser)

    async def run(self, *, prompt: Optional[str] = None, inputs: Optional[dict] = None):
        """
        Runs the agent with either a direct prompt or structured inputs.
        
        Parameters:
        - prompt: An optional string prompt to pass directly to the LLM
        - inputs: An optional dictionary of structured inputs
        
        Returns:
        The response from the LLM
        """
        # If inputs are provided, construct a prompt from them
        if inputs:
            # Convert inputs to a formatted string that the agent can understand
            formatted_prompt = inputs.get(f'{self.name}_input', '')
            output = await self.llm.run(formatted_prompt)
            return self.intermediate_parser.parse_values(output)
        
        # Otherwise, use the direct prompt
        elif prompt:
            output = await self.llm.run(prompt)
            return self.intermediate_parser.parse_values(output)
        
        # Handle the case where neither is provided
        else:
            raise ValueError("Either prompt or inputs must be provided")
        
    async def use_tool(self, response, to_call, to_input):
        for tool in self.agent.tools:
            if to_call == tool.name:
                if isinstance(to_input, dict):
                    if asyncio.iscoroutinefunction(tool.func):
                        return await tool.func(**to_input)
                    else:
                        return tool.func(**to_input)
                elif isinstance(to_input, list):
                    raise ValueError("LLM produced list of parameters - invalid format. Must be a dict or single value.")
                else:
                    if asyncio.iscoroutinefunction(tool.func):
                        return await tool.func(to_input)
                    else:
                        return tool.func(to_input)

        raise KeyError(f"Tool '{to_call}' not found among registered tools.")
