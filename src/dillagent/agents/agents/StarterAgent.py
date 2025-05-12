import asyncio
from ...tools import Tool
from .BaseAgent import BaseAgent
from ...dependencies.prompts.BaseSysPrompt import BaseSysPrompt
from ...dependencies.parsers.intermediate.BaseIntermediateParser import BaseIntermediateParser
from typing import List, Optional
from ...llm.LLM import LLM

class StarterAgent(BaseAgent):
    def __init__(self, llm: LLM, tools: List[Tool], intermediate_parser: BaseIntermediateParser, sys_prompt: BaseSysPrompt, input_description: str, name: str = "Starter Agent", logging_enabled=False, error_policy=None):
        """
        Initialize the BaseAgent with a list of tools and an optional initial prompt.

        Parameters:
        - llm: The LLM instance to associate with this agent.
        - tools: A list of Tool instances representing the available tools for the agent.
        - intermediate_parsser: The IntermediateParser instance to associate with this agent.
        - input_description: A description of what the input to this agent should be.
        - name: The agent's name to be used at runtime.

        Returns:
        None
        """
        super().__init__(llm, tools, intermediate_parser, sys_prompt, name)
        self.input_description = input_description
        self.logging_enabled = logging_enabled
        self.error_policy = error_policy

    async def run(self, *, prompt: Optional[str] = None, inputs: Optional[dict] = None):
        """
        Runs the agent with either a direct prompt or structured inputs.
        
        Parameters:
        - prompt: An optional string prompt to pass directly to the LLM
        - inputs: An optional dictionary of structured inputs
        
        Returns:
        The response from the LLM
        """
        tool_results = []
        # If inputs are provided, construct a prompt from them
        if inputs:
            # Convert inputs to a formatted string that the agent can understand
            formatted_prompt = inputs.get(f'{self.name}_input', '')
            if self.logging_enabled: print(self.llm.messages)
            if self.logging_enabled: print(formatted_prompt)
            output = await self.llm.run(formatted_prompt)
            if self.logging_enabled: print(output)
            
        # Otherwise, use the direct prompt
        elif prompt:
            output = await self.llm.run(prompt)
            return self.intermediate_parser.parse_values(output)
        
        for response in output:
            if response.type == "function":
                tool_result = await self.use_tool(response)
                tool_results.append(tool_result)
                
        # Handle the case where neither is provided
        else:
            raise ValueError("Either prompt or inputs must be provided")
        
        
        
    async def use_tool(self, response):
        for tool in self.tools:
            if response.name == tool.name:
                output = await tool.execute()
                return output
    
    def describe(self):
        return self.input_description