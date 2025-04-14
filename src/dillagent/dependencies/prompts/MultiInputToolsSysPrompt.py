from typing import List
from .BaseSysPrompt import BaseSysPrompt
from ...tools.Tool import Tool


class MultiInputToolsSysPrompt(BaseSysPrompt):
    def __init__(self, header):
        self.header = header
        self.prompt_str = None

    def get_tool_names(self, tools):
        res = ""
        for i in range(len(tools)):
            if i != len(tools)-1:
                res += f"'{tools[i].name}, '"
            else:
                res += f"'{tools[i].name}'"

    def generate_prompt(self, tools: List[Tool]):
        if (len(tools) < 1):
            raise ValueError(
                "Must provide at least 1 valid tool for this type of prompt")
        prompt = f'''{self.header}
        
Respond to the human as helpfully and accurately as possible. You have access to the following tools:
        
'''
        for tool in tools:
            prompt += tool.describe_tool() + "\n"

        prompt += f'''Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Respond to Human" or {self.get_tool_names(tools)}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: tool output - Note that this is the output from the tool and NOT actually the user
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Respond to Human",
  "action_input": "Final response to human"
}}

Begin! ALWAYS respond with a valid json blob of a single action.

Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation

If addressing the user you MUST use the 'Respond to Human' action.'''

        self.prompt_str = prompt
        return prompt
