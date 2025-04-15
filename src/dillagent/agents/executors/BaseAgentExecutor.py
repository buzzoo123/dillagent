from typing import Dict, Any
from ...agents.agents.BaseAgent import BaseAgent

class BaseAgentExecutor:
    def __init__(
        self,
        agent: BaseAgent,
        tool_indicator_key: str = None,       # e.g., "use_tool"
        tool_name_key: str = "action",        # e.g., "tool", "action"
        tool_input_key: str = "action_input", # e.g., "tool_args"
        tool_output_key: str = None           # e.g., "result", "observation", etc.
    ):
        self.agent = agent
        self.tool_indicator_key = tool_indicator_key
        self.tool_name_key = tool_name_key
        self.tool_input_key = tool_input_key
        self.tool_output_key = tool_output_key

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        output = await self.agent.run(inputs=inputs)

        # Check if tool usage is requested -> NEED TO CHANGE TO BOOLEAN
        if self.tool_indicator_key and output.get(self.tool_indicator_key, False):
            tool_name = output.get(self.tool_name_key)
            tool_input = output.get(self.tool_input_key)

            if not tool_name or tool_input is None:
                raise ValueError(
                    f"Tool call triggered but '{self.tool_name_key}' or '{self.tool_input_key}' is missing."
                )

            #Currently an agent shouldn't HAVE TO use a tool
            if not hasattr(self.agent, "use_tool"):
                raise NotImplementedError("Agent does not implement use_tool()")

            observation = await self.agent.use_tool(
                response=output,
                to_call=tool_name,
                to_input=tool_input
            )

            if self.tool_output_key:
                return {
                    self.tool_output_key: observation,
                    **output
                }
            else:
                return output
 
        return output