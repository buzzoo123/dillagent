from tools.Tool import Tool
from Dependencies.Prompts.Prompt import Prompt
from Dependencies.Prompts.StructuredPrompt import StructuredPrompt
from Dependencies.Parsers.IntermediateParser import IntermediateParser
from typing import List
from LLM.LLM import LLM


class BaseAgent:
    def __init__(self, llm: LLM, tools: List, initial_prompt: Prompt = None):
        """
        Initialize the BaseAgent with a list of tools and an optional initial prompt.

        Parameters:
        - tools: A list of Tool instances representing the available tools for the agent.
        - initial_prompt: An optional initial prompt for the agent. If not provided, a prompt will be generated.

        Returns:
        None
        """
        self.llm = llm
        self.tools = tools  # self._make_tools(tools)
        if initial_prompt is None:
            initial_prompt = self._generate_initial_prompt()
        elif isinstance(initial_prompt, StructuredPrompt):
            initial_prompt = self._generate_from_structured_prompt(
                initial_prompt)
        self.initial_prompt = initial_prompt.get_prompt_str()

    # def _make_tools(self, tool_functions):
    #     tools = []
    #     for func in tool_functions:
    #         tool = Tool(name=func.name,
    #                     description=func.description, schema=func.schema)
    #         tools.append(tool)
    #     return tools

    def _generate_initial_prompt(self):
        """
        Generate the initial prompt for the agent.

        The prompt includes descriptions for each tool, along with instructions for interacting with the agent.

        Returns:
        str: The generated initial prompt.
        """
        prompt = """
    Answer the following questions and obey the following commands as best you can. 

    You have access to the following tools:

    """
        # Add descriptions for each tool
        for tool in self.tools:
            prompt += f"\n{tool.describe_tool()}\n"

        prompt += """
    You will receive a message from the human, then you should start a loop and do one of two things

    Option 1: You use a tool to answer the question.
    For this, you should use the following format:

    Thought: Your thought process to assist the user.
    Action: The action to take, should be one of [ Search ]
    Action Input: the input to the action, to be sent to the tool

    After this, the human will respond with an observation, and you will continue.

    Option 2: You respond to the human.
    For this, you should use the following format:
    Action: Response To Human
    Action Input: your response to the human, summarizing what you did and what you learned

    Begin!
    """
        return Prompt(prompt)

    def _generate_from_structured_prompt(self, structured_prompt):
        prompt = structured_prompt.header
        if not structured_prompt.tool_section:
            # Add descriptions for each tool
            prompt += f"""You have access to the following tools:\n"""
            for tool in self.tools:
                prompt += f"\n{tool.describe_tool()}\n"
        else:
            prompt += structured_prompt.tool_section
        prompt += structured_prompt.loop_condition
        if structured_prompt.footer:
            prompt += structured_prompt.footer
        return Prompt(prompt)

    def run_loop(self, prompt):
        intermediate_parser = IntermediateParser(['Action', 'Action Input'])
        gave_final_answer = False
        messages = [{"role": "system", "content": self.initial_prompt},
                    {"role": "user", "content": prompt}]
        while not gave_final_answer:
            # Change the below line with an output parse to allow for other things.
            response = self.llm.run(
                prompt, self.initial_prompt, messages).choices[0].message.content
            parsed = intermediate_parser.parse_values(response)
            print(response)
            observation = None
            if len(parsed) > 0:
                tool = parsed['Action']
                if (tool == "Search"):
                    observation = self.tools[0].func(input)
                else:
                    print(parsed['Action Input'])
                    exit()
            if (observation):
                messages.extend([{"role": "assistant", "content": response},
                                 {"role": "user", "content": f"Observation: {observation}"}])
            else:
                exit()
